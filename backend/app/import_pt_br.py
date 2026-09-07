import json
from pathlib import Path

from sqlalchemy import text

from app.database import engine


LANG_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "pt_br.json"
)

CUSTOM_NAME_OVERRIDES = {
    ("mob", "mooshroom"):
        "Vaca Cogumelo",
}

TRANSLATION_KEY_ALIASES = {
    # Encantamentos
    ("enchantment", "curse_of_binding"):
        "enchantment.minecraft.binding_curse",

    ("enchantment", "curse_of_vanishing"):
        "enchantment.minecraft.vanishing_curse",

    # Itens
    ("item", "eye_of_ender"):
        "item.minecraft.ender_eye",

    ("item", "redstone_dust"):
        "item.minecraft.redstone",

    # Poções
    ("item", "potion_of_fire_resistance"):
        "item.minecraft.potion.effect.fire_resistance",

    ("item", "potion_of_healing"):
        "item.minecraft.potion.effect.healing",

    ("item", "potion_of_invisibility"):
        "item.minecraft.potion.effect.invisibility",

    ("item", "potion_of_night_vision"):
        "item.minecraft.potion.effect.night_vision",

    ("item", "potion_of_slow_falling"):
        "item.minecraft.potion.effect.slow_falling",

    ("item", "potion_of_swiftness"):
        "item.minecraft.potion.effect.swiftness",

    ("item", "potion_of_strength"):
        "item.minecraft.potion.effect.strength",

    ("item", "potion_of_water_breathing"):
        "item.minecraft.potion.effect.water_breathing",
}

STRUCTURE_TRANSLATIONS = {
    "amethyst-geode":
        "Geodo de ametista",

    "ancient-city":
        "Cidade ancestral",

    "bastion-remnant":
        "Bastião em ruínas",

    "buried-treasure":
        "Tesouro enterrado",

    "desert-pyramid":
        "Templo do deserto",

    "end-city":
        "Cidade do End",

    "end-gateway":
        "Passagem do End",

    "end-ship":
        "Navio do End",

    "igloo":
        "Iglu",

    "jungle-pyramid":
        "Templo da selva",

    "mineshaft":
        "Mina abandonada",

    "nether-fortress":
        "Fortaleza do Nether",

    "ocean-monument":
        "Monumento oceânico",

    "ocean-ruins":
        "Ruína oceânica",

    "pillager-outpost":
        "Posto avançado do saqueador",

    "ruined-portal-nether":
        "Portal em ruínas",

    "ruined-portal-overworld":
        "Portal em ruínas",

    "shipwreck":
        "Naufrágio",

    "stronghold":
        "Fortaleza",

    "trail-ruins":
        "Trilha em ruínas",

    "trial-chamber":
        "Câmaras do desafio",

    "village":
        "Vila",

    "witch-hut":
        "Cabana do pântano",

    "woodland-mansion":
        "Mansão da floresta",
}

def normalize_external_id(
    external_id: str,
) -> str:
    value = external_id

    if ":" in value:
        value = value.split(
            ":",
            maxsplit=1,
        )[1]

    return value.replace(
        "-",
        "_",
    )


def get_translation_keys(
    entity_type: str,
    external_id: str,
) -> list[str]:
    identifier = normalize_external_id(
        external_id
    )

    if entity_type == "mob":
        return [
            f"entity.minecraft.{identifier}",
        ]

    if entity_type == "biome":
        return [
            f"biome.minecraft.{identifier}",
        ]

    if entity_type == "item":
        return [
            f"item.minecraft.{identifier}",
            f"block.minecraft.{identifier}",
        ]

    if entity_type == "enchantment":
        return [
            f"enchantment.minecraft.{identifier}",
        ]

    if entity_type == "structure":
        return [
            f"structure.minecraft.{identifier}",
        ]

    return []


def find_translation(
    translations: dict[str, str],
    entity_type: str,
    external_id: str,
) -> tuple[str, str] | None:
    identifier = normalize_external_id(
        external_id
    )

    custom_translation = (
        CUSTOM_NAME_OVERRIDES.get(
            (
                entity_type,
                identifier,
            )
        )
    )

    if custom_translation:
        return (
            custom_translation,
            "project-pt-br",
        )

    # Traduções definidas pelo projeto.
    if entity_type == "structure":
        structure_translation = (
            STRUCTURE_TRANSLATIONS.get(
                external_id
            )
        )

        if structure_translation:
            return (
                structure_translation,
                "project-pt-br",
            )

    # IDs da Astroworld que precisam
    # apontar para outra chave do
    # arquivo oficial de idioma.
    alias_key = (
        entity_type,
        identifier,
    )

    special_key = (
        TRANSLATION_KEY_ALIASES.get(
            alias_key
        )
    )

    if special_key:
        translated = translations.get(
            special_key
        )

        if translated:
            return (
                translated.strip(),
                "minecraft-pt-br",
            )

    # Busca normal.
    keys = get_translation_keys(
        entity_type,
        external_id,
    )

    for key in keys:
        translated = translations.get(
            key
        )

        if translated:
            return (
                translated.strip(),
                "minecraft-pt-br",
            )

    return None

def save_translation(
    entity_id: int,
    translated_name: str,
    source: str,
):
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO entity_translations (
                    entity_id,
                    locale,
                    translated_name,
                    source
                )
                VALUES (
                    :entity_id,
                    'pt-BR',
                    :translated_name,
                    :source
                )
                ON DUPLICATE KEY UPDATE
                    translated_name =
                        VALUES(translated_name),
                    source =
                        VALUES(source)
                """
            ),
            {
                "entity_id":
                    entity_id,

                "translated_name":
                    translated_name,

                "source":
                    source,
            },
        )

def main():
    if not LANG_FILE.exists():
        print(
            "Arquivo não encontrado:"
        )
        print(LANG_FILE)
        return

    with LANG_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        translations = json.load(
            file
        )

    with engine.connect() as connection:
        entities = connection.execute(
            text(
                """
                SELECT
                    id,
                    external_id,
                    entity_type,
                    name
                FROM entities
                ORDER BY
                    entity_type,
                    name
                """
            )
        ).mappings().all()

    translated_count = 0
    missing = []

    for entity in entities:
        translation_result = find_translation(
            translations,
            entity["entity_type"],
            entity["external_id"],
        )

        if translation_result:
            translated_name, source = (
                translation_result
            )

            save_translation(
                entity_id=entity["id"],
                translated_name=translated_name,
                source=source,
            )

            translated_count += 1

        else:
            missing.append(
                {
                    "type":
                        entity["entity_type"],

                    "external_id":
                        entity["external_id"],

                    "name":
                        entity["name"],
                }
            )

    print("=" * 70)
    print("IMPORTAÇÃO PT-BR")
    print("=" * 70)

    print(
        f"Entidades analisadas: "
        f"{len(entities)}"
    )

    print(
        f"Traduções importadas/localizadas: "
        f"{translated_count}"
    )

    print(
        f"Sem tradução: "
        f"{len(missing)}"
    )

    if missing:
        print()
        print(
            "ENTIDADES SEM CORRESPONDÊNCIA"
        )
        print("-" * 70)

        for entity in missing:
            print(
                f"{entity['type']:<15} "
                f"{entity['external_id']:<35} "
                f"{entity['name']}"
            )

    print("=" * 70)


if __name__ == "__main__":
    main()