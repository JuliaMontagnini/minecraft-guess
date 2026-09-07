import json

import re

import unicodedata

from uuid import uuid4

from sqlalchemy import text

from app.database import engine


CATEGORY_TO_ENTITY_TYPE = {
    "mobs": "mob",
    "biomes": "biome",
    "items": "item",
    "structures": "structure",
    "enchantments": "enchantment",
}


class GameError(Exception):
    pass

class GameNotFoundError(Exception):
    pass


MAX_LIVES = 5
MAX_HINTS = 4

def create_game(category: str):
    with engine.begin() as connection:

        if category == "random":
            secret = connection.execute(
                text(
                    """
                    SELECT
                        id,
                        entity_type
                    FROM entities
                    ORDER BY RAND()
                    LIMIT 1
                    """
                )
            ).mappings().first()

        else:
            entity_type = (
                CATEGORY_TO_ENTITY_TYPE.get(
                    category
                )
            )

            if entity_type is None:
                raise GameError(
                    "Categoria inválida."
                )

            secret = connection.execute(
                text(
                    """
                    SELECT
                        id,
                        entity_type
                    FROM entities
                    WHERE entity_type = :entity_type
                    ORDER BY RAND()
                    LIMIT 1
                    """
                ),
                {
                    "entity_type": entity_type,
                },
            ).mappings().first()

        if secret is None:
            raise GameError(
                "Nenhuma entidade disponível "
                "para esta categoria."
            )

        game_id = str(uuid4())

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
                    5,
                    'playing'
                )
                """
            ),
            {
                "game_id": game_id,
                "secret_entity_id":
                    secret["id"],

                "category":
                    category,
            },
        )

        return {
            "game_id": game_id,
            "category": category,
            "lives": 5,
            "max_lives": 5,
            "status": "playing",
        }

def normalize_guess(value: str) -> str:
    normalized = unicodedata.normalize(
        "NFKC",
        value,
    )

    normalized = " ".join(
        normalized.strip().split()
    )

    return normalized.casefold()

def load_payload(raw_payload):
    if isinstance(raw_payload, dict):
        return raw_payload

    if isinstance(raw_payload, str):
        return json.loads(raw_payload)

    raise GameError(
        "Payload da entidade armazenado "
        "em formato inválido."
    )


def add_hint_if_safe(
    hints: list[str],
    hint: str | None,
    secret_name: str,
):
    if not hint:
        return

    secret_pattern = re.compile(
        rf"(?<!\w){re.escape(secret_name)}(?!\w)",
        re.IGNORECASE,
    )

    if secret_pattern.search(hint):
        return

    if hint not in hints:
        hints.append(hint)


def build_hints(
    entity_type: str,
    payload: dict,
    secret_name: str,
) -> list[str]:
    hints: list[str] = []

    if entity_type == "mob":
        add_hint_if_safe(
            hints,
            f"Sou um mob do tipo {payload.get('type')}.",
            secret_name,
        )

        add_hint_if_safe(
            hints,
            (
                f"Tenho {payload.get('hp')} "
                "pontos de vida."
            ),
            secret_name,
        )

        spawn_biomes = payload.get(
            "spawnBiomes",
            [],
        )

        if spawn_biomes:
            add_hint_if_safe(
                hints,
                (
                    "Posso aparecer em biomas como "
                    + ", ".join(spawn_biomes[:3])
                    + "."
                ),
                secret_name,
            )

        weaknesses = payload.get(
            "weaknesses",
            [],
        )

        if weaknesses:
            add_hint_if_safe(
                hints,
                (
                    "Entre minhas fraquezas estão: "
                    + ", ".join(weaknesses[:2])
                    + "."
                ),
                secret_name,
            )

        add_hint_if_safe(
            hints,
            (
                "Sou domesticável."
                if payload.get("tameable")
                else "Não sou domesticável."
            ),
            secret_name,
        )

    elif entity_type == "biome":
        add_hint_if_safe(
            hints,
            (
                "Estou localizado na dimensão "
                f"{payload.get('dimension')}."
            ),
            secret_name,
        )

        add_hint_if_safe(
            hints,
            (
                "Minha precipitação é "
                f"{payload.get('precipitation')} "
                "e minha temperatura é "
                f"{payload.get('temperature')}."
            ),
            secret_name,
        )

        add_hint_if_safe(
            hints,
            (
                "Minha raridade é "
                f"{payload.get('rarity')}."
            ),
            secret_name,
        )

        terrain = payload.get(
            "terrainFeatures",
            [],
        )

        if terrain:
            add_hint_if_safe(
                hints,
                (
                    "Uma característica do meu "
                    f"terreno é: {terrain[0]}."
                ),
                secret_name,
            )

        structures = payload.get(
            "structuresFound",
            [],
        )

        if structures:
            add_hint_if_safe(
                hints,
                (
                    "Uma estrutura que pode aparecer "
                    f"aqui é {structures[0]}."
                ),
                secret_name,
            )

        unique_blocks = payload.get(
            "uniqueBlocks",
            [],
        )

        if unique_blocks:
            add_hint_if_safe(
                hints,
                (
                    "Um bloco característico "
                    "que pode aparecer em mim é "
                    f"{unique_blocks[0]}."
                ),
                secret_name,
            )

    elif entity_type == "item":
        add_hint_if_safe(
            hints,
            (
                "Sou um item da categoria "
                f"{payload.get('category')}."
            ),
            secret_name,
        )

        add_hint_if_safe(
            hints,
            (
                "Meu tamanho máximo de pilha é "
                f"{payload.get('stackSize')}."
            ),
            secret_name,
        )

        add_hint_if_safe(
            hints,
            (
                "Posso receber encantamentos."
                if payload.get("enchantable")
                else "Não posso receber encantamentos."
            ),
            secret_name,
        )

        obtained = payload.get(
            "obtainedBy",
            [],
        )

        if obtained:
            add_hint_if_safe(
                hints,
                (
                    "Uma forma de me obter é: "
                    f"{obtained[0]}."
                ),
                secret_name,
            )

        durability = payload.get(
            "durability"
        )

        if durability is not None:
            add_hint_if_safe(
                hints,
                (
                    "Minha durabilidade é "
                    f"{durability}."
                ),
                secret_name,
            )

    elif entity_type == "structure":
        add_hint_if_safe(
            hints,
            (
                "Estou localizada na dimensão "
                f"{payload.get('dimension')}."
            ),
            secret_name,
        )

        add_hint_if_safe(
            hints,
            (
                "Minha raridade é "
                f"{payload.get('rarity')}."
            ),
            secret_name,
        )

        y_level = payload.get(
            "yLevel",
            {},
        )

        if y_level:
            add_hint_if_safe(
                hints,
                (
                    "Posso aparecer aproximadamente "
                    "entre os níveis Y "
                    f"{y_level.get('min')} e "
                    f"{y_level.get('max')}."
                ),
                secret_name,
            )

        biomes = payload.get(
            "biomes",
            [],
        )

        if biomes:
            add_hint_if_safe(
                hints,
                (
                    "Um dos biomas em que posso "
                    f"aparecer é {biomes[0]}."
                ),
                secret_name,
            )

        dangers = payload.get(
            "dangers",
            [],
        )

        if dangers:
            add_hint_if_safe(
                hints,
                (
                    "Um perigo associado a mim é: "
                    f"{dangers[0]}."
                ),
                secret_name,
            )

    elif entity_type == "enchantment":
        add_hint_if_safe(
            hints,
            (
                "Meu nível máximo é "
                f"{payload.get('maxLevel')}."
            ),
            secret_name,
        )

        applicable = payload.get(
            "applicableItems",
            [],
        )

        if applicable:
            add_hint_if_safe(
                hints,
                (
                    "Posso ser aplicado em: "
                    + ", ".join(applicable[:3])
                    + "."
                ),
                secret_name,
            )

        add_hint_if_safe(
            hints,
            (
                "Sou um encantamento de tesouro."
                if payload.get("treasureOnly")
                else "Não sou exclusivo de tesouro."
            ),
            secret_name,
        )

        add_hint_if_safe(
            hints,
            (
                "Sou uma maldição."
                if payload.get("curseOf")
                else "Não sou uma maldição."
            ),
            secret_name,
        )

        obtained = payload.get(
            "obtainedFrom",
            [],
        )

        if obtained:
            add_hint_if_safe(
                hints,
                (
                    "Posso ser obtido através de "
                    f"{obtained[0]}."
                ),
                secret_name,
            )
        # -------------------------------------------------
    # FALLBACKS
    # Usados somente quando as dicas específicas
    # não são suficientes.
    # -------------------------------------------------

    if len(hints) < MAX_HINTS:
        category = payload.get(
            "category"
        )

        if category:
            add_hint_if_safe(
                hints,
                (
                    "Faço parte da categoria "
                    f"{category}."
                ),
                secret_name,
            )

    if len(hints) < MAX_HINTS:
        version_added = payload.get(
            "versionAdded"
        )

        if version_added:
            add_hint_if_safe(
                hints,
                (
                    "Estou presente no jogo "
                    "desde a versão "
                    f"{version_added}."
                ),
                secret_name,
            )
    return hints[:MAX_HINTS]

def submit_guess(
    game_id: str,
    guess: str,
):
    with engine.begin() as connection:
        game = connection.execute(
            text(
                """
                SELECT
                    g.id,
                    g.lives_remaining,
                    g.status,
                    e.name AS secret_name
                FROM games g
                JOIN entities e
                    ON e.id = g.secret_entity_id
                WHERE g.id = :game_id
                FOR UPDATE
                """
            ),
            {
                "game_id": game_id,
            },
        ).mappings().first()

        if game is None:
            raise GameNotFoundError(
                "Partida não encontrada."
            )

        if game["status"] != "playing":
            raise GameError(
                "Esta partida já terminou."
            )

        clean_guess = guess.strip()

        correct = (
            normalize_guess(clean_guess)
            ==
            normalize_guess(
                game["secret_name"]
            )
        )

        if correct:
            connection.execute(
                text(
                    """
                    INSERT INTO game_guesses (
                        game_id,
                        guess_text,
                        correct
                    )
                    VALUES (
                        :game_id,
                        :guess,
                        TRUE
                    )
                    """
                ),
                {
                    "game_id": game_id,
                    "guess": clean_guess,
                },
            )

            connection.execute(
                text(
                    """
                    UPDATE games
                    SET
                        status = 'won',
                        finished_at = CURRENT_TIMESTAMP
                    WHERE id = :game_id
                    """
                ),
                {
                    "game_id": game_id,
                },
            )

            return {
                "game_id": game_id,
                "correct": True,
                "lives": game[
                    "lives_remaining"
                ],
                "status": "won",
                "answer": game[
                    "secret_name"
                ],
            }

        new_lives = max(
            game["lives_remaining"] - 1,
            0,
        )

        new_status = (
            "lost"
            if new_lives == 0
            else "playing"
        )

        connection.execute(
            text(
                """
                INSERT INTO game_guesses (
                    game_id,
                    guess_text,
                    correct
                )
                VALUES (
                    :game_id,
                    :guess,
                    FALSE
                )
                """
            ),
            {
                "game_id": game_id,
                "guess": clean_guess,
            },
        )

        connection.execute(
            text(
                """
                UPDATE games
                SET
                    lives_remaining = :lives,
                    status = :status,
                    finished_at =
                        CASE
                            WHEN :status = 'lost'
                            THEN CURRENT_TIMESTAMP
                            ELSE finished_at
                        END
                WHERE id = :game_id
                """
            ),
            {
                "game_id": game_id,
                "lives": new_lives,
                "status": new_status,
            },
        )

        return {
            "game_id": game_id,
            "correct": False,
            "lives": new_lives,
            "status": new_status,

            "answer": (
                game["secret_name"]
                if new_status == "lost"
                else None
            ),
        }

def reveal_hint(
    game_id: str,
):
    with engine.begin() as connection:
        game = connection.execute(
            text(
                """
                SELECT
                    g.id,
                    g.lives_remaining,
                    g.status,
                    e.name AS secret_name,
                    e.entity_type,
                    e.raw_payload
                FROM games g
                JOIN entities e
                    ON e.id = g.secret_entity_id
                WHERE g.id = :game_id
                FOR UPDATE
                """
            ),
            {
                "game_id": game_id,
            },
        ).mappings().first()

        if game is None:
            raise GameNotFoundError(
                "Partida não encontrada."
            )

        if game["status"] != "playing":
            raise GameError(
                "Esta partida já terminou."
            )

        payload = load_payload(
            game["raw_payload"]
        )

        available_hints = build_hints(
            entity_type=game["entity_type"],
            payload=payload,
            secret_name=game["secret_name"],
        )

        used_hints = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM game_hints
                WHERE game_id = :game_id
                """
            ),
            {
                "game_id": game_id,
            },
        ).scalar_one()

        if used_hints >= len(
            available_hints
        ):
            raise GameError(
                "Não há mais dicas disponíveis."
            )

        hint_number = used_hints + 1

        hint_text = available_hints[
            used_hints
        ]

        new_lives = max(
            game["lives_remaining"] - 1,
            0,
        )

        new_status = (
            "lost"
            if new_lives == 0
            else "playing"
        )

        connection.execute(
            text(
                """
                INSERT INTO game_hints (
                    game_id,
                    hint_number,
                    hint_text
                )
                VALUES (
                    :game_id,
                    :hint_number,
                    :hint_text
                )
                """
            ),
            {
                "game_id": game_id,
                "hint_number": hint_number,
                "hint_text": hint_text,
            },
        )

        connection.execute(
            text(
                """
                UPDATE games
                SET
                    lives_remaining = :lives,
                    status = :status,
                    finished_at =
                        CASE
                            WHEN :status = 'lost'
                            THEN CURRENT_TIMESTAMP
                            ELSE finished_at
                        END
                WHERE id = :game_id
                """
            ),
            {
                "game_id": game_id,
                "lives": new_lives,
                "status": new_status,
            },
        )

        return {
            "game_id": game_id,
            "hint_number": hint_number,
            "hint": hint_text,
            "lives": new_lives,
            "status": new_status,

            "answer": (
                game["secret_name"]
                if new_status == "lost"
                else None
            ),
        }

