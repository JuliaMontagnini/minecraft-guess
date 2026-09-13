from uuid import uuid4

import pytest
from sqlalchemy import text

from app.database import engine
from app.game_service import (
    MAX_HINTS,
    MAX_LIVES,
    GameError,
    create_game,
    get_game_state,
    reveal_hint,
    submit_guess,
)


# =========================================================
# FIXTURE DE LIMPEZA
# =========================================================


@pytest.fixture
def created_game_ids():
    """
    Guarda os IDs das partidas criadas durante cada
    teste e remove tudo do banco quando o teste termina.
    """

    game_ids: list[str] = []

    yield game_ids

    with engine.begin() as connection:
        for game_id in game_ids:
            connection.execute(
                text(
                    """
                    DELETE FROM game_hints
                    WHERE game_id = :game_id
                    """
                ),
                {
                    "game_id": game_id,
                },
            )

            connection.execute(
                text(
                    """
                    DELETE FROM game_guesses
                    WHERE game_id = :game_id
                    """
                ),
                {
                    "game_id": game_id,
                },
            )

            connection.execute(
                text(
                    """
                    DELETE FROM games
                    WHERE id = :game_id
                    """
                ),
                {
                    "game_id": game_id,
                },
            )

TEST_MEDIA_URL = (
    "https://example.com/"
    "minecraftguess-test-cow.png"
)


@pytest.fixture
def media_for_cow():
    """
    Instala uma mídia temporária para Cow e,
    ao final do teste, restaura o estado anterior.

    Nenhuma requisição HTTP externa é feita.
    """
    with engine.begin() as connection:
        entity_id = connection.execute(
            text(
                """
                SELECT id
                FROM entities
                WHERE
                    entity_type = 'mob'
                    AND name = 'Cow'
                LIMIT 1
                """
            )
        ).scalar_one()

        previous = connection.execute(
            text(
                """
                SELECT
                    source_page_url,
                    file_name,
                    image_url,
                    license_note
                FROM entity_media
                WHERE
                    entity_id = :entity_id
                    AND source =
                        'minecraft_wiki'
                """
            ),
            {
                "entity_id":
                    entity_id,
            },
        ).mappings().first()

        previous = (
            dict(previous)
            if previous is not None
            else None
        )

        connection.execute(
            text(
                """
                INSERT INTO entity_media (
                    entity_id,
                    source,
                    source_page_url,
                    file_name,
                    image_url,
                    license_note
                )
                VALUES (
                    :entity_id,
                    'minecraft_wiki',
                    'https://minecraft.wiki/w/Cow',
                    'test-file.png',
                    :image_url,
                    'test'
                )

                ON DUPLICATE KEY UPDATE
                    source_page_url =
                        VALUES(source_page_url),

                    file_name =
                        VALUES(file_name),

                    image_url =
                        VALUES(image_url),

                    license_note =
                        VALUES(license_note)
                """
            ),
            {
                "entity_id":
                    entity_id,

                "image_url":
                    TEST_MEDIA_URL,
            },
        )

    yield TEST_MEDIA_URL

    with engine.begin() as connection:
        if previous is None:
            connection.execute(
                text(
                    """
                    DELETE FROM entity_media
                    WHERE
                        entity_id =
                            :entity_id
                        AND source =
                            'minecraft_wiki'
                    """
                ),
                {
                    "entity_id":
                        entity_id,
                },
            )
        else:
            connection.execute(
                text(
                    """
                    UPDATE entity_media
                    SET
                        source_page_url =
                            :source_page_url,

                        file_name =
                            :file_name,

                        image_url =
                            :image_url,

                        license_note =
                            :license_note

                    WHERE
                        entity_id =
                            :entity_id
                        AND source =
                            'minecraft_wiki'
                    """
                ),
                {
                    "entity_id":
                        entity_id,

                    **previous,
                },
            )

# =========================================================
# HELPERS
# =========================================================


