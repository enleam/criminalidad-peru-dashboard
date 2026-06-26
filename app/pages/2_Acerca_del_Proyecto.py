import streamlit as st

st.set_page_config(
    page_title="Acerca del Proyecto",
    page_icon="ℹ️",
    layout="wide"
)

st.title("Acerca del Proyecto")

st.markdown("""
## Dashboard de Criminalidad en el Perú

Este proyecto presenta un dashboard interactivo desarrollado con **Python, Streamlit, SQL Server y Plotly** para analizar denuncias policiales registradas en el Perú.

La información utilizada proviene del dataset público de **Denuncias Policiales del MININTER/SIDPOL**, correspondiente al periodo 2018 - 2026.

---

## Objetivo

El objetivo del proyecto es transformar datos públicos en indicadores visuales que permitan explorar el comportamiento de las denuncias policiales por:

- Año
- Mes
- Departamento
- Provincia
- Distrito
- Modalidad del hecho denunciado

---

## Funcionalidades principales

- KPIs generales de denuncias.
- Ranking de departamentos con más denuncias.
- Ranking de modalidades más reportadas.
- Tendencias anuales y mensuales.
- Mapa interactivo por departamento.
- Análisis detallado por provincia y distrito.
- Tabla filtrable con descarga en CSV.

---

## Tecnologías utilizadas

- Python
- Pandas
- SQL Server
- SQLAlchemy
- PyODBC
- Streamlit
- Plotly
- PyDeck

---

## Consideraciones

El dashboard analiza **denuncias policiales registradas**, no necesariamente la totalidad de delitos ocurridos.  
Además, las coordenadas utilizadas en el mapa son puntos de referencia aproximados por departamento para fines de visualización.

---

## Valor del proyecto

Este proyecto demuestra habilidades en:

- Limpieza y transformación de datos reales.
- Carga de datos a SQL Server.
- Modelado básico para análisis.
- Creación de vistas y consultas SQL.
- Desarrollo de dashboards interactivos.
- Visualización geográfica de indicadores.
""")