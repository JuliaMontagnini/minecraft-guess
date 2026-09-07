import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy import text

from app.database import engine
from app.game_service import (
    build_hints,
    load_name_translations,
    load_payload,
)
from app.localization import (
    translate_game_text,
    translate_reference,
    translate_value,
)


REPORT_FILE = (
    Path(__file__).resolve().parent.parent
    / "localization_audit_report.json"
)


# Palavras que são normais no contexto do Minecraft
# mesmo em uma interface em português.
ALLOWED_TERMS = {
    "minecraft",
    "nether",
    "end",
    "redstone",
    "mob",
    "mobs",
    "hp",
    "xp",
    "lava",
}


# Palavras que são um forte indício de que algum
# trecho da API passou sem localização.
#
# Não precisa conter todas as palavras do inglês:
# este conjunto serve como segunda camada da auditoria.
SUSPICIOUS_ENGLISH_WORDS = {
    "helmet",
    "helmets",
    "chestplate",
    "chestplates",
    "leggings",
    "boots",
    "sword",
    "swords",
    "axe",
    "axes",
    "pickaxe",
    "pickaxes",
    "shovel",
    "shovels",
    "hoe",
    "hoes",
    "bow",
    "bows",
    "crossbow",
    "crossbows",
    "trident",
    "tridents",
    "elytra",
    "mace",
    "shears",
    "and",
    "attack",
    "attacks",
    "bane",
    "brewing",
    "causes",
    "chest",
    "chests",
    "crafting",
    "damage",
    "damages",
    "deals",
    "desert",
    "enchantment",
    "enchantments",
    "fire",
    "first",
    "fishing",
    "forest",
    "from",
    "ground",
    "healing",
    "immune",
    "jungle",
    "kill",
    "killed",
    "loot",
    "melee",
    "mineshaft",
    "mineshafts",
    "near",
    "needs",
    "ocean",
    "oceans",
    "only",
    "open",
    "plains",
    "potion",
    "potions",
    "ranged",
    "splash",
    "sunlight",
    "table",
    "takes",
    "them",
    "trading",
    "under",
    "village",
    "villages",
    "water",
    "weapon",
    "weapons",
    "with",
    "levitation",
    "over",
    "void",
    "becomes",
    "effect",
    "fatal",
    "fireballs",
    "fungus",
    "levitation",
    "mycelium",
    "portals",
    "repels",
    "zombified",
}


def collect_payload_strings(
    value: Any,
) -> list[str]:
    """
    Percorre o raw_payload procurando textos
    que podem acabar sendo usados nas dicas.
    """

    result: list[str] = []

    if isinstance(value, str):
        text_value = value.strip()

        if text_value:
            result.append(
                text_value
            )

        return result

    if isinstance(value, list):
        for item in value:
            result.extend(
                collect_payload_strings(
                    item
                )
            )

        return result

    if isinstance(value, dict):
        for item in value.values():
            result.extend(
                collect_payload_strings(
                    item
                )
            )

        return result

    return result


def normalize_text(
    value: str,
) -> str:
    return re.sub(
        r"\s+",
        " ",
        value.strip(),
    ).casefold()


def contains_text(
    text: str,
    fragment: str,
) -> bool:
    """
    Verifica se o fragmento aparece no texto
    respeitando limites de palavras.
    """

    if not fragment:
        return False

    pattern = re.compile(
        rf"(?<!\w)"
        rf"{re.escape(fragment)}"
        rf"(?!\w)",
        flags=re.IGNORECASE,
    )

    return bool(
        pattern.search(text)
    )


def find_english_words(
    hint: str,
) -> list[str]:
    words = re.findall(
        r"[A-Za-z]+",
        hint.casefold(),
    )

    suspicious = []

    for word in words:
        if word in ALLOWED_TERMS:
            continue

        if (
            word
            in SUSPICIOUS_ENGLISH_WORDS
        ):
            suspicious.append(
                word
            )

    return sorted(
        set(suspicious)
    )


def find_original_entity_names(
    hint: str,
    name_translations:
        dict[str, str],
) -> list[str]:
    """
    Detecta quando um nome original em inglês
    aparece na dica mesmo tendo tradução pt-BR.

    Exemplo:
        Jungle em vez de Selva.
    """

    found = []

    # Ordenamos pelos maiores nomes primeiro
    # para lidar melhor com nomes compostos.
    original_names = sorted(
        name_translations.keys(),
        key=len,
        reverse=True,
    )

    for original_name in original_names:
        translated_name = (
            name_translations[
                original_name
            ]
        )

        if (
            normalize_text(original_name)
            == normalize_text(
                translated_name
            )
        ):
            continue

        if contains_text(
            hint,
            original_name,
        ):
            found.append(
                original_name
            )

    return found


