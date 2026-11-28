"""Dashboard OperIA (Hackatón EstudIA - Capa 2) para Green Services and Solutions SAS.

Todas las cifras se leen de outputs/ (vista_clientes_360.csv, cifras_dashboard.json,
metricas_modelo.json): no hay números escritos a mano en esta interfaz.
Los datos y la TRM son DATOS DE PRUEBA del paquete del reto, no información real ni oficial.
"""
import io
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DATA_RAW_DIR, OUTPUTS_DIR, load_config
from src.modelos_operativos import (
    ModeloClasificacionComercial, ModeloPredictivoRecompra, construir_dataset_operia_completo,
    ESTADOS_COBERTURA, COB_SIN, ORDEN_PRIORIDAD,
)
from src.modelo_predictivo import entrenar_y_evaluar_modelo
from src.operaciones import procesar_operaciones
from src.validador import validar_casos_controlados, analizar_incidencias_opcionales

st.set_page_config(page_title="OperIA | Green Services SAS", page_icon="🟢", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
 .main-header{font-size:2.1rem;font-weight:800;color:#1E3A8A;margin-bottom:0}
 .sub-header{font-size:1.02rem;color:#4B5563;margin-bottom:12px}
 .aviso{background:#FEF3C7;border-left:5px solid #D97706;padding:10px 16px;border-radius:0 8px 8px 0;margin-bottom:14px;color:#78350F}
 .info-box{background:#EFF6FF;border-left:5px solid #2563EB;padding:14px 18px;border-radius:0 8px 8px 0;margin-bottom:16px}
 .formula-box{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:16px;font-family:monospace;margin:10px 0}
</style>""", unsafe_allow_html=True)

REQUIRED = [OUTPUTS_DIR / "vista_clientes_360.csv", OUTPUTS_DIR / "cifras_dashboard.json",
            OUTPUTS_DIR / "OperIA_Dataset_Consolidado.csv", OUTPUTS_DIR / "metricas_modelo.json"]


def ejecutar_pipeline():
    procesar_operaciones()
    entrenar_y_evaluar_modelo()
    construir_dataset_operia_completo()
    st.cache_data.clear()


@st.cache_data(show_spinner=False)
def cargar():
    vista = pd.read_csv(OUTPUTS_DIR / "vista_clientes_360.csv")
    ventas = pd.read_csv(OUTPUTS_DIR / "OperIA_Dataset_Consolidado.csv")
    ventas["Fecha"] = pd.to_datetime(ventas["Fecha"])
    cifras = json.loads((OUTPUTS_DIR / "cifras_dashboard.json").read_text(encoding="utf-8"))
    return vista, ventas, cifras


if not all(p.exists() for p in REQUIRED):
    with st.spinner("Generando resultados por primera vez..."):
        ejecutar_pipeline()

vista, df, cif = cargar()
met = cif["metricas_modelo"]
cfg = load_config()
modelo = ModeloPredictivoRecompra.desde_metricas()
clasificador = ModeloClasificacionComercial(dias_frio=cfg["frio_dias_sin_compra"], dias_renovacion=cfg["renovacion_dias"])
est = cif["estados"]
FRIO, FREC, SEG, SINC = ("Frío (Riesgo de Abandono)", "Frecuente (Activo)", "Base Instalada (Seguimiento)", "Sin Compras (Prospecto)")

# ---------------- Sidebar ----------------
st.sidebar.title("OperIA 360°")
st.sidebar.markdown("**Reto 4: IA en Operaciones**  \n*Green Services and Solutions SAS*  \n*Hackatón EstudIA (Capa 2)*")
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Re-ejecutar pipeline completo", use_container_width=True):
    with st.spinner("Procesando..."):
        ejecutar_pipeline()
    st.rerun()
st.sidebar.caption("Los datos de `data/raw` son los oficiales del paquete (verificados por SHA-256). "
                   "Los datos sintéticos viven aparte en `data/synthetic`.")
st.sidebar.markdown("---")
st.sidebar.markdown("• [Visor web (GitHub Pages)](https://calderonbrahian.github.io/OperIA-Green-Services/)")
st.sidebar.markdown("• [Repositorio GitHub](https://github.com/calderonbrahian/OperIA-Green-Services)")
st.sidebar.caption("Autor: Brahian Calderón · 2026")

# ---------------- Encabezado ----------------
st.markdown('<div class="main-header">OperIA · Panel de Operaciones e Inteligencia Comercial</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Green Services and Solutions SAS — cruce de datos, predicción de recompra a 30 días y semáforo explicable.</div>', unsafe_allow_html=True)
st.markdown(f'<div class="aviso">⚠️ <b>Datos de prueba.</b> {cif["advertencia"]} '
            f'Corte: <b>{cif["fecha_corte"]}</b>. Integridad de datos oficiales: '
            f'<b>{"verificada ✓" if cif["datos_oficiales_integros"] else "ALTERADOS ✗"}</b>.</div>', unsafe_allow_html=True)

n = cif["clientes_total"]
proy = cif["proyeccion"]
k = st.columns(6)
k[0].metric("Cartera total", f"{n} clientes")
k[1].metric("🟢 Frecuentes (≤30 d)", est[FREC], f"{est[FREC]/n:.0%}")
k[2].metric("🟡 Seguimiento (31–89 d)", est[SEG], f"{est[SEG]/n:.0%}")
k[3].metric("🔴 Fríos (≥90 d)", est[FRIO], f"{est[FRIO]/n:.0%}", delta_color="inverse")
k[4].metric(f"🔮 Proyección {proy['mes_objetivo']}", f"${proy['ingreso_esperado_cop']/1e6:,.1f}M COP", f"{proy['compradores_esperados']} con P ≥ {met['umbral_seleccionado']:.0%}")
k[5].metric("Sin compras", est[SINC])
st.markdown("---")

tabs = st.tabs(["🚨 Semáforo", "🔮 Proyección y backtest", "🧠 Cómo funciona el modelo", "🧪 Probar mis datos",
                "📋 Pruebas y evidencias", "📈 Ventas vs TRM", "👤 Ficha 360°", "🎯 Objetivos", "🔍 Datos"])
t_sem, t_proy, t_mod, t_sim, t_test, t_trm, t_fic, t_obj, t_dat = tabs

# ---------------- 1. Semáforo ----------------
with t_sem:
    st.subheader("Semáforo de gestión comercial")
    with st.expander("🔍 ¿Cómo se hizo el cruce y qué variables decidieron?", expanded=True):
        st.markdown(f"""
**Cruce (clave `cliente_id`)** — se parte de los **{n} clientes** de `clientes.csv` (nadie se pierde) y se une:
`ventas.csv` (solo *Confirmada*; USD × TRM de la misma fecha), `base_instalada.csv` (cobertura) y el modelo de IA.

| Paso | Variable | Regla |
|---|---|---|
| 1 | **Recencia** = corte − última compra confirmada | ≤ {clasificador.dias_frecuente} d 🟢 Frecuente · {clasificador.dias_frecuente+1}–{clasificador.dias_frio-1} d 🟡 Seguimiento · ≥ {clasificador.dias_frio} d 🔴 Frío · sin compras = categoría aparte |
| 2 | **Estado de cobertura** (contratos) | Próxima a renovar (0–{cfg['renovacion_dias']} d) · Vigente · Vencida · Sin cobertura |
| 3 | **Prioridad** | 🔴 Frío = **ALTA** · cobertura Próxima o Vencida = **MEDIA** · resto = **BAJA** (frecuente) / **NORMAL** |
| 4 | **Orden dentro de la prioridad** | mayor **probabilidad de recompra (IA)** primero. *La IA no cambia la prioridad, solo ordena.* |

Además se muestran, **como etiquetas independientes** (definición oficial del reto): *Frecuente ≥ {cfg['frecuente_min_transacciones']} operaciones* y *Frío ≥ {cfg['frio_dias_sin_compra']} d*: un cliente puede ser ambos.
Parámetros editables en `config/parametros.json` (supuestos didácticos, no políticas de Green Services).
""")
    c1, c2, c3, c4 = st.columns(4)
    if "f_est" not in st.session_state:
        st.session_state["f_est"] = "Todos"
    if c1.button(f"👁️ Todos ({n})", use_container_width=True): st.session_state["f_est"] = "Todos"
    if c2.button(f"🟢 Frecuentes ({est[FREC]})", use_container_width=True): st.session_state["f_est"] = FREC
    if c3.button(f"🟡 Seguimiento ({est[SEG]})", use_container_width=True): st.session_state["f_est"] = SEG
    if c4.button(f"🔴 Fríos ({est[FRIO]})", use_container_width=True): st.session_state["f_est"] = FRIO
    f1, f2, f3, f4, f5 = st.columns(5)
    opts = ["Todos", FREC, SEG, FRIO, SINC]
    fe = f1.selectbox("Semáforo", opts, index=opts.index(st.session_state["f_est"]))
    fc = f2.selectbox("Cobertura", ["Todas"] + list(ESTADOS_COBERTURA))
    fp = f3.selectbox("Prioridad", ["Todas"] + list(ORDEN_PRIORIDAD))
    fs = f4.selectbox("Sector", ["Todos"] + sorted(vista["Sector"].dropna().unique()))
    fq = f5.text_input("Buscar", placeholder="CLI012 o nombre")
    v = vista.copy()
    if fe != "Todos": v = v[v["Estado_Cliente"] == fe]
    if fc != "Todas": v = v[v["Estado_Cobertura"] == fc]
    if fp != "Todas": v = v[v["Prioridad_Llamada"] == fp]
    if fs != "Todos": v = v[v["Sector"] == fs]
    if fq: v = v[v["Cliente"].str.contains(fq, case=False) | v["Cliente_ID"].str.contains(fq, case=False)]
    st.markdown(f"**{len(v)} de {n} clientes** · ordenados por prioridad y luego por probabilidad de recompra")
    cols = ["Cliente_ID", "Cliente", "Sector", "Estado_Cliente", "Dias_Sin_Comprar", "Estado_Cobertura", "Prioridad_Llamada",
            "Prob_Recompra_Pct", "Es_Frecuente_8ops", "Es_Frio", "Criterio_Decision", "Accion_Recomendada", "Ventas_COP"]
    st.dataframe(v[cols].rename(columns={"Estado_Cliente": "Semáforo", "Dias_Sin_Comprar": "Días sin compra",
                 "Estado_Cobertura": "Cobertura", "Prioridad_Llamada": "Prioridad", "Prob_Recompra_Pct": "P recompra 30d (%)",
                 "Es_Frecuente_8ops": "Frecuente (≥8 ops)", "Es_Frio": "Frío (≥90 d)", "Criterio_Decision": "Por qué",
                 "Accion_Recomendada": "Acción", "Ventas_COP": "Facturación COP"}), use_container_width=True, hide_index=True)
    d1, d2 = st.columns(2)
    d1.download_button("📥 Lista filtrada (CSV)", v.to_csv(index=False).encode("utf-8-sig"), "OperIA_lista_filtrada.csv", "text/csv", use_container_width=True)
    d2.download_button("📥 Cartera completa (CSV)", vista.to_csv(index=False).encode("utf-8-sig"), "OperIA_cartera_completa.csv", "text/csv", use_container_width=True)

# ---------------- 2. Proyección y backtest ----------------
with t_proy:
    bt = cif["backtest_pronostico"]
    st.subheader(f"🔮 Proyección de {proy['mes_objetivo']} y su validación")
    st.markdown(f"Método: **{proy['metodo']}**. {proy['nota']}")
    a, b, c, d = st.columns(4)
    a.metric("Ingreso esperado", f"${proy['ingreso_esperado_cop']:,.0f}")
    b.metric(f"Clientes con P ≥ {met['umbral_seleccionado']:.0%}", proy["compradores_esperados"])
    c.metric("MAE modelo (backtest)", f"${bt['mae_modelo_cop']/1e6:,.1f}M")
    d.metric("MAE «repetir último mes»", f"${bt['mae_linea_base_cop']/1e6:,.1f}M")
    (st.success if bt["gana_modelo"] else st.warning)(
        bt["conclusion"] + " Con solo 3 cortes de prueba la conclusión es indicativa, no definitiva.")
    st.markdown("##### Backtest: pronóstico con datos ≤ corte vs lo que realmente ocurrió")
    st.dataframe(pd.DataFrame(bt["detalle"]).rename(columns={
        "corte": "Corte", "mes_objetivo": "Mes pronosticado", "pronostico_modelo_cop": "Modelo (COP)",
        "linea_base_ultimo_mes_cop": "Último mes (COP)", "real_cop": "Real (COP)"}), use_container_width=True, hide_index=True)
    mens = df[df["Estado_Venta"] == "Confirmada"].assign(Mes=lambda x: x["Fecha"].dt.strftime("%Y-%m")).groupby("Mes")["Ventas_COP"].sum().reset_index()
    if HAS_PLOTLY:
        fig = go.Figure()
        fig.add_bar(x=mens["Mes"], y=mens["Ventas_COP"], name="Ventas confirmadas (COP)", marker_color="#2563EB")
        fig.add_bar(x=[proy["mes_objetivo"] + " (proy.)"], y=[proy["ingreso_esperado_cop"]], name="Proyección", marker_color="#7C3AED")
        fig.update_layout(height=380, title="Ventas mensuales y proyección", legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
    top = vista.sort_values("Venta_Esperada_Prox_Mes_COP", ascending=False)
    st.markdown("##### Clientes ordenados por venta esperada")
    st.dataframe(top[["Cliente_ID", "Cliente", "Estado_Cliente", "Prob_Recompra_Pct", "Ticket_Promedio_COP", "Venta_Esperada_Prox_Mes_COP"]],
                 use_container_width=True, hide_index=True)
    st.download_button("📥 Proyección por cliente (CSV)", top.to_csv(index=False).encode("utf-8-sig"), "OperIA_proyeccion.csv", "text/csv")

# ---------------- 3. Cómo funciona el modelo ----------------
with t_mod:
    st.subheader("🧠 El modelo, paso a paso (caja blanca)")
    vm, tm, bm = met["metricas_validacion"], met["metricas_prueba_modelo"], met["metricas_prueba_linea_base_compra_reciente"]
    st.markdown(f"""
**Qué predice:** probabilidad de que el cliente tenga al menos una compra confirmada en los siguientes **{met['ventana_objetivo_dias']} días**.
**Partición temporal (sin fuga del futuro):** entrenamiento {met['entrenamiento_rango']} · validación {met['validacion_rango']} (aquí se eligió el umbral {met['umbral_seleccionado']}) · prueba {met['prueba_rango']}.
""")
    names = ["Recencia (días)", "Compras 30 d", "Compras 90 d", "Historial total"]
    st.dataframe(pd.DataFrame({"Variable": names, "Media (μ)": met["medias_escalado"], "Desv. (σ)": met["desviaciones_escalado"],
                               "Peso (w)": met["pesos_modelo"][1:]}).round(4), hide_index=True, use_container_width=True)
    st.caption(f"Intercepto w₀ = {met['pesos_modelo'][0]:.4f}. Fórmula: z = w₀ + Σ wᵢ·(xᵢ−μᵢ)/σᵢ ;  P = 1/(1+e^(−z)) ; se marca «comprará» si P ≥ {met['umbral_seleccionado']}.")
    st.markdown("##### Resultados en la prueba temporal (matriz de confusión)")
    def cm(m): return pd.DataFrame([[m["TP"], m["FN"]], [m["FP"], m["TN"]]], index=["Real: compra", "Real: no compra"], columns=["Predice: compra", "Predice: no compra"])
    x1, x2 = st.columns(2)
    x1.markdown(f"**Modelo (θ={met['umbral_seleccionado']})** — precisión {tm['precision']:.1%} · recall {tm['recall']:.1%} · F1 {tm['F1']:.3f} · exactitud {tm['accuracy']:.1%}")
    x1.table(cm(tm))
    x2.markdown(f"**Línea base «compró en últimos 30 d»** — precisión {bm['precision']:.1%} · recall {bm['recall']:.1%} · F1 {bm['F1']:.3f} · exactitud {bm['accuracy']:.1%}")
    x2.table(cm(bm))
    st.info(f"**Lectura honesta:** el modelo detecta más recompras (recall {tm['recall']:.0%} vs {bm['recall']:.0%}) y tiene mejor F1, "
            f"pero **pierde en precisión y exactitud**: genera {tm['FP']} falsos positivos frente a {bm['FP']} de la línea base. "
            "Sirve para no dejar pasar clientes con probabilidad, a costa de más llamadas innecesarias. Resultados sobre datos de prueba: "
            "no demuestran desempeño en operaciones reales.")
    st.markdown("##### Desglose para un cliente")
    sel = st.selectbox("Cliente", vista["Cliente_ID"] + " · " + vista["Cliente"], key="mod_sel")
    r = vista[vista["Cliente_ID"] == sel.split(" · ")[0]].iloc[0]
    rec = int(r["Dias_Sin_Comprar"]) if pd.notna(r["Dias_Sin_Comprar"]) else 730
    vals = [rec, int(r["Compras_30d"]), int(r["Compras_90d"]), int(r["Transacciones"])]
    zs = [(x - m) / s for x, m, s in zip(vals, met["medias_escalado"], met["desviaciones_escalado"])]
    contrib = [w * z for w, z in zip(met["pesos_modelo"][1:], zs)]
    zt = met["pesos_modelo"][0] + sum(contrib)
    p = 1 / (1 + math.exp(-zt))
    st.dataframe(pd.DataFrame({"Variable": names, "Valor": vals, "z": zs, "w·z": contrib}).round(3), hide_index=True, use_container_width=True)
    st.markdown(f"z total = {met['pesos_modelo'][0]:+.3f} {''.join(f'{c:+.3f} ' for c in contrib)}= **{zt:+.3f}** → P = **{p:.1%}** "
                f"(tabla: {r['Prob_Recompra_Pct']}%) · semáforo **{r['Estado_Cliente']}** · prioridad **{r['Prioridad_Llamada']}**")

# ---------------- 4. Probar mis datos ----------------
with t_sim:
    st.subheader("🧪 Probar mis datos")
    st.markdown("##### 1. Cliente hipotético")
    s1, s2, s3 = st.columns(3)
    in_d = s1.number_input("Días sin compra", 0, 3650, 15)
    in_f30 = s2.number_input("Compras últimos 30 d", 0, 100, 1)
    in_f90 = s2.number_input("Compras últimos 90 d", 0, 100, 2)
    in_h = s3.number_input("Compras históricas", 0, 1000, 8)
    in_cob = s3.selectbox("Cobertura", list(ESTADOS_COBERTURA), index=1)
    if st.button("⚡ Evaluar", type="primary"):
        pr = modelo.predecir_probabilidad(in_d, in_f30, in_f90, in_h)
        e, pri, acc, crit = clasificador.clasificar_cliente(in_d, in_h, in_cob)
        m1, m2, m3 = st.columns(3)
        m1.metric("Semáforo", e); m2.metric("P recompra 30 d", f"{pr:.1%}"); m3.metric("Prioridad", pri)
        st.info(f"**Acción:** {acc}"); st.caption(crit)
    st.markdown("---")
    st.markdown("##### 2. Subir un CSV y descargar los resultados")
    plantilla = "cliente_id,dias_sin_compra,compras_30d,compras_90d,historial,estado_cobertura\nPRUEBA01,15,1,2,8,Vigente (> 45d)\nPRUEBA02,120,0,0,3,Vencida (< 0d)\n"
    st.download_button("📄 Descargar plantilla CSV", plantilla, "plantilla_operia.csv", "text/csv")
    up = st.file_uploader("CSV con columnas: cliente_id, dias_sin_compra, compras_30d, compras_90d, historial, estado_cobertura (opcional)", type=["csv"])
    if up is not None:
        try:
            u = pd.read_csv(up)
            falt = [c for c in ["cliente_id", "dias_sin_compra", "compras_30d", "compras_90d", "historial"] if c not in u.columns]
            if falt:
                st.error(f"Faltan columnas: {falt}")
            else:
                if "estado_cobertura" not in u.columns: u["estado_cobertura"] = COB_SIN
                filas = []
                for _, x in u.iterrows():
                    dias = None if pd.isna(x["dias_sin_compra"]) else int(x["dias_sin_compra"])
                    cob = x["estado_cobertura"] if x["estado_cobertura"] in ESTADOS_COBERTURA else COB_SIN
                    pr = modelo.predecir_probabilidad(dias if dias is not None else 730, int(x["compras_30d"]), int(x["compras_90d"]), int(x["historial"]))
                    e, pri, acc, crit = clasificador.clasificar_cliente(dias, int(x["historial"]), cob)
                    filas.append({"cliente_id": x["cliente_id"], "semaforo": e, "prioridad": pri, "prob_recompra_pct": round(pr * 100, 1), "accion": acc, "criterio": crit})
                res = pd.DataFrame(filas).sort_values("prob_recompra_pct", ascending=False)
                st.success(f"{len(res)} registros evaluados con el modelo y las reglas del proyecto.")
                st.dataframe(res, use_container_width=True, hide_index=True)
                st.download_button("📥 Descargar resultados (CSV)", res.to_csv(index=False).encode("utf-8-sig"), "OperIA_resultados_cargados.csv", "text/csv")
        except Exception as ex:
            st.error(f"No se pudo leer el archivo: {ex}")

# ---------------- 5. Pruebas y evidencias ----------------
with t_test:
    st.subheader("📋 Pruebas y evidencias")
    casos = validar_casos_controlados()
    incid = analizar_incidencias_opcionales()
    ok = sum(c["aprobado"] for c in casos)
    e1, e2 = st.columns(2)
    e1.success(f"✅ Casos controlados: {ok} de {len(casos)} aprobados")
    e2.info(f"🛡️ Incidencias identificadas: {len(incid)} (archivo opcional, nunca mezclado con ventas.csv)")
    df_c = pd.DataFrame([{"Caso": c["caso"], "Esperado": str(c["esperado"]), "Obtenido": str(c["obtenido"]),
                          "Estado": "✅ APROBADO" if c["aprobado"] else "❌ FALLÓ"} for c in casos])
    st.dataframe(df_c, use_container_width=True, hide_index=True)
    st.markdown("##### Incidencias y decisión por fila")
    df_i = pd.DataFrame(incid)
    st.dataframe(df_i, use_container_width=True, hide_index=True)
    st.markdown("Para ejecutar las pruebas automáticas: `python -m unittest discover tests` (incluye reglas de semáforo, cobertura, no-fuga del futuro y coincidencia con la referencia oficial).")
    evid = {"fecha_generacion": datetime.now().isoformat(timespec="seconds"), "proyecto": "OperIA", "advertencia": cif["advertencia"],
            "datos_oficiales_integros": cif["datos_oficiales_integros"], "casos_controlados": casos, "incidencias": incid,
            "metricas_modelo": {k2: met[k2] for k2 in ("metricas_validacion", "metricas_prueba_modelo", "metricas_prueba_linea_base_compra_reciente")},
            "backtest_pronostico": cif["backtest_pronostico"]}
    q1, q2 = st.columns(2)
    q1.download_button("📥 Evidencias completas (JSON)", json.dumps(evid, ensure_ascii=False, indent=2, default=str), "OperIA_Evidencias.json", "application/json", use_container_width=True)
    q2.download_button("📥 Casos controlados (CSV)", df_c.to_csv(index=False).encode("utf-8-sig"), "OperIA_Casos.csv", "text/csv", use_container_width=True)

# ---------------- 6. Ventas vs TRM ----------------
with t_trm:
    st.subheader("Ventas en COP frente a la TRM de prueba (no oficial)")
    m_ = df.assign(Mes=lambda x: x["Fecha"].dt.to_period("M").dt.to_timestamp()).groupby("Mes").agg(Ventas=("Ventas_COP", "sum"), TRM=("TRM", "mean")).reset_index()
    if HAS_PLOTLY:
        fig = go.Figure()
        fig.add_bar(x=m_["Mes"], y=m_["Ventas"], name="Ventas (COP)", marker_color="#2563EB", opacity=.75)
        fig.add_scatter(x=m_["Mes"], y=m_["TRM"], name="TRM de prueba", yaxis="y2", line=dict(color="#DC2626", width=3))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right"), height=430, hovermode="x unified", legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
    t = cif["trm"]
    st.info(f"Correlación de Pearson TRM–ventas: **{t['correlacion_trm_ventas']}** ({t.get('meses_analizados', '?')} meses). {t['interpretacion']}")
    st.caption("La TRM del paquete es una serie construida matemáticamente (incluye fines de semana); no es la tasa oficial.")

# ---------------- 7. Ficha 360 ----------------
with t_fic:
    st.subheader("Ficha 360° del cliente")
    sel = st.selectbox("Cliente", vista["Cliente_ID"] + " · " + vista["Cliente"], key="ficha_sel")
    r = vista[vista["Cliente_ID"] == sel.split(" · ")[0]].iloc[0]
    f1, f2, f3 = st.columns(3)
    f1.markdown(f"**{r['Cliente']}** (`{r['Cliente_ID']}`)  \n{r['Ciudad']} · {r['Sector']}  \nProductos: {r['Productos_Historicos'] or '—'}")
    f2.markdown(f"**Semáforo:** {r['Estado_Cliente']}  \n**Cobertura:** {r['Estado_Cobertura']}  \n**Días sin compra:** {r['Dias_Sin_Comprar']}  \n**Frecuente ≥8 ops:** {'Sí' if r['Es_Frecuente_8ops'] else 'No'} · **Frío:** {'Sí' if r['Es_Frio'] else 'No'}")
    f3.markdown(f"**Prioridad:** {r['Prioridad_Llamada']}  \n**P recompra 30 d:** {r['Prob_Recompra_Pct']}%  \n**Facturación:** ${r['Ventas_COP']:,.0f}  \n**Ticket:** ${r['Ticket_Promedio_COP']:,.0f}")
    st.caption(r["Criterio_Decision"])
    st.dataframe(df[df["Cliente_ID"] == r["Cliente_ID"]].sort_values("Fecha", ascending=False)[
        ["Fecha", "Producto", "Familia_Producto", "Cantidad", "Moneda", "Precio_Unitario", "TRM", "Ventas_COP", "Estado_Venta"]],
        use_container_width=True, hide_index=True)

# ---------------- 8. Objetivos ----------------
with t_obj:
    st.subheader("🎯 Objetivo y alcance")
    st.markdown('<div class="info-box"><b>Pregunta guía:</b> ¿Cómo ayudar a Operaciones y Comercial a automatizar el cruce de datos para anticipar recompras y priorizar clientes con una visualización interactiva?</div>', unsafe_allow_html=True)
    st.markdown(f"""
* **Usuario principal:** equipo Comercial y Operaciones. **Decisión:** a qué clientes llamar hoy y con qué evidencia.
* **Qué hace:** integra ventas, TRM de prueba, clientes y base instalada; clasifica con reglas transparentes; estima la probabilidad de recompra a 30 días con un modelo comparado contra una línea base.
* **Qué NO hace:** no contacta clientes, no promete ventas, no usa datos reales; no integra compras/proveedores todavía (ver plan de producto).
* **Resultados del modelo en prueba temporal:** F1 {met['metricas_prueba_modelo']['F1']:.3f} (línea base {met['metricas_prueba_linea_base_compra_reciente']['F1']:.3f}), recall {met['metricas_prueba_modelo']['recall']:.0%} (línea base {met['metricas_prueba_linea_base_compra_reciente']['recall']:.0%}), precisión {met['metricas_prueba_modelo']['precision']:.0%} (línea base {met['metricas_prueba_linea_base_compra_reciente']['precision']:.0%}).
* **Preguntas pendientes para la empresa:** definición real de cliente frío, periodicidad de renovación, indicadores de éxito, permisos de uso de datos, significado de «com», calidad e historia de datos.
""")

# ---------------- 9. Datos ----------------
with t_dat:
    st.subheader("Datos procesados (operaciones con TRM aplicada)")
    mon = st.radio("Moneda original", ["Todas", "COP", "USD"], horizontal=True)
    x = df if mon == "Todas" else df[df["Moneda"] == mon]
    st.dataframe(x[["Fecha", "Cliente", "Producto", "Cantidad", "Moneda", "Precio_Unitario", "TRM", "Ventas_COP", "Estado_Venta"]].head(200),
                 use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("OperIA · Reto 4: IA en Operaciones · Green Services and Solutions SAS · Hackatón EstudIA · datos de prueba")
