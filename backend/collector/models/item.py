from pydantic import Field

from .common import (
    ApiModel,
    CraftingRecipe,
    FoodValue,
)


class Item(ApiModel):
    name: str = Field(min_length=1)
    id: str = Field(min_length=1)

    category: str

    stack_size: int = Field(
        alias="stackSize",
        ge=1,
    )

    durability: int | None = Field(
        default=None,
        ge=0,
    )

    description: str

    obtained_by: list[str] = Field(
        alias="obtainedBy"
    )

    crafting_recipe: CraftingRecipe | None = Field(
        alias="craftingRecipe"
    )

    enchantable: bool

    applicable_enchantments: list[str] = Field(
        alias="applicableEnchantments"
    )

    food_value: FoodValue | None = Field(
        alias="foodValue"
    )

    fuel_value: int | None = Field(
        alias="fuelValue",
        ge=0,
    )

    version_added: str = Field(
        alias="versionAdded"
    )

    notes: str