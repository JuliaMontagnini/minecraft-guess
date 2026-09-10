from app.localization import (
    translate_game_text,
    translate_reference,
    translate_value,
)


# =========================================================
# VALORES SIMPLES
# =========================================================


def test_translate_mob_type():
    assert (
        translate_value("hostile")
        == "hostil"
    )


def test_translate_item_category():
    assert (
        translate_value("miscellaneous")
        == "diversos"
    )


def test_translate_equipment_type():
    assert (
        translate_value("helmet")
        == "capacete"
    )


def test_translate_crafting():
    assert (
        translate_value("Crafting")
        == "fabricação"
    )


def test_translate_dimension():
    assert (
        translate_value("overworld")
        == "Mundo Superior"
    )


# =========================================================
# NOMES DE ENTIDADES
# =========================================================


def test_translate_entity_reference():
    translations = {
        "jungle": "Selva",
        "cow": "Vaca",
    }

    assert (
        translate_reference(
            "Jungle",
            translations,
        )
        == "Selva"
    )


def test_custom_reference_alias():
    assert (
        translate_reference(
            "Mycelium",
            {},
        )
        == "Micélio"
    )


# =========================================================
# TEXTOS MAIS COMPLEXOS
# =========================================================


def test_translate_water_damage():
    result = translate_game_text(
        "Water (damages them)",
        {},
    )

    assert result == (
        "água (causa dano)"
    )


def test_translate_lava_oceans():
    result = translate_game_text(
        "Nether (lava oceans)",
        {},
    )

    assert result == (
        "Nether (oceanos de lava)"
    )


def test_translate_mob_drop():
    translations = {
        "skeleton": "Esqueleto",
    }

    result = translate_game_text(
        "Mob drops (Skeleton)",
        translations,
    )

    assert result == (
        "itens derrubados por "
        "Esqueleto"
    )


def test_translate_enchantment_reference():
    translations = {
        "bane of arthropods":
            "Ruína dos Artrópodes",
    }

    result = translate_game_text(
        "Bane of Arthropods enchantment",
        translations,
    )

    assert result == (
        "encantamento "
        "Ruína dos Artrópodes"
    )


def test_translate_terrain_text():
    result = translate_game_text(
        (
            "pointed dripstone "
            "stalactites and stalagmites"
        ),
        {},
    )

    assert result == (
        "estalactites e estalagmites "
        "de espeleotema pontiagudo"
    )


def test_translate_structure_danger():
    result = translate_game_text(
        (
            "Magma blocks deal damage "
            "when stood on"
        ),
        {},
    )

    assert result == (
        "blocos de magma causam dano "
        "quando pisados"
    )

def test_translate_milk_mining_fatigue():
    result = translate_game_text(
        "Milk (removes Mining Fatigue)",
        {},
    )

    assert result == (
        "leite (remove a fadiga de mineração)"
    )


def test_translate_dense_flowers():
    result = translate_game_text(
        "dense flowers",
        {},
    )

    assert result == (
        "grande concentração de flores"
    )


def test_remaining_audit_terms_are_translated():
    cases = {
        "massive packed ice pillars":
            "enormes pilares de gelo compactado",
        "dense bamboo stalks":
            "bambuzal denso",
        "dense birch trees":
            "vegetação densa de bétulas",
        "dense dark oak canopy":
            "copa densa de carvalhos escuros",
        "dense mangrove trees":
            "vegetação densa de mangues",
        "exposed stone mountain peaks":
            "picos montanhosos com pedra exposta",
        "steep stone cliffs":
            "penhascos íngremes de pedra",
        "Snow Block":
            "Bloco de Neve",
        "Packed Ice":
            "Gelo Compactado",
        "Ice":
            "Gelo",
        "Powder Snow":
            "Neve Fofa",
        "Jungle Leaves":
            "Folhas da Selva",
        "Egg":
            "Ovo",
        "Milk Bucket":
            "Balde de Leite",
        "Chest":
            "Baú",
        "Inventory Crafting":
            "Fabricação no Inventário",
        "Breeze Rod":
            "Bastão de Brisa",
        "Heavy Core":
            "Núcleo Pesado",
        "Spider Eye":
            "Olho de Aranha",
        "Bone":
            "Osso",
        "Arrow of Poison":
            "Flecha de Veneno",
        "String":
            "Linha",
        "Raw Cod":
            "Bacalhau Cru",
        "Golden Axe":
            "Machado de Ouro",
        "Emerald":
            "Esmeralda",
        "Iron Axe":
            "Machado de Ferro",
    }

    for original, expected in cases.items():
        assert (
            translate_game_text(
                original,
                {},
            )
            == expected
        )
