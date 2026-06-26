import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


RUTA_CSV = Path("data/raw/denuncias_policiales_2018_2026.csv")


def limpiar_texto(serie):
    return (
        serie.astype("string")
        .str.strip()
        .str.upper()
    )


def limpiar_ubigeo(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip().replace(".0", "")
    solo_digitos = "".join(caracter for caracter in valor if caracter.isdigit())

    if solo_digitos == "":
        return None

    return solo_digitos.zfill(6)


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


def cargar_dataset():
    print("Leyendo CSV...")

    df = pd.read_csv(
        RUTA_CSV,
        encoding="utf-8-sig",
        sep=",",
        dtype={"UBIGEO_HECHO": "string"},
        low_memory=False
    )

    print(f"Filas leídas: {len(df):,}")

    df = df.rename(columns={
        "ANIO": "anio",
        "MES": "mes",
        "DPTO_HECHO_NEW": "departamento",
        "PROV_HECHO": "provincia",
        "DIST_HECHO": "distrito",
        "UBIGEO_HECHO": "ubigeo",
        "P_MODALIDADES": "modalidad",
        "cantidad": "cantidad"
    })

    columnas_necesarias = [
        "anio",
        "mes",
        "departamento",
        "provincia",
        "distrito",
        "ubigeo",
        "modalidad",
        "cantidad"
    ]

    df = df[columnas_necesarias]

    print("Limpiando datos...")

    df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
    df["mes"] = pd.to_numeric(df["mes"], errors="coerce")
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")

    df["departamento"] = limpiar_texto(df["departamento"])
    df["provincia"] = limpiar_texto(df["provincia"])
    df["distrito"] = limpiar_texto(df["distrito"])
    df["modalidad"] = limpiar_texto(df["modalidad"])

    df["ubigeo"] = df["ubigeo"].apply(limpiar_ubigeo)

    df = df.dropna(subset=[
        "anio",
        "mes",
        "departamento",
        "modalidad",
        "cantidad"
    ])

    df["anio"] = df["anio"].astype(int)
    df["mes"] = df["mes"].astype(int)
    df["cantidad"] = df["cantidad"].astype(int)

    df = df[
        (df["anio"] >= 2018) &
        (df["mes"] >= 1) &
        (df["mes"] <= 12) &
        (df["cantidad"] >= 0)
    ]

    df["fecha_periodo"] = pd.to_datetime(
        df["anio"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2) + "-01"
    ).dt.date

    df["fuente"] = "MININTER - SIDPOL"

    df = df[
        [
            "anio",
            "mes",
            "fecha_periodo",
            "departamento",
            "provincia",
            "distrito",
            "ubigeo",
            "modalidad",
            "cantidad",
            "fuente"
        ]
    ]

    print(f"Filas limpias para cargar: {len(df):,}")
    print("Conectando a SQL Server...")

    engine = obtener_engine_sql_server()

    with engine.begin() as conn:
        print("Limpiando tabla analytics.fact_denuncias...")
        conn.execute(text("TRUNCATE TABLE analytics.fact_denuncias;"))

    print("Cargando datos a SQL Server...")

    df.to_sql(
        name="fact_denuncias",
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        chunksize=10000
    )

    print("Carga completada correctamente.")
    print(f"Total cargado: {len(df):,} filas")


if __name__ == "__main__":
    cargar_dataset()