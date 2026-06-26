import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text

# Permite importar db.py desde la carpeta app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from db import obtener_engine_sql_server


st.set_page_config(
    page_title="Análisis Detallado - Criminalidad Perú",
    page_icon="🔎",
    layout="wide"
)


@st.cache_resource
def get_engine():
    return obtener_engine_sql_server()


def cargar_dataframe(query, params=None):
    engine = get_engine()

    with engine.connect() as conn:
        return pd.read_sql_query(
            sql=text(query),
            con=conn,
            params=params or {}
        )


def construir_filtros(
    anios,
    departamentos,
    provincias,
    distritos,
    modalidades
):
    condiciones = ["1 = 1"]
    params = {}

    if anios:
        placeholders = []
        for i, anio in enumerate(anios):
            key = f"anio_{i}"
            placeholders.append(f":{key}")
            params[key] = int(anio)

        condiciones.append(f"anio IN ({', '.join(placeholders)})")

    if departamentos:
        placeholders = []
        for i, departamento in enumerate(departamentos):
            key = f"departamento_{i}"
            placeholders.append(f":{key}")
            params[key] = departamento

        condiciones.append(f"departamento IN ({', '.join(placeholders)})")

    if provincias:
        placeholders = []
        for i, provincia in enumerate(provincias):
            key = f"provincia_{i}"
            placeholders.append(f":{key}")
            params[key] = provincia

        condiciones.append(f"provincia IN ({', '.join(placeholders)})")

    if distritos:
        placeholders = []
        for i, distrito in enumerate(distritos):
            key = f"distrito_{i}"
            placeholders.append(f":{key}")
            params[key] = distrito

        condiciones.append(f"distrito IN ({', '.join(placeholders)})")

    if modalidades:
        placeholders = []
        for i, modalidad in enumerate(modalidades):
            key = f"modalidad_{i}"
            placeholders.append(f":{key}")
            params[key] = modalidad

        condiciones.append(f"modalidad IN ({', '.join(placeholders)})")

    where_sql = " AND ".join(condiciones)

    return where_sql, params


st.title("Análisis Detallado de Denuncias Policiales")
st.caption("Fuente: MININTER - SIDPOL | Dataset de denuncias policiales 2018 - 2026")

# =========================
# Carga de opciones
# =========================

df_anios = cargar_dataframe("""
    SELECT DISTINCT anio
    FROM analytics.fact_denuncias
    ORDER BY anio;
""")

df_departamentos = cargar_dataframe("""
    SELECT DISTINCT departamento
    FROM analytics.fact_denuncias
    WHERE departamento IS NOT NULL
    ORDER BY departamento;
""")

df_provincias = cargar_dataframe("""
    SELECT DISTINCT provincia
    FROM analytics.fact_denuncias
    WHERE provincia IS NOT NULL
    ORDER BY provincia;
""")

df_distritos = cargar_dataframe("""
    SELECT DISTINCT distrito
    FROM analytics.fact_denuncias
    WHERE distrito IS NOT NULL
    ORDER BY distrito;
""")

df_modalidades = cargar_dataframe("""
    SELECT DISTINCT modalidad
    FROM analytics.fact_denuncias
    WHERE modalidad IS NOT NULL
    ORDER BY modalidad;
""")

opciones_anio = df_anios["anio"].tolist()
opciones_departamento = df_departamentos["departamento"].tolist()
opciones_provincia = df_provincias["provincia"].tolist()
opciones_distrito = df_distritos["distrito"].tolist()
opciones_modalidad = df_modalidades["modalidad"].tolist()

# =========================
# Filtros
# =========================

st.sidebar.header("Filtros detallados")

anios_seleccionados = st.sidebar.multiselect(
    "Año",
    opciones_anio,
    default=opciones_anio
)

departamentos_seleccionados = st.sidebar.multiselect(
    "Departamento",
    opciones_departamento
)

provincias_seleccionadas = st.sidebar.multiselect(
    "Provincia",
    opciones_provincia
)

distritos_seleccionados = st.sidebar.multiselect(
    "Distrito",
    opciones_distrito
)

modalidades_seleccionadas = st.sidebar.multiselect(
    "Modalidad",
    opciones_modalidad
)

where_sql, params = construir_filtros(
    anios_seleccionados,
    departamentos_seleccionados,
    provincias_seleccionadas,
    distritos_seleccionados,
    modalidades_seleccionadas
)

# =========================
# KPIs detallados
# =========================

df_kpis = cargar_dataframe(f"""
    SELECT
        SUM(cantidad) AS total_denuncias,
        COUNT(*) AS total_registros,
        COUNT(DISTINCT departamento) AS departamentos,
        COUNT(DISTINCT provincia) AS provincias,
        COUNT(DISTINCT distrito) AS distritos,
        COUNT(DISTINCT modalidad) AS modalidades
    FROM analytics.fact_denuncias
    WHERE {where_sql};
""", params)

