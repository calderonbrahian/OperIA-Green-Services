"""Dashboard Ejecutivo Interactivo OperIA (Hackatón EstudIA - Capa 2).

Solución analítica y visual para Green Services and Solutions SAS:
- Semáforo Inteligente de Clientes (Frecuentes, Seguimiento, Fríos)
- Predicción de Recompra a 30 días
- Análisis y Correlación de Ventas vs. Variación de la TRM
- Desglose por Familia de Producto y Sector Económico
- Ficha 360 del Cliente y Descarga de Listado para el Equipo Comercial
"""

import sys
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd

# Manejo de Plotly si está disponible
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# Configuración de página
st.set_page_config(
    page_title="OperIA | Green Services SAS",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 5px solid #2563EB;
    }
    .badge-frecuente {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
    }
    .badge-seguimiento {
        background-color: #FEF08A;
        color: #713F12;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
    }
    .badge-frio {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Rutas predeterminadas
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_CONSOLIDADA_CSV = PROJECT_ROOT / "outputs" / "OperIA_Dataset_Consolidado.csv"
DATA_CONSOLIDADA_XLSX = PROJECT_ROOT / "outputs" / "OperIA_Dataset_Consolidado.xlsx"

# Barra lateral
st.sidebar.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=70)
st.sidebar.title("OperIA 360°")
st.sidebar.markdown("**Reto 4: IA en Operaciones**  \n*Green Services and Solutions SAS*  \n*Alcaldía de Medellín · EstudIA*")
st.sidebar.markdown("---")

fuente_datos = st.sidebar.radio(
    "Fuente de Datos:",
    ["Dataset Consolidado Oficial (Outputs)", "Cargar archivo (CSV / Excel)"]
)

df_cargado = None
if fuente_datos == "Cargar archivo (CSV / Excel)":
    uploaded_file = st.sidebar.file_uploader("Subir dataset consolidado", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".xlsx"):
                df_cargado = pd.read_excel(uploaded_file)
            else:
                df_cargado = pd.read_csv(uploaded_file)
        except Exception as e:
            st.sidebar.error(f"Error al leer archivo: {e}")
else:
    if DATA_CONSOLIDADA_CSV.exists():
        df_cargado = pd.read_csv(DATA_CONSOLIDADA_CSV)
    elif DATA_CONSOLIDADA_XLSX.exists():
        df_cargado = pd.read_excel(DATA_CONSOLIDADA_XLSX)

if df_cargado is None:
    st.warning("⚠️ No se encontró el dataset consolidado en `outputs/`. Ejecuta primero `python main.py` para generarlo o sube un archivo desde la barra lateral.")
    st.stop()

# Convertir tipos
df = df_cargado.copy()
df["Fecha"] = pd.to_datetime(df["Fecha"])
if "Ventas_COP" not in df.columns and "ingreso_cop" in df.columns:
    df["Ventas_COP"] = df["ingreso_cop"]
if "TRM" not in df.columns:
    df["TRM"] = 4100.0

# Encabezado Principal
st.markdown('<p class="main-header">OperIA: Centro de Mando Operacional y Comercial</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Predicción de recompras, semáforo inteligente de clientes y monitoreo de impacto cambiario (TRM).</p>', unsafe_allow_html=True)

# Métricas Ejecutivas Consolidadas
clientes_unicos = df.groupby("Cliente_ID").agg(
    Cliente=("Cliente", "first"),
    Sector=("Sector", "first"),
    Ciudad=("Ciudad", "first"),
    Estado=("Estado_Cliente", "first"),
    Dias_Sin_Comprar=("Dias_Sin_Comprar", "first"),
    Prob_Recompra=("Prob_Recompra_Pct", "first"),
    Prioridad=("Prioridad_Llamada", "first"),
    Accion=("Accion_Recomendada", "first"),
    Total_Ventas_COP=("Ventas_COP", "sum"),
    Transacciones=("Venta_ID", "count")
).reset_index()

