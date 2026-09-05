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


def describe_type(value):
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

    if isinstance(value, list):
        if not value:
            return "list[empty]"

        inner_types = {
            describe_type(item)
            for item in value
        }

        return f"list[{', '.join(sorted(inner_types))}]"

    if isinstance(value, dict):
        return "dict"

    return type(value).__name__


def inspect_endpoint(endpoint):
    url = f"{BASE_URL}/{endpoint}"

    print("\n" + "=" * 70)
    print(f"ENDPOINT: {endpoint}")
    print("=" * 70)

    response = requests.get(
        url,
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

    print(f"Registros informados pela API: {result.get('count')}")
    print(f"Registros realmente recebidos: {len(data)}")

    field_types = defaultdict(set)

    for record in data:
        if not isinstance(record, dict):
            continue

        for key, value in record.items():
            field_types[key].add(
                describe_type(value)
            )

    print("\nCampos encontrados:")

    for field in sorted(field_types):
        types = ", ".join(
            sorted(field_types[field])
        )

        print(
            f"  {field:<25} -> {types}"
        )

    if data:
        print("\nExemplo de registro:")

        for key, value in data[0].items():
            preview = repr(value)

            if len(preview) > 150:
                preview = preview[:147] + "..."

            print(
                f"  {key:<25} = {preview}"
            )


def main():
    for endpoint in ENDPOINTS:
        try:
            inspect_endpoint(endpoint)

        except requests.RequestException as error:
            print(
                f"\nErro de HTTP em {endpoint}: "
                f"{error}"
            )

        except (
            ValueError,
            TypeError,
        ) as error:
            print(
                f"\nErro nos dados de {endpoint}: "
                f"{error}"
            )


if __name__ == "__main__":
    main()