from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.game_service import (
    GameError,
    GameNotFoundError,
    create_game,
    get_game_state,
    reveal_hint,
    submit_guess,
)

from app.schemas import (
    GameCreateRequest,
    GameCreateResponse,
    GameStateResponse,
    GuessRequest,
    GuessResponse,
    HintResponse,
)

app = FastAPI(
    title="MinecraftGuess API",
    version="1.0.0",
    description=(
        "API responsável pelas partidas "
        "do MinecraftGuess."
    ),
)


# ---------------------------------------------------------
# CORS
# Permite que o frontend React local acesse esta API.
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.get(
    "/games/{game_id}",
    response_model=GameStateResponse,
)
def game_state(
    game_id: str,
):
    try:
        return get_game_state(
            game_id
        )

    except GameNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

# ---------------------------------------------------------
# CRIAR NOVA PARTIDA
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# ENVIAR PALPITE
# ---------------------------------------------------------

@app.post(
    "/games/{game_id}/guess",
    response_model=GuessResponse,
)
def guess(
    game_id: str,
    request: GuessRequest,
):
    try:
        return submit_guess(
            game_id,
            request.guess,
        )

    except GameNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except GameError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


# ---------------------------------------------------------
# SOLICITAR NOVA DICA
# ---------------------------------------------------------

@app.post(
    "/games/{game_id}/hint",
    response_model=HintResponse,
)
def hint(
    game_id: str,
):
    try:
        return reveal_hint(
            game_id
        )

    except GameNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except GameError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error