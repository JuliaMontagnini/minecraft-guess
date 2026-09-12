import json
from pathlib import Path
from urllib.parse import quote

from sqlalchemy import text

from app.database import engine


MEDIA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "entity_media.json"
)

WIKI_FILE_BASE_URL = (
    "https://minecraft.wiki/w/"
    "Special:Redirect/file/"
)


def build_image_url(
    file_name: str | None,
) -> str | None:
    if not file_name:
        return None

    return (
        WIKI_FILE_BASE_URL
        + quote(
            file_name,
            safe="",
        )
    )


def main():
    if not MEDIA_FILE.exists():
        print(
            "Arquivo não encontrado:"
        )
        print(MEDIA_FILE)
        return

    with MEDIA_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        entries = json.load(file)

    imported = 0
    missing_entities = []

    with engine.begin() as connection:
        for entry in entries:
            entity = connection.execute(
                text(
                    """
                    SELECT
                        id,
                        name,
                        entity_type
                    FROM entities
                    WHERE
                        entity_type =
                            :entity_type
                        AND name =
                            :entity_name
                    LIMIT 1
                    """
                ),
                {
                    "entity_type":
                        entry["entity_type"],

                    "entity_name":
                        entry["entity_name"],
                },
            ).mappings().first()

            if entity is None:
                missing_entities.append(
                    (
                        entry["entity_type"],
                        entry["entity_name"],
                    )
                )
                continue

            image_url = build_image_url(
                entry.get(
                    "file_name"
                )
            )

            connection.execute(
                text(
                    """
                    INSERT INTO entity_media (
                        entity_id,
                        source,
                        source_page_url,
                        file_name,
                        image_url,
                        license_note
                    )
                    VALUES (
                        :entity_id,
                        'minecraft_wiki',
                        :source_page_url,
                        :file_name,
                        :image_url,
                        :license_note
                    )

                    ON DUPLICATE KEY UPDATE
                        source_page_url =
                            VALUES(source_page_url),

                        file_name =
                            VALUES(file_name),

                        image_url =
                            VALUES(image_url),

                        license_note =
                            VALUES(license_note)
                    """
                ),
                {
                    "entity_id":
                        entity["id"],

                    "source_page_url":
                        entry[
                            "source_page_url"
                        ],

                    "file_name":
                        entry.get(
                            "file_name"
                        ),

                    "image_url":
                        image_url,

                    "license_note":
                        entry.get(
                            "license_note"
                        ),
                },
            )

            imported += 1

    print("=" * 70)
    print("IMPORTAÇÃO DE MÍDIA")
    print("=" * 70)

    print(
        f"Entradas importadas: "
        f"{imported}"
    )

    print(
        f"Entidades não encontradas: "
        f"{len(missing_entities)}"
    )

    for entity_type, entity_name in (
        missing_entities
    ):
        print(
            f"- {entity_type}: "
            f"{entity_name}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()
