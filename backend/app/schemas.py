from typing import Literal

from pydantic import BaseModel


Category = Literal[
    "mobs",
    "biomes",
    "items",
    "structures",
    "enchantments",
    "random",
]


class GameCreateRequest(BaseModel):
    category: Category


class GameCreateResponse(BaseModel):
    game_id: str
    category: str
    lives: int
    max_lives: int
    status: str