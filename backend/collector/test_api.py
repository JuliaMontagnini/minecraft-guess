import requests


API_URL = "https://api.astroworldmc.com/v1/mobs"


def main():
    try:
        response = requests.get(
            API_URL,
            timeout=10,
        )

        response.raise_for_status()

        result = response.json()

        print("Status:", response.status_code)
        print("Tipo da resposta:", type(result))

        if isinstance(result, dict):
            print("Campos principais:", result.keys())

        print("\nPrimeiro trecho recebido:")
        print(str(result)[:1000])

    except requests.RequestException as error:
        print("Erro ao consultar a API:")
        print(error)

    except ValueError as error:
        print("A API não retornou JSON válido:")
        print(error)


if __name__ == "__main__":
    main()