import json

from sqlalchemy import text


def upsert_entity(
    connection,
    *,
    entity_type: str,
    entity,
    raw_data: dict,
) -> int:
    connection.execute(
        text(
            """
            INSERT INTO entities (
                external_id,
                entity_type,
                name,
                category,
                version_added,
                notes,
                raw_payload
            )
            VALUES (
                :external_id,
                :entity_type,
                :name,
                :category,
                :version_added,
                :notes,
                :raw_payload
            )
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                category = VALUES(category),
                version_added = VALUES(version_added),
                notes = VALUES(notes),
                raw_payload = VALUES(raw_payload),
                id = LAST_INSERT_ID(id)
            """
        ),
        {
            "external_id": entity.id,
            "entity_type": entity_type,
            "name": entity.name,
            "category": entity.category,
            "version_added": entity.version_added,
            "notes": entity.notes,
            "raw_payload": json.dumps(
                raw_data,
                ensure_ascii=False,
            ),
        },
    )

    return connection.execute(
        text("SELECT LAST_INSERT_ID()")
    ).scalar_one()


def replace_list_values(
    connection,
    entity_id: int,
    attributes: dict[str, list[str]],
):
    connection.execute(
        text(
            """
            DELETE FROM entity_list_values
            WHERE entity_id = :entity_id
            """
        ),
        {"entity_id": entity_id},
    )

    for attribute_name, values in attributes.items():
        for index, value in enumerate(values):
            connection.execute(
                text(
                    """
                    INSERT INTO entity_list_values (
                        entity_id,
                        attribute_name,
                        position_index,
                        value
                    )
                    VALUES (
                        :entity_id,
                        :attribute_name,
                        :position_index,
                        :value
                    )
                    """
                ),
                {
                    "entity_id": entity_id,
                    "attribute_name": attribute_name,
                    "position_index": index,
                    "value": value,
                },
            )