def find_translatable_payload_fragments(
    hint: str,
    payload: dict,
    name_translations:
        dict[str, str],
) -> list[dict]:
    """
    Detecta casos em que um valor da API
    aparece literalmente na dica apesar de
    nosso localization.py já saber traduzi-lo.
    """

    problems = []

    raw_strings = set(
        collect_payload_strings(
            payload
        )
    )

    for raw_value in raw_strings:
        if len(raw_value) < 2:
            continue

        if not contains_text(
            hint,
            raw_value,
        ):
            continue

        translations = {
            translate_value(
                raw_value
            ),

            translate_reference(
                raw_value,
                name_translations,
            ),

            translate_game_text(
                raw_value,
                name_translations,
            ),
        }

        raw_normalized = (
            normalize_text(
                raw_value
            )
        )

        translated_versions = [
            translated
            for translated
            in translations
            if (
                normalize_text(
                    translated
                )
                != raw_normalized
            )
        ]

        if translated_versions:
            problems.append(
                {
                    "original":
                        raw_value,

                    "possible_translations":
                        sorted(
                            translated_versions
                        ),
                }
            )

    return problems


def main():
    # ---------------------------------------------
    # Carregar banco e traduções
    # ---------------------------------------------

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

        name_translations = (
            load_name_translations(
                connection
            )
        )

    issues = []

    total_hints = 0

    # ---------------------------------------------
    # Gerar as dicas das 304 entidades
    # ---------------------------------------------

    for entity in entities:
        try:
            payload = load_payload(
                entity["raw_payload"]
            )

            hints = build_hints(
                entity_type=
                    entity["entity_type"],

                payload=payload,

                secret_name=
                    entity["name"],

                name_translations=
                    name_translations,
            )

            total_hints += len(
                hints
            )

            for hint_number, hint in enumerate(
                hints,
                start=1,
            ):
                reasons = []

                # ---------------------------------
                # 1. Nomes de entidades em inglês
                # ---------------------------------

                original_names = (
                    find_original_entity_names(
                        hint,
                        name_translations,
                    )
                )

                if original_names:
                    reasons.append(
                        {
                            "type":
                                "original_entity_name",

                            "values":
                                original_names,
                        }
                    )

                # ---------------------------------
                # 2. Valores que já sabemos traduzir
                # ---------------------------------

                raw_fragments = (
                    find_translatable_payload_fragments(
                        hint,
                        payload,
                        name_translations,
                    )
                )

                if raw_fragments:
                    reasons.append(
                        {
                            "type":
                                "known_translation_not_used",

                            "values":
                                raw_fragments,
                        }
                    )

                # ---------------------------------
                # 3. Palavras provavelmente inglesas
                # ---------------------------------

                english_words = (
                    find_english_words(
                        hint
                    )
                )

                if english_words:
                    reasons.append(
                        {
                            "type":
                                "possible_english",

                            "values":
                                english_words,
                        }
                    )

                if reasons:
                    issues.append(
                        {
                            "entity_type":
                                entity[
                                    "entity_type"
                                ],

                            "external_id":
                                entity[
                                    "external_id"
                                ],

                            "name":
                                entity["name"],

                            "hint_number":
                                hint_number,

                            "hint":
                                hint,

                            "reasons":
                                reasons,
                        }
                    )

        except Exception as error:
            issues.append(
                {
                    "entity_type":
                        entity[
                            "entity_type"
                        ],

                    "external_id":
                        entity[
                            "external_id"
                        ],

                    "name":
                        entity["name"],

                    "error":
                        str(error),
                }
            )

    # ---------------------------------------------
    # Salvar relatório
    # ---------------------------------------------

    report = {
        "entities_checked":
            len(entities),

        "hints_checked":
            total_hints,

        "issues_found":
            len(issues),

        "issues":
            issues,
    }

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # ---------------------------------------------
    # Mostrar resultado
    # ---------------------------------------------

    print("=" * 70)
    print(
        "AUDITORIA DE LOCALIZAÇÃO"
    )
    print("=" * 70)

    print(
        "Entidades verificadas: "
        f"{len(entities)}"
    )

    print(
        "Dicas verificadas: "
        f"{total_hints}"
    )

    print(
        "Dicas suspeitas: "
        f"{len(issues)}"
    )

    if issues:
        print()
        print(
            "POSSÍVEIS PROBLEMAS"
        )
        print("-" * 70)

        for issue in issues:
            if "error" in issue:
                print(
                    f"[ERRO] "
                    f"{issue['entity_type']} | "
                    f"{issue['name']} | "
                    f"{issue['error']}"
                )

                continue

            print()
            print(
                f"{issue['entity_type']} | "
                f"{issue['name']} | "
                f"Dica #{issue['hint_number']}"
            )

            print(
                f"  {issue['hint']}"
            )

            for reason in (
                issue["reasons"]
            ):
                print(
                    "  -> "
                    f"{reason['type']}: "
                    f"{reason['values']}"
                )

    print()
    print("=" * 70)

    if issues:
        print(
            "⚠ Foram encontrados textos "
            "que precisam de revisão."
        )
    else:
        print(
            "✓ Nenhum texto suspeito "
            "foi encontrado."
        )

    print(
        "Relatório: "
        f"{REPORT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()