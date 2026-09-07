import json
import re
import unicodedata
from uuid import uuid4

from sqlalchemy import text

from app.database import engine
from app.localization import (
    translate_game_text,
    translate_reference,
    translate_references,
    translate_value,
)


# =========================================================
# CONFIGURAÇÕES DO JOGO
# =========================================================

MAX_LIVES = 10
MAX_HINTS = 5


CATEGORY_TO_ENTITY_TYPE = {
    "mobs": "mob",
    "biomes": "biome",
    "items": "item",
    "structures": "structure",
    "enchantments": "enchantment",
}


# =========================================================
# EXCEÇÕES
# =========================================================


class GameError(Exception):
    pass


class GameNotFoundError(GameError):
    pass


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================


def normalize_guess(
    value: str,
) -> str:
    """
    Normaliza um palpite para permitir comparações
    mais amigáveis.

    Exemplos equivalentes:
        Vaca
        vaca
        VACA

    Também remove acentos:
        Câmaras
        Camaras
    """

    normalized = unicodedata.normalize(
        "NFKD",
        value,
    )

    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(
            character
        )
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized.strip(),
    )

    return normalized.casefold()


def load_payload(
    raw_payload,
) -> dict:
    """
    Converte o JSON salvo no MySQL para dict.
    """

    if raw_payload is None:
        return {}

    if isinstance(
        raw_payload,
        dict,
    ):
        return raw_payload

    if isinstance(
        raw_payload,
        str,
    ):
        return json.loads(
            raw_payload
        )

    return dict(
        raw_payload
    )


def add_hint_if_safe(
    hints: list[str],
    hint: str,
    secret_name: str,
) -> None:
    """
    Adiciona uma dica somente se ela não revelar
    diretamente o nome secreto.
    """

    if not hint:
        return

    clean_hint = hint.strip()

    if not clean_hint:
        return

    secret_pattern = re.compile(
        rf"(?<!\w)"
        rf"{re.escape(secret_name)}"
        rf"(?!\w)",
        flags=re.IGNORECASE,
    )

    if secret_pattern.search(
        clean_hint
    ):
        return

    if clean_hint in hints:
        return

    hints.append(
        clean_hint
    )


def load_name_translations(
    connection,
) -> dict[str, str]:
    """
    Carrega os nomes pt-BR das entidades.

    Exemplo:
        cow -> Vaca
        jungle -> Selva
        crafting table -> Bancada de Trabalho
    """

    rows = connection.execute(
        text(
            """
            SELECT
                e.name,
                t.translated_name

            FROM entities e

            JOIN entity_translations t
                ON t.entity_id = e.id

            WHERE t.locale = 'pt-BR'
            """
        )
    ).mappings().all()

    return {
        row["name"].casefold():
            row["translated_name"]

        for row in rows
    }


# =========================================================
# GERAÇÃO DE DICAS
# =========================================================