# Clientes clasificados
n_total = len(clientes_unicos)
n_frecuentes = sum(clientes_unicos["Estado"].str.contains("Frecuente", na=False))
n_seguimiento = sum(clientes_unicos["Estado"].str.contains("Seguimiento|Base", na=False))
n_frios = sum(clientes_unicos["Estado"].str.contains("Frío", na=False))
total_facturado = df[df["Estado_Venta"] == "Confirmada"]["Ventas_COP"].sum() if "Estado_Venta" in df.columns else df["Ventas_COP"].sum()
trm_reciente = df.sort_values("Fecha")["TRM"].iloc[-1]

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Clientes", f"{n_total}")
k2.metric("🟢 Frecuentes (Activos)", f"{n_frecuentes}", f"{round(n_frecuentes/n_total*100, 1)}%")
k3.metric("🟡 Base Instalada", f"{n_seguimiento}", f"{round(n_seguimiento/n_total*100, 1)}%")
k4.metric("🔴 Fríos (Llamar)", f"{n_frios}", f"-{round(n_frios/n_total*100, 1)}%", delta_color="inverse")
k5.metric("TRM Actual", f"${trm_reciente:,.0f} COP")

st.markdown("---")

# Pestañas principales
tab_semaforo, tab_trm, tab_productos, tab_ficha = st.tabs([
    "🚨 Semáforo de Clientes (Llamadas Prioritarias)",
    "📈 Comportamiento Ventas vs. TRM",
    "📦 Portafolio y Sectores",
    "👤 Ficha 360 del Cliente"
])

# ----------------- TAB 1: SEMÁFORO INTELIGENTE -----------------
with tab_semaforo:
    st.subheader("Semáforo Inteligente de Gestión Comercial")
    st.caption("Filtra y prioriza las llamadas de hoy según el modelo predictivo de riesgo y recompra.")

    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        filtro_estado = st.selectbox(
            "Filtrar por Estado:",
            ["Todos", "🔴 Fríos (Riesgo de Abandono)", "🟡 Base Instalada (Seguimiento)", "🟢 Frecuentes (Activos)"]
        )
    with f2:
        filtro_sector = st.selectbox(
            "Filtrar por Sector:",
            ["Todos"] + sorted(clientes_unicos["Sector"].dropna().unique().tolist())
        )
    with f3:
        busqueda = st.text_input("Buscar cliente por nombre o ID:", placeholder="Ej: CLI005 o Corporativo")

    df_view = clientes_unicos.copy()
    if filtro_estado != "Todos":
        patron = "Frío" if "Frío" in filtro_estado else "Base|Seguimiento" if "Base" in filtro_estado else "Frecuente"
        df_view = df_view[df_view["Estado"].str.contains(patron, na=False)]
    if filtro_sector != "Todos":
        df_view = df_view[df_view["Sector"] == filtro_sector]
    if busqueda:
        df_view = df_view[df_view["Cliente"].str.contains(busqueda, case=False, na=False) |
                          df_view["Cliente_ID"].str.contains(busqueda, case=False, na=False)]

    st.markdown(f"**Mostrando {len(df_view)} clientes**")

    # Columnas a mostrar
    columnas_tabla = [
        "Cliente_ID", "Cliente", "Sector", "Estado", "Dias_Sin_Comprar",
        "Prob_Recompra", "Prioridad", "Accion", "Total_Ventas_COP"
    ]
    st.dataframe(
        df_view[columnas_tabla].rename(columns={
            "Cliente_ID": "ID",
            "Cliente": "Empresa",
            "Dias_Sin_Comprar": "Días sin Compra",
            "Prob_Recompra": "Prob. Recompra 30d (%)",
            "Prioridad": "Prioridad Llamada",
            "Accion": "Acción Sugerida",
            "Total_Ventas_COP": "Facturación COP"
        }),
        use_container_width=True,
        hide_index=True
    )

    # Descarga directa en CSV o Excel
    csv_bytes = df_view.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Descargar Lista de Contacto Filtrada (CSV)",
        data=csv_bytes,
        file_name="OperIA_Clientes_Prioritarios.csv",
        mime="text/csv"
    )