total_denuncias = int(df_kpis.loc[0, "total_denuncias"] or 0)
total_registros = int(df_kpis.loc[0, "total_registros"] or 0)
total_departamentos = int(df_kpis.loc[0, "departamentos"] or 0)
total_provincias = int(df_kpis.loc[0, "provincias"] or 0)
total_distritos = int(df_kpis.loc[0, "distritos"] or 0)
total_modalidades = int(df_kpis.loc[0, "modalidades"] or 0)

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

col1.metric("Total de denuncias", f"{total_denuncias:,}")
col2.metric("Registros agregados", f"{total_registros:,}")
col3.metric("Departamentos", f"{total_departamentos:,}")
col4.metric("Provincias", f"{total_provincias:,}")
col5.metric("Distritos", f"{total_distritos:,}")
col6.metric("Modalidades", f"{total_modalidades:,}")

st.divider()

# =========================
# Top 20 distritos
# =========================

st.subheader("Top 20 distritos con más denuncias")

df_top_distritos = cargar_dataframe(f"""
    SELECT TOP 20
        departamento,
        provincia,
        distrito,
        SUM(cantidad) AS total_denuncias
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    GROUP BY departamento, provincia, distrito
    ORDER BY total_denuncias DESC;
""", params)

if df_top_distritos.empty:
    st.warning("No hay datos para mostrar con los filtros seleccionados.")
else:
    df_top_distritos["ubicacion"] = (
        df_top_distritos["distrito"] + " - " +
        df_top_distritos["provincia"] + " - " +
        df_top_distritos["departamento"]
    )

    fig_top_distritos = px.bar(
        df_top_distritos.sort_values("total_denuncias"),
        x="total_denuncias",
        y="ubicacion",
        orientation="h",
        title="Ranking de distritos por total de denuncias"
    )

    fig_top_distritos.update_layout(
        xaxis_title="Total de denuncias",
        yaxis_title="Distrito / Provincia / Departamento"
    )

    st.plotly_chart(fig_top_distritos, use_container_width=True)

st.divider()

# =========================
# Evolución mensual por modalidad
# =========================

st.subheader("Evolución mensual por modalidad")

df_mensual_modalidad = cargar_dataframe(f"""
    SELECT
        fecha_periodo,
        modalidad,
        SUM(cantidad) AS total_denuncias
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    GROUP BY fecha_periodo, modalidad
    ORDER BY fecha_periodo;
""", params)

if df_mensual_modalidad.empty:
    st.warning("No hay datos para la evolución mensual.")
else:
    top_modalidades = (
        df_mensual_modalidad
        .groupby("modalidad")["total_denuncias"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .index
    )

    df_mensual_top = df_mensual_modalidad[
        df_mensual_modalidad["modalidad"].isin(top_modalidades)
    ]

    fig_mensual_modalidad = px.line(
        df_mensual_top,
        x="fecha_periodo",
        y="total_denuncias",
        color="modalidad",
        title="Evolución mensual de las 5 modalidades más frecuentes"
    )

    fig_mensual_modalidad.update_layout(
        xaxis_title="Periodo",
        yaxis_title="Total de denuncias",
        legend_title="Modalidad"
    )

    st.plotly_chart(fig_mensual_modalidad, use_container_width=True)

st.divider()

# =========================
# Comparación por modalidad
# =========================

st.subheader("Ranking de modalidades")

df_ranking_modalidad = cargar_dataframe(f"""
    SELECT TOP 15
        modalidad,
        SUM(cantidad) AS total_denuncias
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    GROUP BY modalidad
    ORDER BY total_denuncias DESC;
""", params)

if df_ranking_modalidad.empty:
    st.warning("No hay modalidades para mostrar.")
else:
    fig_modalidad = px.bar(
        df_ranking_modalidad.sort_values("total_denuncias"),
        x="total_denuncias",
        y="modalidad",
        orientation="h",
        title="Top 15 modalidades con más denuncias"
    )

    fig_modalidad.update_layout(
        xaxis_title="Total de denuncias",
        yaxis_title="Modalidad"
    )

    st.plotly_chart(fig_modalidad, use_container_width=True)

st.divider()

# =========================
# Tabla detallada
# =========================

st.subheader("Tabla detallada para exploración")

df_detalle = cargar_dataframe(f"""
    SELECT TOP 1000
        anio,
        mes,
        fecha_periodo,
        departamento,
        provincia,
        distrito,
        ubigeo,
        modalidad,
        cantidad
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    ORDER BY cantidad DESC;
""", params)

st.dataframe(df_detalle, use_container_width=True)

csv = df_detalle.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Descargar tabla filtrada en CSV",
    data=csv,
    file_name="denuncias_filtradas.csv",
    mime="text/csv"
)

st.caption(
    "Nota: la información corresponde a denuncias policiales registradas. "
    "No representa necesariamente la totalidad de delitos ocurridos."
)