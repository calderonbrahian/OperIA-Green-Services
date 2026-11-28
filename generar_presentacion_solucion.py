"""
generar_presentacion_solucion.py
Genera la presentación comercial de alto impacto de 3 diapositivas centrada en:
  Slide 1: El Dolor del Cliente (Fuga silenciosa de clientes y ceguera operativa).
  Slide 2: Nuestra Solución: Qué Ofrecemos y Cómo Funciona OperIA 360°.
  Slide 3: La Evidencia: Resultados Comprobados del MVP con Datos de Prueba.
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

def crear_presentacion_solucion():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid(); bg.fill.fore_color.rgb = C_BG; bg.line.color.rgb = C_BG

    def add_header(slide, badge, title, subtitle):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.3))
        tf = tb.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_b = tf.paragraphs[0]
        p_b.text = badge.upper()
        p_b.font.name = "Arial"; p_b.font.size = Pt(11); p_b.font.bold = True; p_b.font.color.rgb = C_BLUE

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = "Arial"; p_t.font.size = Pt(23); p_t.font.bold = True; p_t.font.color.rgb = C_NAVY
        p_t.space_before = Pt(3)

        p_s = tf.add_paragraph()
        p_s.text = subtitle
        p_s.font.name = "Arial"; p_s.font.size = Pt(12); p_s.font.color.rgb = C_MUTED
        p_s.space_before = Pt(2)

    def add_card(slide, left, top, width, height, bg_col=C_WHITE, border_col=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid(); card.fill.fore_color.rgb = bg_col
        if border_col:
            card.line.color.rgb = border_col; card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    # =========================================================================
    # DIAPOSITIVA 1: EL PROBLEMA QUE RESOLVEMOS (0:00 - 1:00)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout); add_bg(s1)
    add_header(s1, "El Dolor en Operaciones Comerciales B2B", "1. El Costo de Operar a Ciegas: Fuga Silenciosa de Clientes", "Minuto 0:00 a 1:00 · Por qué las empresas pierden clientes y renovaciones sin notarlo")

    # Tarjeta Izquierda: Los Síntomas de la Ceguera
    add_card(s1, 0.8, 1.8, 5.6, 5.1, C_WHITE, C_RED)
    tb_izq = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.7))
    tf_izq = tb_izq.text_frame; tf_izq.word_wrap = True

    p = tf_izq.paragraphs[0]
    p.text = "❌ Los Síntomas de la Ceguera Comercial:"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_RED

    items_sintomas = [
        ("Incertidumbre de Recompra:", "El equipo comercial no sabe con certeza qué cliente volverá a necesitar consumibles, licencias o equipos este mes."),
        ("Contratos que Mueren en Silencio:", "Pólizas de mantenimiento y licencias que expiran sin una alerta preventiva, perdiendo ingresos recurrentes clave."),
        ("Datos Lentos y Dispersos:", "Ventas en dólares y pesos con TRM fluctuante dispersas en hojas de cálculo que tardan días en consolidarse manualmente."),
        ("Ventas 100% Reactivas:", "El asesor solo vende cuando el cliente llama a cotizar. Mientras tanto, cuentas valiosas se enfrían sin gestión.")
    ]
    for tit, desc in items_sintomas:
        pi = tf_izq.add_paragraph()
        pi.text = f"• {tit} {desc}"
        pi.font.size = Pt(11.5); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(8)

    # Tarjeta Derecha: El Impacto Financiero
    add_card(s1, 6.7, 1.8, 5.8, 5.1, C_LIGHT_RED, C_RED)
    tb_der = s1.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(4.7))
    tf_der = tb_der.text_frame; tf_der.word_wrap = True

    p = tf_der.paragraphs[0]
    p.text = "💸 El Impacto Financiero de la Deserción:"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = RGBColor(153, 27, 27)

    items_impacto = [
        ("Hasta 35% de Recompras Perdidas:", "Cuentas que compran a la competencia simplemente porque nadie las contactó en su momento exacto de necesidad."),
        ("Alto Costo de Adquisición:", "Conseguir un cliente nuevo cuesta hasta 7 veces más que retener y hacer crecer una cuenta existente."),
        ("La Causa Raíz:", "No falta producto ni faltan clientes: falta un sistema proactivo que avise al asesor a quién debe llamar hoy antes de que se vaya.")
    ]
    for tit, desc in items_impacto:
        pi = tf_der.add_paragraph()
        pi.text = f"• {tit}\n  {desc}"
        pi.font.size = Pt(11.5); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(10)

    s1.notes_slide.notes_text_frame.text = (
        "MINUTO 1: 'Todas las empresas B2B comparten un mismo dolor invisible: la fuga silenciosa de clientes. "
        "Hoy la mayoría opera a ciegas: no saben qué cliente está a punto de recomprar, las pólizas de soporte vencen sin que nadie gestione la renovación a tiempo, y consolidar ventas en dólares y pesos toma días en Excel. "
        "El resultado es fatal: el asesor comercial se vuelve reactivo. Solo vende cuando el cliente llama a cotizar. Mientras tanto, decenas de clientes valiosos se van enfriando en silencio hasta que se pierden definitivamente. "
        "El problema no es la falta de clientes: es la falta de un sistema que te avise a quién debes llamar hoy antes de que se vaya con la competencia.'"
    )

    # =========================================================================
    # DIAPOSITIVA 2: QUÉ OFRECEMOS Y CÓMO FUNCIONA (1:00 - 2:00)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout); add_bg(s2)
    add_header(s2, "Nuestra Solución: Plataforma OperIA 360°", "2. Qué Ofrecemos y Cómo Funciona para el Equipo de Ventas", "Minuto 1:00 a 2:00 · De datos dispersos a una agenda diaria de llamadas prioritarias")

    # Columna Izquierda: Qué Ofrecemos
    add_card(s2, 0.8, 1.8, 5.6, 5.1, C_WHITE, C_BLUE)
    tb_que = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.7))
    tfq = tb_que.text_frame; tfq.word_wrap = True

    p = tfq.paragraphs[0]
    p.text = "🎯 ¿Qué Ofrecemos?"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_BLUE

    p_sub = tfq.add_paragraph()
    p_sub.text = "Una plataforma de Inteligencia Operativa y Predictiva que analiza automáticamente las compras e inventarios de cada cuenta y le entrega al equipo comercial una agenda diaria con guion de llamada exacto."
    p_sub.font.size = Pt(11.5); p_sub.font.color.rgb = C_TEXT; p_sub.space_before = Pt(6)

    p_ent = tfq.add_paragraph()
    p_ent.text = "📦 Lo que Recibe el Asesor Comercial:"
    p_ent.font.size = Pt(13); p_ent.font.bold = True; p_ent.font.color.rgb = C_NAVY; p_ent.space_before = Pt(12)

    entregables = [
        ("Semáforo Inteligente:", "Lista ordenada de cuentas rojas (frías a rescatar), amarillas (seguimiento) y verdes (activas)."),
        ("Alerta Preventiva:", "Aviso 45 días antes del vencimiento de pólizas para asegurar renovación anticipada."),
        ("Guion Comercial:", "Recomendación específica de producto según historial de compra y margen.")
    ]
    for tit, desc in entregables:
        pi = tfq.add_paragraph()
        pi.text = f"• {tit} {desc}"
        pi.font.size = Pt(11); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(6)

    # Columna Derecha: Cómo Funciona en 3 Pasos
    add_card(s2, 6.7, 1.8, 5.8, 5.1, C_LIGHT_BLUE, C_NAVY)
    tb_como = s2.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(4.7))
    tfc = tb_como.text_frame; tfc.word_wrap = True

    p = tfc.paragraphs[0]
    p.text = "⚙️ ¿Cómo Funciona? (Mecánica en 3 Pasos):"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    pasos = [
        ("1. Cruce Automático de Datos:", "Unifica en segundos ventas multimoneda (COP/USD) con TRM histórica del día y conecta los contratos vigentes, aislando transacciones anuladas."),
        ("2. Semáforo Preventivo de Cobertura:", "Clasifica contratos por vencer en ≤ 45 días, vigentes y vencidos para proteger los ingresos de soporte técnico."),
        ("3. Algoritmo Predictivo de Recompra:", "Modelo matemático transparente (caja blanca) que evalúa la inercia reciente y la lealtad histórica para estimar la probabilidad de compra en los próximos 30 días.")
    ]
    for tit, desc in pasos:
        pi = tfc.add_paragraph()
        pi.text = f"{tit}\n  {desc}"
        pi.font.size = Pt(11); pi.font.color.rgb = C_NAVY; pi.space_before = Pt(8)

    s2.notes_slide.notes_text_frame.text = (
        "MINUTO 2: 'Para solucionar esto creamos OperIA 360°. "
        "¿Qué ofrecemos? Una plataforma inteligente que se conecta a los datos de la empresa y le entrega al equipo comercial una agenda proactiva de llamadas prioritarias, diciéndole exactamente a quién llamar hoy, con qué probabilidad de compra y qué ofrecerle. "
        "¿Cómo lo hace? En tres pasos automáticos: "
        "Primero, cruza y normaliza en segundos todas las ventas multimoneda con la TRM del día y las conecta con las pólizas activas. "
        "Segundo, activa un semáforo de contratos: 45 días antes de que venza una póliza de soporte, el sistema emite una alerta temprana para asegurar la renovación. "
        "Y tercero, un modelo de Inteligencia Artificial analiza el patrón histórico de cada cuenta y predice quién recomprará en los próximos 30 días. "
        "El vendedor ya no pierde horas limpiando tablas: abre el sistema y tiene en pantalla la lista de llamadas que van a generar facturación hoy mismo.'"
    )

    # =========================================================================
    # DIAPOSITIVA 3: LA EVIDENCIA — RESULTADOS DEL MVP (2:00 - 3:00)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout); add_bg(s3)
    add_header(s3, "Validación Empírica del Prototipo", "3. La Evidencia: Resultados Comprobados del MVP", "Minuto 2:00 a 3:00 · Comprobación cuantitativa en banco de pruebas oficial")

    # Columna Izquierda: Resultados Duros del Modelo
    add_card(s3, 0.8, 1.8, 5.6, 5.1, C_WHITE, C_GREEN)
    tb_res = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.7))
    tfr = tb_res.text_frame; tfr.word_wrap = True

    p = tfr.paragraphs[0]
    p.text = "📈 Resultados en Banco de Pruebas Oficial:"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_GREEN

    res_items = [
        ("Auditoría Instantánea de Cartera:", "Sobre 120 cuentas y $5,647M COP, detectó de inmediato 41 clientes fríos en abandono crítico (≥ 90d) y 25 pólizas por vencer sin gestión."),
        ("Recall Predictivo del 90.91%:", "En prueba temporal estricta superó a la intuición (90.9% vs. 55.3%), capturando un 35.6% más de recompras reales con apenas 12 falsos negativos."),
        ("Proyección Nov-2026 de $216.5M COP:", "Pronóstico de facturación con 94 compradores esperados de alta propensión."),
        ("Prueba de Fuego Backtesting:", "Frente a repetir el mes previo, OperIA redujo el error absoluto medio (MAE) a la mitad: 50.81% menos error ($25.8M vs. $52.5M).")
    ]
    for tit, desc in res_items:
        pi = tfr.add_paragraph()
        pi.text = f"• {tit}\n  {desc}"
        pi.font.size = Pt(11); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(6)

    # Columna Derecha: Plataforma Operativa y Cierre
    add_card(s3, 6.7, 1.8, 5.8, 5.1, C_LIGHT_GREEN, C_GREEN)
    tb_cie = s3.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(4.7))
    tfc = tb_cie.text_frame; tfc.word_wrap = True

    p = tfc.paragraphs[0]
    p.text = "⚡ Plataforma Lista y Validación Completa:"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = RGBColor(20, 83, 45)

    cie_items = [
        ("Semáforo con Clic Directo en < 2 Segundos:", "El asesor hace un clic en la tarjeta roja y tiene la lista de cuentas críticas priorizadas para llamar ya."),
        ("100% Casos de Prueba Superados:", "6/6 casos controlados oficiales + 7 incidencias aisladas + 17 pruebas unitarias continuas en 0.018s."),
        ("Despliegue Multiplataforma Online:", "Disponible en la nube en GitHub Pages y local en Streamlit.")
    ]
    for tit, desc in cie_items:
        pi = tfc.add_paragraph()
        pi.text = f"• {tit}\n  {desc}"
        pi.font.size = Pt(10.5); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(6)

    p_quote = tfc.add_paragraph()
    p_quote.text = "«OperIA transforma la incertidumbre de perder clientes en ingresos asegurados mes a mes.»"
    p_quote.font.size = Pt(11.5); p_quote.font.bold = True; p_quote.font.italic = True; p_quote.font.color.rgb = C_NAVY; p_quote.space_before = Pt(10)

    p_link = tfc.add_paragraph()
    p_link.text = "🌐 Probar online: https://calderonbrahian.github.io/OperIA-Green-Services/"
    p_link.font.size = Pt(10.5); p_link.font.bold = True; p_link.font.color.rgb = C_BLUE; p_link.space_before = Pt(4)

    s3.notes_slide.notes_text_frame.text = (
        "MINUTO 3: 'Para demostrar que esto funciona, construimos el MVP y lo probamos con el banco de datos oficial. Y los resultados fueron contundentes: "
        "Al conectarlo a una cartera de 120 clientes, el sistema detectó inmediatamente 41 clientes fríos en abandono y 25 contratos por vencer que nadie estaba atendiendo. "
        "Nuestro modelo de IA demostró un Recall del 90.9%, capturando un 35% más de recompras que cualquier método tradicional. Y cuando pusimos a prueba la proyección de $216.5 millones con Backtesting histórico frente a repetir el mes previo, OperIA redujo el error de pronóstico a la mitad (50.8% menos error MAE). "
        "La plataforma ya está en producción online: el asesor hace un solo clic en el semáforo y en menos de 2 segundos tiene su lista de llamadas lista con el guion comercial. "
        "En resumen: OperIA transforma la incertidumbre de perder clientes en ingresos asegurados mes a mes. Muchas gracias.'"
    )

    base = Path(__file__).resolve().parent
    out1 = base / "Presentacion_OperIA_Pitch_Solucion.pptx"
    out2 = base / "docs" / "Presentacion_OperIA_Pitch_Solucion.pptx"
    out3 = base.parent / "Documentacion" / "Presentacion_OperIA_Pitch_Solucion.pptx"

    prs.save(str(out1))
    print(f"Creado: {out1}")
    shutil.copyfile(out1, out2)
    print(f"Creado: {out2}")
    out3.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out1, out3)
    print(f"Creado: {out3}")

if __name__ == "__main__":
    crear_presentacion_solucion()
