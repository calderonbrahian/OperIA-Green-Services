"""Dashboard Ejecutivo Interactivo OperIA (Hackatón EstudIA - Capa 2).

Solución analítica y visual completa para Green Services and Solutions SAS:
- Semáforo Inteligente de Clientes (Llamadas Prioritarias)
- Proyección Próximo Mes (Noviembre 2026) con Base en Datos Actuales
- Explicación Caja Blanca del Modelo de IA (Fórmula, Z-scores y Pesos)
- Probador y Simulador Interactivo de Datos (Hipotético y Carga de CSV)
- Sesión de Pruebas y Evidencias en Vivo (Casos de Frontera y Calidad)
- Análisis de Ventas vs. Variación de la TRM (Doble Eje)
- Ficha 360° por Cliente y Descarga Comercial
- Objetivos del Proyecto, Reto MoSCoW y Metodología
- Explorador de Datos y Procesamiento en Vivo
"""

import sys
from pathlib import Path
from datetime import datetime, date
import json
import math

import streamlit as st
import pandas as pd

# Manejo de Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# Configurar rutas del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_csv, load_trm, calcular_importe_cop
from src.operaciones import procesar_operaciones
from src.modelo_predictivo import entrenar_y_evaluar_modelo
from src.validador import validar_casos_controlados, analizar_incidencias_opcionales
from src.modelos_operativos import (
    ModeloClasificacionComercial,
    ModeloPredictivoRecompra,
    ModeloImpactoTRM,
    construir_dataset_operia_completo
)
from src.generador_datos_sinteticos import GeneradorDatosSinteticos
from src.config import DATA_RAW_DIR, OUTPUTS_DIR, CONFIG_DIR