def get_game_state(
    game_id: str,
):
    with engine.connect() as connection:
        game = connection.execute(
            text(
                """
                SELECT
                    g.id,
                    g.requested_category,
                    g.lives_remaining,
                    g.status,
                    e.name AS secret_name
                FROM games g
                JOIN entities e
                    ON e.id = g.secret_entity_id
                WHERE g.id = :game_id
                """
            ),
            {
                "game_id": game_id,
            },
        ).mappings().first()

        if game is None:
            raise GameNotFoundError(
                "Partida não encontrada."
            )

        guesses = connection.execute(
            text(
                """
                SELECT
                    guess_text,
                    correct
                FROM game_guesses
                WHERE game_id = :game_id
                ORDER BY id
                """
            ),
            {
                "game_id": game_id,
            },
        ).mappings().all()

        hints = connection.execute(
            text(
                """
                SELECT
                    hint_number,
                    hint_text
                FROM game_hints
                WHERE game_id = :game_id
                ORDER BY hint_number
                """
            ),
            {
                "game_id": game_id,
            },
        ).mappings().all()

        answer = (
            game["secret_name"]
            if game["status"] in (
                "won",
                "lost",
            )
            else None
        )

        return {
            "game_id": game["id"],

            "category":
                game["requested_category"],

            "lives":
                game["lives_remaining"],

            "max_lives": MAX_LIVES,

            "status":
                game["status"],

            "answer":
                answer,

            "guesses": [
                {
                    "guess":
                        guess["guess_text"],

                    "correct":
                        bool(
                            guess["correct"]
                        ),
                }
                for guess in guesses
            ],

            "hints": [
                {
                    "hint_number":
                        hint["hint_number"],

                    "hint":
                        hint["hint_text"],
                }
                for hint in hints
            ],
        }