from difflib import SequenceMatcher

from sqlalchemy import text

from app.database import engine
from app.game_service import (
    CATEGORY_TO_ENTITY_TYPE,
    normalize_guess,
)


ENTITY_TYPE_TO_CATEGORY = {
    "mob": "mobs",
    "biome": "biomes",
    "item": "items",
    "structure": "structures",
    "enchantment": "enchantments",
}


MIN_QUERY_LENGTH = 2
FUZZY_MIN_LENGTH = 3
FUZZY_THRESHOLD = 0.68
DEFAULT_LIMIT = 6
MAX_LIMIT = 10


def _similarity(
    query: str,
    candidate: str,
) -> float:
    return SequenceMatcher(
        None,
        query,
        candidate,
    ).ratio()


def _get_match_rank(
    query: str,
    english_name: str,
    portuguese_name: str,
) -> tuple[int, float] | None:
    """
    Retorna:

        (prioridade, similaridade)

    Prioridades:
        0 -> correspondência exata
        1 -> começa com o texto digitado
        2 -> contém o texto digitado
        3 -> correspondência aproximada

    Quanto menor a prioridade, melhor.
    """

    normalized_english = normalize_guess(
        english_name
    )

    normalized_portuguese = normalize_guess(
        portuguese_name
    )

    candidates = {
        normalized_english,
        normalized_portuguese,
    }

    # -------------------------------------------------
    # Correspondência exata
    # -------------------------------------------------

    if query in candidates:
        return (
            0,
            1.0,
        )

    # -------------------------------------------------
    # Começa com o que o usuário digitou
    # -------------------------------------------------

    if any(
        candidate.startswith(query)
        for candidate in candidates
    ):
        best_similarity = max(
            _similarity(
                query,
                candidate,
            )
            for candidate in candidates
        )

        return (
            1,
            best_similarity,
        )

    # -------------------------------------------------
    # Contém o que o usuário digitou
    # -------------------------------------------------

    if any(
        query in candidate
        for candidate in candidates
    ):
        best_similarity = max(
            _similarity(
                query,
                candidate,
            )
            for candidate in candidates
        )

        return (
            2,
            best_similarity,
        )

    # -------------------------------------------------
    # Busca aproximada
    #
    # Só usamos fuzzy search a partir de 3 caracteres
    # para evitar sugestões aleatórias demais.
    # -------------------------------------------------

    if len(query) < FUZZY_MIN_LENGTH:
        return None

    best_similarity = max(
        _similarity(
            query,
            candidate,
        )
        for candidate in candidates
    )

    if (
        best_similarity
        >= FUZZY_THRESHOLD
    ):
        return (
            3,
            best_similarity,
        )

    return None


def suggest_entities(
    query: str,
    category: str = "random",
    limit: int = DEFAULT_LIMIT,
) -> list[dict]:
    """
    Busca sugestões de respostas.

    A pesquisa considera:
    - nome em português;
    - nome original em inglês;
    - maiúsculas/minúsculas;
    - acentos;
    - correspondências parciais;
    - pequenos erros ortográficos.

    O segredo da partida não é consultado.
    A busca acontece entre todas as respostas
    possíveis da categoria.
    """

    normalized_query = normalize_guess(
        query
    )

    if (
        len(normalized_query)
        < MIN_QUERY_LENGTH
    ):
        return []

    safe_limit = max(
        1,
        min(
            limit,
            MAX_LIMIT,
        ),
    )

    parameters = {}

    sql = """
        SELECT
            e.id,
            e.entity_type,
            e.name AS english_name,

            COALESCE(
                t.translated_name,
                e.name
            ) AS portuguese_name

        FROM entities e

        LEFT JOIN entity_translations t
            ON t.entity_id = e.id
            AND t.locale = 'pt-BR'
    """

    if category != "random":
        entity_type = (
            CATEGORY_TO_ENTITY_TYPE.get(
                category
            )
        )

        if entity_type is None:
            return []

        sql += """
            WHERE e.entity_type = :entity_type
        """

        parameters[
            "entity_type"
        ] = entity_type

    sql += """
        ORDER BY e.name
    """

    with engine.connect() as connection:
        entities = connection.execute(
            text(sql),
            parameters,
        ).mappings().all()

    ranked_results = []

    for entity in entities:
        rank = _get_match_rank(
            normalized_query,
            entity["english_name"],
            entity["portuguese_name"],
        )

        if rank is None:
            continue

        priority, similarity = rank

        display_name = (
            entity["portuguese_name"]
        )

        ranked_results.append(
            {
                "name":
                    display_name,

                "category":
                    ENTITY_TYPE_TO_CATEGORY[
                        entity["entity_type"]
                    ],

                "priority":
                    priority,

                "similarity":
                    similarity,
            }
        )

    ranked_results.sort(
        key=lambda item: (
            item["priority"],
            -item["similarity"],
            len(
                normalize_guess(
                    item["name"]
                )
            ),
            item["name"].casefold(),
        )
    )

    # -------------------------------------------------
    # Remove duplicatas pelo nome exibido.
    # -------------------------------------------------

    suggestions = []
    seen_names = set()

    for result in ranked_results:
        normalized_name = (
            normalize_guess(
                result["name"]
            )
        )

        if (
            normalized_name
            in seen_names
        ):
            continue

        seen_names.add(
            normalized_name
        )

        suggestions.append(
            {
                "name":
                    result["name"],

                "category":
                    result["category"],
            }
        )

        if (
            len(suggestions)
            >= safe_limit
        ):
            break

    return suggestions