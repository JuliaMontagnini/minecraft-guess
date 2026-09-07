from fastapi import (
    FastAPI,
    HTTPException,
    Query,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.game_service import (
    GameError,
    GameNotFoundError,
    create_game,
    get_game_state,
    reveal_hint,
    submit_guess,
)

from app.schemas import (
    Category,
    GameCreateRequest,
    GameCreateResponse,
    GameStateResponse,
    GuessRequest,
    GuessResponse,
    HintResponse,
    SuggestionResponse,
)

from app.suggestion_service import (
    suggest_entities,
)


app = FastAPI(
    title="MinecraftGuess API",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=[
        "*",
    ],

    allow_headers=[
        "*",
    ],
)


# =========================================================
# HEALTH CHECK
# =========================================================


@app.get(
    "/health"
)
def health():
    return {
        "status": "ok",
    }


# =========================================================
# AUTOCOMPLETE
# =========================================================


@app.get(
    "/entities/suggestions",
    response_model=
        SuggestionResponse,
)
def entity_suggestions(
    q: str,

    category:
        Category = "random",

    limit: int = Query(
        default=6,
        ge=1,
        le=10,
    ),
):
    suggestions = (
        suggest_entities(
            query=q,
            category=category,
            limit=limit,
        )
    )

    return {
        "suggestions":
            suggestions,
    }


# =========================================================
# CRIAR PARTIDA
# =========================================================


@app.post(
    "/games",
    response_model=
        GameCreateResponse,
    status_code=201,
)
def new_game(
    request:
        GameCreateRequest,
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


# =========================================================
# RECUPERAR PARTIDA
# =========================================================


@app.get(
    "/games/{game_id}",
    response_model=
        GameStateResponse,
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


# =========================================================
# PALPITE
# =========================================================


@app.post(
    "/games/{game_id}/guess",
    response_model=
        GuessResponse,
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


# =========================================================
# DICA
# =========================================================


@app.post(
    "/games/{game_id}/hint",
    response_model=
        HintResponse,
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