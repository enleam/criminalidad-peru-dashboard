import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def obtener_engine_sql_server():
    load_dotenv()

    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "yes").lower()

    if not server or not database:
        raise ValueError("Faltan DB_SERVER o DB_DATABASE en el archivo .env")

    if trusted_connection in ["yes", "true", "1"]:
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
    else:
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")

        if not user or not password:
            raise ValueError("Faltan DB_USER o DB_PASSWORD en el archivo .env")

        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )

    connection_url = URL.create(
        "mssql+pyodbc",
        query={"odbc_connect": connection_string}
    )

    return create_engine(connection_url, fast_executemany=True)