import logging

from pydantic import ValidationError

from logging_config import configure_logging

from models.biome import Biome
from models.enchantment import Enchantment
from models.item import Item
from models.mob import Mob
from models.structure import Structure

from repositories.biome_repository import (
    save_biome,
)

from repositories.enchantment_repository import (
    save_enchantment,
)

from repositories.ingestion_repository import (
    fail_ingestion,
    finish_ingestion,
    record_ingestion_error,
    start_ingestion,
)

from repositories.item_repository import (
    save_item,
)

from repositories.mob_repository import (
    save_mob,
)

from repositories.structure_repository import (
    save_structure,
)

from services.astroworld import (
    AstroworldError,
    fetch_endpoint,
)


configure_logging()

logger = logging.getLogger(
    "minecraft_guess.collector"
)


COLLECTORS = {
    "mobs": {
        "model": Mob,
        "save": save_mob,
    },

    "biomes": {
        "model": Biome,
        "save": save_biome,
    },

    "items": {
        "model": Item,
        "save": save_item,
    },

    "structures": {
        "model": Structure,
        "save": save_structure,
    },

    "enchantments": {
        "model": Enchantment,
        "save": save_enchantment,
    },
}


def collect_endpoint(
    endpoint: str,
    model,
    save_function,
):
    logger.info(
        "Iniciando coleta do endpoint %s",
        endpoint,
    )

    run_id = start_ingestion(
        endpoint
    )

    accepted = 0
    rejected = 0

    try:
        records = fetch_endpoint(
            endpoint
        )

        received = len(records)

        logger.info(
            "%s: %d registros recebidos",
            endpoint,
            received,
        )

        for raw_record in records:
            try:
                validated = model.model_validate(
                    raw_record
                )

                save_function(
                    validated,
                    raw_record,
                )

                accepted += 1

            except ValidationError as error:
                rejected += 1

                name = raw_record.get(
                    "name",
                    "desconhecido",
                )

                logger.error(
                    "%s: falha de validação em %s",
                    endpoint,
                    name,
                )

                record_ingestion_error(
                    run_id=run_id,
                    raw_record=raw_record,
                    error_type="validation_error",
                    error_message=str(error),
                )

            except Exception as error:
                rejected += 1

                name = raw_record.get(
                    "name",
                    "desconhecido",
                )

                logger.exception(
                    "%s: falha ao persistir %s",
                    endpoint,
                    name,
                )

                record_ingestion_error(
                    run_id=run_id,
                    raw_record=raw_record,
                    error_type="persistence_error",
                    error_message=str(error),
                )

        finish_ingestion(
            run_id=run_id,
            received=received,
            accepted=accepted,
            rejected=rejected,
        )

        logger.info(
            (
                "%s finalizado: "
                "%d recebidos, "
                "%d aceitos, "
                "%d rejeitados"
            ),
            endpoint,
            received,
            accepted,
            rejected,
        )

        return {
            "endpoint": endpoint,
            "received": received,
            "accepted": accepted,
            "rejected": rejected,
        }

    except AstroworldError as error:
        fail_ingestion(
            run_id,
            str(error),
        )

        logger.exception(
            "Falha ao consultar %s",
            endpoint,
        )

        return {
            "endpoint": endpoint,
            "received": 0,
            "accepted": 0,
            "rejected": 0,
            "failed": True,
        }

    except Exception as error:
        fail_ingestion(
            run_id,
            str(error),
        )

        logger.exception(
            "Falha inesperada em %s",
            endpoint,
        )

        return {
            "endpoint": endpoint,
            "received": 0,
            "accepted": 0,
            "rejected": 0,
            "failed": True,
        }


def print_summary(results):
    print()
    print("=" * 62)
    print("RESUMO DA COLETA")
    print("=" * 62)

    total_received = 0
    total_accepted = 0
    total_rejected = 0

    for result in results:
        endpoint = result["endpoint"]

        received = result["received"]
        accepted = result["accepted"]
        rejected = result["rejected"]

        total_received += received
        total_accepted += accepted
        total_rejected += rejected

        print(
            f"{endpoint:<15} "
            f"{accepted:>3}/{received:<3} "
            f"rejeitados: {rejected}"
        )

    print("-" * 62)

    print(
        f"{'TOTAL':<15} "
        f"{total_accepted:>3}/{total_received:<3} "
        f"rejeitados: {total_rejected}"
    )


def main():
    results = []

    logger.info(
        "Iniciando coleta completa"
    )

    for endpoint, config in COLLECTORS.items():
        result = collect_endpoint(
            endpoint=endpoint,
            model=config["model"],
            save_function=config["save"],
        )

        results.append(result)

    print_summary(results)

    logger.info(
        "Coleta completa finalizada"
    )


if __name__ == "__main__":
    main()