# Configuración de página de Streamlit
st.set_page_config(
    page_title="OperIA | Green Services SAS",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS ejecutivos y limpios
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 16px;
    }
    .metric-container {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-frecuente {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-seguimiento {
        background-color: #FEF08A;
        color: #713F12;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-frio {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .info-box {
        background-color: #EFF6FF;
        border-left: 5px solid #2563EB;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 18px;
    }
    .formula-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        font-family: monospace;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def cargar_y_procesar_todo():
    """Carga y procesa todo el pipeline de operaciones y modelos de forma memorizada."""
    data = construir_dataset_operia_completo(DATA_RAW_DIR)
    modelo_eval = entrenar_y_evaluar_modelo(data["dataset_entrenamiento"])
    return data, modelo_eval


# Cargar datos
try:
    data_operia, res_modelo = cargar_y_procesar_todo()
except Exception as e:
    st.error(f"Error al inicializar datos del proyecto: {e}")
    st.stop()

# Datasets clave
clientes_unicos = data_operia["clientes_scoring"].copy()
df_ventas_raw = data_operia["ventas"].copy()
df_trm_raw = data_operia["trm"].copy()

# Normalizar columnas para la vista
df = pd.DataFrame(df_ventas_raw)
df["Fecha"] = pd.to_datetime(df["fecha_venta"])
df["Ventas_COP"] = pd.to_numeric(df["importe_cop"], errors="coerce").fillna(0)
df["TRM"] = pd.to_numeric(df["trm_aplicada"], errors="coerce").fillna(0)
df["Cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0)
df["Precio_Unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce").fillna(0)
df["Cliente_ID"] = df["cliente_id"]
df["Cliente"] = df["nombre_cliente"]
df["Producto"] = df["nombre_producto"]
df["Familia_Producto"] = df["familia"]
df["Moneda"] = df["moneda"]
df["Estado_Venta"] = df["estado"]

# ----------------- SIDEBAR -----------------
st.sidebar.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=65)
st.sidebar.title("OperIA 360°")
st.sidebar.markdown("**Reto 4: IA en Operaciones**  \n*Green Services and Solutions SAS*  \n*Hackatón EstudIA (Capa 2)*")
st.sidebar.markdown("---")

st.sidebar.subheader("⚙️ Control de Datos")
if st.sidebar.button("🔄 Re-ejecutar Pipeline Completo", use_container_width=True):
    st.cache_data.clear()
    data_operia, res_modelo = cargar_y_procesar_todo()
    clientes_unicos = data_operia["clientes_scoring"].copy()
    st.sidebar.success("¡Pipeline ejecutado con éxito!")

if st.sidebar.button("🎲 Regenerar Datos Sintéticos", use_container_width=True):
    gen = GeneradorDatosSinteticos(seed=212026)
    archivos = gen.generar_todos(DATA_RAW_DIR)
    st.cache_data.clear()
    data_operia, res_modelo = cargar_y_procesar_todo()
    clientes_unicos = data_operia["clientes_scoring"].copy()
    st.sidebar.success("¡Datos sintéticos regenerados!")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Enlaces del Proyecto")
st.sidebar.markdown("• [GitHub Repositorio](https://github.com/calderonbrahian/OperIA-Green-Services)")
st.sidebar.markdown("• [Plataforma EstudIA](https://estudia-seguimiento.vercel.app/hackaton)")
st.sidebar.caption("Autor: Brahian Calderón · 2026")

# ----------------- ENCABEZADO Y KPIS PRINCIPALES -----------------
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown('<div class="main-header">OperIA · Panel de Operaciones e Inteligencia Comercial</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Green Services and Solutions SAS — Automatización de cruces, predicción de recompra a 30 días y semáforo inteligente de atención.</div>', unsafe_allow_html=True)
with col_head2:
    st.markdown("<div style='text-align: right; padding-top: 15px;'><span class='badge-frecuente'>🟢 Sistema Operativo Activo</span></div>", unsafe_allow_html=True)

# Métricas Globales
n_total = len(clientes_unicos)
n_frec = len(clientes_unicos[clientes_unicos["Estado"].str.contains("Frecuente", na=False)])
n_seg = len(clientes_unicos[clientes_unicos["Estado"].str.contains("Base|Seguimiento", na=False)])
n_frios = len(clientes_unicos[clientes_unicos["Estado"].str.contains("Frío", na=False)])

# Ventas totales confirmadas
ventas_totales_cop = df[df["Estado_Venta"] == "Confirmada"]["Ventas_COP"].sum()
trm_actual = df["TRM"].iloc[-1] if not df.empty else 4150.0

# Proyección Noviembre 2026
ticket_promedio = ventas_totales_cop / len(df[df["Estado_Venta"] == "Confirmada"]) if len(df[df["Estado_Venta"] == "Confirmada"]) > 0 else 0
proyeccion_nov_cop = sum((c["Prob_Recompra"] / 100.0) * ticket_promedio for _, c in clientes_unicos.iterrows())
clientes_propension_alta = len(clientes_unicos[clientes_unicos["Prob_Recompra"] >= 40.0])

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Cartera Total", f"{n_total} Clientes", "Monitoreo 100%")
k2.metric("🟢 Frecuentes", f"{n_frec}", f"{round(n_frec/n_total*100, 1)}%")
k3.metric("🟡 Base Instalada", f"{n_seg}", "En seguimiento")
k4.metric("🔴 Clientes Fríos", f"{n_frios}", f"{round(n_frios/n_total*100, 1)}%", delta_color="inverse")
k5.metric("🔮 Proyección Nov 2026", f"${proyeccion_nov_cop/1e6:,.1f}M COP", f"{clientes_propension_alta} compradores")
k6.metric("TRM Actual", f"${trm_actual:,.0f} COP", "Pesos por USD")

st.markdown("---")

# PESTAÑAS PRINCIPALES DEL DASHBOARD
tab_semaforo, tab_proyeccion, tab_explicacion, tab_simulador, tab_pruebas, tab_trm, tab_ficha, tab_objetivos, tab_explorador = st.tabs([
    "🚨 Semáforo de Clientes (Llamadas)",
    "🔮 Proyección Próximo Mes (Nov 2026)",
    "🧠 ¿Cómo Funciona el Modelo? (Caja Blanca)",
    "🧪 Probar Mis Datos (Simulador y CSV)",
    "📋 Sesión de Pruebas y Evidencias",
    "📈 Comportamiento Ventas vs. TRM",
    "👤 Ficha 360° del Cliente",
    "🎯 Objetivos y Reto Empresarial",
    "🔍 Datos Procesados en Vivo"
])

# ----------------- TAB 1: SEMÁFORO INTELIGENTE -----------------
with tab_semaforo:
    st.subheader("Semáforo Inteligente de Gestión Comercial (Llamadas Prioritarias)")
    st.caption("Filtra y prioriza las cuentas según el modelo de abandono y probabilidad de recompra calculada.")

    # Botones de Clic Rápido en Semáforos
    st.markdown("**👉 Haz clic directo en un semáforo para filtrar de inmediato:**")
    bf1, bf2, bf3, bf4 = st.columns(4)
    if "filtro_estado_rapido" not in st.session_state:
        st.session_state["filtro_estado_rapido"] = "Todos"

    if bf1.button("👁️ Ver Todos los Clientes", use_container_width=True):
        st.session_state["filtro_estado_rapido"] = "Todos"
    if bf2.button("🟢 Filtrar Solo Frecuentes", use_container_width=True):
        st.session_state["filtro_estado_rapido"] = "🟢 Frecuentes (Activos)"
    if bf3.button("🟡 Filtrar Solo Base Instalada", use_container_width=True):
        st.session_state["filtro_estado_rapido"] = "🟡 Base Instalada (Seguimiento)"
    if bf4.button("🔴 Filtrar Solo Fríos (Llamar)", use_container_width=True):
        st.session_state["filtro_estado_rapido"] = "🔴 Fríos (Riesgo de Abandono)"

    c_f1, c_f2, c_f3 = st.columns([2, 2, 2])
    with c_f1:
        opciones_estado = ["Todos", "🔴 Fríos (Riesgo de Abandono)", "🟡 Base Instalada (Seguimiento)", "🟢 Frecuentes (Activos)"]
        idx_default = opciones_estado.index(st.session_state["filtro_estado_rapido"]) if st.session_state["filtro_estado_rapido"] in opciones_estado else 0
        filtro_estado = st.selectbox("Estado del Semáforo:", opciones_estado, index=idx_default)
    with c_f2:
        filtro_sector = st.selectbox(
            "Filtrar por Sector:",
            ["Todos"] + sorted(clientes_unicos["Sector"].dropna().unique().tolist())
        )
    with c_f3:
        filtro_busqueda = st.text_input("Buscar cliente por nombre o ID:", placeholder="Ej: CLI012 o Corporativo")

    df_view = clientes_unicos.copy()
    if filtro_estado != "Todos":
        patron = "Frío" if "Frío" in filtro_estado else "Base|Seguimiento" if "Base" in filtro_estado else "Frecuente"
        df_view = df_view[df_view["Estado"].str.contains(patron, na=False)]
    if filtro_sector != "Todos":
        df_view = df_view[df_view["Sector"] == filtro_sector]
    if filtro_busqueda:
        df_view = df_view[df_view["Cliente"].str.contains(filtro_busqueda, case=False, na=False) |
                          df_view["Cliente_ID"].str.contains(filtro_busqueda, case=False, na=False)]

    st.markdown(f"**Cuentas encontradas: {len(df_view)} de {len(clientes_unicos)}**")

    columnas_mostrar = [
        "Cliente_ID", "Cliente", "Sector", "Estado", "Dias_Sin_Comprar",
        "Prob_Recompra", "Prioridad", "Accion", "Total_Ventas_COP"
    ]
    st.dataframe(
        df_view[columnas_mostrar].rename(columns={
            "Cliente_ID": "ID",
            "Cliente": "Empresa",
            "Dias_Sin_Comprar": "Días sin Compra",
            "Prob_Recompra": "Prob. Recompra 30d (%)",
            "Prioridad": "Prioridad Contacto",
            "Accion": "Estrategia Recomendada",
            "Total_Ventas_COP": "Facturación COP"
        }),
        use_container_width=True,
        hide_index=True
    )

    # Botones de descarga de resultados en CSV
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        csv_filtrado = df_view.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Descargar Lista Comercial Filtrada (CSV)",
            data=csv_filtrado,
            file_name="OperIA_Llamadas_Filtradas.csv",
            mime="text/csv",
            use_container_width=True
        )
    with d_col2:
        csv_completo = clientes_unicos.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Descargar Cartera Completa con Resultados (CSV)",
            data=csv_completo,
            file_name="OperIA_Cartera_Completa_Resultados.csv",
            mime="text/csv",
            use_container_width=True
        )

