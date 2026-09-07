from typing import Literal

from pydantic import BaseModel, Field


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


class GuessRequest(BaseModel):
    guess: str = Field(
        min_length=1,
        max_length=255,
    )


class GuessResponse(BaseModel):
    game_id: str
    correct: bool
    lives: int
    status: str
    answer: str | None = None


class HintResponse(BaseModel):
    game_id: str
    hint_number: int
    hint: str
    lives: int
    status: str
    answer: str | None = None

class GameGuessHistoryItem(BaseModel):
    guess: str
    correct: bool


class GameHintHistoryItem(BaseModel):
    hint_number: int
    hint: str


class GameStateResponse(BaseModel):
    game_id: str
    category: str
    lives: int
    max_lives: int
    status: str
    answer: str | None = None
    guesses: list[GameGuessHistoryItem]
    hints: list[GameHintHistoryItem]