import json
from collections import Counter
from pathlib import Path


REPORT_FILE = (
    Path(__file__).resolve().parent.parent
    / "localization_audit_report.json"
)


def main():
    if not REPORT_FILE.exists():
        print(
            "Relatório não encontrado:"
        )
        print(REPORT_FILE)
        return

    with REPORT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    original_names = Counter()
    unused_translations = Counter()
    possible_english = Counter()
    suspicious_hints = Counter()

    errors = []

    for issue in report.get(
        "issues",
        [],
    ):
        if "error" in issue:
            errors.append(issue)
            continue

        hint = issue.get(
            "hint",
            "",
        ).strip()

        if hint:
            suspicious_hints[hint] += 1

        for reason in issue.get(
            "reasons",
            [],
        ):
            reason_type = reason.get(
                "type"
            )

            values = reason.get(
                "values",
                [],
            )

            if (
                reason_type
                == "original_entity_name"
            ):
                for value in values:
                    original_names[value] += 1

            elif (
                reason_type
                == "known_translation_not_used"
            ):
                for value in values:
                    original = value.get(
                        "original",
                        "",
                    )

                    translations = value.get(
                        "possible_translations",
                        [],
                    )

                    translated_text = (
                        " / ".join(
                            translations
                        )
                    )

                    key = (
                        f"{original} "
                        f"→ {translated_text}"
                    )

                    unused_translations[
                        key
                    ] += 1

            elif (
                reason_type
                == "possible_english"
            ):
                for value in values:
                    possible_english[
                        value
                    ] += 1

    print("=" * 70)
    print(
        "RESUMO DA AUDITORIA DE LOCALIZAÇÃO"
    )
    print("=" * 70)

    print(
        "Entidades verificadas: "
        f"{report.get('entities_checked', 0)}"
    )

    print(
        "Dicas verificadas: "
        f"{report.get('hints_checked', 0)}"
    )

    print(
        "Ocorrências suspeitas: "
        f"{report.get('issues_found', 0)}"
    )

    print()


    print("=" * 70)
    print(
        "1. NOMES DE ENTIDADES EM INGLÊS"
    )
    print("=" * 70)

    if original_names:
        for value, count in (
            original_names.most_common()
        ):
            print(
                f"{count:>4}x | {value}"
            )
    else:
        print(
            "Nenhum."
        )

    print()


    print("=" * 70)
    print(
        "2. TRADUÇÕES CONHECIDAS "
        "QUE NÃO FORAM USADAS"
    )
    print("=" * 70)

    if unused_translations:
        for value, count in (
            unused_translations.most_common()
        ):
            print(
                f"{count:>4}x | {value}"
            )
    else:
        print(
            "Nenhuma."
        )

    print()


    print("=" * 70)
    print(
        "3. PALAVRAS SUSPEITAS EM INGLÊS"
    )
    print("=" * 70)

    if possible_english:
        for value, count in (
            possible_english.most_common()
        ):
            print(
                f"{count:>4}x | {value}"
            )
    else:
        print(
            "Nenhuma."
        )

    print()


    print("=" * 70)
    print(
        "4. TEXTOS SUSPEITOS ÚNICOS"
    )
    print("=" * 70)

    for hint, count in (
        suspicious_hints.most_common()
    ):
        print()
        print(
            f"[{count}x]"
        )

        print(
            hint
        )

    print()

    print("=" * 70)

    if errors:
        print(
            f"Erros encontrados: "
            f"{len(errors)}"
        )
    else:
        print(
            "Erros encontrados: 0"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()