def build_hints(
    entity_type: str,
    payload: dict,
    secret_name: str,
    name_translations:
        dict[str, str] | None = None,
) -> list[str]:
    """
    Gera dicas para uma entidade.

    As dicas são criadas em ordem de prioridade.
    Apenas as MAX_HINTS primeiras dicas seguras
    são disponibilizadas.
    """

    name_translations = (
        name_translations or {}
    )

    hints: list[str] = []

    # =====================================================
    # MOBS
    # =====================================================

    if entity_type == "mob":
        mob_type = payload.get(
            "type"
        )

        if mob_type:
            add_hint_if_safe(
                hints,
                (
                    "Sou um mob do tipo "
                    f"{translate_value(mob_type)}."
                ),
                secret_name,
            )

        hp = payload.get(
            "hp"
        )

        if hp is not None:
            add_hint_if_safe(
                hints,
                (
                    f"Tenho {hp} "
                    "pontos de vida."
                ),
                secret_name,
            )

        spawn_biomes = payload.get(
            "spawnBiomes",
            [],
        )

        if spawn_biomes:
            translated_locations = [
                translate_game_text(
                    location,
                    name_translations,
                )
                for location
                in spawn_biomes[:3]
            ]

            add_hint_if_safe(
                hints,
                (
                    "Posso aparecer em locais como "
                    + ", ".join(
                        translated_locations
                    )
                    + "."
                ),
                secret_name,
            )

        weaknesses = payload.get(
            "weaknesses",
            [],
        )

        if weaknesses:
            translated_weaknesses = [
                translate_game_text(
                    weakness,
                    name_translations,
                )
                for weakness
                in weaknesses[:2]
            ]

            add_hint_if_safe(
                hints,
                (
                    "Entre minhas fraquezas estão: "
                    + ", ".join(
                        translated_weaknesses
                    )
                    + "."
                ),
                secret_name,
            )

        tameable = payload.get(
            "tameable"
        )

        if tameable is not None:
            tameable_hint = (
                "Sou domesticável."
                if tameable
                else "Não sou domesticável."
            )

            add_hint_if_safe(
                hints,
                tameable_hint,
                secret_name,
            )

    # =====================================================
    # BIOMAS
    # =====================================================

    elif entity_type == "biome":
        dimension = payload.get(
            "dimension"
        )

        if dimension:
            add_hint_if_safe(
                hints,
                (
                    "Estou localizado na dimensão "
                    f"{translate_value(dimension)}."
                ),
                secret_name,
            )

        precipitation = payload.get(
            "precipitation"
        )

        temperature = payload.get(
            "temperature"
        )

        if (
            precipitation is not None
            or temperature is not None
        ):
            precipitation_text = (
                translate_value(
                    precipitation
                )
                if precipitation
                else "desconhecida"
            )

            add_hint_if_safe(
                hints,
                (
                    "Minha precipitação é "
                    f"{precipitation_text} "
                    "e minha temperatura é "
                    f"{temperature}."
                ),
                secret_name,
            )

        rarity = payload.get(
            "rarity"
        )

        if rarity:
            add_hint_if_safe(
                hints,
                (
                    "Minha raridade é "
                    f"{translate_value(rarity)}."
                ),
                secret_name,
            )

        terrain = payload.get(
            "terrainFeatures",
            [],
        )

        if terrain:
            translated_terrain = (
                translate_game_text(
                    terrain[0],
                    name_translations,
                )
            )

            add_hint_if_safe(
                hints,
                (
                    "Uma característica do meu "
                    "terreno é: "
                    f"{translated_terrain}."
                ),
                secret_name,
            )

        structures = payload.get(
            "structuresFound",
            [],
        )

        if structures:
            translated_structure = (
                translate_game_text(
                    structures[0],
                    name_translations,
                )
            )

            add_hint_if_safe(
                hints,
                (
                    "Uma estrutura que pode "
                    "aparecer aqui é "
                    f"{translated_structure}."
                ),
                secret_name,
            )

        unique_blocks = payload.get(
            "uniqueBlocks",
            [],
        )

        if unique_blocks:
            translated_block = (
                translate_game_text(
                    unique_blocks[0],
                    name_translations,
                )
            )

            add_hint_if_safe(
                hints,
                (
                    "Um bloco característico "
                    "que pode aparecer em mim é "
                    f"{translated_block}."
                ),
                secret_name,
            )

    # =====================================================
    # ITENS
    # =====================================================

    elif entity_type == "item":
        category = payload.get(
            "category"
        )

        if category:
            add_hint_if_safe(
                hints,
                (
                    "Faço parte da categoria "
                    f"{translate_value(category)}."
                ),
                secret_name,
            )

        stack_size = payload.get(
            "stackSize"
        )

        if stack_size is not None:
            if stack_size == 1:
                stack_hint = (
                    "Não posso ser empilhado "
                    "com outro item igual."
                )

            else:
                stack_hint = (
                    "Posso ser empilhado em "
                    f"até {stack_size} unidades."
                )

            add_hint_if_safe(
                hints,
                stack_hint,
                secret_name,
            )

        enchantable = payload.get(
            "enchantable"
        )

        if enchantable is not None:
            if enchantable:
                enchant_hint = (
                    "Posso receber "
                    "encantamentos."
                )

            else:
                enchant_hint = (
                    "Normalmente não recebo "
                    "encantamentos."
                )

            add_hint_if_safe(
                hints,
                enchant_hint,
                secret_name,
            )

        applicable_enchantments = (
            payload.get(
                "applicableEnchantments",
                [],
            )
        )

        if applicable_enchantments:
            translated_enchantments = [
                translate_game_text(
                    enchantment,
                    name_translations,
                )
                for enchantment
                in applicable_enchantments[:2]
            ]

            add_hint_if_safe(
                hints,
                (
                    "Entre os encantamentos "
                    "que podem ser usados em mim "
                    "estão "
                    + ", ".join(
                        translated_enchantments
                    )
                    + "."
                ),
                secret_name,
            )

        obtained_by = payload.get(
            "obtainedBy",
            [],
        )

        if obtained_by:
            translated_methods = [
                translate_game_text(
                    method,
                    name_translations,
                )
                for method
                in obtained_by[:2]
            ]

            add_hint_if_safe(
                hints,
                (
                    "Uma forma de me obter é: "
                    + ", ".join(
                        translated_methods
                    )
                    + "."
                ),
                secret_name,
            )

        durability = payload.get(
            "durability"
        )

        if durability:
            add_hint_if_safe(
                hints,
                (
                    "Minha durabilidade é de "
                    f"{durability} usos."
                ),
                secret_name,
            )

        food_value = payload.get(
            "foodValue"
        )

        if food_value:
            hunger = food_value.get(
                "hunger"
            )

            saturation = (
                food_value.get(
                    "saturation"
                )
            )

            if hunger is not None:
                add_hint_if_safe(
                    hints,
                    (
                        "Sou consumível e recupero "
                        f"{hunger} pontos de fome."
                    ),
                    secret_name,
                )

            if saturation is not None:
                add_hint_if_safe(
                    hints,
                    (
                        "Meu valor de saturação "
                        f"é {saturation}."
                    ),
                    secret_name,
                )

        fuel_value = payload.get(
            "fuelValue"
        )

        if fuel_value:
            add_hint_if_safe(
                hints,
                (
                    "Também posso ser utilizado "
                    "como combustível."
                ),
                secret_name,
            )

        recipe = payload.get(
            "craftingRecipe"
        )

        if recipe:
            station = recipe.get(
                "station"
            )

            ingredients = recipe.get(
                "ingredients",
                {},
            )

            if station:
                translated_station = (
                    translate_reference(
                        station,
                        name_translations,
                    )
                )

                add_hint_if_safe(
                    hints,
                    (
                        "Minha fabricação utiliza "
                        f"{translated_station}."
                    ),
                    secret_name,
                )

            if ingredients:
                ingredient_names = []

                for ingredient in (
                    list(
                        ingredients.keys()
                    )[:3]
                ):
                    ingredient_names.append(
                        translate_game_text(
                            ingredient,
                            name_translations,
                        )
                    )

                if ingredient_names:
                    add_hint_if_safe(
                        hints,
                        (
                            "Minha receita pode "
                            "utilizar: "
                            + ", ".join(
                                ingredient_names
                            )
                            + "."
                        ),
                        secret_name,
                    )

    # =====================================================
    # ESTRUTURAS
    # =====================================================

    elif entity_type == "structure":
        dimension = payload.get(
            "dimension"
        )

        if dimension:
            add_hint_if_safe(
                hints,
                (
                    "Estou localizado na dimensão "
                    f"{translate_value(dimension)}."
                ),
                secret_name,
            )

        rarity = payload.get(
            "rarity"
        )

        if rarity:
            add_hint_if_safe(
                hints,
                (
                    "Minha raridade é "
                    f"{translate_value(rarity)}."
                ),
                secret_name,
            )

        y_level = payload.get(
            "yLevel"
        )

        if isinstance(
            y_level,
            dict,
        ):
            minimum = y_level.get(
                "min"
            )

            maximum = y_level.get(
                "max"
            )

            if (
                minimum is not None
                and maximum is not None
            ):
                add_hint_if_safe(
                    hints,
                    (
                        "Posso aparecer aproximadamente "
                        "entre os níveis Y "
                        f"{minimum} e {maximum}."
                    ),
                    secret_name,
                )

        biomes = payload.get(
            "biomes",
            [],
        )

        if biomes:
            translated_biomes = [
                translate_game_text(
                    biome,
                    name_translations,
                )
                for biome
                in biomes[:3]
            ]

            add_hint_if_safe(
                hints,
                (
                    "Posso aparecer em biomas como "
                    + ", ".join(
                        translated_biomes
                    )
                    + "."
                ),
                secret_name,
            )

        dangers = payload.get(
            "dangers",
            [],
        )

        if dangers:
            translated_danger = (
                translate_game_text(
                    dangers[0],
                    name_translations,
                )
            )

            add_hint_if_safe(
                hints,
                (
                    "Um perigo associado a mim é: "
                    f"{translated_danger}."
                ),
                secret_name,
            )

    # =====================================================
    # ENCANTAMENTOS
    # =====================================================

    elif entity_type == "enchantment":
        max_level = payload.get(
            "maxLevel"
        )

        if max_level is not None:
            add_hint_if_safe(
                hints,
                (
                    "Meu nível máximo é "
                    f"{max_level}."
                ),
                secret_name,
            )

        applicable = payload.get(
            "applicableItems",
            [],
        )

        if applicable:
            translated_applicable = [
                translate_game_text(
                    item,
                    name_translations,
                )
                for item
                in applicable[:3]
            ]

            add_hint_if_safe(
                hints,
                (
                    "Posso ser aplicado em: "
                    + ", ".join(
                        translated_applicable
                    )
                    + "."
                ),
                secret_name,
            )

        treasure_only = payload.get(
            "treasureOnly"
        )

        if treasure_only is not None:
            add_hint_if_safe(
                hints,
                (
                    "Sou um encantamento de tesouro."
                    if treasure_only
                    else (
                        "Não sou exclusivo "
                        "de tesouro."
                    )
                ),
                secret_name,
            )

        curse = payload.get(
            "curseOf"
        )

        if curse is not None:
            add_hint_if_safe(
                hints,
                (
                    "Sou uma maldição."
                    if curse
                    else "Não sou uma maldição."
                ),
                secret_name,
            )

        obtained = payload.get(
            "obtainedFrom",
            [],
        )

        if obtained:
            translated_obtained = [
                translate_game_text(
                    method,
                    name_translations,
                )
                for method
                in obtained[:2]
            ]

            add_hint_if_safe(
                hints,
                (
                    "Posso ser obtido através de "
                    + ", ".join(
                        translated_obtained
                    )
                    + "."
                ),
                secret_name,
            )

    # =====================================================
    # FALLBACKS
    #
    # Só entram se os campos específicos acima não
    # produzirem 5 dicas seguras.
    # =====================================================

    if len(hints) < MAX_HINTS:
        category = payload.get(
            "category"
        )

        if category:
            add_hint_if_safe(
                hints,
                (
                    "Faço parte da categoria "
                    f"{translate_value(category)}."
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


# =========================================================
# CRIAÇÃO DE PARTIDA
# =========================================================


def create_game(
    category: str,
) -> dict:
    if (
        category != "random"
        and category
        not in CATEGORY_TO_ENTITY_TYPE
    ):
        raise GameError(
            "Categoria inválida."
        )

    game_id = str(
        uuid4()
    )

    with engine.begin() as connection:
        if category == "random":
            secret = connection.execute(
                text(
                    """
                    SELECT
                        id,
                        entity_type,
                        name

                    FROM entities

                    ORDER BY RAND()

                    LIMIT 1
                    """
                )
            ).mappings().first()

        else:
            entity_type = (
                CATEGORY_TO_ENTITY_TYPE[
                    category
                ]
            )

            secret = connection.execute(
                text(
                    """
                    SELECT
                        id,
                        entity_type,
                        name

                    FROM entities

                    WHERE entity_type =
                        :entity_type

                    ORDER BY RAND()

                    LIMIT 1
                    """
                ),
                {
                    "entity_type":
                        entity_type,
                },
            ).mappings().first()

        if secret is None:
            raise GameError(
                "Não há entidades disponíveis "
                "para esta categoria."
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
                    secret["id"],

                "category":
                    category,

                "max_lives":
                    MAX_LIVES,
            },
        )

    return {
        "game_id":
            game_id,

        "category":
            category,

        "lives":
            MAX_LIVES,

        "max_lives":
            MAX_LIVES,

        "status":
            "playing",
    }


# =========================================================
# PALPITE
# =========================================================


def submit_guess(
    game_id: str,
    guess: str,
) -> dict:
    with engine.begin() as connection:
        game = connection.execute(
            text(
                """
                SELECT
                    g.id,
                    g.lives_remaining,
                    g.status,

                    e.name
                        AS secret_name,

                    (
                        SELECT
                            t.translated_name

                        FROM entity_translations t

                        WHERE
                            t.entity_id = e.id
                            AND t.locale = 'pt-BR'

                        LIMIT 1
                    )
                        AS translated_secret_name

                FROM games g

                JOIN entities e
                    ON e.id =
                        g.secret_entity_id

                WHERE g.id = :game_id

                FOR UPDATE
                """
            ),
            {
                "game_id":
                    game_id,
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

        clean_guess = (
            guess.strip()
        )

        if not clean_guess:
            raise GameError(
                "Informe um palpite."
            )

        normalized_guess = (
            normalize_guess(
                clean_guess
            )
        )

        normalized_secret_en = (
            normalize_guess(
                game["secret_name"]
            )
        )

        translated_secret = (
            game[
                "translated_secret_name"
            ]
            or game["secret_name"]
        )

        normalized_secret_pt = (
            normalize_guess(
                translated_secret
            )
        )

        correct = (
            normalized_guess
            in {
                normalized_secret_en,
                normalized_secret_pt,
            }
        )

        # -------------------------------------------------
        # ACERTO
        # -------------------------------------------------

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
                    "game_id":
                        game_id,

                    "guess":
                        clean_guess,
                },
            )

            connection.execute(
                text(
                    """
                    UPDATE games

                    SET
                        status = 'won',
                        finished_at =
                            CURRENT_TIMESTAMP

                    WHERE id = :game_id
                    """
                ),
                {
                    "game_id":
                        game_id,
                },
            )

            return {
                "game_id":
                    game_id,

                "correct":
                    True,

                "lives":
                    game[
                        "lives_remaining"
                    ],

                "status":
                    "won",

                "answer":
                    translated_secret,
            }

        # -------------------------------------------------
        # ERRO
        # -------------------------------------------------

        new_lives = max(
            0,
            game["lives_remaining"] - 1,
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
                "game_id":
                    game_id,

                "guess":
                    clean_guess,
            },
        )

        connection.execute(
            text(
                """
                UPDATE games

                SET
                    lives_remaining =
                        :lives,

                    status =
                        :status,

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
                "game_id":
                    game_id,

                "lives":
                    new_lives,

                "status":
                    new_status,
            },
        )

        answer = (
            translated_secret
            if new_status == "lost"
            else None
        )

        return {
            "game_id":
                game_id,

            "correct":
                False,

            "lives":
                new_lives,

            "status":
                new_status,

            "answer":
                answer,
        }


# =========================================================
# NOVA DICA
# =========================================================


def reveal_hint(
    game_id: str,
) -> dict:
    with engine.begin() as connection:
        game = connection.execute(
            text(
                """
                SELECT
                    g.id,
                    g.lives_remaining,
                    g.status,

                    e.entity_type,
                    e.name
                        AS secret_name,

                    e.raw_payload,

                    (
                        SELECT
                            t.translated_name

                        FROM entity_translations t

                        WHERE
                            t.entity_id = e.id
                            AND t.locale = 'pt-BR'

                        LIMIT 1
                    )
                        AS translated_secret_name

                FROM games g

                JOIN entities e
                    ON e.id =
                        g.secret_entity_id

                WHERE g.id = :game_id

                FOR UPDATE
                """
            ),
            {
                "game_id":
                    game_id,
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

        name_translations = (
            load_name_translations(
                connection
            )
        )

        available_hints = build_hints(
            entity_type=
                game["entity_type"],

            payload=
                payload,

            secret_name=
                game["secret_name"],

            name_translations=
                name_translations,
        )

        hints_used = connection.execute(
            text(
                """
                SELECT COUNT(*)

                FROM game_hints

                WHERE game_id = :game_id
                """
            ),
            {
                "game_id":
                    game_id,
            },
        ).scalar_one()

        if (
            hints_used >= MAX_HINTS
            or hints_used
            >= len(available_hints)
        ):
            raise GameError(
                "Não há mais dicas disponíveis."
            )

        hint_number = (
            hints_used + 1
        )

        hint_text = (
            available_hints[
                hints_used
            ]
        )

        new_lives = max(
            0,
            game["lives_remaining"] - 1,
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
                "game_id":
                    game_id,

                "hint_number":
                    hint_number,

                "hint_text":
                    hint_text,
            },
        )

        connection.execute(
            text(
                """
                UPDATE games

                SET
                    lives_remaining =
                        :lives,

                    status =
                        :status,

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
                "game_id":
                    game_id,

                "lives":
                    new_lives,

                "status":
                    new_status,
            },
        )

        translated_secret = (
            game[
                "translated_secret_name"
            ]
            or game["secret_name"]
        )

        answer = (
            translated_secret
            if new_status == "lost"
            else None
        )

        return {
            "game_id":
                game_id,

            "hint_number":
                hint_number,

            "hint":
                hint_text,

            "lives":
                new_lives,

            "status":
                new_status,

            "answer":
                answer,
        }


