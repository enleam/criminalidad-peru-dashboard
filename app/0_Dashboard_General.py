import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text
import pydeck as pdk

from db import obtener_engine_sql_server


st.set_page_config(
    page_title="Dashboard de Criminalidad en Perú",
    page_icon="📊",
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


def construir_filtros(anios, departamentos, modalidades):
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

    if modalidades:
        placeholders = []
        for i, modalidad in enumerate(modalidades):
            key = f"modalidad_{i}"
            placeholders.append(f":{key}")
            params[key] = modalidad

        condiciones.append(f"modalidad IN ({', '.join(placeholders)})")

    where_sql = " AND ".join(condiciones)

    return where_sql, params


st.title("Dashboard de Criminalidad en el Perú")
st.caption("Fuente: MININTER - SIDPOL | Dataset de denuncias policiales 2018 - 2026")

# =========================
# Carga de filtros
# =========================

df_anios = cargar_dataframe("""
    SELECT DISTINCT anio
    FROM analytics.fact_denuncias
    ORDER BY anio;
""")

df_departamentos = cargar_dataframe("""
    SELECT DISTINCT departamento
    FROM analytics.fact_denuncias
    ORDER BY departamento;
""")

df_modalidades = cargar_dataframe("""
    SELECT DISTINCT modalidad
    FROM analytics.fact_denuncias
    ORDER BY modalidad;
""")

opciones_anio = df_anios["anio"].tolist()
opciones_departamento = df_departamentos["departamento"].tolist()
opciones_modalidad = df_modalidades["modalidad"].tolist()

st.sidebar.header("Filtros")

anios_seleccionados = st.sidebar.multiselect(
    "Año",
    opciones_anio,
    default=opciones_anio
)

departamentos_seleccionados = st.sidebar.multiselect(
    "Departamento",
    opciones_departamento
)

modalidades_seleccionadas = st.sidebar.multiselect(
    "Modalidad",
    opciones_modalidad
)

where_sql, params = construir_filtros(
    anios_seleccionados,
    departamentos_seleccionados,
    modalidades_seleccionadas
)

# =========================
# KPIs
# =========================

df_kpi = cargar_dataframe(f"""
    SELECT
        SUM(cantidad) AS total_denuncias,
        COUNT(*) AS total_registros,
        COUNT(DISTINCT departamento) AS total_departamentos,
        COUNT(DISTINCT modalidad) AS total_modalidades
    FROM analytics.fact_denuncias
    WHERE {where_sql};
""", params)

df_top_departamento = cargar_dataframe(f"""
    SELECT TOP 1
        departamento,
        SUM(cantidad) AS total_denuncias
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    GROUP BY departamento
    ORDER BY total_denuncias DESC;
""", params)

df_top_modalidad = cargar_dataframe(f"""
    SELECT TOP 1
        modalidad,
        SUM(cantidad) AS total_denuncias
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    GROUP BY modalidad
    ORDER BY total_denuncias DESC;
""", params)

total_denuncias = int(df_kpi.loc[0, "total_denuncias"] or 0)
total_registros = int(df_kpi.loc[0, "total_registros"] or 0)
total_departamentos = int(df_kpi.loc[0, "total_departamentos"] or 0)
total_modalidades = int(df_kpi.loc[0, "total_modalidades"] or 0)

top_departamento = (
    df_top_departamento.loc[0, "departamento"]
    if not df_top_departamento.empty
    else "Sin datos"
)

top_modalidad = (
    df_top_modalidad.loc[0, "modalidad"]
    if not df_top_modalidad.empty
    else "Sin datos"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de denuncias", f"{total_denuncias:,}")
col2.metric("Registros agregados", f"{total_registros:,}")
col3.metric("Departamentos", f"{total_departamentos:,}")
col4.metric("Modalidades", f"{total_modalidades:,}")

col5, col6 = st.columns(2)

col5.info(f"Departamento con más denuncias: **{top_departamento}**")
col6.info(f"Modalidad más reportada: **{top_modalidad}**")

st.divider()

# =========================
# Mapa interactivo
# =========================

st.subheader("Mapa interactivo de denuncias por departamento")

df_mapa = cargar_dataframe(f"""
    SELECT
        departamento,
        latitud,
        longitud,
        SUM(cantidad) AS total_denuncias
    FROM (
        SELECT
            f.departamento,
            g.latitud,
            g.longitud,
            f.cantidad,
            f.anio,
            f.modalidad
        FROM analytics.fact_denuncias f
        INNER JOIN analytics.dim_departamento_geo g
            ON f.departamento = g.departamento
    ) base
    WHERE {where_sql}
    GROUP BY departamento, latitud, longitud
    ORDER BY total_denuncias DESC;
""", params)

if df_mapa.empty:
    st.warning("No hay datos para mostrar en el mapa con los filtros seleccionados.")
else:
    max_denuncias = df_mapa["total_denuncias"].max()

    df_mapa["radio"] = (
        df_mapa["total_denuncias"] / max_denuncias
    ) * 60000 + 15000

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_mapa,
        get_position="[longitud, latitud]",
        get_radius="radio",
        get_fill_color="[220, 50, 50, 140]",
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=-9.19,
        longitude=-75.0152,
        zoom=4.5,
        pitch=0,
    )

    tooltip = {
        "html": """
            <b>Departamento:</b> {departamento}<br/>
            <b>Total denuncias:</b> {total_denuncias}
        """,
        "style": {
            "backgroundColor": "white",
            "color": "black"
        }
    }

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
    )

    st.pydeck_chart(deck, use_container_width=True)

