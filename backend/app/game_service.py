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