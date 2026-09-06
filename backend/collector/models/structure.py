from pydantic import Field

from .common import ApiModel, CoordinateRange, Drop


class Structure(ApiModel):
    name: str = Field(min_length=1)
    id: str = Field(min_length=1)

    dimension: str
    biomes: list[str]

    rarity: str

    y_level: CoordinateRange = Field(
    alias="yLevel"
)

    features: list[str]

    hostile_mobs: list[str] = Field(
        alias="hostileMobs"
    )

    loot: list[Drop]

    unique_loot: list[str] = Field(
        alias="uniqueLoot"
    )

    how_to_find: str = Field(
        alias="howToFind"
    )

    dangers: list[str]
    rewards: list[str]

    version_added: str = Field(
        alias="versionAdded"
    )

    category: str
    notes: str