# ----------------- TAB 2: VENTAS VS TRM -----------------
with tab_trm:
    st.subheader("Análisis de Sensibilidad: Ventas en COP frente a la TRM")
    st.caption("Monitorea cómo la fluctuación de la tasa de cambio incide en el volumen facturado mensual.")

    # Agrupar ventas mensuales
    df_mensual = df.copy()
    df_mensual["Mes"] = df_mensual["Fecha"].dt.to_period("M").dt.to_timestamp()
    mensual = df_mensual.groupby("Mes").agg(
        Ventas_COP=("Ventas_COP", "sum"),
        TRM_Promedio=("TRM", "mean")
    ).reset_index()

    if HAS_PLOTLY:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=mensual["Mes"],
            y=mensual["Ventas_COP"],
            name="Ventas en COP",
            marker_color="#2563EB",
            opacity=0.7,
            yaxis="y1"
        ))
        fig.add_trace(go.Scatter(
            x=mensual["Mes"],
            y=mensual["TRM_Promedio"],
            name="TRM Promedio (COP/USD)",
            mode="lines+markers",
            line=dict(color="#DC2626", width=3),
            yaxis="y2"
        ))
        fig.update_layout(
            title="Evolución Mensual de Facturación vs. Tasa de Cambio (TRM)",
            xaxis=dict(title="Mes"),
            yaxis=dict(title="Ventas Facturadas (COP)", side="left", showgrid=True),
            yaxis2=dict(title="TRM (Pesos por Dólar)", side="right", overlaying="y", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(mensual.set_index("Mes")[["Ventas_COP"]])

# ----------------- TAB 3: PRODUCTOS Y SECTORES -----------------
with tab_productos:
    st.subheader("Distribución de la Demanda por Portafolio y Sector")
    p1, p2 = st.columns(2)

    with p1:
        st.markdown("**Ventas por Familia de Producto**")
        df_fam = df.groupby("Familia_Producto")["Ventas_COP"].sum().reset_index().sort_values("Ventas_COP", ascending=False)
        if HAS_PLOTLY:
            fig_fam = px.pie(df_fam, names="Familia_Producto", values="Ventas_COP", hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig_fam, use_container_width=True)
        else:
            st.dataframe(df_fam, use_container_width=True)

    with p2:
        st.markdown("**Ventas por Sector Económico**")
        df_sec = df.groupby("Sector")["Ventas_COP"].sum().reset_index().sort_values("Ventas_COP", ascending=False)
        if HAS_PLOTLY:
            fig_sec = px.bar(df_sec, x="Ventas_COP", y="Sector", orientation="h",
                             color="Ventas_COP", color_continuous_scale="Blues")
            fig_sec.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_sec, use_container_width=True)
        else:
            st.dataframe(df_sec, use_container_width=True)

# ----------------- TAB 4: FICHA 360 DEL CLIENTE -----------------
with tab_ficha:
    st.subheader("Visión 360° Detallada por Cliente")
    cliente_seleccionado = st.selectbox(
        "Seleccione un Cliente para inspección individual:",
        options=clientes_unicos["Cliente_ID"].tolist(),
        format_func=lambda x: f"{x} - {clientes_unicos.loc[clientes_unicos['Cliente_ID'] == x, 'Cliente'].values[0]}"
    )

    info_c = clientes_unicos[clientes_unicos["Cliente_ID"] == cliente_seleccionado].iloc[0]
    sub_ventas = df[df["Cliente_ID"] == cliente_seleccionado].sort_values("Fecha", ascending=False)

    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.markdown(f"**Empresa:** {info_c['Cliente']}  \n**Sector:** {info_c['Sector']}  \n**Ciudad:** {info_c['Ciudad']}")
    col_c2.markdown(f"**Estado:** {info_c['Estado']}  \n**Días sin Compra:** {info_c['Dias_Sin_Comprar']} días  \n**Prob. Recompra:** {info_c['Prob_Recompra']}%")
    col_c3.markdown(f"**Prioridad:** {info_c['Prioridad']}  \n**Acción:** *{info_c['Accion']}*  \n**Total Facturado:** ${info_c['Total_Ventas_COP']:,.2f} COP")

    st.markdown("##### Historial de Operaciones Confirmadas del Cliente")
    st.dataframe(
        sub_ventas[["Fecha", "Producto", "Familia_Producto", "Cantidad", "Moneda", "Precio_Unitario", "TRM", "Ventas_COP"]],
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
st.caption("Solución desarrollada para el Reto 4 (IA en Operaciones) · EstudIA · Green Services and Solutions SAS")
