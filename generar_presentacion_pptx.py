"""
generar_presentacion_pptx.py
Genera la presentación ejecutiva profesional de 10 diapositivas en formato PowerPoint (.pptx)
para OperIA 360° (Green Services and Solutions SAS).
Diseño en formato panorámico 16:9 con paleta corporativa, métricas oficiales y notas para el orador.
"""
import shutil
from pathlib import Path

import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Paleta Corporativa Oficial
C_NAVY = RGBColor(30, 58, 138)       # #1E3A8A - Fondo portada y títulos primarios
C_BLUE = RGBColor(37, 99, 235)       # #2563EB - Azul activo / primario claro
C_LIGHT_BLUE = RGBColor(239, 246, 255) # #EFF6FF - Fondo de tarjetas azul suave
C_GREEN = RGBColor(16, 185, 129)     # #10B981 - Éxito / Frecuente
C_LIGHT_GREEN = RGBColor(220, 252, 231) # #DCFCE7 - Fondo verde suave
C_YELLOW = RGBColor(245, 158, 11)    # #F59E0B - Advertencia / Base instalada
C_LIGHT_YELLOW = RGBColor(254, 243, 199) # #FEF3C7 - Fondo amarillo suave
C_RED = RGBColor(239, 68, 68)        # #EF4444 - Alerta / Clientes fríos
C_LIGHT_RED = RGBColor(254, 226, 226) # #FEE2E2 - Fondo rojo suave
C_PURPLE = RGBColor(139, 92, 246)    # #8B5CF6 - Proyección
C_LIGHT_PURPLE = RGBColor(237, 233, 254) # #EDE9FE - Fondo púrpura
C_BG = RGBColor(248, 250, 252)       # #F8FAFC - Fondo de diapositivas claras
C_CARD_BG = RGBColor(255, 255, 255)  # #FFFFFF - Fondo de tarjetas
C_TEXT = RGBColor(15, 23, 42)        # #0F172A - Texto oscuro principal
C_MUTED = RGBColor(100, 116, 139)    # #64748B - Texto secundario
C_BORDER = RGBColor(226, 232, 240)   # #E2E8F0 - Bordes
C_WHITE = RGBColor(255, 255, 255)