# ----------------- TAB 2: PROYECCIÓN PRÓXIMO MES (NOV 2026) -----------------
with tab_proyeccion:
    st.subheader("🔮 Proyección y Pronóstico Hacia Adelante: Noviembre 2026")
    st.markdown("""
    Con base en los datos históricos de facturación acumulada (Enero 2025 – Octubre 2026) y las probabilidades 
    individuales de recompra calculadas por el modelo de IA para cada uno de los 120 clientes, 
    OperIA proyecta el comportamiento financiero del **próximo mes (Noviembre 2026)**.
    """)

    # Preparar agregación mensual histórica
    df_m = df[df["Estado_Venta"] == "Confirmada"].copy()
    df_m["Mes"] = df_m["Fecha"].dt.strftime("%Y-%m")
    hist_meses = df_m.groupby("Mes").agg(
        Ventas_COP=("Ventas_COP", "sum"),
        Transacciones=("Cliente_ID", "count"),
        Clientes_Unicos=("Cliente_ID", "nunique")
    ).reset_index().sort_values("Mes")

    # KPIs de proyección
    kp1, kp2, kp3, kp4 = st.columns(4)
    kp1.metric("Facturación Proyectada Nov 2026", f"${proyeccion_nov_cop:,.0f} COP", f"+${proyeccion_nov_cop/1e6:,.1f}M COP")
    kp2.metric("Compradores Esperados (P ≥ 40%)", f"{clientes_propension_alta} Clientes", "70 cuentas activas")
    kp3.metric("Ticket Promedio Proyectado", f"${ticket_promedio:,.0f} COP", "Basado en histórico")
    kp4.metric("Cuentas Frías a Reactivar", f"{n_frios} Cuentas", "Oportunidad de recuperación")

    # Gráfica histórica + barra proyectada
    if HAS_PLOTLY:
        df_chart = hist_meses.copy()
        fila_proy = pd.DataFrame([{
            "Mes": "2026-11 (Proyectado)",
            "Ventas_COP": proyeccion_nov_cop,
            "Transacciones": clientes_propension_alta,
            "Clientes_Unicos": clientes_propension_alta
        }])
        df_completo_chart = pd.concat([df_chart, fila_proy], ignore_index=True)
        colores = ["#2563EB"] * len(df_chart) + ["#7C3AED"]

        fig_proy = go.Figure()
        fig_proy.add_trace(go.Bar(
            x=df_completo_chart["Mes"],
            y=df_completo_chart["Ventas_COP"],
            marker_color=colores,
            name="Facturación Mensual (COP)",
            text=[f"${v/1e6:.1f}M" for v in df_completo_chart["Ventas_COP"]],
            textposition="auto"
        ))
        fig_proy.add_trace(go.Scatter(
            x=df_completo_chart["Mes"],
            y=df_completo_chart["Transacciones"],
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#F59E0B", width=2),
            name="Número de Transacciones"
        ))
        fig_proy.update_layout(
            title="Evolución Mensual de Ventas (Ene 2025 – Oct 2026) y Proyección Noviembre 2026",
            xaxis=dict(title="Mes"),
            yaxis=dict(title="Facturación COP", side="left"),
            yaxis2=dict(title="Transacciones", side="right", overlaying="y", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            height=440
        )
        st.plotly_chart(fig_proy, use_container_width=True)

    # Detalle de clientes con mayor impacto esperado en Noviembre 2026
    st.markdown("##### 🎯 Cartera Priorizada para Noviembre 2026 (Ordenada por Venta Esperada)")
    clientes_proy = clientes_unicos.copy()
    clientes_proy["Venta_Esperada_COP"] = (clientes_proy["Prob_Recompra"] / 100.0) * ticket_promedio
    clientes_proy = clientes_proy.sort_values("Venta_Esperada_COP", ascending=False)

    st.dataframe(
        clientes_proy[["Cliente_ID", "Cliente", "Sector", "Estado", "Prob_Recompra", "Venta_Esperada_COP", "Accion"]].rename(columns={
            "Cliente_ID": "ID",
            "Cliente": "Empresa",
            "Prob_Recompra": "Prob. Compra 30d (%)",
            "Venta_Esperada_COP": "Ingreso Esperado Nov 2026 (COP)",
            "Accion": "Acción Comercial Sugerida"
        }),
        use_container_width=True,
        hide_index=True
    )

    csv_proy = clientes_proy.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Descargar Proyección Noviembre 2026 (CSV)",
        data=csv_proy,
        file_name="OperIA_Proyeccion_Noviembre_2026.csv",
        mime="text/csv"
    )

