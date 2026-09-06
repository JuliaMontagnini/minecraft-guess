import json

import requests
from pydantic import ValidationError

from models.mob import Mob
from models.biome import Biome
from models.item import Item
from models.structure import Structure
from models.enchantment import Enchantment


BASE_URL = "https://api.astroworldmc.com/v1"


MODELS = {
    "mobs": Mob,
    "biomes": Biome,
    "items": Item,
    "structures": Structure,
    "enchantments": Enchantment,
}


def validate_endpoint(endpoint, model):
    print("\n" + "=" * 70)
    print(f"VALIDANDO: {endpoint}")
    print("=" * 70)

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        timeout=15,
    )

    response.raise_for_status()

    result = response.json()

    data = result.get("data", [])

    valid = []
    errors = []

    for index, raw_record in enumerate(data):
        try:
            validated = model.model_validate(
                raw_record
            )

            valid.append(validated)

        except ValidationError as error:
            errors.append(
                {
                    "index": index,
                    "id": raw_record.get("id"),
                    "name": raw_record.get("name"),
                    "errors": error.errors(),
                }
            )

    print(f"Recebidos: {len(data)}")
    print(f"Válidos:   {len(valid)}")
    print(f"Inválidos: {len(errors)}")

    return {
        "endpoint": endpoint,
        "received": len(data),
        "valid": len(valid),
        "invalid": len(errors),
        "errors": errors,
    }


def main():
    report = []

    for endpoint, model in MODELS.items():
        try:
            result = validate_endpoint(
                endpoint,
                model,
            )

            report.append(result)

        except requests.RequestException as error:
            report.append(
                {
                    "endpoint": endpoint,
                    "http_error": str(error),
                }
            )

            print(f"Erro HTTP: {error}")

    with open(
        "validation_report.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "\nRelatório salvo em "
        "validation_report.json"
    )


if __name__ == "__main__":
    main()