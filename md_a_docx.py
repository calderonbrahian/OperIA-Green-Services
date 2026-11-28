"""Convierte un Markdown simple (títulos, tablas, listas, código, citas) a Word (.docx)."""
import re
import sys
from pathlib import Path

import docx
from docx.shared import Pt, RGBColor, Inches
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

AZUL = RGBColor(30, 58, 138)


def runs(par, texto, size=None):
    """Agrega texto con **negrita** y `código` a un párrafo."""
    for parte in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", texto):
        if not parte:
            continue
        if parte.startswith("**") and parte.endswith("**"):
            r = par.add_run(parte[2:-2]); r.bold = True
        elif parte.startswith("`") and parte.endswith("`"):
            r = par.add_run(parte[1:-1]); r.font.name = "Consolas"
        else:
            r = par.add_run(parte)
        if size:
            r.font.size = Pt(size)


def sombrear(celda, color):
    celda._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>'))


def tabla(d, filas):
    filas = [f for f in filas if not re.match(r"^\|\s*:?-{2,}", f)]
    celdas = [[c.strip() for c in f.strip().strip("|").split("|")] for f in filas]
    n = max(len(c) for c in celdas)
    t = d.add_table(rows=0, cols=n)
    t.style = "Table Grid"
    for i, fila in enumerate(celdas):
        fila += [""] * (n - len(fila))
        cs = t.add_row().cells
        for j, txt in enumerate(fila):
            cs[j].paragraphs[0].text = ""
            runs(cs[j].paragraphs[0], txt.replace("\\$", "$"), 8.5)
            if i == 0:
                sombrear(cs[j], "1E3A8A")
                for r in cs[j].paragraphs[0].runs:
                    r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
            elif i % 2 == 0:
                sombrear(cs[j], "F1F5F9")
    d.add_paragraph()


def convertir(origen: Path, destino: Path):
    d = docx.Document()
    for s in d.sections:
        s.left_margin = s.right_margin = Inches(0.8)
        s.top_margin = s.bottom_margin = Inches(0.8)
    d.styles["Normal"].font.name = "Calibri"
    d.styles["Normal"].font.size = Pt(10.5)
    lineas = origen.read_text(encoding="utf-8-sig").splitlines()
    i = 0
    while i < len(lineas):
        l = lineas[i]
        if l.startswith("```"):
            i += 1; buf = []
            while i < len(lineas) and not lineas[i].startswith("```"):
                buf.append(lineas[i]); i += 1
            p = d.add_paragraph()
            r = p.add_run("\n".join(buf)); r.font.name = "Consolas"; r.font.size = Pt(8.5)
        elif l.startswith("|"):
            bloque = []
            while i < len(lineas) and lineas[i].startswith("|"):
                bloque.append(lineas[i]); i += 1
            tabla(d, bloque); continue
        elif l.startswith("#"):
            nivel = len(l) - len(l.lstrip("#"))
            h = d.add_heading(l.lstrip("# ").strip(), level=min(nivel, 3) if nivel > 1 else 0)
            for r in h.runs:
                r.font.color.rgb = AZUL
        elif l.startswith(">"):
            p = d.add_paragraph(); p.paragraph_format.left_indent = Inches(0.3)
            runs(p, l.lstrip("> ").strip()); [setattr(r, "italic", True) for r in p.runs]
        elif re.match(r"^\s*([-*]|\d+\.)\s", l):
            estilo = "List Number" if re.match(r"^\s*\d+\.", l) else "List Bullet"
            p = d.add_paragraph(style=estilo)
            runs(p, re.sub(r"^\s*([-*]|\d+\.)\s", "", l))
        elif l.strip() == "---":
            pass
        elif l.strip():
            runs(d.add_paragraph(), l.replace("\\$", "$"))
        i += 1
    destino.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(destino))


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    
    # 1. Informe de Revision y Memoria
    md1 = base / "docs" / "07_INFORME_REVISION_PLAN_PRODUCTO_Y_MEMORIA.md"
    for out in (base / "docs" / "Informe_Revision_Plan_Producto_Memoria_OperIA.docx",
                base.parent / "Documentacion" / "Informe_Revision_Plan_Producto_Memoria_OperIA.docx"):
        convertir(md1, out)
        print("Creado:", out)

    # 2. Manual Universo de Decisiones
    md2 = base / "docs" / "06_UNIVERSO_DE_DECISIONES_Y_LOGICA_DE_MODELOS.md"
    for out in (base / "docs" / "Manual_Universo_Decisiones_OperIA.docx",
                base.parent / "Documentacion" / "Manual_Universo_Decisiones_OperIA.docx"):
        convertir(md2, out)
        print("Creado:", out)
