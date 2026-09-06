from pydantic import Field

from .common import ApiModel


class Enchantment(ApiModel):
    name: str = Field(min_length=1)
    id: str = Field(min_length=1)

    max_level: int = Field(
        alias="maxLevel",
        ge=1,
    )

    description: str

    effect_per_level: list[str] = Field(
        alias="effectPerLevel"
    )

    applicable_items: list[str] = Field(
        alias="applicableItems"
    )

    incompatible_with: list[str] = Field(
        alias="incompatibleWith"
    )

    obtained_from: list[str] = Field(
        alias="obtainedFrom"
    )

    weight: int = Field(ge=0)

    treasure_only: bool = Field(
        alias="treasureOnly"
    )

    curse_of: bool = Field(
        alias="curseOf"
    )

    version_added: str = Field(
        alias="versionAdded"
    )

    category: str
    notes: str