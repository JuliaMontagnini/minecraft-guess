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