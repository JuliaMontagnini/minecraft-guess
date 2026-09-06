from models.biome import Biome

from repositories.biome_repository import (
    save_biome,
)

from services.astroworld import fetch_endpoint


def main():
    records = fetch_endpoint("biomes")

    accepted = 0

    for raw_record in records:
        biome = Biome.model_validate(
            raw_record
        )

        save_biome(
            biome,
            raw_record,
        )

        accepted += 1

        print(f"✓ {biome.name}")

    print()
    print(f"Biomas persistidos: {accepted}")


if __name__ == "__main__":
    main()