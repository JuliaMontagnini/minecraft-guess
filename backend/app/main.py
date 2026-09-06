from fastapi import (
    FastAPI,
    HTTPException,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.game_service import (
    GameError,
    create_game,
)

from app.schemas import (
    GameCreateRequest,
    GameCreateResponse,
)


app = FastAPI(
    title="MinecraftGuess API",
    version="1.0.0",
    description=(
        "API responsável pelas partidas "
        "do MinecraftGuess."
    ),
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.post(
    "/games",
    response_model=GameCreateResponse,
    status_code=201,
)
def new_game(
    request: GameCreateRequest,
):
    try:
        return create_game(
            request.category
        )

    except GameError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error