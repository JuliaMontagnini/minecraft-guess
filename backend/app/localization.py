import re

from typing import Any


# =========================================================
# VALORES SIMPLES
# =========================================================

VALUE_TRANSLATIONS = {

    # -----------------------------------------------------
    # Tipos genéricos de equipamento
    # usados em applicableItems
    # -----------------------------------------------------
    "helmet": "capacete",
    "helmets": "capacetes",

    "chestplate": "peitoral",
    "chestplates": "peitorais",

    "leggings": "calças",

    "boots": "botas",

    "sword": "espada",
    "swords": "espadas",

    "axe": "machado",
    "axes": "machados",

    "pickaxe": "picareta",
    "pickaxes": "picaretas",

    "shovel": "pá",
    "shovels": "pás",

    "hoe": "enxada",
    "hoes": "enxadas",

    "bow": "arco",
    "bows": "arcos",

    "crossbow": "besta",
    "crossbows": "bestas",

    "trident": "tridente",
    "tridents": "tridentes",

    "fishing rod": "vara de pesca",
    "fishing rods": "varas de pesca",

    "shield": "escudo",
    "shields": "escudos",

    "elytra": "élitros",

    "mace": "maça",

    "shears": "tesoura",

    "armor": "armadura",
    "armour": "armadura",
    
    # -----------------------------------------------------
    # Dimensões
    # -----------------------------------------------------
    "overworld": "Mundo Superior",
    "the overworld": "Mundo Superior",
    "nether": "Nether",
    "the nether": "Nether",
    "end": "End",
    "the end": "End",

    # -----------------------------------------------------
    # Raridades
    # -----------------------------------------------------
    "common": "comum",
    "uncommon": "incomum",
    "rare": "raro",
    "very rare": "muito raro",
    "epic": "épico",

    # -----------------------------------------------------
    # Tipos de mobs
    # -----------------------------------------------------
    "passive": "passivo",
    "neutral": "neutro",
    "hostile": "hostil",
    "boss": "chefe",
    "utility": "utilitário",
    "ambient": "ambiente",
    "water": "água",
    "aquatic": "aquático",

    # -----------------------------------------------------
    # Precipitação
    # -----------------------------------------------------
    "rain": "chuva",
    "snow": "neve",
    "none": "nenhuma",

    # -----------------------------------------------------
    # Categorias
    # -----------------------------------------------------
    "tool": "ferramenta",
    "tools": "ferramentas",
    "weapon": "arma",
    "weapons": "armas",
    "food": "alimento",
    "foods": "alimentos",
    "block": "bloco",
    "blocks": "blocos",
    "material": "material",
    "materials": "materiais",
    "armor": "armadura",
    "armour": "armadura",
    "redstone": "redstone",
    "transportation": "transporte",
    "combat": "combate",
    "building": "construção",
    "decoration": "decoração",
    "miscellaneous": "diversos",
    "potion": "poção",

    # -----------------------------------------------------
    # Booleanos
    # -----------------------------------------------------
    "yes": "sim",
    "no": "não",
    "true": "sim",
    "false": "não",

    # -----------------------------------------------------
    # Fabricação / obtenção
    # -----------------------------------------------------
    "crafting": "fabricação",

    "crafting table":
        "Bancada de Trabalho",

    "smithing table":
        "Bancada de Ferraria",

    "enchanting table":
        "Mesa de Encantamentos",

    "enchanting":
        "encantamento",

    "brewing":
        "alquimia",

    "villager trading":
        "trocas com aldeões",

    "trading":
        "trocas",

    "fishing":
        "pesca",

    "anvil":
        "bigorna",

    "loot":
        "saques",

    "loot chest":
        "baú de saque",

    "chest loot":
        "saques de baús",

    "loot chests":
        "baús de saque",

    "chests":
        "baús",

    "books":
        "livros",

    "enchanted books":
        "livros encantados",

    "piglin bartering":
        "trocas com piglins",

    # -----------------------------------------------------
    # Profissões
    # -----------------------------------------------------
    "farmer": "fazendeiro",
    "fletcher": "flecheiro",
    "librarian": "bibliotecário",
    "cleric": "clérigo",
    "armorer": "armeiro",

    "toolsmith":
        "ferreiro de ferramentas",

    "weaponsmith":
        "ferreiro de armas",

    # -----------------------------------------------------
    # Combate
    # -----------------------------------------------------
    "fire": "fogo",
    "sunlight": "luz do sol",

    "fall damage":
        "dano de queda",

    "melee":
        "corpo a corpo",

    "ranged":
        "à distância",

    "shields":
        "escudos",

    "shield":
        "escudo",

    "arrows":
        "flechas",

    "arrow":
        "flecha",

    "lightning":
        "raios",

    "snowballs":
        "bolas de neve",

    # -----------------------------------------------------
    # Terreno
    # -----------------------------------------------------
    "surface":
        "superfície",

    "underground":
        "subsolo",

    "underground water":
        "água subterrânea",

    # -----------------------------------------------------
    # Ingredientes / itens recorrentes
    # -----------------------------------------------------
    "awkward potion":
        "Poção Estranha",

    "magma cream":
        "Creme de Magma",

    "glistering melon slice":
        "Fatia de Melancia Reluzente",

    "fermented spider eye":
        "Olho de Aranha Fermentado",

    "golden carrot":
        "Cenoura Dourada",

    "phantom membrane":
        "Membrana de Espectro",

    "sugar":
        "Açúcar",

    "blaze powder":
        "Pó de Blaze",

    "pufferfish":
        "Baiacu",

    "lingering potion":
        "Poção Prolongada",

    "netherite upgrade":
        "Melhoria de Netherita",

    "netherite ingot":
        "Barra de Netherita",
}


