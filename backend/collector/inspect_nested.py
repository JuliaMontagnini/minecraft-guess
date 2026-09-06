import requests
from collections import defaultdict


BASE_URL = "https://api.astroworldmc.com/v1"

ENDPOINTS = [
    "mobs",
    "biomes",
    "items",
    "structures",
    "enchantments",
]


def get_type(value):
    if value is None:
        return "null"

    if isinstance(value, bool):
        return "bool"

    if isinstance(value, int):
        return "int"

    if isinstance(value, float):
        return "float"

    if isinstance(value, str):
        return "str"

    if isinstance(value, dict):
        return "dict"

    if isinstance(value, list):
        return "list"

    return type(value).__name__


def inspect_value(value, path, field_types):
    field_types[path].add(get_type(value))

    if isinstance(value, dict):
        for key, nested_value in value.items():
            nested_path = f"{path}.{key}"

            inspect_value(
                nested_value,
                nested_path,
                field_types,
            )

    elif isinstance(value, list):
        for item in value:
            nested_path = f"{path}[]"

            inspect_value(
                item,
                nested_path,
                field_types,
            )


def inspect_endpoint(endpoint):
    print("\n" + "=" * 80)
    print(f"ENDPOINT: {endpoint}")
    print("=" * 80)

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        timeout=15,
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("success"):
        raise ValueError(
            f"A API informou falha em {endpoint}"
        )

    data = result.get("data")

    if not isinstance(data, list):
        raise TypeError(
            f"'data' de {endpoint} não é uma lista"
        )

    field_types = defaultdict(set)

    for record in data:
        if not isinstance(record, dict):
            continue

        for key, value in record.items():
            inspect_value(
                value,
                key,
                field_types,
            )

    for path in sorted(field_types):
        types = ", ".join(
            sorted(field_types[path])
        )

        print(
            f"{path:<45} -> {types}"
        )


def main():
    for endpoint in ENDPOINTS:
        try:
            inspect_endpoint(endpoint)

        except requests.RequestException as error:
            print(
                f"Erro HTTP em {endpoint}: {error}"
            )

        except (ValueError, TypeError) as error:
            print(
                f"Erro de dados em {endpoint}: {error}"
            )


if __name__ == "__main__":
    main()