def create_game_for_entity(
    entity_name: str,
    category: str,
    created_game_ids: list[str],
) -> dict:
    """
    Cria uma partida determinística para uma entidade.

    Isso é útil porque create_game() escolhe o segredo
    aleatoriamente, enquanto alguns testes precisam
    saber exatamente qual é a resposta.
    """

    game_id = str(
        uuid4()
    )

    with engine.begin() as connection:
        entity = connection.execute(
            text(
                """
                SELECT
                    e.id,
                    e.name,
                    e.entity_type,
                    t.translated_name

                FROM entities e

                JOIN entity_translations t
                    ON t.entity_id = e.id
                    AND t.locale = 'pt-BR'

                WHERE e.name = :entity_name

                LIMIT 1
                """
            ),
            {
                "entity_name":
                    entity_name,
            },
        ).mappings().first()

        assert entity is not None, (
            f"Entidade de teste não encontrada: "
            f"{entity_name}"
        )

        connection.execute(
            text(
                """
                INSERT INTO games (
                    id,
                    secret_entity_id,
                    requested_category,
                    lives_remaining,
                    status
                )
                VALUES (
                    :game_id,
                    :secret_entity_id,
                    :category,
                    :max_lives,
                    'playing'
                )
                """
            ),
            {
                "game_id":
                    game_id,

                "secret_entity_id":
                    entity["id"],

                "category":
                    category,

                "max_lives":
                    MAX_LIVES,
            },
        )

    created_game_ids.append(
        game_id
    )

    return {
        "game_id":
            game_id,

        "english_name":
            entity["name"],

        "portuguese_name":
            entity["translated_name"],
    }


# =========================================================
# CRIAÇÃO DA PARTIDA
# =========================================================


def test_new_game_starts_with_ten_lives(
    created_game_ids,
):
    game = create_game(
        "mobs"
    )

    created_game_ids.append(
        game["game_id"]
    )

    assert game["lives"] == 10
    assert game["max_lives"] == 10

    assert game["lives"] == (
        MAX_LIVES
    )

    assert game["status"] == (
        "playing"
    )

    assert game["category"] == (
        "mobs"
    )


def test_invalid_category_is_rejected():
    with pytest.raises(
        GameError
    ):
        create_game(
            "invalid-category"
        )


# =========================================================
# SEGREDO NÃO PODE VAZAR
# =========================================================