# =========================================================
# NOMES / REFERÊNCIAS QUE NÃO BATEM DIRETAMENTE
# =========================================================

REFERENCE_ALIASES = {
    "mycelium":
        "Micélio",

    "villages":
        "Vilas",

    "mineshafts":
        "Minas abandonadas",

    "desert village":
        "Vila do deserto",

    "swamp hut":
        "Cabana do pântano",

    "jungle log":
        "Tronco da selva",

    "ominous vault":
        "Cofre sinistro",

    # Plurais usados em frases da API
    "cows":
        "vacas",

    "chickens":
        "galinhas",

    "pigs":
        "porcos",

    "cats":
        "gatos",

    "ocelots":
        "jaguatiricas",

    "zombies":
        "zumbis",
}


# =========================================================
# TEXTOS LIVRES DA ASTROWORLD
#
# São frases que não podem ser traduzidas corretamente
# somente palavra por palavra.
# =========================================================

TEXT_TRANSLATIONS = {

    "mycelium ground":
        "solo de micélio",

    "deflected fireballs (one-shot kill)":
        (
            "bolas de fogo rebatidas "
            "(podem derrotar com um único golpe)"
        ),

    "warped fungus (repels them)":
        (
            "Fungo Distorcido "
            "(faz com que se afastem)"
        ),

    "nether portals":
        "Portais do Nether",

    "smite enchantment (becomes zombified in overworld)":
        (
            "encantamento Julgamento "
            "(torna-se zumbificado no Mundo Superior)"
        ),

    "shulker levitation effect causes fatal falls":
        (
            "o efeito de levitação dos Shulkers "
            "pode causar quedas fatais"
        ),

    "shulker levitation over the void":
    (
        "shulkers podem causar "
        "levitação sobre o vazio"
    ),
    # -----------------------------------------------------
    # Terreno / biomas
    # -----------------------------------------------------

    "lava oceans":
        "oceanos de lava",

    "damages them":
        "causa dano",

    "pointed dripstone stalactites and stalagmites":
        (
            "estalactites e estalagmites "
            "de espeleotema pontiagudo"
        ),

    "dense oak and birch trees":
        (
            "vegetação densa de "
            "carvalhos e bétulas"
        ),

    "frozen surface water":
        "água congelada na superfície",

    "smooth snow-covered peaks":
        "picos suaves cobertos de neve",

    "frozen water surface":
        "superfície de água congelada",

    "moderate depth water":
        "água de profundidade moderada",

    "giant 2x2 spruce trees with dense leaf cover":
        (
            "pinheiros gigantes 2x2 "
            "com folhagem densa"
        ),

    "narrow water channel":
        "canal estreito de água",

    "snow-covered spruce trees":
        "pinheiros cobertos de neve",

    "soul sand and soul soil terrain":
        (
            "terreno de Areia das Almas "
            "e Solo das Almas"
        ),

    "scattered jungle trees":
        "árvores de selva espalhadas",

    "shallow water":
        "água rasa",

    "terracotta plateaus with oak trees":
        (
            "planaltos de terracota "
            "com carvalhos"
        ),

    "deep water":
        "águas profundas",

    "deep water under ice":
        "águas profundas sob o gelo",

    "very deep water":
        "águas muito profundas",

    "any overworld biome":
        (
            "qualquer bioma do "
            "Mundo Superior"
        ),

    "all overworld biomes":
        (
            "todos os biomas do "
            "Mundo Superior"
        ),

    # -----------------------------------------------------
    # Fraquezas
    # -----------------------------------------------------

    "cracking appearance indicates damage":
        (
            "rachaduras na aparência "
            "indicam dano"
        ),

    "all damage sources":
        "todas as fontes de dano",

    "fall damage":
        "dano de queda",

    "healing splash potions":
        "poções arremessáveis de cura",

    "cats and ocelots (flees from them)":
        (
            "gatos e jaguatiricas "
            "(foge deles)"
        ),

    "suffocation on land":
        "sufocamento em terra",

    "drowning (needs both air and water)":
        (
            "afogamento "
            "(precisa de ar e água)"
        ),

    "destroy end crystals first":
        (
            "destruir primeiro "
            "os Cristais do End"
        ),

    "beds (explode in the end)":
        (
            "camas "
            "(explodem no End)"
        ),

    "melee rush (prevent spellcasting)":
        (
            "investida corpo a corpo "
            "(impede a conjuração)"
        ),

    "ranged attacks":
        "ataques à distância",

    "cats (flees from them)":
        (
            "gatos "
            "(foge deles)"
        ),

    "fire (but immune to lava)":
        (
            "fogo "
            "(mas é imune à lava)"
        ),

    "shields":
        "escudos",

    "melee rush":
        "investida corpo a corpo",

    "shield stun":
        "atordoamento com escudo",

    "high ground":
        "terreno elevado",

    "attack when shell is open":
        (
            "atacar quando a concha "
            "estiver aberta"
        ),

    "arrows":
        "flechas",

    "lightning":
        "raios",

    "zombies and drowned target baby turtles":
        (
            "zumbis e afogados atacam "
            "filhotes de tartaruga"
        ),

    "limited lifespan":
        "tempo de vida limitado",

    "ranged attacks (kiting)":
        (
            "ataques à distância "
            "(mantendo distância)"
        ),

    "instant damage potions":
        "poções de dano instantâneo",

    "melee while drinking":
        (
            "ataques corpo a corpo "
            "enquanto bebe"
        ),

    # -----------------------------------------------------
    # Obtenção
    # -----------------------------------------------------

    "loot chest":
        "baú de saque",

    "piglin bartering":
        "trocas com piglins",

    "bastion remnant loot":
        (
            "saques do "
            "Bastião em ruínas"
        ),

    "ancient city loot chest":
        (
            "baús da "
            "Cidade ancestral"
        ),

    "ominous vault":
        "Cofre sinistro",

    "trial chamber loot":
        (
            "saques das "
            "Câmaras do desafio"
        ),

    "village church":
        "igreja da vila",

    "smelting raw beef":
        (
            "assar carne bovina crua"
        ),

    "killing cows with fire aspect":
        (
            "matar vacas usando "
            "Aspecto Flamejante"
        ),

    "smelting raw chicken":
        "assar frango cru",

    "killing chickens with fire aspect":
        (
            "matar galinhas usando "
            "Aspecto Flamejante"
        ),

    "smelting raw porkchop":
        (
            "assar costeleta de "
            "porco crua"
        ),

    "killing pigs with fire aspect":
        (
            "matar porcos usando "
            "Aspecto Flamejante"
        ),

    "using glass bottle on full beehive or bee nest":
        (
            "usar um frasco de vidro "
            "em uma colmeia ou ninho "
            "de abelhas cheio"
        ),

    "mining redstone ore":
        "minerar minério de redstone",

    "witch drops":
        "itens derrubados por bruxas",

    # -----------------------------------------------------
    # Locais
    # -----------------------------------------------------

    "desert village":
        "Vila do deserto",

    "swamp hut":
        "Cabana do pântano",

    "underground water":
        "água subterrânea",

    "jungle log":
        "Tronco da selva",

    # -----------------------------------------------------
    # Perigos de estruturas
    # -----------------------------------------------------

    "warden is the most dangerous mob in the game "
    "(500 hp, can kill in 2 hits)":
        (
            "há um mob extremamente perigoso "
            "com 500 pontos de vida, capaz "
            "de derrotar o jogador em poucos golpes"
        ),

    "piglin brutes cannot be distracted with gold "
    "and deal massive damage":
        (
            "brutos piglins não podem ser "
            "distraídos com ouro e causam "
            "muito dano"
        ),

    "drowning if buried under water":
        (
            "há risco de afogamento "
            "caso fique preso sob a água"
        ),

    "must defeat the ender dragon first":
        (
            "é necessário derrotar "
            "o Dragão Ender primeiro"
        ),

    "zombie villager in basement can attack":
        (
            "um aldeão zumbi no porão "
            "pode atacar"
        ),

    "arrow trap dispensers on the first floor":
        (
            "há ejetores com armadilhas "
            "de flechas no primeiro andar"
        ),

    "cave spider spawners are very dangerous "
    "in tight spaces":
        (
            "geradores de aranhas das cavernas "
            "são muito perigosos "
            "em espaços apertados"
        ),

    "blaze fireballs and fire damage":
        (
            "bolas de fogo de Blaze "
            "e dano causado por fogo"
        ),

    "mining fatigue from elder guardians "
    "(slows mining by 99.7%)":
        (
            "guardiões anciões podem causar "
            "fadiga de mineração, reduzindo "
            "drasticamente a velocidade de mineração"
        ),

    "drowned can carry tridents":
        (
            "afogados podem carregar "
            "tridentes"
        ),

    "continuous pillager spawning":
        (
            "saqueadores podem aparecer "
            "continuamente"
        ),

    "magma blocks deal damage when stood on":
        (
            "blocos de magma causam dano "
            "quando pisados"
        ),

    "silverfish spawner near end portal":
        (
            "há um gerador de traças "
            "próximo ao portal do End"
        ),

    "trial spawners scale difficulty "
    "with player count":
        (
            "geradores de desafio aumentam "
            "a dificuldade de acordo com "
            "a quantidade de jogadores"
        ),

    "zombie sieges at night":
        (
            "podem ocorrer cercos de "
            "zumbis durante a noite"
        ),

    "witch throws harmful potions":
        (
            "bruxas arremessam "
            "poções nocivas"
        ),

    "vindicators deal heavy melee damage":
        (
            "vingadores causam muito dano "
            "em ataques corpo a corpo"
        ),
}


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================


