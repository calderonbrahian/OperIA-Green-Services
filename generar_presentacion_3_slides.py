"""
generar_presentacion_3_slides.py
Genera una presentación condensada de alto impacto en EXACTAMENTE 3 DIAPOSITIVAS
para el Pitch de 3 minutos de OperIA 360° (1 diapositiva por minuto).
"""
import shutil
from pathlib import Path

import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

C_NAVY = RGBColor(30, 58, 138)         # #1E3A8A
C_BLUE = RGBColor(37, 99, 235)         # #2563EB
C_LIGHT_BLUE = RGBColor(239, 246, 255) # #EFF6FF
C_GREEN = RGBColor(16, 185, 129)       # #10B981
C_LIGHT_GREEN = RGBColor(220, 252, 231)# #DCFCE7
C_YELLOW = RGBColor(245, 158, 11)      # #F59E0B
C_LIGHT_YELLOW = RGBColor(254, 243, 199)# #FEF3C7
C_RED = RGBColor(239, 68, 68)          # #EF4444
C_LIGHT_RED = RGBColor(254, 226, 226)  # #FEE2E2
C_PURPLE = RGBColor(139, 92, 246)      # #8B5CF6
C_BG = RGBColor(248, 250, 252)         # #F8FAFC
C_WHITE = RGBColor(255, 255, 255)
C_TEXT = RGBColor(15, 23, 42)
C_MUTED = RGBColor(100, 116, 139)
C_BORDER = RGBColor(226, 232, 240)

