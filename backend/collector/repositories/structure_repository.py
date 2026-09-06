from sqlalchemy import text

from database import engine
from models.structure import Structure

from repositories.entity_repository import (
    replace_list_values,
    upsert_entity,
)


def save_structure(
    structure: Structure,
    raw_data: dict,
) -> int:
    with engine.begin() as connection:
        entity_id = upsert_entity(
            connection,
            entity_type="structure",
            entity=structure,
            raw_data=raw_data,
        )

        connection.execute(
            text(
                """
                INSERT INTO structures (
                    entity_id,
                    dimension,
                    rarity,
                    y_min,
                    y_max,
                    how_to_find
                )
                VALUES (
                    :entity_id,
                    :dimension,
                    :rarity,
                    :y_min,
                    :y_max,
                    :how_to_find
                )
                ON DUPLICATE KEY UPDATE
                    dimension = VALUES(dimension),
                    rarity = VALUES(rarity),
                    y_min = VALUES(y_min),
                    y_max = VALUES(y_max),
                    how_to_find = VALUES(how_to_find)
                """
            ),
            {
                "entity_id": entity_id,
                "dimension": structure.dimension,
                "rarity": structure.rarity,
                "y_min": structure.y_level.min,
                "y_max": structure.y_level.max,
                "how_to_find": structure.how_to_find,
            },
        )

        connection.execute(
            text(
                """
                DELETE FROM structure_loot
                WHERE structure_entity_id = :entity_id
                """
            ),
            {"entity_id": entity_id},
        )

        for loot in structure.loot:
            connection.execute(
                text(
                    """
                    INSERT INTO structure_loot (
                        structure_entity_id,
                        item_name,
                        count_min,
                        count_max,
                        chance_raw
                    )
                    VALUES (
                        :entity_id,
                        :item_name,
                        :count_min,
                        :count_max,
                        :chance
                    )
                    """
                ),
                {
                    "entity_id": entity_id,
                    "item_name": loot.item,
                    "count_min": loot.count.min,
                    "count_max": loot.count.max,
                    "chance": loot.chance,
                },
            )

        replace_list_values(
            connection,
            entity_id,
            {
                "biomes":
                    structure.biomes,

                "features":
                    structure.features,

                "hostile_mobs":
                    structure.hostile_mobs,

                "unique_loot":
                    structure.unique_loot,

                "dangers":
                    structure.dangers,

                "rewards":
                    structure.rewards,
            },
        )

        return entity_id