def test_secret_is_hidden_while_playing(
    created_game_ids,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    state = get_game_state(
        game["game_id"]
    )

    assert state["status"] == (
        "playing"
    )

    assert state["answer"] is None


# =========================================================
# RESPOSTAS EM INGLÊS E PORTUGUÊS
# =========================================================


def test_english_answer_is_accepted(
    created_game_ids,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    result = submit_guess(
        game["game_id"],
        game["english_name"],
    )

    assert result["correct"] is True
    assert result["status"] == "won"

    # Mesmo acertando em inglês,
    # a resposta revelada deve ser pt-BR.
    assert result["answer"] == (
        game["portuguese_name"]
    )


def test_portuguese_answer_is_accepted(
    created_game_ids,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    result = submit_guess(
        game["game_id"],
        game["portuguese_name"],
    )

    assert result["correct"] is True
    assert result["status"] == "won"

    assert result["answer"] == (
        game["portuguese_name"]
    )


# =========================================================
# PALPITES ERRADOS
# =========================================================


def test_wrong_guess_removes_one_life(
    created_game_ids,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    result = submit_guess(
        game["game_id"],
        "__resposta_completamente_errada__",
    )

    assert result["correct"] is False

    assert result["lives"] == (
        MAX_LIVES - 1
    )

    assert result["status"] == (
        "playing"
    )

    assert result["answer"] is None


# =========================================================
# DICAS
# =========================================================


def test_hint_removes_one_life_and_is_persisted(
    created_game_ids,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    hint_result = reveal_hint(
        game["game_id"]
    )

    assert hint_result["hint_number"] == 1

    assert hint_result["lives"] == (
        MAX_LIVES - 1
    )

    assert hint_result["status"] == (
        "playing"
    )

    state = get_game_state(
        game["game_id"]
    )

    assert state["lives"] == (
        MAX_LIVES - 1
    )

    assert len(
        state["hints"]
    ) == 1

    assert (
        state["hints"][0]["hint"]
        ==
        hint_result["hint"]
    )


def test_sixth_hint_is_rejected(
    created_game_ids,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    for _ in range(
        MAX_HINTS
    ):
        reveal_hint(
            game["game_id"]
        )

    state = get_game_state(
        game["game_id"]
    )

    assert len(
        state["hints"]
    ) == MAX_HINTS

    assert state["lives"] == (
        MAX_LIVES - MAX_HINTS
    )

    with pytest.raises(
        GameError,
        match=(
            "Não há mais dicas "
            "disponíveis"
        ),
    ):
        reveal_hint(
            game["game_id"]
        )


# =========================================================
# DERROTA
# =========================================================


def test_game_is_lost_after_ten_wrong_guesses(
    created_game_ids,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    result = None

    for attempt in range(
        1,
        MAX_LIVES + 1,
    ):
        result = submit_guess(
            game["game_id"],
            (
                "__resposta_errada_"
                f"{attempt}__"
            ),
        )

        assert result["lives"] == (
            MAX_LIVES - attempt
        )

    assert result is not None

    assert result["lives"] == 0
    assert result["status"] == "lost"

    assert result["answer"] == (
        game["portuguese_name"]
    )


# =========================================================
# RECUPERAÇÃO DE ESTADO / F5
# =========================================================


def test_game_state_restores_history(
    created_game_ids,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    hint_result = reveal_hint(
        game["game_id"]
    )

    wrong_guess = (
        "__palpite_errado_para_historico__"
    )

    submit_guess(
        game["game_id"],
        wrong_guess,
    )

    state = get_game_state(
        game["game_id"]
    )

    # Uma dica + um palpite errado.
    assert state["lives"] == (
        MAX_LIVES - 2
    )

    assert state["status"] == (
        "playing"
    )

    assert state["answer"] is None

    assert len(
        state["hints"]
    ) == 1

    assert state["hints"][0] == {
        "hint_number": 1,
        "hint": hint_result["hint"],
    }

    assert len(
        state["guesses"]
    ) == 1

    assert state["guesses"][0] == {
        "guess":
            wrong_guess,

        "correct":
            False,
    }

def test_playing_game_does_not_reveal_image(
    created_game_ids,
    media_for_cow,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    state = get_game_state(
        game["game_id"]
    )

    assert state["status"] == "playing"

    assert state[
        "answer_image_url"
    ] is None

    assert (
        "source_page_url"
        not in state
    )

def test_won_game_can_reveal_image(
    created_game_ids,
    media_for_cow,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    result = submit_guess(
        game["game_id"],
        game["english_name"],
    )

    assert result["status"] == "won"

    assert (
        result["answer_image_url"]
        == media_for_cow
    )

def test_lost_game_can_reveal_image(
    created_game_ids,
    media_for_cow,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    result = None

    for attempt in range(
        1,
        MAX_LIVES + 1,
    ):
        result = submit_guess(
            game["game_id"],
            (
                "__erro_media_"
                f"{attempt}__"
            ),
        )

    assert result is not None
    assert result["status"] == "lost"

    assert (
        result["answer_image_url"]
        == media_for_cow
    )

def test_game_state_restores_image_after_finish(
    created_game_ids,
    media_for_cow,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    result = submit_guess(
        game["game_id"],
        game["portuguese_name"],
    )

    assert result["status"] == "won"

    state = get_game_state(
        game["game_id"]
    )

    assert state["status"] == "won"

    assert (
        state["answer_image_url"]
        == media_for_cow
    )

def test_missing_image_does_not_break_game(
    created_game_ids,
    media_for_cow,
):
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                DELETE m
                FROM entity_media m

                JOIN entities e
                    ON e.id =
                        m.entity_id

                WHERE
                    e.name = 'Cow'
                    AND e.entity_type = 'mob'
                    AND m.source =
                        'minecraft_wiki'
                """
            )
        )

    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    result = submit_guess(
        game["game_id"],
        game["english_name"],
    )

    assert result["status"] == "won"

    assert result["answer"] == (
        game["portuguese_name"]
    )

    assert (
        result["answer_image_url"]
        is None
    )

def test_hint_is_blocked_with_one_hp(
    created_game_ids,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE games
                SET lives_remaining = 1
                WHERE id = :game_id
                """
            ),
            {
                "game_id":
                    game["game_id"],
            },
        )

    with pytest.raises(
        GameError,
        match="pelo menos 2 HP",
    ):
        reveal_hint(
            game["game_id"]
        )

    state = get_game_state(
        game["game_id"]
    )

    assert state["lives"] == 1
    assert state["status"] == "playing"
    assert state["hints"] == []

def test_hint_is_allowed_with_two_hp(
    created_game_ids,
):
    game = create_game_for_entity(
        entity_name="Cow",
        category="mobs",
        created_game_ids=
            created_game_ids,
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE games
                SET lives_remaining = 2
                WHERE id = :game_id
                """
            ),
            {
                "game_id":
                    game["game_id"],
            },
        )

    result = reveal_hint(
        game["game_id"]
    )

    assert result["lives"] == 1
    assert result["status"] == "playing"