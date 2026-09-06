from pydantic import ValidationError

from models.mob import Mob

from repositories.ingestion_repository import (
    fail_ingestion,
    finish_ingestion,
    start_ingestion,
)

from repositories.mob_repository import save_mob

from services.astroworld import (
    AstroworldError,
    fetch_endpoint,
)


def main():
    endpoint = "mobs"

    run_id = start_ingestion(endpoint)

    accepted = 0
    rejected = 0

    try:
        records = fetch_endpoint(endpoint)

        print(
            f"Recebidos da Astroworld: {len(records)}"
        )

        for raw_record in records:
            try:
                mob = Mob.model_validate(
                    raw_record
                )

                save_mob(
                    mob,
                    raw_record,
                )

                accepted += 1

                print(
                    f"✓ {mob.name}"
                )

            except ValidationError as error:
                rejected += 1

                print(
                    "✗ Registro inválido:",
                    raw_record.get(
                        "name",
                        "desconhecido",
                    ),
                )

                print(error)

            except Exception as error:
                rejected += 1

                print(
                    "✗ Erro ao persistir:",
                    raw_record.get(
                        "name",
                        "desconhecido",
                    ),
                )

                print(error)

        finish_ingestion(
            run_id=run_id,
            received=len(records),
            accepted=accepted,
            rejected=rejected,
        )

        print("\n" + "=" * 50)
        print("COLETA CONCLUÍDA")
        print("=" * 50)

        print(f"Recebidos: {len(records)}")
        print(f"Aceitos:   {accepted}")
        print(f"Rejeitados:{rejected}")

    except AstroworldError as error:
        fail_ingestion(
            run_id,
            str(error),
        )

        print(
            "Falha na comunicação com a Astroworld:"
        )
        print(error)

    except Exception as error:
        fail_ingestion(
            run_id,
            str(error),
        )

        print("Falha inesperada:")
        print(error)


if __name__ == "__main__":
    main()