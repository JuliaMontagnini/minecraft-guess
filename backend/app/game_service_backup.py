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


MAX_LIVES = 10
MAX_HINTS = 5

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
                    :max_lives,
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
                "max_lives":
                    MAX_LIVES,
            },
        )

        return {
            "game_id": game_id,
            "category": category,
            "lives": MAX_LIVES,
            "max_lives": MAX_LIVES,
            "status": "playing",
        }

def normalize_guess(value: str) -> str:
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

def load_name_translations(
    connection,
) -> dict[str, str]:
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

def build_hints(
    entity_type: str,
    payload: dict,
    secret_name: str,
    name_translations: dict[str, str] | None = None,
) -> list[str]:
    name_translations = (
        name_translations or {}
    )

    hints: list[str] = []

    if entity_type == "mob":
        add_hint_if_safe(
            hints,
            f"Sou um mob do tipo {translate_value(payload.get('type'))}.",
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
            translated_locations = (
                translate_references(
                    spawn_biomes[:3],
                    name_translations,
                )
            )

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
                f"{translate_value(payload.get('dimension'))}"
            ),
            secret_name,
        )

        add_hint_if_safe(
            hints,
            (
                "Minha precipitação é "
                f"{translate_value(payload.get('precipitation'))} "
                "e minha temperatura é "
                f"{payload.get('temperature')}."
            ),
            secret_name,
        )

        add_hint_if_safe(
            hints,
            (
                "Minha raridade é "
                f"{translate_value(payload.get('rarity'))}."
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
                    f"terreno é: {translated_terrain}."
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
                    f"aqui é {translate_reference(structures[0], name_translations)}"
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

        if stack_size:
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
            translated_enchantments = (
                translate_references(
                    applicable_enchantments,
                    name_translations,
                )
            )

            examples = ", ".join(
                translated_enchantments[:2]
            )

            add_hint_if_safe(
                hints,
                (
                    "Entre os encantamentos "
                    "que podem ser usados em mim "
                    f"estão {examples}."
                ),
                secret_name,
            )

        obtained_by = payload.get(
            "obtainedBy",
            [],
        )

        if obtained_by:
            methods = [
                translate_game_text(
                    method,
                    name_translations,
                )
                for method in obtained_by[:2]
            ]

            add_hint_if_safe(
                hints,
                (
                    "Uma forma de me obter é: "
                    f"{', '.join(methods)}."
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

            saturation = food_value.get(
                "saturation"
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
                        translate_reference(
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
                            f"{', '.join(ingredient_names)}."
                        ),
                        secret_name,
                    )

    elif entity_type == "structure":
        add_hint_if_safe(
            hints,
            (
                "Estou localizada na dimensão "
                f"{translate_value(payload.get('dimension'))}."
            ),
            secret_name,
        )

        add_hint_if_safe(
            hints,
            (
                "Minha raridade é "
                f"{translate_value(payload.get('rarity'))}."
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
            translated_biomes = (
                translate_references(
                    biomes[:3],
                    name_translations,
                )
            )

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
            translated_applicable = (
                translate_references(
                    applicable[:3],
                    name_translations,
                )
            )

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
            translated_obtained = [
                translate_value(
                    method
                )
                for method in obtained[:2]
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

                    e.name AS secret_name,

                    t.translated_name
                        AS translated_secret_name

                FROM games g

                JOIN entities e
                    ON e.id = g.secret_entity_id

                LEFT JOIN entity_translations t
                    ON t.entity_id = e.id
                    AND t.locale = 'pt-BR'

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

        normalized_guess = normalize_guess(
            clean_guess
        )

        normalized_secret_en = normalize_guess(
            game["secret_name"]
        )

        translated_secret = (
            game["translated_secret_name"]
            or game["secret_name"]
        )

        normalized_secret_pt = normalize_guess(
            translated_secret
        )

        correct = normalized_guess in {
            normalized_secret_en,
            normalized_secret_pt,
        }

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
                "lives": game["lives_remaining"],
                "status": "won",
                "answer": translated_secret,
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
                translated_secret
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

                    e.entity_type,
                    e.name AS secret_name,
                    e.raw_payload,

                    (
                        SELECT t.translated_name
                        FROM entity_translations t
                        WHERE
                            t.entity_id = e.id
                            AND t.locale = 'pt-BR'
                        LIMIT 1
                    ) AS translated_secret_name

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

        name_translations = (
            load_name_translations(
                connection
            )
        )
        
        available_hints = build_hints(
            entity_type=game["entity_type"],
            payload=payload,
            secret_name=game["secret_name"],
            name_translations=name_translations,
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
                game["translated_secret_name"]
                or game["secret_name"]
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

                    e.name AS secret_name,

                    t.translated_name
                        AS translated_secret_name

                FROM games g

                JOIN entities e
                    ON e.id = g.secret_entity_id

                LEFT JOIN entity_translations t
                    ON t.entity_id = e.id
                    AND t.locale = 'pt-BR'

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

        display_name = (
            game["translated_secret_name"]
            or game["secret_name"]
        )

        answer = (
            display_name
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