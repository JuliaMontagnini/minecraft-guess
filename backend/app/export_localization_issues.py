import json
from collections import Counter
from pathlib import Path


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

REPORT_FILE = (
    BASE_DIR
    / "localization_audit_report.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "localization_issues.txt"
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

    hints = Counter()

    for issue in report.get(
        "issues",
        [],
    ):
        if "error" in issue:
            continue

        hint = (
            issue.get(
                "hint",
                "",
            )
            .strip()
        )

        if hint:
            hints[hint] += 1

    lines = []

    lines.append(
        "TEXTOS SUSPEITOS ÚNICOS"
    )
    lines.append(
        "=" * 70
    )
    lines.append(
        f"Ocorrências suspeitas: "
        f"{report.get('issues_found', 0)}"
    )
    lines.append(
        f"Textos únicos: {len(hints)}"
    )
    lines.append("")

    for hint, count in (
        hints.most_common()
    ):
        lines.append(
            f"[{count}x]"
        )
        lines.append(
            hint
        )
        lines.append("")

    OUTPUT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print("=" * 70)
    print(
        "EXPORTAÇÃO DOS PROBLEMAS "
        "DE LOCALIZAÇÃO"
    )
    print("=" * 70)

    print(
        "Ocorrências suspeitas: "
        f"{report.get('issues_found', 0)}"
    )

    print(
        f"Textos únicos: "
        f"{len(hints)}"
    )

    print()
    print(
        "Arquivo criado:"
    )
    print(
        OUTPUT_FILE
    )

    print("=" * 70)


if __name__ == "__main__":
    main()