# =========================
# Tendencia anual
# =========================

df_anual = cargar_dataframe(f"""
    SELECT
        anio,
        SUM(cantidad) AS total_denuncias
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    GROUP BY anio
    ORDER BY anio;
""", params)

fig_anual = px.line(
    df_anual,
    x="anio",
    y="total_denuncias",
    markers=True,
    title="Tendencia anual de denuncias policiales"
)

fig_anual.update_layout(
    xaxis_title="Año",
    yaxis_title="Total de denuncias"
)

st.plotly_chart(fig_anual, use_container_width=True)

# =========================
# Rankings
# =========================

col7, col8 = st.columns(2)

df_top_departamentos = cargar_dataframe(f"""
    SELECT TOP 10
        departamento,
        SUM(cantidad) AS total_denuncias
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    GROUP BY departamento
    ORDER BY total_denuncias DESC;
""", params)

fig_departamentos = px.bar(
    df_top_departamentos.sort_values("total_denuncias"),
    x="total_denuncias",
    y="departamento",
    orientation="h",
    title="Top 10 departamentos con más denuncias"
)

fig_departamentos.update_layout(
    xaxis_title="Total de denuncias",
    yaxis_title="Departamento"
)

col7.plotly_chart(fig_departamentos, use_container_width=True)

df_top_modalidades = cargar_dataframe(f"""
    SELECT TOP 10
        modalidad,
        SUM(cantidad) AS total_denuncias
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    GROUP BY modalidad
    ORDER BY total_denuncias DESC;
""", params)

fig_modalidades = px.bar(
    df_top_modalidades.sort_values("total_denuncias"),
    x="total_denuncias",
    y="modalidad",
    orientation="h",
    title="Top 10 modalidades más reportadas"
)

fig_modalidades.update_layout(
    xaxis_title="Total de denuncias",
    yaxis_title="Modalidad"
)

col8.plotly_chart(fig_modalidades, use_container_width=True)

st.divider()

# =========================
# Tendencia mensual
# =========================

df_mensual = cargar_dataframe(f"""
    SELECT
        fecha_periodo,
        SUM(cantidad) AS total_denuncias
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    GROUP BY fecha_periodo
    ORDER BY fecha_periodo;
""", params)

fig_mensual = px.line(
    df_mensual,
    x="fecha_periodo",
    y="total_denuncias",
    title="Tendencia mensual de denuncias"
)

fig_mensual.update_layout(
    xaxis_title="Periodo",
    yaxis_title="Total de denuncias"
)

st.plotly_chart(fig_mensual, use_container_width=True)

# =========================
# Tabla
# =========================

st.subheader("Tabla resumen por departamento, provincia y modalidad")

df_tabla = cargar_dataframe(f"""
    SELECT TOP 500
        departamento,
        provincia,
        modalidad,
        SUM(cantidad) AS total_denuncias
    FROM analytics.fact_denuncias
    WHERE {where_sql}
    GROUP BY departamento, provincia, modalidad
    ORDER BY total_denuncias DESC;
""", params)

st.dataframe(df_tabla, use_container_width=True)

st.caption(
    "Nota: el dashboard analiza denuncias policiales registradas, "
    "no necesariamente la totalidad de delitos ocurridos."
)