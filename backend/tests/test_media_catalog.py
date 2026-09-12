import json

from collections import Counter
from pathlib import Path


CATALOG_FILE = (
    Path(__file__).resolve()
    .parent
    .parent
    / "data"
    / "entity_media.json"
)


EXPECTED_COUNTS = {
    "mob": 76,
    "biome": 64,
    "item": 100,
    "structure": 24,
    "enchantment": 40,
}


def load_catalog():
    return json.loads(
        CATALOG_FILE.read_text(
            encoding="utf-8"
        )
    )


def test_media_catalog_has_all_entities():
    catalog = load_catalog()

    assert len(catalog) == 304

    counts = Counter(
        entry["entity_type"]
        for entry in catalog
    )

    assert dict(counts) == (
        EXPECTED_COUNTS
    )


def test_media_catalog_has_no_duplicates():
    catalog = load_catalog()

    keys = [
        (
            entry["entity_type"],
            entry["entity_name"],
        )
        for entry in catalog
    ]

    assert len(keys) == len(
        set(keys)
    )


def test_all_media_entries_have_file_and_source():
    catalog = load_catalog()

    for entry in catalog:
        assert entry[
            "file_name"
        ]

        assert entry[
            "source_page_url"
        ]

        assert entry[
            "license_note"
        ]
