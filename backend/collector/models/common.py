from pydantic import BaseModel, ConfigDict, Field, model_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class IntRange(ApiModel):
    min: int = Field(ge=0)
    max: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_range(self):
        if self.min > self.max:
            raise ValueError(
                "O valor mínimo não pode ser maior que o máximo."
            )

        return self

class CoordinateRange(ApiModel):
    min: int
    max: int

    @model_validator(mode="after")
    def validate_range(self):
        if self.min > self.max:
            raise ValueError(
                "A coordenada mínima não pode ser maior que a máxima."
            )

        return self
    
class Damage(ApiModel):
    easy: int = Field(ge=0)
    normal: int = Field(ge=0)
    hard: int = Field(ge=0)


class Drop(ApiModel):
    item: str = Field(min_length=1)
    count: IntRange

    # Não vamos restringir a 0-1 ou 0-100 ainda.
    # A API aparenta usar formatos diferentes entre categorias.
    chance: float = Field(ge=0)


class BiomeColors(ApiModel):
    grass: str
    water: str
    foliage: str
    sky: str


class RecipeOutput(ApiModel):
    item: str = Field(min_length=1)
    count: int = Field(ge=1)


class CraftingRecipe(ApiModel):
    pattern: list[list[str | None]]
    ingredients: dict[str, str]
    output: RecipeOutput
    station: str


class FoodValue(ApiModel):
    hunger: int = Field(ge=0)
    saturation: float = Field(ge=0)