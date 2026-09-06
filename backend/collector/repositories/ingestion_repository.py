import json

from sqlalchemy import text

from database import engine


def start_ingestion(endpoint: str) -> int:
    with engine.begin() as connection:
        result = connection.execute(
            text(
                """
                INSERT INTO ingestion_runs (
                    endpoint,
                    status
                )
                VALUES (
                    :endpoint,
                    'running'
                )
                """
            ),
            {"endpoint": endpoint},
        )

        return result.lastrowid


def finish_ingestion(
    run_id: int,
    received: int,
    accepted: int,
    rejected: int,
):
    if rejected == 0:
        status = "success"
    elif accepted > 0:
        status = "partial"
    else:
        status = "failed"

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE ingestion_runs
                SET
                    finished_at = CURRENT_TIMESTAMP,
                    records_received = :received,
                    records_accepted = :accepted,
                    records_rejected = :rejected,
                    status = :status
                WHERE id = :run_id
                """
            ),
            {
                "run_id": run_id,
                "received": received,
                "accepted": accepted,
                "rejected": rejected,
                "status": status,
            },
        )


def fail_ingestion(
    run_id: int,
    message: str,
):
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE ingestion_runs
                SET
                    finished_at = CURRENT_TIMESTAMP,
                    status = 'failed',
                    error_message = :message
                WHERE id = :run_id
                """
            ),
            {
                "run_id": run_id,
                "message": message,
            },
        )

def record_ingestion_error(
    run_id: int,
    raw_record: dict,
    error_type: str,
    error_message: str,
):
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO ingestion_errors (
                    ingestion_run_id,
                    external_id,
                    record_name,
                    error_type,
                    error_message,
                    raw_data
                )
                VALUES (
                    :run_id,
                    :external_id,
                    :record_name,
                    :error_type,
                    :error_message,
                    :raw_data
                )
                """
            ),
            {
                "run_id": run_id,
                "external_id": raw_record.get("id"),
                "record_name": raw_record.get("name"),
                "error_type": error_type,
                "error_message": error_message,
                "raw_data": json.dumps(
                    raw_record,
                    ensure_ascii=False,
                ),
            },
        )