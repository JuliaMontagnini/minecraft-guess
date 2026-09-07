import re

from sqlalchemy import text

from app.database import engine
from app.game_service import (
    MAX_HINTS,
    build_hints,
    load_name_translations,
    load_payload,
    normalize_guess,
)


EXPECTED_ENTITY_COUNTS = {
    "mob": 76,
    "biome": 64,
    "item": 100,
    "structure": 24,
    "enchantment": 40,
}

EXPECTED_TOTAL_ENTITIES = 304


def contains_secret(
    hint: str,
    secret: str,
) -> bool:
    """
    Verifica se o nome secreto aparece como
    palavra/expressão completa dentro de uma dica.

    A comparação ignora:
    - maiúsculas/minúsculas;
    - acentos;
    - espaços extras.
    """

    normalized_hint = normalize_guess(
        hint
    )

    normalized_secret = normalize_guess(
        secret
    )

    if not normalized_secret:
        return False

    pattern = re.compile(
        rf"(?<!\w)"
        rf"{re.escape(normalized_secret)}"
        rf"(?!\w)"
    )

    return bool(
        pattern.search(
            normalized_hint
        )
    )


def load_test_data():
    with engine.connect() as connection:
        entities = connection.execute(
            text(
                """
                SELECT
                    id,
                    external_id,
                    entity_type,
                    name,
                    raw_payload
                FROM entities
                ORDER BY
                    entity_type,
                    name
                """
            )
        ).mappings().all()

        translations = (
            load_name_translations(
                connection
            )
        )

    return (
        entities,
        translations,
    )


def test_database_has_304_entities():
    entities, _ = load_test_data()

    assert len(entities) == (
        EXPECTED_TOTAL_ENTITIES
    )


def test_entity_counts_by_category():
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                """
                SELECT
                    entity_type,
                    COUNT(*) AS quantity
                FROM entities
                GROUP BY entity_type
                """
            )
        ).mappings().all()

    actual_counts = {
        row["entity_type"]:
            row["quantity"]
        for row in rows
    }

    assert actual_counts == (
        EXPECTED_ENTITY_COUNTS
    )


def test_all_entities_have_pt_br_translation():
    with engine.connect() as connection:
        missing = connection.execute(
            text(
                """
                SELECT COUNT(*)

                FROM entities e

                LEFT JOIN entity_translations t
                    ON t.entity_id = e.id
                    AND t.locale = 'pt-BR'

                WHERE t.id IS NULL
                """
            )
        ).scalar_one()

    assert missing == 0


def test_all_entities_generate_five_hints():
    entities, translations = (
        load_test_data()
    )

    problems = []

    for entity in entities:
        try:
            payload = load_payload(
                entity["raw_payload"]
            )

            hints = build_hints(
                entity_type=
                    entity["entity_type"],

                payload=
                    payload,

                secret_name=
                    entity["name"],

                name_translations=
                    translations,
            )

            if len(hints) != MAX_HINTS:
                problems.append(
                    (
                        f"{entity['entity_type']} | "
                        f"{entity['name']} | "
                        f"{len(hints)} dicas"
                    )
                )

        except Exception as error:
            problems.append(
                (
                    f"{entity['entity_type']} | "
                    f"{entity['name']} | "
                    f"erro: {error}"
                )
            )

    assert not problems, (
        "\nProblemas encontrados:\n"
        + "\n".join(problems)
    )


def test_all_hints_are_unique_and_non_empty():
    entities, translations = (
        load_test_data()
    )

    problems = []

    for entity in entities:
        payload = load_payload(
            entity["raw_payload"]
        )

        hints = build_hints(
            entity_type=
                entity["entity_type"],

            payload=
                payload,

            secret_name=
                entity["name"],

            name_translations=
                translations,
        )

        if any(
            not hint.strip()
            for hint in hints
        ):
            problems.append(
                (
                    f"{entity['entity_type']} | "
                    f"{entity['name']} | "
                    "dica vazia"
                )
            )

        if (
            len(set(hints))
            != len(hints)
        ):
            problems.append(
                (
                    f"{entity['entity_type']} | "
                    f"{entity['name']} | "
                    "dicas duplicadas"
                )
            )

    assert not problems, (
        "\nProblemas encontrados:\n"
        + "\n".join(problems)
    )


def test_hints_do_not_reveal_english_secret():
    entities, translations = (
        load_test_data()
    )

    leaks = []

    for entity in entities:
        payload = load_payload(
            entity["raw_payload"]
        )

        hints = build_hints(
            entity_type=
                entity["entity_type"],

            payload=
                payload,

            secret_name=
                entity["name"],

            name_translations=
                translations,
        )

        for number, hint in enumerate(
            hints,
            start=1,
        ):
            if contains_secret(
                hint,
                entity["name"],
            ):
                leaks.append(
                    (
                        f"{entity['entity_type']} | "
                        f"{entity['name']} | "
                        f"dica #{number}: "
                        f"{hint}"
                    )
                )

    assert not leaks, (
        "\nVazamentos em inglês:\n"
        + "\n".join(leaks)
    )


def test_hints_do_not_reveal_portuguese_secret():
    entities, translations = (
        load_test_data()
    )

    leaks = []

    for entity in entities:
        translated_secret = (
            translations.get(
                entity["name"].casefold()
            )
        )

        if not translated_secret:
            continue

        payload = load_payload(
            entity["raw_payload"]
        )

        hints = build_hints(
            entity_type=
                entity["entity_type"],

            payload=
                payload,

            secret_name=
                entity["name"],

            name_translations=
                translations,
        )

        for number, hint in enumerate(
            hints,
            start=1,
        ):
            if contains_secret(
                hint,
                translated_secret,
            ):
                leaks.append(
                    (
                        f"{entity['entity_type']} | "
                        f"{entity['name']} "
                        f"({translated_secret}) | "
                        f"dica #{number}: "
                        f"{hint}"
                    )
                )

    assert not leaks, (
        "\nVazamentos em português:\n"
        + "\n".join(leaks)
    )


def test_total_generated_hints_is_1520():
    entities, translations = (
        load_test_data()
    )

    total_hints = 0

    for entity in entities:
        payload = load_payload(
            entity["raw_payload"]
        )

        hints = build_hints(
            entity_type=
                entity["entity_type"],

            payload=
                payload,

            secret_name=
                entity["name"],

            name_translations=
                translations,
        )

        total_hints += len(hints)

    assert total_hints == (
        EXPECTED_TOTAL_ENTITIES
        * MAX_HINTS
    )

    assert total_hints == 1520