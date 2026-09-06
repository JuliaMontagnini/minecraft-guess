import requests


BASE_URL = "https://api.astroworldmc.com/v1"


class AstroworldError(Exception):
    pass


def fetch_endpoint(endpoint: str) -> list[dict]:
    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            timeout=15,
        )

        response.raise_for_status()

        payload = response.json()

    except requests.RequestException as error:
        raise AstroworldError(
            f"Erro ao acessar {endpoint}: {error}"
        ) from error

    except ValueError as error:
        raise AstroworldError(
            f"Resposta JSON inválida em {endpoint}"
        ) from error

    if not payload.get("success"):
        raise AstroworldError(
            f"A API retornou success=false para {endpoint}"
        )

    data = payload.get("data")

    if not isinstance(data, list):
        raise AstroworldError(
            f"O campo data de {endpoint} não é uma lista"
        )

    return data