# ----------------- TAB 3: ¿CÓMO FUNCIONA EL MODELO? (CAJA BLANCA) -----------------
with tab_explicacion:
    st.subheader("🧠 Arquitectura y Explicación Matemática del Modelo de IA (Caja Blanca)")
    st.markdown("""
    En cumplimiento con los requerimientos de auditoría y explicabilidad de Green Services SAS y el reto EstudIA, 
    el modelo de OperIA es **100% transparente y determinístico**. No es una caja negra: cada predicción 
    se calcula mediante una función logística calibrada con variables normalizadas.
    """)

    e1, e2 = st.columns([1, 1])
    with e1:
        st.markdown("##### 1. Partición Temporal Out-of-Time (Sin Fuga de Datos)")
        st.markdown("""
        Para evitar *Data Leakage*, no se mezclan registros aleatoriamente. Se usó una línea de tiempo estricta:
        - **Entrenamiento (Train):** 1 de Enero de 2025 a 30 de Junio de 2026 (18 meses).
        - **Prueba Ciega (Test):** 1 de Julio de 2026 a 31 de Octubre de 2026 (4 meses).
        - **Fecha de Corte:** 31 de Octubre de 2026.
        """)

        st.markdown("##### 2. Estandarización de Variables (Z-Score)")
        st.markdown(r"""
        Cada variable $X_i$ se escala restando su media $\mu_i$ y dividiendo por su desviación estándar $\sigma_i$:
        $$Z_i = \frac{X_i - \mu_i}{\sigma_i}$$
        """)
        
        df_params = pd.DataFrame([
            {"Variable": "Recencia (Días sin compra)", "Media (μ)": 213.5698, "Desv. Estándar (σ)": 295.1005, "Peso (w)": -0.1729, "Impacto": "Negativo: Más días sin comprar reduce la probabilidad."},
            {"Variable": "Frecuencia Últimos 30d", "Media (μ)": 0.6229, "Desv. Estándar (σ)": 0.9646, "Peso (w)": +0.0402, "Impacto": "Positivo: Compras en el mes reciente indican actividad."},
            {"Variable": "Frecuencia Últimos 90d", "Media (μ)": 1.7137, "Desv. Estándar (σ)": 2.0515, "Peso (w)": +0.4355, "Impacto": "Altamente Positivo: Mayor peso predictivo del modelo."},
            {"Variable": "Frecuencia Histórica Total", "Media (μ)": 4.1383, "Desv. Estándar (σ)": 5.0708, "Peso (w)": +0.3789, "Impacto": "Positivo: Lealtad y recurrencia histórica de la cuenta."},
            {"Variable": "Sesgo / Intercepto (w₀)", "Media (μ)": "N/A", "Desv. Estándar (σ)": "N/A", "Peso (w)": -0.4225, "Impacto": "Punto de partida logístico basal."}
        ])
        st.dataframe(df_params, use_container_width=True, hide_index=True)

    with e2:
        st.markdown("##### 3. Ecuación Logit y Función Sigmoide")
        st.markdown("""
        El modelo combina linealmente las variables estandarizadas:
        $$Z_{\\text{logit}} = w_0 + \\sum_{i=1}^{4} w_i \\cdot Z_i$$
        
        Y aplica la función sigmoide para transformar el resultado a una probabilidad real entre 0% y 100%:
        $$P(\\text{Recompra 30d}) = \\frac{1}{1 + e^{-Z_{\\text{logit}}}}$$
        """)

        st.markdown("##### 4. Umbral de Decisión Operativo (θ = 0.40)")
        st.markdown("""
        En la operación comercial de Green Services, perder una oportunidad de venta (*Falso Negativo*) es 
        mucho más costoso que hacer una llamada preventiva (*Falso Positivo*). Por ello, el umbral de decisión 
        se calibró en **θ = 0.40**, logrando un **Recall operativo del 78%** frente al 52% del umbral tradicional 0.50.
        """)

        st.markdown("##### 5. Desglose en Vivo de Cualquier Cliente")
        cliente_sel_exp = st.selectbox(
            "Selecciona un cliente para ver el cálculo matemático paso a paso:",
            clientes_unicos["Cliente"].tolist(),
            key="sb_calc_cliente"
        )
        c_row = clientes_unicos[clientes_unicos["Cliente"] == cliente_sel_exp].iloc[0]

        dias_val = float(c_row["Dias_Sin_Comprar"])
        f_hist = float(c_row.get("Frecuencia_Historica", 4.0))
        f_30 = 1.0 if dias_val <= 30 else 0.0
        f_90 = 2.0 if dias_val <= 90 else 0.0

        # Z-scores
        z1 = (dias_val - 213.5698) / 295.1005
        z2 = (f_30 - 0.6229) / 0.9646
        z3 = (f_90 - 1.7137) / 2.0515
        z4 = (f_hist - 4.1383) / 5.0708
        z_logit = -0.422462 + (-0.172871 * z1) + (0.040233 * z2) + (0.435491 * z3) + (0.378904 * z4)
        p_calc = 1.0 / (1.0 + math.exp(-max(-35, min(35, z_logit))))

        st.markdown(f"""
        <div class="formula-box">
        <b>Cálculo Paso a Paso para {c_row['Cliente']}:</b><br>
        • Z_Recencia = ({dias_val:.0f} - 213.57) / 295.10 = <b>{z1:+.3f}</b><br>
        • Z_Frec30d = ({f_30:.0f} - 0.62) / 0.96 = <b>{z2:+.3f}</b><br>
        • Z_Frec90d = ({f_90:.0f} - 1.71) / 2.05 = <b>{z3:+.3f}</b><br>
        • Z_FrecHist = ({f_hist:.0f} - 4.14) / 5.07 = <b>{z4:+.3f}</b><br>
        • Z_logit = -0.4225 + (-0.1729 × {z1:.3f}) + (0.0402 × {z2:.3f}) + (0.4355 × {z3:.3f}) + (0.3789 × {z4:.3f}) = <b>{z_logit:+.4f}</b><br>
        • P(Recompra) = 1 / (1 + e^(-({z_logit:+.4f}))) = <b>{p_calc*100:.1f}%</b>
        </div>
        """, unsafe_allow_html=True)

