from sqlalchemy import text

from database import engine
from models.enchantment import Enchantment

from repositories.entity_repository import (
    replace_list_values,
    upsert_entity,
)


def save_enchantment(
    enchantment: Enchantment,
    raw_data: dict,
) -> int:
    with engine.begin() as connection:
        entity_id = upsert_entity(
            connection,
            entity_type="enchantment",
            entity=enchantment,
            raw_data=raw_data,
        )

        connection.execute(
            text(
                """
                INSERT INTO enchantments (
                    entity_id,
                    max_level,
                    description,
                    weight,
                    treasure_only,
                    curse_of
                )
                VALUES (
                    :entity_id,
                    :max_level,
                    :description,
                    :weight,
                    :treasure_only,
                    :curse_of
                )
                ON DUPLICATE KEY UPDATE
                    max_level = VALUES(max_level),
                    description = VALUES(description),
                    weight = VALUES(weight),
                    treasure_only = VALUES(treasure_only),
                    curse_of = VALUES(curse_of)
                """
            ),
            {
                "entity_id": entity_id,
                "max_level": enchantment.max_level,
                "description": enchantment.description,
                "weight": enchantment.weight,
                "treasure_only":
                    enchantment.treasure_only,
                "curse_of":
                    enchantment.curse_of,
            },
        )

        replace_list_values(
            connection,
            entity_id,
            {
                "effect_per_level":
                    enchantment.effect_per_level,

                "applicable_items":
                    enchantment.applicable_items,

                "incompatible_with":
                    enchantment.incompatible_with,

                "obtained_from":
                    enchantment.obtained_from,
            },
        )

        return entity_id