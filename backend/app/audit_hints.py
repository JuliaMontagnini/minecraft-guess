import re

from sqlalchemy import text

from app.database import engine
from app.game_service import (
    build_hints,
    load_payload,
)


def main():
    with engine.connect() as connection:
        entities = connection.execute(
            text(
                """
                SELECT
                    id,
                    external_id,
                    entity_type,
                    name,
                    raw_payload
                FROM entities
                ORDER BY entity_type, name
                """
            )
        ).mappings().all()

    total = len(entities)

    insufficient = []
    leaking = []
    errors = []

    print("=" * 70)
    print("AUDITORIA DE DICAS")
    print("=" * 70)

    for entity in entities:
        try:
            payload = load_payload(
                entity["raw_payload"]
            )

            hints = build_hints(
                entity_type=entity["entity_type"],
                payload=payload,
                secret_name=entity["name"],
            )

            if len(hints) < 4:
                insufficient.append(
                    {
                        "type": entity["entity_type"],
                        "name": entity["name"],
                        "count": len(hints),
                        "hints": hints,
                    }
                )

            secret_pattern = re.compile(
                rf"(?<!\w){re.escape(entity['name'])}(?!\w)",
                re.IGNORECASE,
            )

            for hint in hints:
                if secret_pattern.search(hint):
                    leaking.append(
                        {
                            "type": entity["entity_type"],
                            "name": entity["name"],
                            "hint": hint,
                        }
                    )

        except Exception as error:
            errors.append(
                {
                    "type": entity["entity_type"],
                    "name": entity["name"],
                    "error": str(error),
                }
            )

    print(f"Entidades verificadas: {total}")
    print(
        "Com menos de 4 dicas: "
        f"{len(insufficient)}"
    )
    print(
        "Dicas que revelam o nome: "
        f"{len(leaking)}"
    )
    print(
        "Erros durante auditoria: "
        f"{len(errors)}"
    )

    if insufficient:
        print("\n" + "-" * 70)
        print("ENTIDADES COM MENOS DE 4 DICAS")
        print("-" * 70)

        for item in insufficient:
            print(
                f"{item['type']:<15} "
                f"{item['name']:<35} "
                f"{item['count']} dica(s)"
            )

    if leaking:
        print("\n" + "-" * 70)
        print("POSSÍVEIS VAZAMENTOS")
        print("-" * 70)

        for item in leaking:
            print(
                f"{item['type']} | "
                f"{item['name']} | "
                f"{item['hint']}"
            )

    if errors:
        print("\n" + "-" * 70)
        print("ERROS")
        print("-" * 70)

        for item in errors:
            print(
                f"{item['type']} | "
                f"{item['name']} | "
                f"{item['error']}"
            )

    print("\n" + "=" * 70)

    if (
        not insufficient
        and not leaking
        and not errors
    ):
        print(
            "✓ Todas as entidades possuem "
            "4 dicas seguras."
        )
    else:
        print(
            "A auditoria encontrou pontos "
            "que precisam de revisão."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()