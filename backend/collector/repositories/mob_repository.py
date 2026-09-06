from sqlalchemy import text

from database import engine
from models.mob import Mob

from repositories.entity_repository import (
    replace_list_values,
    upsert_entity,
)


def save_mob(
    mob: Mob,
    raw_data: dict,
) -> int:
    with engine.begin() as connection:
        entity_id = upsert_entity(
            connection,
            entity_type="mob",
            entity=mob,
            raw_data=raw_data,
        )

        connection.execute(
            text(
                """
                INSERT INTO mobs (
                    entity_id,
                    mob_type,
                    hp,
                    damage_easy,
                    damage_normal,
                    damage_hard,
                    xp_min,
                    xp_max,
                    spawn_conditions,
                    behavior,
                    tameable,
                    taming_method,
                    breedable,
                    breeding_item
                )
                VALUES (
                    :entity_id,
                    :mob_type,
                    :hp,
                    :damage_easy,
                    :damage_normal,
                    :damage_hard,
                    :xp_min,
                    :xp_max,
                    :spawn_conditions,
                    :behavior,
                    :tameable,
                    :taming_method,
                    :breedable,
                    :breeding_item
                )
                ON DUPLICATE KEY UPDATE
                    mob_type = VALUES(mob_type),
                    hp = VALUES(hp),
                    damage_easy = VALUES(damage_easy),
                    damage_normal = VALUES(damage_normal),
                    damage_hard = VALUES(damage_hard),
                    xp_min = VALUES(xp_min),
                    xp_max = VALUES(xp_max),
                    spawn_conditions = VALUES(spawn_conditions),
                    behavior = VALUES(behavior),
                    tameable = VALUES(tameable),
                    taming_method = VALUES(taming_method),
                    breedable = VALUES(breedable),
                    breeding_item = VALUES(breeding_item)
                """
            ),
            {
                "entity_id": entity_id,
                "mob_type": mob.type,
                "hp": mob.hp,
                "damage_easy": mob.damage.easy,
                "damage_normal": mob.damage.normal,
                "damage_hard": mob.damage.hard,
                "xp_min": mob.xp_drop.min,
                "xp_max": mob.xp_drop.max,
                "spawn_conditions": mob.spawn_conditions,
                "behavior": mob.behavior,
                "tameable": mob.tameable,
                "taming_method": mob.taming_method,
                "breedable": mob.breedable,
                "breeding_item": mob.breeding_item,
            },
        )

        # Reconstrói os drops a cada atualização.
        connection.execute(
            text(
                """
                DELETE FROM mob_drops
                WHERE mob_entity_id = :entity_id
                """
            ),
            {
                "entity_id": entity_id,
            },
        )

        for drop in mob.drops:
            connection.execute(
                text(
                    """
                    INSERT INTO mob_drops (
                        mob_entity_id,
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
                    "item_name": drop.item,
                    "count_min": drop.count.min,
                    "count_max": drop.count.max,
                    "chance": drop.chance,
                },
            )

        replace_list_values(
            connection,
            entity_id,
            {
                "spawn_biomes":
                    mob.spawn_biomes,

                "weaknesses":
                    mob.weaknesses,
            },
        )

        return entity_id