def crear_presentacion():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_bg(slide, color=C_BG):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.color.rgb = color
        return bg

    def add_header(slide, category, title, subtitle=None):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        # Categoría superior en mayúsculas
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_BLUE
        
        # Título principal
        p_tit = tf.add_paragraph()
        p_tit.text = title
        p_tit.font.name = "Arial"
        p_tit.font.size = Pt(22)
        p_tit.font.bold = True
        p_tit.font.color.rgb = C_NAVY
        p_tit.space_before = Pt(3)

        if subtitle:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.name = "Arial"
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = C_MUTED
            p_sub.space_before = Pt(2)

    def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    def set_notes(slide, text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = text

    # =========================================================================
    # SLIDE 1: PORTADA EJECUTIVA
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, C_NAVY)

    # Decoración geométrica sutil
    dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.2), Inches(13.333), Inches(0.3))
    dec.fill.solid(); dec.fill.fore_color.rgb = C_BLUE; dec.line.fill.background()

    # Badge de evento
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.2), Inches(5.2), Inches(0.5))
    badge.fill.solid(); badge.fill.fore_color.rgb = C_BLUE; badge.line.fill.background()
    p_b = badge.text_frame.paragraphs[0]
    p_b.text = "HACKATÓN ESTUDIA 2026 · RETO 4: IA EN OPERACIONES"
    p_b.font.name = "Arial"; p_b.font.size = Pt(11); p_b.font.bold = True; p_b.font.color.rgb = C_WHITE
    p_b.alignment = PP_ALIGN.CENTER

    # Título y Subtítulo
    tb1 = s1.shapes.add_textbox(Inches(0.9), Inches(2.0), Inches(11.5), Inches(3.0))
    tf1 = tb1.text_frame; tf1.word_wrap = True
    
    p1 = tf1.paragraphs[0]
    p1.text = "OperIA 360°"
    p1.font.name = "Arial"; p1.font.size = Pt(46); p1.font.bold = True; p1.font.color.rgb = C_WHITE

    p2 = tf1.add_paragraph()
    p2.text = "Inteligencia Artificial para la Gestión Proactiva de Operaciones y Recompra Comercial"
    p2.font.name = "Arial"; p2.font.size = Pt(20); p2.font.color.rgb = RGBColor(191, 219, 254); p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "Plataforma de Gobernanza Relacional, Semáforo Predictivo y Proyección Financiera con Backtesting"
    p3.font.name = "Arial"; p3.font.size = Pt(14); p3.font.color.rgb = RGBColor(148, 163, 184); p3.space_before = Pt(6)

    # Tarjeta de Metadata / Autor
    meta_card = add_card(s1, 0.9, 5.2, 11.5, 1.4, RGBColor(23, 44, 105), C_BLUE)
    tb_meta = s1.shapes.add_textbox(Inches(1.1), Inches(5.35), Inches(11.1), Inches(1.1))
    tf_m = tb_meta.text_frame; tf_m.word_wrap = True
    p_m1 = tf_m.paragraphs[0]
    p_m1.text = "• Empresa: Green Services and Solutions SAS  |  • Autor: Brahian Calderón  |  • Corte: Octubre 2026"
    p_m1.font.name = "Arial"; p_m1.font.size = Pt(12); p_m1.font.bold = True; p_m1.font.color.rgb = C_WHITE

    p_m2 = tf_m.add_paragraph()
    p_m2.text = "• Visor Online: https://calderonbrahian.github.io/OperIA-Green-Services/  |  • Código: GitHub Oficial"
    p_m2.font.name = "Arial"; p_m2.font.size = Pt(11.5); p_m2.font.color.rgb = RGBColor(203, 213, 225); p_m2.space_before = Pt(4)

    set_notes(s1, "Buenos días. Hoy presentamos OperIA 360°, la solución que transforma la gestión comercial de Green Services and Solutions SAS, pasando de un enfoque reactivo basado en hojas de cálculo a un modelo predictivo con IA explicable que asegura la retención y facturación futura.")

    # =========================================================================
    # SLIDE 2: EL PROBLEMA Y LA PREGUNTA GUÍA
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout); add_bg(s2)
    add_header(s2, "Contexto del Negocio y Diagnóstico Inicial", "De la Reacción Manual al Control Comercial Proactivo")

    # Tarjeta Izquierda: Dolor Actual
    add_card(s2, 0.8, 1.9, 5.7, 4.8, C_WHITE, C_RED)
    tb_d = s2.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.4))
    tfd = tb_d.text_frame; tfd.word_wrap = True
    pd_tit = tfd.paragraphs[0]
    pd_tit.text = "❌ El Dolor Operativo: Gestión en Excel"
    pd_tit.font.size = Pt(16); pd_tit.font.bold = True; pd_tit.font.color.rgb = C_RED

    items_dolor = [
        ("Cruce Multimoneda Disperso:", "1,371 operaciones en COP y USD con TRM variable consolidadas manualmente mes a mes."),
        ("Fuga Silenciosa de Clientes:", "Cuentas que dejan de comprar sin que el equipo comercial detecte la inactividad a tiempo."),
        ("Pólizas y Licencias Desprotegidas:", "Contratos de soporte que vencen sin gestión preventiva de renovación."),
        ("Desgaste en Tareas Operativas:", "Tiempo de asesores consumido en limpiar filas en vez de concretar ventas.")
    ]
    for tit, desc in items_dolor:
        p = tfd.add_paragraph()
        p.text = f"• {tit} {desc}"
        p.font.size = Pt(12); p.font.color.rgb = C_TEXT; p.space_before = Pt(10)

    # Tarjeta Derecha: Solución y Pregunta Guía
    add_card(s2, 6.8, 1.9, 5.7, 3.2, C_WHITE, C_BLUE)
    tb_q = s2.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(2.8))
    tfq = tb_q.text_frame; tfq.word_wrap = True
    pq_tit = tfq.paragraphs[0]
    pq_tit.text = "🎯 La Pregunta Orientadora del Reto"
    pq_tit.font.size = Pt(16); pq_tit.font.bold = True; pq_tit.font.color.rgb = C_BLUE

    pq_txt = tfq.add_paragraph()
    pq_txt.text = "«¿Cómo podríamos ayudar al equipo de Operaciones y Comercial a automatizar el cruce de datos para predecir el comportamiento de sus clientes y anticipar recompras mediante un modelo con visualización interactiva?»"
    pq_txt.font.size = Pt(12.5); pq_txt.font.italic = True; pq_txt.font.color.rgb = C_NAVY; pq_txt.space_before = Pt(8)

    # Tarjeta Métrica Destacada
    add_card(s2, 6.8, 5.3, 5.7, 1.4, C_LIGHT_BLUE, C_BLUE)
    tb_m = s2.shapes.add_textbox(Inches(7.0), Inches(5.4), Inches(5.3), Inches(1.2))
    tfm = tb_m.text_frame; tfm.word_wrap = True
    pm1 = tfm.paragraphs[0]
    pm1.text = "3 a 5 DÍAS HÁBILES AL MES"
    pm1.font.size = Pt(20); pm1.font.bold = True; pm1.font.color.rgb = C_NAVY
    pm2 = tfm.add_paragraph()
    pm2.text = "Tiempo que requería el cruce de tablas en Excel antes de la implementación de OperIA."
    pm2.font.size = Pt(11.5); pm2.font.color.rgb = C_MUTED; pm2.space_before = Pt(2)

    set_notes(s2, "El problema fundamental: el equipo comercial navegaba a ciegas. Cruzar manualmente 1.300 operaciones con TRM diaria tomaba días, lo que provocaba que clientes valiosos se enfriaran sin que nadie se enterara a tiempo.")

    # =========================================================================
    # SLIDE 3: AUDITORÍA DE DATOS DE CARTERA
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout); add_bg(s3)
    add_header(s3, "Diagnóstico Cuantitativo Oficial", "Radiografía de la Cartera Auditada al Corte (Octubre 2026)")

    # 4 Tarjetas de Semáforo
    cards_data = [
        ("CARTERA AUDITADA", "120", "Cuentas Monitoreadas", "100% de la cartera con verificación criptográfica SHA-256.", C_BLUE, C_LIGHT_BLUE, 0.8),
        ("🟢 FRECUENTES (ACTIVOS)", "38", "Recencia ≤ 30 Días", "Cuentas con compras en el último mes. Prioridad regular o preventiva.", C_GREEN, C_LIGHT_GREEN, 3.8),
        ("🟡 BASE INSTALADA", "41", "Recencia 31 a 89 Días", "Cuentas intermedias sin compras recientes pero aún en zona de seguimiento.", C_YELLOW, C_LIGHT_YELLOW, 6.8),
        ("🔴 CLIENTES FRÍOS", "41", "Recencia ≥ 90 Días", "Fuga crítica del 34.2%: Inactividad severa. Requieren reactivación inmediata.", C_RED, C_LIGHT_RED, 9.8)
    ]
    for cat, num, sub, desc, col, bg_col, left in cards_data:
        add_card(s3, left, 1.9, 2.7, 3.5, C_WHITE, col)
        
        # Barra superior de color
        bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(1.9), Inches(2.7), Inches(0.15))
        bar.fill.solid(); bar.fill.fore_color.rgb = col; bar.line.fill.background()

        tb = s3.shapes.add_textbox(Inches(left + 0.15), Inches(2.15), Inches(2.4), Inches(3.1))
        tf = tb.text_frame; tf.word_wrap = True
        
        p1 = tf.paragraphs[0]; p1.text = cat; p1.font.size = Pt(10); p1.font.bold = True; p1.font.color.rgb = col
        p2 = tf.add_paragraph(); p2.text = num; p2.font.size = Pt(38); p2.font.bold = True; p2.font.color.rgb = C_NAVY; p2.space_before = Pt(4)
        p3 = tf.add_paragraph(); p3.text = sub; p3.font.size = Pt(11); p3.font.bold = True; p3.font.color.rgb = C_TEXT; p3.space_before = Pt(2)
        p4 = tf.add_paragraph(); p4.text = desc; p4.font.size = Pt(10.5); p4.font.color.rgb = C_MUTED; p4.space_before = Pt(8)

    # Banner Financiero Inferior
    add_card(s3, 0.8, 5.7, 11.7, 1.2, C_NAVY, None)
    tb_b = s3.shapes.add_textbox(Inches(1.0), Inches(5.8), Inches(11.3), Inches(1.0))
    tfb = tb_b.text_frame; tfb.word_wrap = True
    pb1 = tfb.paragraphs[0]
    pb1.text = "$5,647,449,456.36 COP FACTURADOS EN TOTAL"
    pb1.font.size = Pt(20); pb1.font.bold = True; pb1.font.color.rgb = RGBColor(147, 197, 253)
    pb2 = tfb.add_paragraph()
    pb2.text = "Cifra histórica consolidada sobre 1,371 transacciones confirmadas. La TRM utilizada normaliza ventas USD según la tasa del día."
    pb2.font.size = Pt(11); pb2.font.color.rgb = C_WHITE; pb2.space_before = Pt(2)

    set_notes(s3, "Al aplicar un análisis riguroso sobre los datos oficiales, descubrimos una fuga crítica: 41 clientes fríos, es decir, un tercio de la cartera lleva más de 3 meses sin comprar. Cada cliente frío representa ingresos recurrentes en riesgo.")

    # =========================================================================
    # SLIDE 4: ARQUITECTURA DEL CRUCE RELACIONAL Y COBERTURAS
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout); add_bg(s4)
    add_header(s4, "Ingeniería de Datos y Normalización", "Arquitectura del Cruce Relacional y la Variable Maestra Estado_Cobertura")

    # 3 Pasos del Cruce
    steps = [
        ("1. Ingesta y TRM Diaria", "Cruce automático de cada venta con la TRM de la fecha exacta. Normalización de USD a COP y exclusión estricta de ventas anuladas ($0 COP).", C_BLUE, 0.8),
        ("2. Nueva Variable de Cobertura", "Cálculo determinístico de la vigencia mínima de contratos en base instalada frente a la fecha de corte para blindar el ARR de soporte.", C_PURPLE, 4.8),
        ("3. Vista Única Cliente 360°", "Consolidación de las 120 cuentas (sin excluir prospectos), asignando semáforo por recencia y prioridad modular.", C_GREEN, 8.8)
    ]
    for tit, desc, col, left in steps:
        add_card(s4, left, 1.9, 3.7, 2.3, C_WHITE, col)
        tb = s4.shapes.add_textbox(Inches(left + 0.15), Inches(2.05), Inches(3.4), Inches(2.0))
        tf = tb.text_frame; tf.word_wrap = True
        p1 = tf.paragraphs[0]; p1.text = tit; p1.font.size = Pt(13); p1.font.bold = True; p1.font.color.rgb = col
        p2 = tf.add_paragraph(); p2.text = desc; p2.font.size = Pt(11); p2.font.color.rgb = C_MUTED; p2.space_before = Pt(6)

    # Detalle de la Variable Estado_Cobertura
    add_card(s4, 0.8, 4.5, 11.7, 2.4, C_WHITE, C_BORDER)
    tb_cob = s4.shapes.add_textbox(Inches(1.0), Inches(4.65), Inches(11.3), Inches(2.1))
    tfc = tb_cob.text_frame; tfc.word_wrap = True
    pc_tit = tfc.paragraphs[0]
    pc_tit.text = "🛡️ Distribución Auditada de la Variable Estado_Cobertura (120 Cuentas):"
    pc_tit.font.size = Pt(13.5); pc_tit.font.bold = True; pc_tit.font.color.rgb = C_NAVY

    cobs = [
        ("🟡 Próxima a Renovar (≤ 45d):", "25 clientes (20.8%)", "Contratos con vencimiento inminente. Acción: Renovación anticipada inmediata."),
        ("🟢 Vigente (> 45d):", "45 clientes (37.5%)", "Cuentas con servicio y garantía activos. Acción: Fidelización y propuestas de up-selling."),
        ("🔴 Vencida (< 0d):", "50 clientes (41.7%)", "Contratos vencidos sin renovación. Acción: Regularización contractual y rescate de póliza."),
        ("⚪ Sin Cobertura:", "0 clientes (0.0%)", "Oportunidad de cross-selling para clientes sin póliza en el catálogo maestro.")
    ]
    for name, cnt, act in cobs:
        p = tfc.add_paragraph()
        p.text = f"• {name}  {cnt}  —  {act}"
        p.font.size = Pt(11); p.font.color.rgb = C_TEXT; p.space_before = Pt(4)

    set_notes(s4, "OperIA conecta cuatro fuentes: ventas, TRM, catálogo y contratos. Incorporamos la variable Estado de Cobertura, detectando 25 cuentas prioritarias cuyas pólizas vencen en menos de 45 días para blindar ingresos recurrentes.")

    # =========================================================================
    # SLIDE 5: EL NÚCLEO DE IA — CAJA BLANCA EXPLICABLE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout); add_bg(s5)
    add_header(s5, "Modelo Predictivo Transparente", "Caja Blanca: Regresión Logística L2 con Partición Temporal Estricta")

    # Columna Izquierda: Ecuación y Pesos
    add_card(s5, 0.8, 1.9, 5.7, 4.8, C_WHITE, C_NAVY)
    tb_eq = s5.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.4))
    tfe = tb_eq.text_frame; tfe.word_wrap = True
    pe_tit = tfe.paragraphs[0]
    pe_tit.text = "⚖️ Pesos Aprendidos por la Inteligencia Artificial"
    pe_tit.font.size = Pt(15); pe_tit.font.bold = True; pe_tit.font.color.rgb = C_NAVY

    weights = [
        ("+0.1304", "Frecuencia 90d (f90)", "Mayor impacto positivo: Compras continuas en el último trimestre predicen recompra."),
        ("+0.1013", "Frecuencia 30d (f30)", "Inercia reciente: Una compra en el último mes suma propensión inmediata."),
        ("-0.0595", "Recencia (Días sin compra)", "Penalización por inactividad: A mayor recencia, menor probabilidad."),
        ("-0.1243", "Historial Acumulado", "Regularización L2: Evita falsos positivos en clientes antiguos pero inactivos."),
        ("+0.0267", "Intercepto (Sesgo w0)", "Línea base aprendida en entrenamiento temporal estricto (hasta abr-2026).")
    ]
    for w, var, exp in weights:
        p = tfe.add_paragraph()
        p.text = f"• [{w}] {var}: {exp}"
        p.font.size = Pt(11); p.font.color.rgb = C_TEXT; p.space_before = Pt(8)

    # Columna Derecha: Métricas OOT y Matriz
    add_card(s5, 6.8, 1.9, 5.7, 4.8, C_WHITE, C_BLUE)
    tb_met = s5.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.4))
    tfm = tb_met.text_frame; tfm.word_wrap = True
    pm_tit = tfm.paragraphs[0]
    pm_tit.text = "🔬 Evaluación en Prueba Fuera de Tiempo (Jul–Sep 2026)"
    pm_tit.font.size = Pt(15); pm_tit.font.bold = True; pm_tit.font.color.rgb = C_BLUE

    metrics_oot = [
        ("RECALL (SENSIBILIDAD):", "90.91%", "vs. 55.30% de la línea base intuitiva (+35.6% de recompras capturadas)."),
        ("F1-SCORE BALANCEADO:", "0.5594", "vs. 0.5368 de la línea base: Supera al criterio de compra reciente."),
        ("UMBRAL ÓPTIMO:", "θ = 0.40", "Seleccionado en validación temporal para minimizar clientes perdidos."),
        ("MATRIZ DE CONFUSIÓN:", "360 casos", "120 TP (detectados), 51 TN, 177 FP y solo 12 FN (recompras omitidas).")
    ]
    for lbl, val, exp in metrics_oot:
        p = tfm.add_paragraph()
        p.text = f"• {lbl}  {val}\n   {exp}"
        p.font.size = Pt(11); p.font.color.rgb = C_TEXT; p.space_before = Pt(8)

    set_notes(s5, "Cero cajas negras. OperIA usa Regresión Logística regularizada propia con partición temporal estricta. Logramos un Recall del 90.9%, capturando un 35% más de recompras que cualquier método empírico.")

    # =========================================================================
    # SLIDE 6: PROYECCIÓN NOVIEMBRE 2026 Y BACKTESTING
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout); add_bg(s6)
    add_header(s6, "Proyección Financiera Validada", "Pronóstico Noviembre 2026 y Validación Empírica con Backtesting")

    # 4 Tarjetas de Proyección
    proy_cards = [
        ("FACTURACIÓN PROYECTADA", "$216.5M", "Σ [P(Compra) × Ticket]", C_PURPLE, 0.8),
        ("COMPRADORES ESPERADOS", "94 Cuentas", "Probabilidad IA ≥ 40%", C_GREEN, 3.8),
        ("TICKET PROMEDIO GLOBAL", "$4.12M", "Por transacción estimada", C_BLUE, 6.8),
        ("TRM CIERRE CORTE", "$4,029.85", "Tasa al 31/10/2026", C_YELLOW, 9.8)
    ]
    for tit, val, sub, col, left in proy_cards:
        add_card(s6, left, 1.9, 2.7, 2.0, C_WHITE, col)
        tb = s6.shapes.add_textbox(Inches(left + 0.1), Inches(2.0), Inches(2.5), Inches(1.8))
        tf = tb.text_frame; tf.word_wrap = True
        p1 = tf.paragraphs[0]; p1.text = tit; p1.font.size = Pt(9.5); p1.font.bold = True; p1.font.color.rgb = col
        p2 = tf.add_paragraph(); p2.text = val; p2.font.size = Pt(22); p2.font.bold = True; p2.font.color.rgb = C_NAVY; p2.space_before = Pt(2)
        p3 = tf.add_paragraph(); p3.text = sub; p3.font.size = Pt(10); p3.font.color.rgb = C_MUTED; p3.space_before = Pt(2)

    # Tarjeta de Backtesting Comparativo
    add_card(s6, 0.8, 4.2, 11.7, 2.7, C_LIGHT_GREEN, C_GREEN)
    tb_bt = s6.shapes.add_textbox(Inches(1.0), Inches(4.35), Inches(11.3), Inches(2.4))
    tfbt = tb_bt.text_frame; tfbt.word_wrap = True
    pbt_tit = tfbt.paragraphs[0]
    pbt_tit.text = "🏆 Validación con Backtesting Retrospectivo: El Modelo Frente a la Realidad"
    pbt_tit.font.size = Pt(15); pbt_tit.font.bold = True; pbt_tit.font.color.rgb = RGBColor(20, 83, 45)

    pbt_sub = tfbt.add_paragraph()
    pbt_sub.text = "Se evaluó el pronóstico mes a mes contra la línea base habitual ('el próximo mes venderá lo mismo que el mes anterior'):"
    pbt_sub.font.size = Pt(11); pbt_sub.font.color.rgb = RGBColor(22, 101, 52); pbt_sub.space_before = Pt(3)

    pbt_stats = tfbt.add_paragraph()
    pbt_stats.text = "• Error Absoluto Medio (MAE) Modelo OperIA:  $25,812,479 COP\n• Error Absoluto Medio (MAE) Línea Base:      $52,475,745 COP\n• REDUCCIÓN COMPROBADA DEL ERROR:        ¡50.81% menos error de predicción financiera!"
    pbt_stats.font.size = Pt(12.5); pbt_stats.font.bold = True; pbt_stats.font.color.rgb = C_NAVY; pbt_stats.space_before = Pt(6)

    set_notes(s6, "Para noviembre de 2026 proyectamos $216.5M con 94 compradores esperados. Sometimos el modelo a Backtesting frente a la práctica común de repetir el mes previo: OperIA reduce el error absoluto medio en un 50.81%.")

    # =========================================================================
    # SLIDE 7: DEMOSTRACIÓN DEL PRODUCTO — VISOR WEB Y STREAMLIT
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout); add_bg(s7)
    add_header(s7, "Experiencia de Usuario y Agilidad Operativa", "De los Datos a la Llamada Comercial en Menos de 2 Segundos")

    features = [
        ("🚨 Semáforo con Clic Directo", "Un clic en la tarjeta roja, amarilla o verde segmenta la cartera instantáneamente. Visualización de recencia, cobertura y probabilidad en una sola grilla interactiva.", C_RED, 0.8),
        ("👤 Ficha 360° por Cliente", "Acceso inmediato al perfil del cliente: historial de transacciones en COP/USD, estado de pólizas y el guion sugerido para el asesor comercial.", C_BLUE, 4.8),
        ("🧪 Simulador y Exportación", "Permite ingresar parámetros arbitrarios para simular decisiones de IA en vivo y descargar listas priorizadas en CSV para cargar en el CRM con un solo clic.", C_GREEN, 8.8)
    ]
    for tit, desc, col, left in features:
        add_card(s7, left, 1.9, 3.7, 3.2, C_WHITE, col)
        tb = s7.shapes.add_textbox(Inches(left + 0.15), Inches(2.1), Inches(3.4), Inches(2.8))
        tf = tb.text_frame; tf.word_wrap = True
        p1 = tf.paragraphs[0]; p1.text = tit; p1.font.size = Pt(14); p1.font.bold = True; p1.font.color.rgb = col
        p2 = tf.add_paragraph(); p2.text = desc; p2.font.size = Pt(11.5); p2.font.color.rgb = C_MUTED; p2.space_before = Pt(8)

    # Banner de Despliegue Dual
    add_card(s7, 0.8, 5.4, 11.7, 1.4, C_LIGHT_BLUE, C_BLUE)
    tb_dep = s7.shapes.add_textbox(Inches(1.0), Inches(5.55), Inches(11.3), Inches(1.1))
    tfdp = tb_dep.text_frame; tfdp.word_wrap = True
    pdp1 = tfdp.paragraphs[0]
    pdp1.text = "🌐 ARQUITECTURA DE DESPLIEGUE DUAL (ONLINE + LOCAL)"
    pdp1.font.size = Pt(13); pdp1.font.bold = True; pdp1.font.color.rgb = C_NAVY
    pdp2 = tfdp.add_paragraph()
    pdp2.text = "• Despliegue Online en la Nube: Publicado en GitHub Pages (acceso multiplataforma sin instalación).\n• Dashboard Local en Python: Ejecución ágil con Streamlit (`streamlit run app_operia.py`)."
    pdp2.font.size = Pt(11); pdp2.font.color.rgb = C_TEXT; pdp2.space_before = Pt(3)

    set_notes(s7, "La plataforma está disponible tanto en Streamlit local como online en GitHub Pages. El asesor comercial no busca entre miles de filas: hace un clic en la tarjeta roja y tiene la lista de llamadas prioritarias de hoy con su argumento de venta.")

    # =========================================================================
    # SLIDE 8: BATERÍA DE PRUEBAS Y CALIDAD DE DATOS
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout); add_bg(s8)
    add_header(s8, "Rigor de Ingeniería y Calidad", "100% de Pruebas Superadas y Auditoría de Integridad de Datos")

    # Columna Izquierda: Casos Controlados
    add_card(s8, 0.8, 1.9, 5.7, 4.8, C_WHITE, C_GREEN)
    tb_c = s8.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.4))
    tfc = tb_c.text_frame; tfc.word_wrap = True
    pc_tit = tfc.paragraphs[0]
    pc_tit.text = "✅ 6 Casos Controlados Oficiales: 6/6 APROBADOS"
    pc_tit.font.size = Pt(14); pc_tit.font.bold = True; pc_tit.font.color.rgb = C_GREEN

    tests_data = [
        ("TEST-01 | Conversión COP con Descuento:", "$180,000 COP netos validados."),
        ("TEST-02 | Conversión USD con TRM:", "$1,200,000 COP indexados a $4,000 TRM."),
        ("TEST-03 | Exclusión de Ventas Anuladas:", "$0 COP computados estrictamente."),
        ("TEST-04 | Frío en Frontera 90d:", "90 días exactos evaluado como Frío."),
        ("TEST-05 | Renovación en Frontera 45d:", "45 días exactos clasificado en Renovación."),
        ("TEST-06 | Cliente Sin Datos (CLI999):", "Manejo seguro sin distorsionar la cartera.")
    ]
    for tit, res in tests_data:
        p = tfc.add_paragraph()
        p.text = f"• {tit} {res}"
        p.font.size = Pt(11); p.font.color.rgb = C_TEXT; p.space_before = Pt(6)

    # Columna Derecha: Auditoría de Calidad
    add_card(s8, 6.8, 1.9, 5.7, 4.8, C_WHITE, C_BLUE)
    tb_a = s8.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.4))
    tfa = tb_a.text_frame; tfa.word_wrap = True
    pa_tit = tfa.paragraphs[0]
    pa_tit.text = "🛡️ Auditoría de Incidencias y Tests Unitarios"
    pa_tit.font.size = Pt(14); pa_tit.font.bold = True; pa_tit.font.color.rgb = C_BLUE

    audits_data = [
        ("7 Incidencias de Calidad Aisladas:", "IDs duplicados descartados, fecha inválida 2026-02-30 rechazada, moneda EUR aislada y precios vacíos corregidos."),
        ("17 Pruebas Unitarias Automatizadas:", "Batería continua en `tests/test_reglas_operia.py` ejecutándose en 0.018 segundos sin dependencias externas."),
        ("Verificación Criptográfica SHA-256:", "Integridad garantizada de las 6 tablas maestras originales frente al manifiesto oficial del reto.")
    ]
    for tit, res in audits_data:
        p = tfa.add_paragraph()
        p.text = f"• {tit}\n  {res}"
        p.font.size = Pt(11); p.font.color.rgb = C_TEXT; p.space_before = Pt(10)

    set_notes(s8, "Sometimos el sistema a la batería de pruebas más exigente del reto: 100% de casos controlados de frontera aprobados, 7 incidencias sembradas aisladas y 17 pruebas unitarias automatizadas.")

    # =========================================================================
    # SLIDE 9: ALCANCE MOSCOW Y PLAN DE ESCALABILIDAD
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout); add_bg(s9)
    add_header(s9, "Madurez de Producto y Hoja de Ruta", "Cumplimiento del Alcance MoSCoW y Transición a Producto Final")

    # 4 Cuadrantes MoSCoW
    moscow = [
        ("MUST HAVE (Imprescindible)", "• Cruce relacional ventas + TRM + base instalada.\n• Exclusión estricta de órdenes anuladas.\n• Semáforo de priorización de llamadas comerciales.", C_GREEN, 0.8, 1.9),
        ("SHOULD HAVE (Importante)", "• Modelo de Machine Learning calibrado (Recall 90.9%).\n• Gráfica interactiva dual Ventas COP vs TRM.\n• Ficha 360° individual por cliente con historial.", C_BLUE, 6.8, 1.9),
        ("COULD HAVE (Deseable)", "• Despliegue público en la nube en GitHub Pages.\n• Descarga de listas en CSV y simulador en vivo.\n• Generación automática de informes en Word (.docx).", C_PURPLE, 0.8, 4.4),
        ("WON'T HAVE → FASE PRODUCTO", "• Conexión mediante API REST directa al ERP (SAP/Salesforce).\n• Automatización de disparadores de correos preventivos a los 45d de vencimiento de contrato.", C_MUTED, 6.8, 4.4)
    ]
    for tit, desc, col, left, top in moscow:
        add_card(s9, left, top, 5.7, 2.3, C_WHITE, col)
        tb = s9.shapes.add_textbox(Inches(left + 0.15), Inches(top + 0.15), Inches(5.4), Inches(2.0))
        tf = tb.text_frame; tf.word_wrap = True
        p1 = tf.paragraphs[0]; p1.text = tit; p1.font.size = Pt(13); p1.font.bold = True; p1.font.color.rgb = col
        p2 = tf.add_paragraph(); p2.text = desc; p2.font.size = Pt(11); p2.font.color.rgb = C_TEXT; p2.space_before = Pt(6)

    set_notes(s9, "Cumplimos el 100% de los requisitos Must, Should y Could de MoSCoW. El MVP no es un prototipo desechable: está diseñado modularmente para conectarse por API al ERP corporativo.")

    # =========================================================================
    # SLIDE 10: CONCLUSIÓN Y CIERRE
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout); add_bg(s10)
    add_header(s10, "Resumen Ejecutivo y Propuesta de Valor", "OperIA 360°: Transformando Incertidumbre en Rentabilidad Comercial")

    # 3 Pilares de Cierre
    pillars = [
        ("90.91%", "Recall Predictivo", "Captura casi la totalidad de intenciones de recompra antes de que se pierdan.", C_GREEN, 0.8),
        ("-50.81%", "Reducción de Error MAE", "Mejora demostrada con backtest frente a repetir el mes previo.", C_BLUE, 4.8),
        ("< 2 Seg", "Agilidad Operativa", "Tiempo para obtener la lista comercial priorizada de toda la cartera.", C_PURPLE, 8.8)
    ]
    for num, tit, desc, col, left in pillars:
        add_card(s10, left, 1.9, 3.7, 2.3, C_WHITE, col)
        tb = s10.shapes.add_textbox(Inches(left + 0.1), Inches(2.0), Inches(3.5), Inches(2.1))
        tf = tb.text_frame; tf.word_wrap = True
        p1 = tf.paragraphs[0]; p1.text = num; p1.font.size = Pt(36); p1.font.bold = True; p1.font.color.rgb = col; p1.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph(); p2.text = tit; p2.font.size = Pt(13); p2.font.bold = True; p2.font.color.rgb = C_NAVY; p2.alignment = PP_ALIGN.CENTER; p2.space_before = Pt(2)
        p3 = tf.add_paragraph(); p3.text = desc; p3.font.size = Pt(10.5); p3.font.color.rgb = C_MUTED; p3.alignment = PP_ALIGN.CENTER; p3.space_before = Pt(4)

    # Frase de Cierre y Links
    add_card(s10, 0.8, 4.5, 11.7, 2.3, C_NAVY, None)
    tb_c = s10.shapes.add_textbox(Inches(1.0), Inches(4.65), Inches(11.3), Inches(2.0))
    tfc = tb_c.text_frame; tfc.word_wrap = True
    
    p_quote = tfc.paragraphs[0]
    p_quote.text = "«Con OperIA, Green Services pasa de preguntarse con resignación por qué un cliente se perdió el mes pasado, a saber con exactitud a quién debe llamar hoy para asegurar la facturación de mañana.»"
    p_quote.font.size = Pt(13.5); p_quote.font.bold = True; p_quote.font.italic = True; p_quote.font.color.rgb = RGBColor(191, 219, 254)

    p_links = tfc.add_paragraph()
    p_links.text = "• Visor Online: https://calderonbrahian.github.io/OperIA-Green-Services/\n• Repositorio Oficial: https://github.com/calderonbrahian/OperIA-Green-Services\n¡Muchas Gracias! Espacio abierto para preguntas del jurado evaluador."
    p_links.font.size = Pt(11.5); p_links.font.color.rgb = C_WHITE; p_links.space_before = Pt(10)

    set_notes(s10, "OperIA demuestra cómo la IA práctica resuelve dolores reales de negocio. Los invitamos a probar la plataforma en vivo desde sus propios dispositivos con el enlace público. Muchas gracias y quedamos a su disposición.")

    # Guardar en rutas del proyecto
    base = Path(__file__).resolve().parent
    out1 = base / "Presentacion_OperIA_360.pptx"
    out2 = base / "docs" / "Presentacion_OperIA_360.pptx"
    out3 = base.parent / "Documentacion" / "Presentacion_OperIA_360.pptx"

    prs.save(str(out1))
    print(f"Creado: {out1}")
    shutil.copyfile(out1, out2)
    print(f"Creado: {out2}")
    out3.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out1, out3)
    print(f"Creado: {out3}")

if __name__ == "__main__":
    crear_presentacion()
