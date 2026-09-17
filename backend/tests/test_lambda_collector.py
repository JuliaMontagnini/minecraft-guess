import json

import pytest

import lambda_collector


DATABASE_CONFIG = {
    "DB_HOST":
        "database.internal",

    "DB_PORT":
        "3306",

    "DB_NAME":
        "minecraft_guess",

    "DB_USER":
        "minecraft_admin",

    "DB_PASSWORD":
        "test_password",
}


def set_database_environment(
    monkeypatch,
):
    for variable, value in (
        DATABASE_CONFIG.items()
    ):
        monkeypatch.setenv(
            variable,
            value,
        )


def clear_database_environment(
    monkeypatch,
):
    for variable in (
        lambda_collector
        .DATABASE_VARIABLES
    ):
        monkeypatch.delenv(
            variable,
            raising=False,
        )


def test_loads_database_environment_from_parameter(
    monkeypatch,
):
    clear_database_environment(
        monkeypatch
    )

    monkeypatch.setenv(
        "DB_PARAMETER_NAME",
        "/minecraft-guess/prod/database",
    )

    monkeypatch.setattr(
        lambda_collector,
        "get_parameter_value",
        lambda parameter_name:
            json.dumps(
                DATABASE_CONFIG
            ),
    )

    (
        lambda_collector
        .configure_database_environment()
    )

    for variable, expected in (
        DATABASE_CONFIG.items()
    ):
        assert (
            lambda_collector
            .os.getenv(variable)
        ) == expected


def test_lambda_handler_returns_collection_summary(
    monkeypatch,
):
    set_database_environment(
        monkeypatch
    )

    results = [
        {
            "endpoint": "mobs",
            "received": 76,
            "accepted": 76,
            "rejected": 0,
        },
        {
            "endpoint": "biomes",
            "received": 64,
            "accepted": 64,
            "rejected": 0,
        },
    ]

    monkeypatch.setattr(
        lambda_collector,
        "run_collection",
        lambda: results,
    )

    response = (
        lambda_collector
        .lambda_handler(
            {},
            None,
        )
    )

    assert response["status"] == "ok"

    assert response["summary"] == {
        "received": 140,
        "accepted": 140,
        "rejected": 0,
    }

    assert response[
        "endpoints"
    ] == results


def test_lambda_handler_fails_when_endpoint_fails(
    monkeypatch,
):
    set_database_environment(
        monkeypatch
    )

    results = [
        {
            "endpoint": "items",
            "received": 0,
            "accepted": 0,
            "rejected": 0,
            "failed": True,
        },
    ]

    monkeypatch.setattr(
        lambda_collector,
        "run_collection",
        lambda: results,
    )

    with pytest.raises(
        RuntimeError,
        match="items",
    ):
        (
            lambda_collector
            .lambda_handler(
                {},
                None,
            )
        )