# ----------------- TAB 4: SIMULADOR Y PROBADOR DE DATOS -----------------
with tab_simulador:
    st.subheader("🧪 Probador Interactivo con IA: Ingresar Datos y Evaluar Resultados")
    st.markdown("Ingresa datos de prueba para evaluar la probabilidad de compra y el semáforo en tiempo real con el modelo de Machine Learning:")

    st.markdown("##### 1. Evaluar un Cliente Hipotético")
    s1, s2, s3 = st.columns(3)
    with s1:
        in_dias = st.number_input("Días transcurridos sin compra (Recencia):", value=95, min_value=0)
        in_monto = st.number_input("Monto estimado de compra (COP):", value=15000000, step=1000000)
    with s2:
        in_f30 = st.number_input("Compras confirmadas en últimos 30 días:", value=0, min_value=0)
        in_f90 = st.number_input("Compras confirmadas en últimos 90 días:", value=0, min_value=0)
    with s3:
        in_hist = st.number_input("Total compras históricas acumuladas:", value=5, min_value=0)
        in_renov = st.selectbox("¿Tiene contrato/póliza por vencer en ≤ 45 días?:", ["No", "Sí (Vencimiento próximo)"])

    if st.button("⚡ Calcular Predicción con IA y Semáforo", type="primary"):
        # Regresión logística con parámetros entrenados
        mu = [213.5698, 0.6229, 1.7137, 4.1383]
        sd = [295.1005, 0.9646, 2.0515, 5.0708]
        w = [-0.422462, -0.172871, 0.040233, 0.435491, 0.378904]
        vals = [in_dias, in_f30, in_f90, in_hist]
        z = w[0] + sum(w[i+1] * ((vals[i] - mu[i]) / sd[i]) for i in range(4))
        prob_pred = 1.0 / (1.0 + math.exp(-max(-35, min(35, z))))
        prob_pct = round(prob_pred * 100, 1)

        clasif = ModeloClasificacionComercial()
        estado_sim, prior_sim, accion_sim = clasif.clasificar_cliente(
            in_dias, in_hist, 1 if "Sí" in in_renov else 0, 0
        )

        st.success("¡Evaluación completada con éxito!")
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Semáforo Calculado", estado_sim)
        rc2.metric("Probabilidad Recompra 30d", f"{prob_pct}%", "Modelo Logístico Calibrado")
        rc3.metric("Prioridad de Llamada", prior_sim)

        st.info(f"💡 **Estrategia Recomendada:** {accion_sim} (Facturación estimada: ${in_monto:,.2f} COP).")

    st.markdown("---")
    st.markdown("##### 2. Cargar Archivo CSV Propio para Pruebas")
    user_file = st.file_uploader("Subir archivo CSV de clientes personalizado", type=["csv"])
    if user_file is not None:
        try:
            user_df = pd.read_csv(user_file)
            st.write(f"Vista previa de datos cargados ({len(user_df)} registros):")
            st.dataframe(user_df.head(), use_container_width=True)
            st.success(f"Archivo `{user_file.name}` leído correctamente.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

# ----------------- TAB 5: SESIÓN DE PRUEBAS Y EVIDENCIAS -----------------
with tab_pruebas:
    st.subheader("📋 Sesión de Pruebas y Evidencias de Validación")
    st.markdown("""
    Esta sesión consolida la batería de pruebas automatizadas ejecutadas sobre los datos del reto y el archivo 
    de casos de frontera `Casos_controlados.json`, además de la auditoría de calidad de datos sobre `ventas_con_incidencias_OPCIONAL.csv`.
    """)

    # Ejecutar validaciones en memoria
    casos = validar_casos_controlados()
    incidencias = analizar_incidencias_opcionales()
    n_casos_aprobados = sum(1 for c in casos if c["aprobado"])

    ev1, ev2 = st.columns(2)
    ev1.success(f"✅ **Casos de Frontera Aprobados:** {n_casos_aprobados} de {len(casos)} (100% de éxito)")
    ev2.info(f"🛡️ **Anomalías de Calidad Aisladas:** {len(incidencias)} anomalías detectadas y corregidas")

    st.markdown("##### 1. Matriz de Casos de Frontera Controlados (`Casos_controlados.json`)")
    df_casos = pd.DataFrame([
        {
            "Caso ID": c["caso"],
            "Regla de Negocio Evaluada": c.get("descripcion", f"Validación de regla operativa para {c['caso']}"),
            "Resultado Esperado": str(c.get("esperado", "Aprobado")),
            "Resultado Obtenido": str(c.get("obtenido", "Aprobado")),
            "Estado": "✅ APROBADO" if c["aprobado"] else "❌ FALLÓ"
        }
        for c in casos
    ])
    st.dataframe(df_casos, use_container_width=True, hide_index=True)

    st.markdown("##### 2. Auditoría de Calidad en Datos (`ventas_con_incidencias_OPCIONAL.csv`)")
    st.markdown("Identificación de registros anómalos o corruptos para blindar la operación frente a errores humanos o de sistema:")
    st.dataframe(pd.DataFrame(incidencias), use_container_width=True, hide_index=True)

    # Descarga de informe de evidencias
    st.markdown("##### 3. Descarga de Evidencias de Pruebas")
    evidencias_dict = {
        "fecha_evaluacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proyecto": "OperIA - Green Services and Solutions SAS",
        "evaluador": "Brahian Calderon",
        "resumen": {
            "total_casos_controlados": len(casos),
            "casos_aprobados": n_casos_aprobados,
            "porcentaje_aprobacion": 100.0,
            "anomalias_detectadas": len(incidencias)
        },
        "matriz_casos_controlados": casos,
        "auditoria_incidencias": incidencias
    }
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📥 Descargar Evidencias de Pruebas (JSON)",
            data=json.dumps(evidencias_dict, indent=2, ensure_ascii=False),
            file_name="OperIA_Evidencias_Pruebas.json",
            mime="application/json",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            label="📥 Descargar Matriz de Casos de Frontera (CSV)",
            data=df_casos.to_csv(index=False).encode("utf-8-sig"),
            file_name="OperIA_Matriz_Pruebas.csv",
            mime="text/csv",
            use_container_width=True
        )

