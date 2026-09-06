from sqlalchemy import text

from database import engine
from models.biome import Biome

from repositories.entity_repository import (
    replace_list_values,
    upsert_entity,
)


def save_biome(
    biome: Biome,
    raw_data: dict,
) -> int:
    with engine.begin() as connection:
        entity_id = upsert_entity(
            connection,
            entity_type="biome",
            entity=biome,
            raw_data=raw_data,
        )

        connection.execute(
            text(
                """
                INSERT INTO biomes (
                    entity_id,
                    dimension,
                    temperature,
                    precipitation,
                    rarity,
                    color_grass,
                    color_water,
                    color_foliage,
                    color_sky
                )
                VALUES (
                    :entity_id,
                    :dimension,
                    :temperature,
                    :precipitation,
                    :rarity,
                    :color_grass,
                    :color_water,
                    :color_foliage,
                    :color_sky
                )
                ON DUPLICATE KEY UPDATE
                    dimension = VALUES(dimension),
                    temperature = VALUES(temperature),
                    precipitation = VALUES(precipitation),
                    rarity = VALUES(rarity),
                    color_grass = VALUES(color_grass),
                    color_water = VALUES(color_water),
                    color_foliage = VALUES(color_foliage),
                    color_sky = VALUES(color_sky)
                """
            ),
            {
                "entity_id": entity_id,
                "dimension": biome.dimension,
                "temperature": biome.temperature,
                "precipitation": biome.precipitation,
                "rarity": biome.rarity,
                "color_grass": biome.colors.grass,
                "color_water": biome.colors.water,
                "color_foliage": biome.colors.foliage,
                "color_sky": biome.colors.sky,
            },
        )

        replace_list_values(
            connection,
            entity_id,
            {
                "terrain_features":
                    biome.terrain_features,

                "unique_blocks":
                    biome.unique_blocks,

                "spawning_mobs":
                    biome.spawning_mobs,

                "structures_found":
                    biome.structures_found,
            },
        )

        return entity_id