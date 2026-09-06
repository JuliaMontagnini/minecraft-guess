import json

from sqlalchemy import text

from database import engine
from models.item import Item

from repositories.entity_repository import (
    replace_list_values,
    upsert_entity,
)


def save_item(
    item: Item,
    raw_data: dict,
) -> int:
    with engine.begin() as connection:
        entity_id = upsert_entity(
            connection,
            entity_type="item",
            entity=item,
            raw_data=raw_data,
        )

        crafting_recipe = raw_data.get(
            "craftingRecipe"
        )

        connection.execute(
            text(
                """
                INSERT INTO items (
                    entity_id,
                    stack_size,
                    durability,
                    description,
                    enchantable,
                    food_hunger,
                    food_saturation,
                    fuel_value,
                    crafting_recipe
                )
                VALUES (
                    :entity_id,
                    :stack_size,
                    :durability,
                    :description,
                    :enchantable,
                    :food_hunger,
                    :food_saturation,
                    :fuel_value,
                    :crafting_recipe
                )
                ON DUPLICATE KEY UPDATE
                    stack_size = VALUES(stack_size),
                    durability = VALUES(durability),
                    description = VALUES(description),
                    enchantable = VALUES(enchantable),
                    food_hunger = VALUES(food_hunger),
                    food_saturation = VALUES(food_saturation),
                    fuel_value = VALUES(fuel_value),
                    crafting_recipe = VALUES(crafting_recipe)
                """
            ),
            {
                "entity_id": entity_id,
                "stack_size": item.stack_size,
                "durability": item.durability,
                "description": item.description,
                "enchantable": item.enchantable,

                "food_hunger": (
                    item.food_value.hunger
                    if item.food_value
                    else None
                ),

                "food_saturation": (
                    item.food_value.saturation
                    if item.food_value
                    else None
                ),

                "fuel_value": item.fuel_value,

                "crafting_recipe": (
                    json.dumps(
                        crafting_recipe,
                        ensure_ascii=False,
                    )
                    if crafting_recipe is not None
                    else None
                ),
            },
        )

        replace_list_values(
            connection,
            entity_id,
            {
                "obtained_by":
                    item.obtained_by,

                "applicable_enchantments":
                    item.applicable_enchantments,
            },
        )

        return entity_id