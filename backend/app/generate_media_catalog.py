import json
import re

from collections import Counter
from pathlib import Path
from urllib.parse import quote

from sqlalchemy import text

from app.database import engine
from app.import_media import (
    WIKI_FILE_BASE_URL,
)


BACKEND_DIR = (
    Path(__file__).resolve()
    .parent
    .parent
)

DATA_DIR = (
    BACKEND_DIR
    / "data"
)

OVERRIDES_FILE = (
    DATA_DIR
    / "entity_media_overrides.json"
)

OUTPUT_FILE = (
    DATA_DIR
    / "entity_media.json"
)


EXPECTED_COUNTS = {
    "mob": 76,
    "biome": 64,
    "item": 100,
    "structure": 24,
    "enchantment": 40,
}


SPRITE_PREFIXES = {
    "mob": "EntitySprite",
    "biome": "BiomeSprite",
    "item": "ItemSprite",
    "structure": "EnvSprite",
}


TYPE_ORDER = {
    "mob": 0,
    "biome": 1,
    "item": 2,
    "structure": 3,
    "enchantment": 4,
}


def build_sprite_id(
    name: str,
) -> str:
    """
    Regra documentada pelos templates
    de sprites da Minecraft Wiki:

    - minúsculas
    - espaços -> hífens
    """

    value = (
        name
        .strip()
        .casefold()
    )

    value = re.sub(
        r"[\s_]+",
        "-",
        value,
    )

    value = re.sub(
        r"-+",
        "-",
        value,
    )

    return value.strip("-")


def default_file_name(
    entity_type: str,
    entity_name: str,
) -> tuple[str, str]:
    """
    Retorna:

    (
        file_name,
        strategy
    )
    """

    if entity_type == "enchantment":
        return (
            "ItemSprite enchanted-book.png",
            "representative_enchanted_book",
        )

    prefix = SPRITE_PREFIXES[
        entity_type
    ]

    sprite_id = build_sprite_id(
        entity_name
    )

    return (
        f"{prefix} {sprite_id}.png",
        "sprite_auto",
    )


def build_source_page_url(
    file_name: str,
) -> str:
    """
    Gera a página File: da Wiki.

    Em vez de apontar a origem apenas
    para a página da entidade, apontamos
    para a página exata do arquivo.

    Isso facilita conferir autoria/licença.
    """

    wiki_base = (
        WIKI_FILE_BASE_URL.split(
            "Special:Redirect/file/",
            1,
        )[0]
    )

    encoded_name = quote(
        file_name.replace(
            " ",
            "_",
        ),
        safe="-_.()",
    )

    return (
        wiki_base
        + "File:"
        + encoded_name
    )


def load_overrides():
    if not OVERRIDES_FILE.exists():
        return {}

    with OVERRIDES_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        entries = json.load(file)

    overrides = {}

    for entry in entries:
        key = (
            entry["entity_type"],
            entry["entity_name"],
        )

        overrides[key] = entry

    return overrides


def main():
    overrides = load_overrides()

    with engine.connect() as connection:
        rows = connection.execute(
            text(
                """
                SELECT
                    entity_type,
                    name
                FROM entities
                ORDER BY
                    entity_type,
                    name
                """
            )
        ).mappings().all()

    if len(rows) != 304:
        raise RuntimeError(
            "Esperadas 304 entidades, "
            f"mas foram encontradas "
            f"{len(rows)}."
        )

    catalog = []

    for row in rows:
        entity_type = (
            row["entity_type"]
        )

        entity_name = (
            row["name"]
        )

        file_name, strategy = (
            default_file_name(
                entity_type,
                entity_name,
            )
        )

        key = (
            entity_type,
            entity_name,
        )

        override = overrides.get(
            key
        )

        license_note = (
            "Consultar a página do "
            "arquivo na Minecraft Wiki."
        )

        if override is not None:
            override_file = (
                override.get(
                    "file_name"
                )
            )

            # Um override NULL antigo da POC
            # não deve apagar uma imagem
            # automática válida.
            if override_file:
                file_name = (
                    override_file
                )

                strategy = (
                    "manual_override"
                )

            override_license = (
                override.get(
                    "license_note"
                )
            )

            if override_license:
                license_note = (
                    override_license
                )

        source_page_url = (
            build_source_page_url(
                file_name
            )
        )

        catalog.append(
            {
                "entity_type":
                    entity_type,

                "entity_name":
                    entity_name,

                "source_page_url":
                    source_page_url,

                "file_name":
                    file_name,

                "license_note":
                    license_note,

                "strategy":
                    strategy,
            }
        )

    catalog.sort(
        key=lambda entry: (
            TYPE_ORDER[
                entry["entity_type"]
            ],
            entry["entity_name"]
            .casefold(),
        )
    )

    counts = Counter(
        entry["entity_type"]
        for entry in catalog
    )

    if dict(counts) != EXPECTED_COUNTS:
        raise RuntimeError(
            "Contagens inesperadas: "
            f"{dict(counts)}"
        )

    keys = [
        (
            entry["entity_type"],
            entry["entity_name"],
        )
        for entry in catalog
    ]

    if len(keys) != len(set(keys)):
        raise RuntimeError(
            "Há entidades duplicadas "
            "no catálogo de mídia."
        )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            catalog,
            file,
            ensure_ascii=False,
            indent=2,
        )

        file.write("\n")

    strategies = Counter(
        entry["strategy"]
        for entry in catalog
    )

    print("=" * 70)
    print(
        "CATÁLOGO DE MÍDIA GERADO"
    )
    print("=" * 70)

    print(
        f"Total: {len(catalog)}"
    )

    print()

    print("Por categoria:")

    for entity_type in (
        EXPECTED_COUNTS
    ):
        print(
            f"- {entity_type}: "
            f"{counts[entity_type]}"
        )

    print()

    print("Por estratégia:")

    for strategy, count in (
        sorted(
            strategies.items()
        )
    ):
        print(
            f"- {strategy}: "
            f"{count}"
        )

    print()

    print(
        f"Arquivo: {OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
