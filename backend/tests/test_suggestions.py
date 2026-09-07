from app.suggestion_service import (
    suggest_entities,
)


def suggestion_names(
    suggestions: list[dict],
) -> list[str]:
    return [
        suggestion["name"]
        for suggestion in suggestions
    ]


def test_portuguese_prefix():
    suggestions = suggest_entities(
        query="va",
        category="mobs",
    )

    names = suggestion_names(
        suggestions
    )

    assert "Vaca" in names
    assert "Vaca Cogumelo" in names


def test_search_ignores_case():
    suggestions = suggest_entities(
        query="VACA",
        category="mobs",
    )

    names = suggestion_names(
        suggestions
    )

    assert "Vaca" in names


def test_small_typo_is_supported():
    suggestions = suggest_entities(
        query="vca",
        category="mobs",
    )

    names = suggestion_names(
        suggestions
    )

    assert "Vaca" in names


def test_english_name_returns_portuguese():
    suggestions = suggest_entities(
        query="phantom",
        category="mobs",
    )

    names = suggestion_names(
        suggestions
    )

    assert "Espectro" in names


def test_category_filter():
    suggestions = suggest_entities(
        query="sel",
        category="biomes",
    )

    assert suggestions

    assert all(
        suggestion["category"]
        == "biomes"

        for suggestion
        in suggestions
    )

    names = suggestion_names(
        suggestions
    )

    assert "Selva" in names


def test_compound_item_name():
    suggestions = suggest_entities(
        query="picareta d",
        category="items",
    )

    names = suggestion_names(
        suggestions
    )

    assert any(
        name.startswith(
            "Picareta"
        )
        for name in names
    )


def test_one_character_does_not_search():
    suggestions = suggest_entities(
        query="v",
        category="mobs",
    )

    assert suggestions == []


def test_limit_is_respected():
    suggestions = suggest_entities(
        query="a",
        category="random",
        limit=2,
    )

    # Como consultas com 1 caractere
    # são ignoradas, deve retornar vazio.
    assert suggestions == []

    suggestions = suggest_entities(
        query="de",
        category="random",
        limit=2,
    )

    assert len(
        suggestions
    ) <= 2