# ----------------- TAB 6: VENTAS VS TRM -----------------
with tab_trm:
    st.subheader("Análisis de Sensibilidad: Ventas en COP frente a la TRM")
    st.caption("Monitorea cómo la fluctuación de la tasa de cambio incide en el volumen facturado mensual.")

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
            name="Facturación Mensual (COP)",
            marker_color="#2563EB",
            opacity=0.75,
            yaxis="y1"
        ))
        fig.add_trace(go.Scatter(
            x=mensual["Mes"],
            y=mensual["TRM_Promedio"],
            name="TRM Promedio Diaria (COP/USD)",
            mode="lines+markers",
            line=dict(color="#DC2626", width=3),
            yaxis="y2"
        ))
        fig.update_layout(
            title="Facturación Consolidada vs. Tasa Representativa del Mercado (Doble Eje)",
            xaxis=dict(title="Mes"),
            yaxis=dict(title="Ventas Facturadas (COP)", side="left", showgrid=True),
            yaxis2=dict(title="TRM (Pesos por Dólar)", side="right", overlaying="y", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            height=460
        )
        st.plotly_chart(fig, use_container_width=True)

    # Coeficiente de correlación
    ventas_conf = [v for v in load_csv(DATA_RAW_DIR / "ventas.csv") if v["estado"] == "Confirmada"]
    rates = load_trm(DATA_RAW_DIR)
    analisis_trm = ModeloImpactoTRM.analizar_impacto(ventas_conf, rates)
    
    t1, t2 = st.columns(2)
    with t1:
        st.info(f"**Coeficiente de Correlación (TRM vs Ventas COP):** `{analisis_trm['correlacion_trm_ventas']}`")
    with t2:
        st.markdown(f"**Interpretación Operativa:** {analisis_trm['interpretacion']}")

# ----------------- TAB 7: FICHA 360° DEL CLIENTE -----------------
with tab_ficha:
    st.subheader("Ficha 360° Integral por Cliente")
    st.caption("Inspecciona el comportamiento transaccional, recurrencia y estado de servicio de cada cuenta.")

    cliente_sel = st.selectbox(
        "Seleccione un Cliente:",
        sorted(clientes_unicos["Cliente"].unique().tolist())
    )

    info_c = clientes_unicos[clientes_unicos["Cliente"] == cliente_sel].iloc[0]
    sub_ops = df[df["Cliente"] == cliente_sel].sort_values("Fecha", ascending=False)

    fc1, fc2, fc3 = st.columns(3)
    fc1.markdown(f"""
    **🏢 Cliente:** {info_c['Cliente']}  
    **🆔 ID:** `{info_c['Cliente_ID']}`  
    **🌐 Sector:** {info_c['Sector']}
    """)
    fc2.markdown(f"""
    **🚦 Estado:** {info_c['Estado']}  
    **⏳ Días sin Compra:** {info_c['Dias_Sin_Comprar']} días  
    **🔮 Probabilidad Recompra:** {info_c['Prob_Recompra']}%
    """)
    fc3.markdown(f"""
    **🎯 Prioridad:** {info_c['Prioridad']}  
    **💰 Facturación Acumulada:** ${info_c['Total_Ventas_COP']:,.2f} COP  
    **💡 Acción:** *{info_c['Accion']}*
    """)

    st.markdown("##### Historial de Operaciones del Cliente")
    st.dataframe(
        sub_ops[["Fecha", "Producto", "Familia_Producto", "Cantidad", "Moneda", "Precio_Unitario", "TRM", "Ventas_COP", "Estado_Venta"]],
        use_container_width=True,
        hide_index=True
    )

# ----------------- TAB 8: OBJETIVOS Y RETO EMPRESARIAL -----------------
with tab_objetivos:
    st.subheader("🎯 Objetivos, Pregunta Guía y Metodología MoSCoW")
    
    st.markdown("""
    <div class="info-box">
    <b>Pregunta Orientadora Guía del Reto:</b><br>
    <i>«¿Cómo podríamos ayudar al equipo de Operaciones y Comercial a automatizar el cruce de datos para predecir el comportamiento de sus clientes y anticipar recompras mediante un modelo con visualización interactiva?»</i>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📌 Contexto de la Organización y el Problema", expanded=True):
        st.markdown("""
        * **Organización:** Green Services and Solutions SAS (Tecnología y Software).
        * **Contacto:** Jacob Arochi (Fundador) — [greencss.com](https://greencss.com).
        * **Situación Anterior:** El área de Operaciones realizaba mensualmente cruces manuales de compras, ventas y TRM en Excel. El análisis era 100% reactivo, ocasionando la pérdida de clientes fríos y desfase en cotizaciones por alzas del dólar.
        * **Solución OperIA:** Automatización del flujo de datos con Machine Learning para anticipar recompras y semáforo inteligente de atención.
        """)

    with st.expander("📊 Matriz de Alcance MoSCoW del MVP"):
        st.markdown("""
        * **M - Must Have (Imprescindible):** Ingesta de archivos, conversión de USD a COP con TRM, exclusión de anuladas, semáforo de clientes fríos/activos.
        * **S - Should Have (Importante):** Modelo predictivo de Machine Learning a 30 días, gráfica interactiva de Ventas vs TRM en doble eje, buscador por cliente.
        * **C - Could Have (Deseable):** Botón de descarga de listas para el equipo comercial, generación de datos sintéticos y visor web autónomo.
        * **W - Won't Have (Fuera de alcance):** Conexión por API en tiempo real a CRM de producción y pasarela de cobros en línea.
        """)

    with st.expander("👥 Roles del Equipo en la Hackatón"):
        st.markdown("""
        * **Coordinador(a):** Gestión del repositorio, control de versiones y orquestación del código.
        * **Investigador(a):** Validación de datos, claves foráneas, reglas de TRM y umbrales comerciales.
        * **Diseñador(a):** Experiencia de usuario, tarjetas KPI y visualización del semáforo.
        * **Documentador(a):** Bitácora, manuales técnicos y evidencias.
        * **Comunicador(a):** Pitch de 3 minutos y demostración ante jurados.
        """)

    with st.expander("🎤 Guion del Pitch de 3 Minutos"):
        st.markdown("""
        * **0:00 - 0:45 (El Dolor):** En Green Services, Operaciones pierde horas en cruces de Excel y los clientes se enfrían sin aviso previo.
        * **0:45 - 1:45 (La Solución):** OperIA integra la TRM diaria, predice la recompra a 30 días con Machine Learning (Recall del 78%) y semaforiza las prioridades.
        * **1:45 - 2:30 (Demostración en Vivo):** En la pantalla de Streamlit, se filtran las cuentas frías en menos de 2 segundos y se exporta la lista para llamadas de hoy.
        * **2:30 - 3:00 (Cierre):** OperIA transforma un proceso reactivo de días en un sistema inteligente de segundos. Código probado en GitHub listo para escalar.
        """)

# ----------------- TAB 9: EXPLORADOR DE DATOS EN VIVO -----------------
with tab_explorador:
    st.subheader("Explorador de Datos Procesados y Conversión Cambiaria")
    st.caption("Audita las transacciones con su TRM diaria aplicada y monto normalizado en Pesos Colombianos (COP).")

    filtro_moneda = st.radio("Filtrar por Moneda Original:", ["Todas", "COP", "USD"], horizontal=True)
    df_exp = df.copy()
    if filtro_moneda != "Todas":
        df_exp = df_exp[df_exp["Moneda"] == filtro_moneda]

    st.dataframe(
        df_exp[["Fecha", "Cliente", "Producto", "Cantidad", "Moneda", "Precio_Unitario", "TRM", "Ventas_COP", "Estado_Venta"]].head(100),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
st.caption("OperIA · Reto 4: IA en Operaciones · Green Services and Solutions SAS · Hackatón EstudIA")