def crear_presentacion_3_slides():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid(); bg.fill.fore_color.rgb = C_BG; bg.line.color.rgb = C_BG

    def add_header(slide, badge, title, timing):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.3))
        tf = tb.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_b = tf.paragraphs[0]
        p_b.text = f"{badge.upper()}   |   ⏱️ {timing.upper()}"
        p_b.font.name = "Arial"; p_b.font.size = Pt(11); p_b.font.bold = True; p_b.font.color.rgb = C_BLUE

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = "Arial"; p_t.font.size = Pt(23); p_t.font.bold = True; p_t.font.color.rgb = C_NAVY
        p_t.space_before = Pt(3)

    def add_card(slide, left, top, width, height, bg_col=C_WHITE, border_col=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid(); card.fill.fore_color.rgb = bg_col
        if border_col:
            card.line.color.rgb = border_col; card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    # =========================================================================
    # DIAPOSITIVA 1: MINUTO 0:00 A 1:00 — EL DOLOR Y LA RADIOGRAFÍA DE CARTERA
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout); add_bg(s1)
    add_header(s1, "Reto 4: IA en Operaciones · Green Services SAS", "1. El Problema y la Fuga Crítica en la Cartera Auditada", "Minuto 0:00 a 1:00")

    # Columna Izquierda: El Dolor y la Pregunta Orientadora
    add_card(s1, 0.8, 1.8, 5.6, 5.1, C_WHITE, C_RED)
    tb_izq = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.7))
    tf_izq = tb_izq.text_frame; tf_izq.word_wrap = True
    
    p = tf_izq.paragraphs[0]
    p.text = "❌ El Dolor Operativo en Hojas de Cálculo:"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_RED

    items_d = [
        ("Procesos Manuales Lentos:", "Consolidar 1,371 transacciones en COP y USD con TRM variable tomaba de 3 a 5 días al mes."),
        ("Pólizas Desprotegidas:", "Vencimiento imprevisto de contratos de soporte sin aviso ni renovación previa."),
        ("La Pregunta Orientadora:", "«¿Cómo ayudar a Operaciones y Ventas a automatizar el cruce de datos para predecir el comportamiento y anticipar recompras?»")
    ]
    for tit, desc in items_d:
        pi = tf_izq.add_paragraph()
        pi.text = f"• {tit} {desc}"
        pi.font.size = Pt(11.5); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(8)

    # Tarjeta de Pérdida
    callout = tf_izq.add_paragraph()
    callout.text = "⚠️ Diagnóstico Crítico: ¡1 de cada 3 clientes está en abandono comercial!"
    callout.font.size = Pt(12); callout.font.bold = True; callout.font.color.rgb = C_RED; callout.space_before = Pt(14)

    # Columna Derecha: 4 Tarjetas de Semáforo de Cartera Real
    add_card(s1, 6.7, 1.8, 5.8, 5.1, C_LIGHT_BLUE, C_BLUE)
    tb_der = s1.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(4.7))
    tf_der = tb_der.text_frame; tf_der.word_wrap = True

    p = tf_der.paragraphs[0]
    p.text = "📊 Radiografía Oficial de Cartera (120 Clientes):"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    cards_stat = [
        ("🔴 41 Clientes Fríos (34.2%):", "≥ 90 días sin comprar. ¡Fuga crítica de clientes que requieren rescate urgente!"),
        ("🟡 41 Base Instalada (34.2%):", "Recencia 31 a 89 días. Cuentas intermedias para seguimiento y renovación de pólizas."),
        ("🟢 38 Frecuentes Activos (31.7%):", "Recencia ≤ 30 días. Cuentas sanas con compras en el último mes."),
        ("🔵 $5,647.4M COP Facturados:", "1,371 operaciones confirmadas consolidadas con TRM histórica oficial.")
    ]
    for tit, desc in cards_stat:
        pi = tf_der.add_paragraph()
        pi.text = f"{tit}\n  {desc}"
        pi.font.size = Pt(11.5); pi.font.bold = True; pi.font.color.rgb = C_NAVY; pi.space_before = Pt(8)

    s1.notes_slide.notes_text_frame.text = (
        "MINUTO 1: 'Buenos días. En empresas de tecnología como Green Services, el equipo comercial suele operar a ciegas frente al Excel: cruzar ventas multimoneda con TRM toma días y los clientes dejan de comprar sin que nadie lo note a tiempo. "
        "Al auditar la cartera oficial de 120 clientes y $5,647 millones de facturación, descubrimos una fuga crítica: 41 clientes fríos, es decir, el 34% de la cartera lleva más de 90 días sin comprar. "
        "Por eso creamos OperIA 360°: la plataforma que automatiza este cruce y anticipa recompras mediante Inteligencia Artificial.'"
    )

    # =========================================================================
    # DIAPOSITIVA 2: MINUTO 1:00 A 2:00 — EL CRUCE RELACIONAL Y EL CEREBRO DE IA
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout); add_bg(s2)
    add_header(s2, "Arquitectura y Modelo Predictivo", "2. OperIA: Cruce de Coberturas y Caja Blanca de IA", "Minuto 1:00 a 2:00")

    # Columna Izquierda: Cruce y Coberturas
    add_card(s2, 0.8, 1.8, 5.6, 5.1, C_WHITE, C_PURPLE)
    tb_cruce = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.7))
    tfc = tb_cruce.text_frame; tfc.word_wrap = True

    p = tfc.paragraphs[0]
    p.text = "🛡️ Cruce Relacional y Estado_Cobertura:"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_PURPLE

    cruce_points = [
        ("Conversión TRM Automática:", "Normalización monetaria según la fecha exacta de transacción. Exclusión de anuladas ($0 COP)."),
        ("Nueva Variable Estado_Cobertura:", "Monitoreo de vencimiento de contratos sobre 120 clientes:"),
        (" • 🟡 25 Próxima a Renovar (≤ 45d):", "Cuentas con póliza por expirar. Renovación anticipada urgente."),
        (" • 🟢 45 Vigentes (> 45d):", "Cuentas con soporte garantizado y al día."),
        (" • 🔴 50 Vencidas (< 0d):", "Cuentas que requieren regularización contractual.")
    ]
    for tit, desc in cruce_points:
        pi = tfc.add_paragraph()
        pi.text = f"{tit} {desc}"
        pi.font.size = Pt(11); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(6)

    # Columna Derecha: El Cerebro de IA
    add_card(s2, 6.7, 1.8, 5.8, 5.1, C_WHITE, C_BLUE)
    tb_ia = s2.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(4.7))
    tfia = tb_ia.text_frame; tfia.word_wrap = True

    p = tfia.paragraphs[0]
    p.text = "🧠 Cerebro de IA: Caja Blanca Explicable"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_BLUE

    ia_points = [
        ("Regresión Logística L2 Temporal:", "Sin cajas negras. Aprende del pasado para predecir recompra a 30 días."),
        ("Pesos Aprendidos y Auditables:", "Frecuencia 90d (+0.13) y 30d (+0.10) impulsan propensión; Recencia (-0.06) penaliza inactividad."),
        ("Rendimiento Fuera de Tiempo (Out-Of-Time):", "En prueba temporal estricta supera a la intuición:"),
        (" • RECALL OPERIA: 90.91%", "vs. 55.30% de la línea base (+35.6% más recompras capturadas)."),
        (" • MATRIZ DE CONFUSIÓN:", "120 TP detectados, solo 12 Falsos Negativos (recompras omitidas).")
    ]
    for tit, desc in ia_points:
        pi = tfia.add_paragraph()
        pi.text = f"{tit} {desc}"
        pi.font.size = Pt(11); pi.font.bold = True if "RECALL" in tit else False; pi.font.color.rgb = C_NAVY if "RECALL" in tit else C_TEXT; pi.space_before = Pt(6)

    s2.notes_slide.notes_text_frame.text = (
        "MINUTO 2: 'OperIA no es una caja negra: es un motor relacional y predictivo 100% transparente. "
        "Primero, automatiza la ingesta: indexa TRM histórica, excluye anuladas y clasifica el Estado de Cobertura de las pólizas, identificando 25 cuentas por vencer en menos de 45 días para blindar ingresos de soporte. "
        "Segundo, implementamos una Regresión Logística regularizada con partición temporal estricta. ¿El resultado? Mientras el criterio intuitivo solo detecta el 55% de las recompras, OperIA alcanza un Recall del 90.9% en prueba fuera de tiempo. Capturamos casi todas las oportunidades antes de que se enfríen.'"
    )

    # =========================================================================
    # DIAPOSITIVA 3: MINUTO 2:00 A 3:00 — PROYECCIÓN, BACKTESTING Y DEMO EN VIVO
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout); add_bg(s3)
    add_header(s3, "Validación Empírica y Propuesta de Valor", "3. Pronóstico $216.5M Validado y Acción en < 2 Segundos", "Minuto 2:00 a 3:00")

    # Columna Izquierda: Proyección y Backtesting
    add_card(s3, 0.8, 1.8, 5.6, 5.1, C_LIGHT_GREEN, C_GREEN)
    tb_proy = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.7))
    tfp = tb_proy.text_frame; tfp.word_wrap = True

    p = tfp.paragraphs[0]
    p.text = "🔮 Proyección Nov 2026 y Backtesting:"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = RGBColor(20, 83, 45)

    p_stat = tfp.add_paragraph()
    p_stat.text = "$216,486,299 COP PROYECTADOS\n94 Compradores con Alta Propensión (P ≥ 40%)"
    p_stat.font.size = Pt(13); p_stat.font.bold = True; p_stat.font.color.rgb = C_NAVY; p_stat.space_before = Pt(4)

    p_bt_tit = tfp.add_paragraph()
    p_bt_tit.text = "🏆 Validación Empírica con Backtest (Jul–Oct 2026):"
    p_bt_tit.font.size = Pt(12); p_bt_tit.font.bold = True; p_bt_tit.font.color.rgb = RGBColor(22, 101, 52); p_bt_tit.space_before = Pt(10)

    bt_items = [
        ("MAE Modelo OperIA:", "$25,812,479 COP"),
        ("MAE Línea Base (Mes previo):", "$52,475,745 COP"),
        ("REDUCCIÓN COMPROBADA:", "¡50.81% menos error que la intuición!")
    ]
    for lbl, val in bt_items:
        pi = tfp.add_paragraph()
        pi.text = f"• {lbl}  {val}"
        pi.font.size = Pt(11); pi.font.bold = True if "REDUCCIÓN" in lbl else False; pi.font.color.rgb = C_NAVY; pi.space_before = Pt(4)

    # Columna Derecha: Demo en Vivo, Rigor y Cierre
    add_card(s3, 6.7, 1.8, 5.8, 5.1, C_WHITE, C_BLUE)
    tb_demo = s3.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(4.7))
    tfd = tb_demo.text_frame; tfd.word_wrap = True

    p = tfd.paragraphs[0]
    p.text = "⚡ Demo en Vivo y Rigor de Ingeniería:"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_BLUE

    demo_items = [
        ("Semáforo con Clic Directo (< 2 seg):", "Un clic en la tarjeta roja filtra los clientes fríos de inmediato con su guion comercial."),
        ("100% Pruebas Aprobadas:", "6/6 casos controlados oficiales + 7 incidencias aisladas + 17 pruebas unitarias (0.018s)."),
        ("Despliegue Dual en Producción:", "Online en GitHub Pages (sin instalación) y local en Streamlit.")
    ]
    for tit, desc in demo_items:
        pi = tfd.add_paragraph()
        pi.text = f"• {tit} {desc}"
        pi.font.size = Pt(11); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(6)

    # Cita de Cierre
    p_quote = tfd.add_paragraph()
    p_quote.text = "«Green Services pasa de lamentar clientes perdidos el mes pasado, a saber con exactitud a quién llamar hoy para asegurar la facturación de mañana.»"
    p_quote.font.size = Pt(11.5); p_quote.font.bold = True; p_quote.font.italic = True; p_quote.font.color.rgb = C_NAVY; p_quote.space_before = Pt(10)

    p_url = tfd.add_paragraph()
    p_url.text = "🌐 Probar online: https://calderonbrahian.github.io/OperIA-Green-Services/"
    p_url.font.size = Pt(10.5); p_url.font.bold = True; p_url.font.color.rgb = C_BLUE; p_url.space_before = Pt(6)

    s3.notes_slide.notes_text_frame.text = (
        "MINUTO 3: 'Para Noviembre de 2026 proyectamos $216.5M con 94 compradores esperados. Sometimos este pronóstico a Backtesting histórico contra la práctica habitual de repetir el mes previo: OperIA reduce el error absoluto a la mitad (50.81% menos error). "
        "En la demo en vivo, el asesor no revisa 1,300 filas: hace un solo clic en la tarjeta de clientes fríos y en menos de 2 segundos tiene la lista priorizada con el guion de llamada. "
        "Pasa el 100% de casos de prueba y está desplegado públicamente en GitHub Pages. Con OperIA, Green Services pasa de lamentar clientes perdidos a saber a quién llamar hoy para asegurar la facturación de mañana. Muchas gracias.'"
    )

    base = Path(__file__).resolve().parent
    out1 = base / "Presentacion_OperIA_Pitch_3_Slides.pptx"
    out2 = base / "docs" / "Presentacion_OperIA_Pitch_3_Slides.pptx"
    out3 = base.parent / "Documentacion" / "Presentacion_OperIA_Pitch_3_Slides.pptx"

    prs.save(str(out1))
    print(f"Creado: {out1}")
    shutil.copyfile(out1, out2)
    print(f"Creado: {out2}")
    out3.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out1, out3)
    print(f"Creado: {out3}")

if __name__ == "__main__":
    crear_presentacion_3_slides()
