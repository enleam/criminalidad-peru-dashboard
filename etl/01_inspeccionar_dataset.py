import pandas as pd
from pathlib import Path

RUTA_CSV = Path("data/raw/denuncias_policiales_2018_2026.csv")

def leer_csv_seguro(ruta):
    intentos = [
        {"encoding": "utf-8-sig", "sep": ","},
        {"encoding": "latin1", "sep": ","},
        {"encoding": "utf-8-sig", "sep": ";"},
        {"encoding": "latin1", "sep": ";"},
    ]

    for config in intentos:
        try:
            df = pd.read_csv(ruta, **config, nrows=10)
            print("Archivo leído correctamente con:")
            print(config)
            return df, config
        except Exception:
            pass

    raise Exception("No se pudo leer el CSV con las configuraciones probadas.")

df, config = leer_csv_seguro(RUTA_CSV)

print("\nCOLUMNAS DEL DATASET:")
for col in df.columns:
    print("-", col)

print("\nPRIMERAS FILAS:")
print(df.head())

print("\nCantidad de columnas:", len(df.columns))