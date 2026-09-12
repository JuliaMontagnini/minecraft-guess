import argparse
import time

from collections import Counter
from pathlib import Path

import requests

from sqlalchemy import text

from app.database import engine


PROJECT_DIR = (
    Path(__file__).resolve()
    .parents[2]
)

REPORT_FILE = (
    PROJECT_DIR
    / "docs"
    / "audits"
    / "media-coverage.md"
)


EXPECTED_COUNTS = {
    "mob": 76,
    "biome": 64,
    "item": 100,
    "structure": 24,
    "enchantment": 40,
}


USER_AGENT = (
    "MinecraftGuessAcademicProject/1.0"
)


def validate_remote_image(
    session: requests.Session,
    url: str,
):
    headers = {
        "User-Agent":
            USER_AGENT,
    }

    try:
        response = session.head(
            url,
            allow_redirects=True,
            timeout=15,
            headers=headers,
        )

        content_type = (
            response.headers
            .get(
                "Content-Type",
                "",
            )
            .lower()
        )

        if (
            response.ok
            and content_type.startswith(
                "image/"
            )
        ):
            return {
                "ok": True,
                "status":
                    response.status_code,
                "content_type":
                    content_type,
                "final_url":
                    response.url,
            }

        # Alguns servidores tratam HEAD
        # de maneira diferente de GET.
        response.close()

        response = session.get(
            url,
            allow_redirects=True,
            timeout=15,
            headers=headers,
            stream=True,
        )

        content_type = (
            response.headers
            .get(
                "Content-Type",
                "",
            )
            .lower()
        )

        result = {
            "ok":
                (
                    response.ok
                    and
                    content_type.startswith(
                        "image/"
                    )
                ),

            "status":
                response.status_code,

            "content_type":
                content_type,

            "final_url":
                response.url,
        }

        response.close()

        return result

    except requests.RequestException as error:
        return {
            "ok": False,
            "status": None,
            "content_type": "",
            "final_url": "",
            "error": str(error),
        }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--network",
        action="store_true",
        help=(
            "Também valida as URLs "
            "remotamente."
        ),
    )

    args = parser.parse_args()

    with engine.connect() as connection:
        rows = connection.execute(
            text(
                """
                SELECT
                    e.entity_type,
                    e.name,

                    m.id
                        AS media_id,

                    m.source_page_url,
                    m.file_name,
                    m.image_url

                FROM entities e

                LEFT JOIN entity_media m
                    ON m.entity_id = e.id
                    AND m.source =
                        'minecraft_wiki'

                ORDER BY
                    e.entity_type,
                    e.name
                """
            )
        ).mappings().all()

    total_entities = len(rows)

    total_by_type = Counter(
        row["entity_type"]
        for row in rows
    )

    covered_rows = [
        row
        for row in rows
        if (
            row["media_id"]
            is not None
            and
            row["image_url"]
        )
    ]

    covered_by_type = Counter(
        row["entity_type"]
        for row in covered_rows
    )

    missing = [
        row
        for row in rows
        if (
            row["media_id"]
            is None
            or
            not row["image_url"]
        )
    ]

    network_results = {}
    invalid_remote = []

    if args.network:
        session = requests.Session()

        unique_urls = {
            row["image_url"]
            for row in covered_rows
            if row["image_url"]
        }

        print(
            "Validando "
            f"{len(unique_urls)} "
            "URLs únicas..."
        )

        for index, url in enumerate(
            sorted(unique_urls),
            start=1,
        ):
            print(
                f"[{index}/"
                f"{len(unique_urls)}] "
                f"{url}"
            )

            result = (
                validate_remote_image(
                    session,
                    url,
                )
            )

            network_results[url] = (
                result
            )

            # Pequeno intervalo para não
            # disparar centenas de requests
            # instantaneamente.
            time.sleep(0.20)

        session.close()

        for row in covered_rows:
            result = (
                network_results[
                    row["image_url"]
                ]
            )

            if not result["ok"]:
                invalid_remote.append(
                    {
                        **row,
                        "result":
                            result,
                    }
                )

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = []

    lines.append(
        "# MinecraftGuess — "
        "Auditoria de mídia"
    )

    lines.append("")

    lines.append(
        f"- Entidades: "
        f"{total_entities}"
    )

    lines.append(
        f"- Com mídia cadastrada: "
        f"{len(covered_rows)}"
    )

    lines.append(
        f"- Sem mídia: "
        f"{len(missing)}"
    )

    if args.network:
        lines.append(
            f"- URLs remotas inválidas: "
            f"{len(invalid_remote)}"
        )

    lines.append("")

    lines.append(
        "## Cobertura por categoria"
    )

    lines.append("")

    lines.append(
        "| Categoria | Entidades | "
        "Com mídia |"
    )

    lines.append(
        "|---|---:|---:|"
    )

    for entity_type in (
        EXPECTED_COUNTS
    ):
        lines.append(
            f"| {entity_type} "
            f"| {total_by_type[entity_type]} "
            f"| {covered_by_type[entity_type]} |"
        )

    lines.append("")

    if missing:
        lines.append(
            "## Entidades sem mídia"
        )

        lines.append("")

        for row in missing:
            lines.append(
                f"- {row['entity_type']} "
                f"— {row['name']}"
            )

        lines.append("")

    if invalid_remote:
        lines.append(
            "## URLs remotas inválidas"
        )

        lines.append("")

        for entry in invalid_remote:
            result = (
                entry["result"]
            )

            lines.append(
                "- "
                f"{entry['entity_type']} "
                f"— {entry['name']} "
                f"— arquivo: "
                f"`{entry['file_name']}` "
                f"— HTTP: "
                f"{result.get('status')} "
                f"— Content-Type: "
                f"`{result.get('content_type')}`"
            )

        lines.append("")

    if (
        not missing
        and
        (
            not args.network
            or
            not invalid_remote
        )
    ):
        lines.append(
            "## Resultado"
        )

        lines.append("")

        lines.append(
            "**Cobertura de mídia aprovada.**"
        )

        lines.append("")

    REPORT_FILE.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print("AUDITORIA DE MÍDIA")
    print("=" * 70)

    print(
        f"Entidades: "
        f"{total_entities}"
    )

    print(
        f"Cobertas: "
        f"{len(covered_rows)}"
    )

    print(
        f"Sem mídia: "
        f"{len(missing)}"
    )

    if args.network:
        print(
            "URLs remotas inválidas: "
            f"{len(invalid_remote)}"
        )

    print(
        f"Relatório: "
        f"{REPORT_FILE}"
    )

    print("=" * 70)

    if missing:
        raise SystemExit(1)

    if (
        args.network
        and
        invalid_remote
    ):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