def _normalize(
    value: Any,
) -> str:
    return (
        str(value)
        .strip()
        .casefold()
    )


def _lookup_name(
    value: str,
    name_translations:
        dict[str, str],
) -> str | None:
    """
    Procura o nome com algumas variações comuns
    de representação da API.
    """

    candidates = {
        value.strip().casefold(),

        value
        .replace("_", " ")
        .strip()
        .casefold(),

        value
        .replace("-", " ")
        .strip()
        .casefold(),
    }

    for candidate in candidates:
        translated = (
            name_translations.get(
                candidate
            )
        )

        if translated:
            return translated

    return None


def _replace_known_entity_names(
    value: str,
    name_translations:
        dict[str, str],
) -> str:
    """
    Substitui nomes originais de entidades que
    eventualmente ainda apareçam dentro de uma
    frase já traduzida.
    """

    result = value

    ordered_names = sorted(
        name_translations.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for original, translated in (
        ordered_names
    ):
        if (
            original.casefold()
            == translated.casefold()
        ):
            continue

        result = re.sub(
            rf"(?<!\w)"
            rf"{re.escape(original)}"
            rf"(?!\w)",
            translated,
            result,
            flags=re.IGNORECASE,
        )

    return result


# =========================================================
# VALORES SIMPLES
# =========================================================


def translate_value(
    value: Any,
) -> str:
    if value is None:
        return "desconhecido"

    if isinstance(
        value,
        bool,
    ):
        return (
            "sim"
            if value
            else "não"
        )

    text = str(value).strip()

    normalized = (
        text.casefold()
    )

    translated_text = (
        TEXT_TRANSLATIONS.get(
            normalized
        )
    )

    if translated_text:
        return translated_text

    translated_value = (
        VALUE_TRANSLATIONS.get(
            normalized
        )
    )

    if translated_value:
        return translated_value

    return text.replace(
        "_",
        " ",
    )


# =========================================================
# REFERÊNCIAS A ENTIDADES
# =========================================================


def translate_reference(
    value: Any,
    name_translations:
        dict[str, str],
) -> str:
    if value is None:
        return "desconhecido"

    text = str(value).strip()

    normalized = (
        text.casefold()
    )

    alias = (
        REFERENCE_ALIASES.get(
            normalized
        )
    )

    if alias:
        return alias

    translated_name = (
        _lookup_name(
            text,
            name_translations,
        )
    )

    if translated_name:
        return translated_name

    return translate_value(
        text
    )


def translate_references(
    values: list[Any],
    name_translations:
        dict[str, str],
) -> list[str]:
    return [
        translate_reference(
            value,
            name_translations,
        )
        for value in values
    ]


# =========================================================
# DETALHES ENTRE PARÊNTESES
# =========================================================


def _translate_detail(
    value: str,
    name_translations:
        dict[str, str],
) -> str:
    text = value.strip()

    normalized = (
        text.casefold()
    )

    # Exemplo:
    # with Lingering Potion
    if normalized.startswith(
        "with "
    ):
        remainder = text[
            len("with "):
        ]

        return (
            "com "
            + translate_game_text(
                remainder,
                name_translations,
            )
        )

    # Exemplo:
    # 3 damage
    damage_match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s+damage",
        text,
        flags=re.IGNORECASE,
    )

    if damage_match:
        return (
            f"{damage_match.group(1)} "
            "de dano"
        )

    # Exemplo:
    # Diamond Boots + Netherite Upgrade + ...
    if " + " in text:
        parts = text.split(
            " + "
        )

        return " + ".join(
            translate_game_text(
                part,
                name_translations,
            )
            for part in parts
        )

    # Exemplo:
    # Warped Forest, Soul Sand Valley
    if ", " in text:
        parts = text.split(
            ", "
        )

        return ", ".join(
            translate_game_text(
                part,
                name_translations,
            )
            for part in parts
        )

    return translate_game_text(
        text,
        name_translations,
    )


