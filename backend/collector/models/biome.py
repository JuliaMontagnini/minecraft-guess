from pydantic import Field

from .common import ApiModel, BiomeColors


class Biome(ApiModel):
    name: str = Field(min_length=1)
    id: str = Field(min_length=1)

    dimension: str
    category: str

    temperature: float
    precipitation: str

    terrain_features: list[str] = Field(
        alias="terrainFeatures"
    )

    unique_blocks: list[str] = Field(
        alias="uniqueBlocks"
    )

    spawning_mobs: list[str] = Field(
        alias="spawningMobs"
    )

    structures_found: list[str] = Field(
        alias="structuresFound"
    )

    colors: BiomeColors

    version_added: str = Field(
        alias="versionAdded"
    )

    rarity: str
    notes: str