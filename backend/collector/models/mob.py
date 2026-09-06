from pydantic import Field

from .common import ApiModel, Damage, Drop, IntRange


class Mob(ApiModel):
    name: str = Field(min_length=1)
    id: str = Field(min_length=1)

    type: str
    hp: int = Field(ge=0)

    damage: Damage

    xp_drop: IntRange = Field(
        alias="xpDrop"
    )

    spawn_biomes: list[str] = Field(
        alias="spawnBiomes"
    )

    spawn_conditions: str = Field(
        alias="spawnConditions"
    )

    drops: list[Drop]

    behavior: str
    weaknesses: list[str]

    tameable: bool

    taming_method: str | None = Field(
        alias="tamingMethod"
    )

    breedable: bool

    breeding_item: str | None = Field(
        alias="breedingItem"
    )

    version_added: str = Field(
        alias="versionAdded"
    )

    category: str
    notes: str