# =========================================================
# TEXTOS COMPLEXOS
# =========================================================


def translate_game_text(
    value: Any,
    name_translations:
        dict[str, str],
) -> str:
    if value is None:
        return "desconhecido"

    text = str(value).strip()

    if not text:
        return ""

    normalized = (
        text.casefold()
    )

    # -----------------------------------------------------
    # 1. Traduções exatas
    # -----------------------------------------------------

    translated_text = (
        TEXT_TRANSLATIONS.get(
            normalized
        )
    )

    if translated_text:
        return (
            _replace_known_entity_names(
                translated_text,
                name_translations,
            )
        )

    # -----------------------------------------------------
    # 2. Alias ou entidade direta
    # -----------------------------------------------------

    alias = (
        REFERENCE_ALIASES.get(
            normalized
        )
    )

    if alias:
        return alias

    translated_name = (
        _lookup_name(
            text,
            name_translations,
        )
    )

    if translated_name:
        return translated_name

    # -----------------------------------------------------
    # 3. Water (takes damage)
    # -----------------------------------------------------

    damage_match = re.fullmatch(
        r"(.+?)\s*"
        r"\(takes damage\)\.?",
        text,
        flags=re.IGNORECASE,
    )

    if damage_match:
        source = (
            damage_match
            .group(1)
            .strip()
        )

        return (
            translate_game_text(
                source,
                name_translations,
            )
            + " (causa dano)"
        )

    # -----------------------------------------------------
    # 4. takes extra damage
    # -----------------------------------------------------

    extra_damage_match = re.fullmatch(
        r"(.+?)\s*"
        r"\(takes extra damage\)\.?",
        text,
        flags=re.IGNORECASE,
    )

    if extra_damage_match:
        source = (
            extra_damage_match
            .group(1)
            .strip()
        )

        return (
            translate_game_text(
                source,
                name_translations,
            )
            + " (causa dano adicional)"
        )

    # -----------------------------------------------------
    # 5. Encantamento
    #
    # Bane of Arthropods enchantment
    # Smite enchantment (...)
    # -----------------------------------------------------

    enchantment_match = re.fullmatch(
        r"(.+?)\s+enchantment"
        r"(?:\s*\((.+?)\))?\.?",
        text,
        flags=re.IGNORECASE,
    )

    if enchantment_match:
        enchantment_name = (
            enchantment_match
            .group(1)
            .strip()
        )

        detail = (
            enchantment_match
            .group(2)
        )

        translated_enchantment = (
            translate_reference(
                enchantment_name,
                name_translations,
            )
        )

        result = (
            "encantamento "
            f"{translated_enchantment}"
        )

        if detail:
            result += (
                " ("
                + _translate_detail(
                    detail,
                    name_translations,
                )
                + ")"
            )

        return result

    # -----------------------------------------------------
    # 6. Mob drops (Skeleton)
    # -----------------------------------------------------

    mob_drop_match = re.fullmatch(
        r"mob\s+drops\s*"
        r"\((.+?)\)\.?",
        text,
        flags=re.IGNORECASE,
    )

    if mob_drop_match:
        mob_name = (
            mob_drop_match
            .group(1)
            .strip()
        )

        translated_mob = (
            translate_reference(
                mob_name,
                name_translations,
            )
        )

        return (
            "itens derrubados por "
            f"{translated_mob}"
        )

    # -----------------------------------------------------
    # 7. Witch drops
    # -----------------------------------------------------

    drops_match = re.fullmatch(
        r"(.+?)\s+drops\.?",
        text,
        flags=re.IGNORECASE,
    )

    if drops_match:
        entity_name = (
            drops_match
            .group(1)
            .strip()
        )

        translated_entity = (
            translate_reference(
                entity_name,
                name_translations,
            )
        )

        return (
            "itens derrubados por "
            f"{translated_entity}"
        )

    # -----------------------------------------------------
    # 8. Creeper killed by Skeleton
    # -----------------------------------------------------

    killed_by_match = re.fullmatch(
        r"(.+?)\s+killed\s+by\s+(.+?)\.?",
        text,
        flags=re.IGNORECASE,
    )

    if killed_by_match:
        victim = (
            killed_by_match
            .group(1)
            .strip()
        )

        attacker = (
            killed_by_match
            .group(2)
            .strip()
        )

        translated_victim = (
            translate_reference(
                victim,
                name_translations,
            )
        )

        translated_attacker = (
            translate_reference(
                attacker,
                name_translations,
            )
        )

        return (
            f"{translated_victim} "
            "morto por "
            f"{translated_attacker}"
        )

    # -----------------------------------------------------
    # 9. Trading (Farmer)
    # -----------------------------------------------------

    trading_match = re.fullmatch(
        r"trading\s*"
        r"\((.+?)\)\.?",
        text,
        flags=re.IGNORECASE,
    )

    if trading_match:
        profession = (
            trading_match
            .group(1)
            .strip()
        )

        return (
            "trocas com aldeão "
            f"{translate_value(profession)}"
        )

    # -----------------------------------------------------
    # 10. Bridge chest loot (Bastion Remnant)
    # -----------------------------------------------------

    contextual_chest_match = (
        re.fullmatch(
            r"(.+?)\s+chest\s+loot\s*"
            r"\((.+?)\)\.?",
            text,
            flags=re.IGNORECASE,
        )
    )

    if contextual_chest_match:
        chest_type = (
            contextual_chest_match
            .group(1)
            .strip()
        )

        location = (
            contextual_chest_match
            .group(2)
            .strip()
        )

        chest_type_pt = (
            translate_value(
                chest_type
            )
        )

        if (
            chest_type.casefold()
            == "bridge"
        ):
            chest_type_pt = "ponte"

        location_pt = (
            translate_reference(
                location,
                name_translations,
            )
        )

        return (
            "saque do baú da "
            f"{chest_type_pt} "
            f"em {location_pt}"
        )

    # -----------------------------------------------------
    # 11. End City chest loot
    # -----------------------------------------------------

    chest_loot_match = re.fullmatch(
        r"(.+?)\s+chest\s+loot\.?",
        text,
        flags=re.IGNORECASE,
    )

    if chest_loot_match:
        location = (
            chest_loot_match
            .group(1)
            .strip()
        )

        location_pt = (
            translate_reference(
                location,
                name_translations,
            )
        )

        return (
            "saques de baús de "
            f"{location_pt}"
        )

    # -----------------------------------------------------
    # 12. Ancient City Loot Chest
    # -----------------------------------------------------

    loot_chest_match = re.fullmatch(
        r"(.+?)\s+loot\s+chest\.?",
        text,
        flags=re.IGNORECASE,
    )

    if loot_chest_match:
        location = (
            loot_chest_match
            .group(1)
            .strip()
        )

        location_pt = (
            translate_reference(
                location,
                name_translations,
            )
        )

        return (
            "baús de "
            f"{location_pt}"
        )

    # -----------------------------------------------------
    # 13. Bastion Remnant Loot
    # -----------------------------------------------------

    location_loot_match = re.fullmatch(
        r"(.+?)\s+loot\.?",
        text,
        flags=re.IGNORECASE,
    )

    if location_loot_match:
        location = (
            location_loot_match
            .group(1)
            .strip()
        )

        location_pt = (
            translate_reference(
                location,
                name_translations,
            )
        )

        return (
            "saques de "
            f"{location_pt}"
        )

    # -----------------------------------------------------
    # 14. Forma genérica com parênteses
    #
    # Smithing Table (...)
    # Brewing (...)
    # Nether (...)
    # End Ship (End City)
    # Snowballs (3 damage)
    # -----------------------------------------------------

    parenthetical_match = re.fullmatch(
        r"(.+?)\s*\((.+)\)\.?",
        text,
        flags=re.IGNORECASE,
    )

    if parenthetical_match:
        base = (
            parenthetical_match
            .group(1)
            .strip()
        )

        detail = (
            parenthetical_match
            .group(2)
            .strip()
        )

        base_pt = (
            translate_reference(
                base,
                name_translations,
            )
        )

        if (
            base_pt.casefold()
            == base.casefold()
        ):
            base_pt = (
                translate_value(
                    base
                )
            )

        detail_pt = (
            _translate_detail(
                detail,
                name_translations,
            )
        )

        if (
            base_pt.casefold()
            != base.casefold()
            or detail_pt.casefold()
            != detail.casefold()
        ):
            return (
                f"{base_pt} "
                f"({detail_pt})"
            )

    # -----------------------------------------------------
    # 15. Última tentativa: valor simples
    # -----------------------------------------------------

    return translate_value(
        text
    )