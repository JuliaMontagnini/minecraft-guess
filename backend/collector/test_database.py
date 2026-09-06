from sqlalchemy import text

from database import engine


def main():
    try:
        with engine.connect() as connection:
            database_name = connection.execute(
                text("SELECT DATABASE()")
            ).scalar_one()

            mysql_version = connection.execute(
                text("SELECT VERSION()")
            ).scalar_one()

        print("Conexão realizada com sucesso!")
        print(f"Banco: {database_name}")
        print(f"MySQL: {mysql_version}")

    except Exception as error:
        print("Erro ao conectar ao banco:")
        print(error)


if __name__ == "__main__":
    main()