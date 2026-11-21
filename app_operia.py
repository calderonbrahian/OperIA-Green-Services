"""Dashboard Ejecutivo Interactivo OperIA (Hackatón EstudIA - Capa 2).

Solución analítica y visual completa para Green Services and Solutions SAS:
- Semáforo Inteligente de Clientes (Llamadas Prioritarias)
- Análisis de Ventas vs. Variación de la TRM
- Explorador de Datos y Procesamiento en Vivo (Ingesta y Transformaciones)
- Objetivos del Proyecto, Reto MoSCoW y Contexto Empresarial
- Validador en Vivo de Casos Controlados y Calidad
- Ficha 360° por Cliente y Descarga Comercial
"""

import sys
from pathlib import Path
from datetime import datetime, date
import json

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
        border-radius: 6px;
        margin-bottom: 16px;
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

# Rutas de datos
CSV_CONSOLIDADO = OUTPUTS_DIR / "OperIA_Dataset_Consolidado.csv"
XLSX_CONSOLIDADO = OUTPUTS_DIR / "OperIA_Dataset_Consolidado.xlsx"

# BARRA LATERAL (Sidebar)
st.sidebar.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=65)
st.sidebar.title("OperIA 360°")
st.sidebar.markdown("**Reto 4: IA en Operaciones**  \n*Green Services and Solutions SAS*  \n*Hackatón EstudIA (Capa 2)*")
st.sidebar.markdown("---")

st.sidebar.subheader("⚙️ Control de Datos")
if st.sidebar.button("🔄 Re-ejecutar Pipeline Completo", use_container_width=True):
    with st.spinner("Procesando datos y ejecutando modelos..."):
        procesar_operaciones()
        entrenar_y_evaluar_modelo()
        construir_dataset_operia_completo()
    st.sidebar.success("¡Pipeline ejecutado con éxito!")
    st.rerun()

if st.sidebar.button("🎲 Regenerar Datos Sintéticos", use_container_width=True):
    with st.spinner("Generando datos reproducibles (seed=212026)..."):
        gen = GeneradorDatosSinteticos(seed=212026)
        gen.guardar_dataset_completo(DATA_RAW_DIR)
        procesar_operaciones()
        entrenar_y_evaluar_modelo()
        construir_dataset_operia_completo()
    st.sidebar.success("¡Datos sintéticos regenerados!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Enlaces del Proyecto")
st.sidebar.markdown("• [GitHub Repositorio](https://github.com/calderonbrahian/OperIA-Green-Services)")
st.sidebar.markdown("• [Plataforma EstudIA](https://estudia-seguimiento.vercel.app/hackaton)")
st.sidebar.caption("Autor: Brahian Calderón · 2026")

# Cargar dataset consolidado
@st.cache_data
def get_consolidated_data():
    if CSV_CONSOLIDADO.exists():
        return pd.read_csv(CSV_CONSOLIDADO)
    elif XLSX_CONSOLIDADO.exists():
        return pd.read_excel(XLSX_CONSOLIDADO)
    else:
        # Generar automáticamente si no existe
        procesar_operaciones()
        entrenar_y_evaluar_modelo()
        construir_dataset_operia_completo()
        return pd.read_csv(CSV_CONSOLIDADO)

df = get_consolidated_data()
df["Fecha"] = pd.to_datetime(df["Fecha"])

# Encabezado Principal
st.markdown('<p class="main-header">OperIA: Plataforma Inteligente de Operaciones y Clientes</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Integración de ventas, compras, TRM y base instalada con Machine Learning para anticipar recompras y retención.</p>', unsafe_allow_html=True)

# Clientes únicos agregados
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

# Tarjetas KPI
n_total = len(clientes_unicos)
n_frec = sum(clientes_unicos["Estado"].str.contains("Frecuente", na=False))
n_seg = sum(clientes_unicos["Estado"].str.contains("Seguimiento|Base", na=False))
n_frios = sum(clientes_unicos["Estado"].str.contains("Frío", na=False))
total_facturado = df[df["Estado_Venta"] == "Confirmada"]["Ventas_COP"].sum()
trm_actual = df.sort_values("Fecha")["TRM"].iloc[-1]

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Cartera de Clientes", f"{n_total}", "100% monitoreados")
k2.metric("🟢 Clientes Frecuentes", f"{n_frec}", f"{round(n_frec/n_total*100, 1)}%")
k3.metric("🟡 Base Instalada", f"{n_seg}", "En seguimiento")
k4.metric("🔴 Clientes Fríos", f"{n_frios}", f"{round(n_frios/n_total*100, 1)}%", delta_color="inverse")
k5.metric("TRM Actual", f"${trm_actual:,.0f} COP", "Pesos por USD")

st.markdown("---")

# PESTAÑAS PRINCIPALES DEL DASHBOARD
tab_semaforo, tab_trm, tab_explorador, tab_ficha, tab_objetivos, tab_pruebas = st.tabs([
    "🚨 Semáforo de Clientes (Llamadas)",
    "📈 Comportamiento Ventas vs. TRM",
    "🔍 Datos Procesados en Vivo",
    "👤 Ficha 360° del Cliente",
    "🎯 Objetivos y Reto Empresarial",
    "🧪 Batería de Pruebas y Validación"
])

