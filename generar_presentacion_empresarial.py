"""
generar_presentacion_empresarial.py
Genera una presentación de 3 diapositivas centrada en:
  Slide 1: La Empresa (Green Services), su modelo de negocio y su desafío operativo.
  Slide 2: La Solución Propuesta (OperIA), por qué elegir este enfoque y arquitectura de valor.
  Slide 3: El MVP y Validación Técnica/Comercial (Resultados del prototipo con datos de prueba).
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

def crear_presentacion_empresarial():
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
    # SLIDE 1: LA EMPRESA, SU MODELO DE NEGOCIO Y EL CUELLO DE BOTELLA
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout); add_bg(s1)
    add_header(s1, "Green Services and Solutions SAS · Modelo B2B", "1. Quiénes Somos, Qué Hacemos y el Desafío de Crecer", "Minuto 0:00 a 1:00 · El Negocio y el Cuello de Botella Operativo")

    # Tarjeta Izquierda: Quién es Green Services
    add_card(s1, 0.8, 1.8, 5.6, 5.1, C_WHITE, C_BLUE)
    tb_izq = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.7))
    tf_izq = tb_izq.text_frame; tf_izq.word_wrap = True

    p = tf_izq.paragraphs[0]
    p.text = "🏢 Nuestro Negocio: Soluciones para la Información"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_BLUE

    items_empresa = [
        ("Propósito Empresarial:", "Integramos infraestructura, servicios gestionados y soluciones tecnológicas para el ciclo de vida de la información corporativa."),
        ("Portafolio B2B Mixto:", "Comercializamos hardware, licencias de software multimoneda (COP/USD) y servicios de soporte técnico especializado."),
        ("El Corazón del Margen (ARR):", "La rentabilidad sostenible de la empresa depende de la renovación continua de pólizas de mantenimiento y contratos de garantía recurrente.")
    ]
    for tit, desc in items_empresa:
        pi = tf_izq.add_paragraph()
        pi.text = f"• {tit} {desc}"
        pi.font.size = Pt(11.5); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(8)

    p_badge = tf_izq.add_paragraph()
    p_badge.text = "💡 Modelo de Alto Valor: Relaciones de largo plazo donde perder un cliente corporativo cuesta hasta 7 veces más que retenerlo."
    p_badge.font.size = Pt(11.5); p_badge.font.bold = True; p_badge.font.color.rgb = C_NAVY; p_badge.space_before = Pt(12)

    # Tarjeta Derecha: El Cuello de Botella Operativo
    add_card(s1, 6.7, 1.8, 5.8, 5.1, C_WHITE, C_RED)
    tb_der = s1.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(4.7))
    tf_der = tb_der.text_frame; tf_der.word_wrap = True

    p = tf_der.paragraphs[0]
    p.text = "⚠️ El Cuello de Botella: Cuando Crecer Cuesta Control"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_RED

    items_friccion = [
        ("Ventas y Monedas Dispersas:", "Facturación en USD indexada a TRM fluctuante que dificulta consolidar rápidamente el valor real de cada cuenta."),
        ("Pólizas que Vencen en Silencio:", "Sin un control centralizado de contratos de soporte, las renovaciones se gestionan tarde, dejando a clientes desprotegidos."),
        ("Gestión Comercial Reactiva:", "El asesor vende cuando el cliente llama, no cuando el cliente necesita recomprar. Falta anticipación."),
        ("El Costo Oculto:", "Días de trabajo consumidos en cruces manuales de hojas de cálculo que retrasan la toma de decisiones directivas.")
    ]
    for tit, desc in items_friccion:
        pi = tf_der.add_paragraph()
        pi.text = f"• {tit} {desc}"
        pi.font.size = Pt(11.5); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(8)

    s1.notes_slide.notes_text_frame.text = (
        "MINUTO 1: 'Green Services and Solutions SAS es una compañía especializada en integrar soluciones para el ciclo de vida de la información corporativa. "
        "Nuestro modelo B2B combina hardware, licencias y servicios de soporte. En este negocio, la rentabilidad no está en vender una sola vez, sino en retener al cliente corporativo y renovar sus pólizas de soporte año tras año. "
        "Sin embargo, el crecimiento trajo un cuello de botella crítico: datos dispersos en distintas monedas con TRM variable, contratos que vencen sin gestión preventiva y un equipo comercial que reacciona tarde cuando el cliente ya dejó de comprar. "
        "Para resolver este dolor estructural, diseñamos OperIA 360°.'"
    )

    # =========================================================================
    # SLIDE 2: LA SOLUCIÓN PROPUESTA Y POR QUÉ ELEGIR ESTE ENFOQUE
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout); add_bg(s2)
    add_header(s2, "Propuesta de Valor e Innovación", "2. OperIA 360°: Por Qué Elegir Inteligencia Operativa", "Minuto 1:00 a 2:00 · La Solución y su Diferenciación Frente a Métodos Tradicionales")

    # Columna Izquierda: Los 3 Pilares de la Solución
    add_card(s2, 0.8, 1.8, 5.6, 5.1, C_WHITE, C_NAVY)
    tb_sol = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.7))
    tfs = tb_sol.text_frame; tfs.word_wrap = True

    p = tfs.paragraphs[0]
    p.text = "⚙️ Los 3 Pilares de OperIA 360°"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_NAVY

    pilares = [
        ("1. Cruce Relacional Automatizado:", "Integra en segundos transacciones multimoneda (COP/USD) indexadas a la TRM oficial del día, aislando órdenes anuladas."),
        ("2. Gestión de Ciclo de Vida Contractual:", "Introduce la variable Estado_Cobertura para clasificar contratos por vencer (≤ 45 días), vigentes y vencidos."),
        ("3. Motor de Machine Learning Explicable:", "Predice la propensión de compra a 30 días con algoritmos de caja blanca, sin dependencias externas complejas.")
    ]
    for tit, desc in pilares:
        pi = tfs.add_paragraph()
        pi.text = f"{tit}\n  {desc}"
        pi.font.size = Pt(11.5); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(8)

    # Columna Derecha: Por Qué Elegir Este Enfoque
    add_card(s2, 6.7, 1.8, 5.8, 5.1, C_LIGHT_BLUE, C_BLUE)
    tb_por = s2.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(4.7))
    tfp = tb_por.text_frame; tfp.word_wrap = True

    p = tfp.paragraphs[0]
    p.text = "🎯 ¿Por Qué Elegir Este Tipo de Solución?"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_BLUE

    diferenciales = [
        ("De Reactivo a Proactivo:", "En lugar de esperar a que el cliente pida una cotización, el sistema avisa al asesor semanas antes de que venza su póliza o necesite reponer consumibles."),
        ("Caja Blanca 100% Auditable:", "A diferencia de IAs opacas, cada recomendación comercial muestra exactamente qué variables pesaron en la decisión (recencia, historial, cobertura)."),
        ("Bajo Costo de Adopción e Integración:", "No requiere reemplazar el ERP ni pagar licencias astronómicas de software privativo. Corre localmente y en la nube."),
        ("Retorno Inmediato en Retención (ARR):", "Evita la fuga de cuentas estratégicas y maximiza la tasa de renovación contractual.")
    ]
    for tit, desc in diferenciales:
        pi = tfp.add_paragraph()
        pi.text = f"• {tit}\n  {desc}"
        pi.font.size = Pt(11); pi.font.color.rgb = C_NAVY; pi.space_before = Pt(6)

    s2.notes_slide.notes_text_frame.text = (
        "MINUTO 2: '¿Por qué elegir OperIA en lugar de contratar más personal o comprar un software genérico costoso? "
        "Porque OperIA resuelve exactamente la naturaleza de nuestro negocio B2B en tres pilares: "
        "Primero, automatiza el cruce relacional entre ventas, TRM diaria y base de contratos instalados. "
        "Segundo, introduce la gestión activa de coberturas, alertando renovaciones con 45 días de anticipación. "
        "Y tercero, incorpora Inteligencia Artificial explicable: una caja blanca matemática donde el director comercial sabe con precisión por qué se prioriza a cada cliente. "
        "Es una solución ligera, integrable y diseñada para transformar llamadas frías en asesoría oportuna.'"
    )

    # =========================================================================
    # SLIDE 3: EL MVP Y LOS RESULTADOS VALIDADOS
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout); add_bg(s3)
    add_header(s3, "Validación Experimental del Prototipo", "3. El MVP en Acción: Evidencia Cuantitativa y Retorno", "Minuto 2:00 a 3:00 · Demostración Técnica y Resultados del Banco de Pruebas")

    # Columna Izquierda: Resultados Cuantitativos del Modelo
    add_card(s3, 0.8, 1.8, 5.6, 5.1, C_WHITE, C_GREEN)
    tb_mvp = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.7))
    tfm = tb_mvp.text_frame; tfm.word_wrap = True

    p = tfm.paragraphs[0]
    p.text = "📊 Resultados del Prototipo (Set de Prueba)"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_GREEN

    stats_mvp = [
        ("Auditoría de Cartera (120 Cuentas):", "Clasificó automáticamente 38 frecuentes, 41 en seguimiento y detectó 41 clientes fríos críticos (≥ 90 días inactivos)."),
        ("Detección de Recompras (Recall 90.9%):", "En prueba temporal estricta superó a la intuición (90.9% vs 55.3%), capturando un 35.6% más de recompras."),
        ("Proyección Nov-2026 Validada ($216.5M COP):", "94 compradores estimados con alta propensión (P ≥ 40%)."),
        ("Prueba de Fuego Backtesting:", "Frente a repetir el mes previo, OperIA redujo el error absoluto medio (MAE) en un 50.81% ($25.8M vs $52.5M).")
    ]
    for tit, desc in stats_mvp:
        pi = tfm.add_paragraph()
        pi.text = f"• {tit}\n  {desc}"
        pi.font.size = Pt(11); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(6)

    # Columna Derecha: Demo Operativa y Cierre
    add_card(s3, 6.7, 1.8, 5.8, 5.1, C_LIGHT_BLUE, C_BLUE)
    tb_cierre = s3.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(4.7))
    tfc = tb_cierre.text_frame; tfc.word_wrap = True

    p = tfc.paragraphs[0]
    p.text = "⚡ Plataforma Operativa Lista y Cierre"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = C_BLUE

    items_cierre = [
        ("Semáforo Interactivo con Clic Directo:", "El asesor hace clic en la tarjeta roja y en < 2 segundos tiene la lista de clientes a reactivar con su guion comercial."),
        ("100% Pruebas Técnicas Superadas:", "Aprobó los 6 casos controlados oficiales, aisló 7 incidencias sembradas y cuenta con 17 pruebas unitarias continuas."),
        ("Despliegue Dual en la Nube y Local:", "Disponible online en GitHub Pages (sin instalaciones) y localmente en Streamlit.")
    ]
    for tit, desc in items_cierre:
        pi = tfc.add_paragraph()
        pi.text = f"• {tit} {desc}"
        pi.font.size = Pt(10.5); pi.font.color.rgb = C_TEXT; pi.space_before = Pt(6)

    # Cita Final
    p_quote = tfc.add_paragraph()
    p_quote.text = "«OperIA permite a Green Services pasar de preguntarse con resignación por qué un cliente se perdió el mes pasado, a saber a quién llamar hoy para asegurar el ingreso de mañana.»"
    p_quote.font.size = Pt(11); p_quote.font.bold = True; p_quote.font.italic = True; p_quote.font.color.rgb = C_NAVY; p_quote.space_before = Pt(10)

    p_link = tfc.add_paragraph()
    p_link.text = "🌐 Visor Online: https://calderonbrahian.github.io/OperIA-Green-Services/"
    p_link.font.size = Pt(10); p_link.font.bold = True; p_link.font.color.rgb = C_BLUE; p_link.space_before = Pt(4)

    s3.notes_slide.notes_text_frame.text = (
        "MINUTO 3: 'Para comprobar que este concepto funciona en el mundo real, construimos el MVP y lo validamos contra el set de datos del reto. "
        "Los resultados hablan por sí solos: identificó de inmediato 41 clientes fríos en abandono, alcanzó un Recall del 90.9% prediciendo recompras y en el Backtesting histórico demostró un 50.8% menos de error en proyección de facturación que la práctica habitual. "
        "En la demo en vivo, un asesor comercial hace un solo clic en el semáforo y en menos de dos segundos tiene su agenda priorizada con el guion exacto de contacto. "
        "Pasa el 100% de las pruebas y está desplegado públicamente en la nube. Con OperIA, Green Services pasa de lamentar clientes perdidos a saber a quién llamar hoy para asegurar la facturación de mañana. Muchas gracias.'"
    )

    base = Path(__file__).resolve().parent
    out1 = base / "Presentacion_OperIA_Pitch_Empresarial.pptx"
    out2 = base / "docs" / "Presentacion_OperIA_Pitch_Empresarial.pptx"
    out3 = base.parent / "Documentacion" / "Presentacion_OperIA_Pitch_Empresarial.pptx"

    prs.save(str(out1))
    print(f"Creado: {out1}")
    shutil.copyfile(out1, out2)
    print(f"Creado: {out2}")
    out3.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out1, out3)
    print(f"Creado: {out3}")

if __name__ == "__main__":
    crear_presentacion_empresarial()
