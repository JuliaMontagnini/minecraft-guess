import json
import os
import sys
from pathlib import Path
from typing import Any


DATABASE_VARIABLES = (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
)


def get_parameter_value(
    parameter_name: str,
) -> str:
    """
    Busca no Parameter Store um parâmetro
    SecureString contendo a configuração
    JSON do banco.
    """
    import boto3

    client = boto3.client(
        "ssm"
    )

    response = client.get_parameter(
        Name=parameter_name,
        WithDecryption=True,
    )

    return response[
        "Parameter"
    ][
        "Value"
    ]


def configure_database_environment() -> None:
    """
    Prepara as variáveis usadas pelo
    collector/database.py.

    Em desenvolvimento, as variáveis podem
    já existir no ambiente.

    Na Lambda, elas são carregadas de um
    parâmetro SecureString.
    """
    missing_variables = [
        variable
        for variable
        in DATABASE_VARIABLES
        if not os.getenv(variable)
    ]

    if not missing_variables:
        return

    parameter_name = os.getenv(
        "DB_PARAMETER_NAME"
    )

    if not parameter_name:
        raise RuntimeError(
            "DB_PARAMETER_NAME não foi "
            "configurado e faltam variáveis "
            "do banco: "
            + ", ".join(
                missing_variables
            )
        )

    raw_parameter = (
        get_parameter_value(
            parameter_name
        )
    )

    try:
        database_config = json.loads(
            raw_parameter
        )
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "O parâmetro do banco não "
            "contém um JSON válido."
        ) from error

    if not isinstance(
        database_config,
        dict,
    ):
        raise RuntimeError(
            "A configuração do banco "
            "deve ser um objeto JSON."
        )

    missing_keys = [
        variable
        for variable
        in DATABASE_VARIABLES
        if not database_config.get(
            variable
        )
    ]

    if missing_keys:
        raise RuntimeError(
            "Configuração do banco "
            "incompleta no Parameter Store: "
            + ", ".join(
                missing_keys
            )
        )

    for variable in DATABASE_VARIABLES:
        os.environ[variable] = str(
            database_config[
                variable
            ]
        )


def run_collection() -> list[dict]:
    """
    Importa o coletor somente depois que
    as variáveis do banco foram carregadas.
    """
    collector_directory = (
        Path(__file__).resolve().parent
        / "collector"
    )

    collector_path = str(
        collector_directory
    )

    if collector_path not in sys.path:
        sys.path.insert(
            0,
            collector_path,
        )

    from collector import main

    return main()


def build_summary(
    results: list[dict],
) -> dict[str, Any]:
    total_received = sum(
        result["received"]
        for result in results
    )

    total_accepted = sum(
        result["accepted"]
        for result in results
    )

    total_rejected = sum(
        result["rejected"]
        for result in results
    )

    return {
        "received": total_received,
        "accepted": total_accepted,
        "rejected": total_rejected,
    }


def lambda_handler(
    event,
    context,
) -> dict[str, Any]:
    configure_database_environment()

    results = run_collection()

    failed_endpoints = [
        result["endpoint"]
        for result in results
        if result.get(
            "failed",
            False,
        )
    ]

    if failed_endpoints:
        raise RuntimeError(
            "Falha na coleta dos endpoints: "
            + ", ".join(
                failed_endpoints
            )
        )

    return {
        "status": "ok",
        "summary": build_summary(
            results
        ),
        "endpoints": results,
    }