# =========================================================
# RECUPERAR ESTADO DA PARTIDA
# =========================================================


def get_game_state(
    game_id: str,
) -> dict:
    with engine.connect() as connection:
        game = connection.execute(
            text(
                """
                SELECT
                    g.id,
                    g.requested_category,
                    g.lives_remaining,
                    g.status,

                    e.name
                        AS secret_name,

                    (
                        SELECT
                            t.translated_name

                        FROM entity_translations t

                        WHERE
                            t.entity_id = e.id
                            AND t.locale = 'pt-BR'

                        LIMIT 1
                    )
                        AS translated_secret_name

                FROM games g

                JOIN entities e
                    ON e.id =
                        g.secret_entity_id

                WHERE g.id = :game_id
                """
            ),
            {
                "game_id":
                    game_id,
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
                "game_id":
                    game_id,
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
                "game_id":
                    game_id,
            },
        ).mappings().all()

    display_name = (
        game[
            "translated_secret_name"
        ]
        or game["secret_name"]
    )

    answer = (
        display_name
        if game["status"]
        in (
            "won",
            "lost",
        )
        else None
    )

    return {
        "game_id":
            game["id"],

        "category":
            game[
                "requested_category"
            ],

        "lives":
            game[
                "lives_remaining"
            ],

        "max_lives":
            MAX_LIVES,

        "status":
            game["status"],

        "answer":
            answer,

        "guesses": [
            {
                "guess":
                    guess[
                        "guess_text"
                    ],

                "correct":
                    bool(
                        guess[
                            "correct"
                        ]
                    ),
            }
            for guess in guesses
        ],

        "hints": [
            {
                "hint_number":
                    hint[
                        "hint_number"
                    ],

                "hint":
                    hint[
                        "hint_text"
                    ],
            }
            for hint in hints
        ],
    }