# ----------------- TAB 1: SEMÁFORO INTELIGENTE -----------------
with tab_semaforo:
    st.subheader("Semáforo Inteligente de Gestión Comercial (Llamadas Prioritarias)")
    st.caption("Filtra y prioriza las cuentas según el modelo de abandono y probabilidad de recompra calculada.")

    c_f1, c_f2, c_f3 = st.columns([2, 2, 2])
    with c_f1:
        filtro_estado = st.selectbox(
            "Filtrar por Semáforo:",
            ["Todos", "🔴 Fríos (Riesgo de Abandono)", "🟡 Base Instalada (Seguimiento)", "🟢 Frecuentes (Activos)"]
        )
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

    st.markdown(f"**Cuentas encontradas: {len(df_view)}**")

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

    # Botón de descarga
    csv_data = df_view.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Descargar Listado Comercial Filtrado (CSV)",
        data=csv_data,
        file_name="OperIA_Listado_Llamadas_Prioritarias.csv",
        mime="text/csv"
    )

# ----------------- TAB 2: VENTAS VS TRM -----------------
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

# ----------------- TAB 3: EXPLORADOR DE DATOS EN VIVO -----------------
with tab_explorador:
    st.subheader("🔍 Explorador de Datos y Transformaciones en Tiempo Real")
    st.markdown("Visualiza las tablas originales que alimentan el pipeline de OperIA y cómo se transforman:")

    tabla_sel = st.selectbox(
        "Seleccionar Fuente de Información a Inspeccionar:",
        ["Dataset Consolidado Enriquecido (OperIA)", "ventas.csv (1.407 filas)", "clientes.csv (120 filas)",
         "productos.csv (Catálogo)", "trm_prueba.csv (Serie diaria)", "base_instalada.csv (Contratos)", "compras.csv"]
    )

    if "Consolidado" in tabla_sel:
        st.dataframe(df.head(100), use_container_width=True)
        st.caption(f"Mostrando primeros 100 de {len(df)} registros consolidados.")
    else:
        archivo_map = {
            "ventas.csv": DATA_RAW_DIR / "ventas.csv",
            "clientes.csv": DATA_RAW_DIR / "clientes.csv",
            "productos.csv": DATA_RAW_DIR / "productos.csv",
            "trm_prueba.csv": DATA_RAW_DIR / "trm_prueba.csv",
            "base_instalada.csv": DATA_RAW_DIR / "base_instalada.csv",
            "compras.csv": DATA_RAW_DIR / "compras.csv"
        }
        for clave, path_f in archivo_map.items():
            if clave in tabla_sel:
                raw_df = pd.read_csv(path_f)
                st.dataframe(raw_df.head(100), use_container_width=True)
                st.caption(f"Archivo: `{path_f.name}` ({len(raw_df)} registros totales).")

    st.markdown("---")
    st.subheader("⚡ Resumen de Procesamiento de Ingesta")
    st.markdown("""
    * **1. Normalización de TRM:** Las operaciones pactadas en dólares (USD) se multiplican por la tasa exacta de `cop_por_usd` del día de la venta.
    * **2. Depuración de Anuladas:** Las operaciones con estado `Anulada` se identifican y su valor en ventas se fija en $0 COP.
    * **3. Métricas Temporales:** Se calcula la recencia en días contra la fecha de corte (`2026-10-31`) y las frecuencias de compra a 30 y 90 días.
    """)

# ----------------- TAB 4: FICHA 360° DEL CLIENTE -----------------
with tab_ficha:
    st.subheader("Ficha 360° Individual por Cliente")
    cli_sel = st.selectbox(
        "Seleccionar Cliente para Inspección Detallada:",
        options=clientes_unicos["Cliente_ID"].tolist(),
        format_func=lambda x: f"{x} - {clientes_unicos.loc[clientes_unicos['Cliente_ID'] == x, 'Cliente'].values[0]}"
    )

    info_c = clientes_unicos[clientes_unicos["Cliente_ID"] == cli_sel].iloc[0]
    sub_ops = df[df["Cliente_ID"] == cli_sel].sort_values("Fecha", ascending=False)

    fc1, fc2, fc3 = st.columns(3)
    fc1.markdown(f"""
    **🏢 Empresa:** {info_c['Cliente']}  
    **📍 Ciudad:** {info_c['Ciudad']}  
    **🏭 Sector:** {info_c['Sector']}
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

# ----------------- TAB 5: OBJETIVOS Y RETO EMPRESARIAL -----------------
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

# ----------------- TAB 6: VALIDACIÓN Y CASOS CONTROLADOS -----------------
with tab_pruebas:
    st.subheader("🧪 Batería de Validación y Casos Controlados en Vivo")
    st.markdown("Verifica en tiempo real que las reglas de negocio y los casos de frontera de `Casos_controlados.json` se cumplan al 100%:")

    if st.button("▶️ Ejecutar Validación en Vivo"):
        casos = validar_casos_controlados()
        incidencias = analizar_incidencias_opcionales()

        st.markdown("##### Resultados de Casos de Frontera:")
        for c in casos:
            if c["aprobado"]:
                st.success(f"✅ **Caso: {c['caso']}** — APROBADO (Resultado: {c['obtenido']})")
            else:
                st.error(f"❌ **Caso: {c['caso']}** — FALLÓ")

        st.markdown("##### Auditoría de Calidad en Datos de Prueba (`ventas_con_incidencias_OPCIONAL.csv`):")
        st.info(f"Se identificaron y aislaron **{len(incidencias)} anomalías sembradas** exitosamente:")
        st.dataframe(pd.DataFrame(incidencias), use_container_width=True)

st.markdown("---")
st.caption("OperIA · Reto 4: IA en Operaciones · Green Services and Solutions SAS · Hackatón EstudIA")
