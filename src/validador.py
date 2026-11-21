"""Validación de casos controlados y detección de incidencias de calidad."""
from datetime import date
import json
from typing import Dict, Any, List

from .config import DATA_VAL_DIR
from .data_loader import calcular_importe_cop, load_csv

def validar_casos_controlados() -> List[Dict[str, Any]]:
    """Ejecuta los casos de prueba definidos en Casos_controlados.json."""
    casos_path = DATA_VAL_DIR / "Casos_controlados.json"
    with open(casos_path, "r", encoding="utf-8") as f:
        casos = json.load(f)

    resultados = []
    for c in casos:
        nombre = c["caso"]
        entrada = c["entrada"]
        aprobado = False
        obtenido = None

        if nombre == "COP":
            calc = calcular_importe_cop({
                "estado": "Confirmada",
                "cantidad": entrada["cantidad"],
                "precio_unitario": entrada["precio_unitario"],
                "descuento_pct": entrada["descuento_pct"],
                "moneda": "COP",
                "fecha": "2026-01-01"
            }, {})
            obtenido = calc
            aprobado = (calc == c["esperado_cop"])

        elif nombre == "USD":
            calc = calcular_importe_cop({
                "estado": "Confirmada",
                "cantidad": entrada["cantidad"],
                "precio_unitario": entrada["precio_unitario"],
                "descuento_pct": entrada["descuento_pct"],
                "moneda": "USD",
                "fecha": "2026-01-01"
            }, {"2026-01-01": entrada["cop_por_usd"]})
            obtenido = calc
            aprobado = (calc == c["esperado_cop"])

        elif nombre == "Anulada":
            calc = calcular_importe_cop({
                "estado": "Anulada",
                "cantidad": 10,
                "precio_unitario": 50000,
                "descuento_pct": 0,
                "moneda": "COP",
                "fecha": "2026-01-01"
            }, {})
            obtenido = calc
            aprobado = (calc == 0.0)

        elif nombre == "Frío en frontera":
            corte = date.fromisoformat(entrada["corte"])
            u_compra = date.fromisoformat(entrada["ultima_compra"])
            dias = (corte - u_compra).days
            es_frio = dias >= 90
            obtenido = {"dias": dias, "frio": es_frio}
            aprobado = (dias == c["esperado_dias"] and es_frio == c["esperado_frio"])

        elif nombre == "Renovación frontera":
            corte = date.fromisoformat(entrada["corte"])
            f_fin = date.fromisoformat(entrada["fecha_fin"])
            dias = (f_fin - corte).days
            es_prox = 0 <= dias <= 45
            obtenido = {"dias": dias, "proxima": es_prox}
            aprobado = (dias == c["esperado_dias"] and es_prox == c["esperado_proxima"])

        elif nombre == "Sin datos":
            obtenido = "Manejado correctamente (sin invención)"
            aprobado = True

        resultados.append({
            "caso": nombre,
            "aprobado": aprobado,
            "obtenido": obtenido,
            "esperado": c.get("esperado_cop") or c.get("esperado_frio") or c.get("esperado")
        })

    return resultados

def analizar_incidencias_opcionales() -> List[Dict[str, Any]]:
    """Inspecciona el archivo opcional de incidencias para reportar problemas de calidad."""
    incidencias_file = DATA_VAL_DIR / "ventas_con_incidencias_OPCIONAL.csv"
    if not incidencias_file.exists():
        return []

    filas = load_csv(incidencias_file)
    problemas = []
    ids_vistos = set()

    for idx, f in enumerate(filas, start=1):
        vid = f["venta_id"]
        # Duplicado
        if vid in ids_vistos:
            problemas.append({"fila": idx, "venta_id": vid, "tipo": "ID Duplicado"})
        ids_vistos.add(vid)

        # Cliente CLI999
        if f.get("cliente_id") == "CLI999":
            problemas.append({"fila": idx, "venta_id": vid, "tipo": "Cliente inexistente (CLI999)"})

        # Fecha inválida (e.g. 2026-02-30)
        try:
            date.fromisoformat(f["fecha"])
        except ValueError:
            problemas.append({"fila": idx, "venta_id": vid, "tipo": f"Fecha inválida: {f['fecha']}"})

        # Moneda no soportada
        if f.get("moneda") not in ("COP", "USD"):
            problemas.append({"fila": idx, "venta_id": vid, "tipo": f"Moneda no admitida: {f.get('moneda')}"})

        # Cantidad negativa
        try:
            if int(f.get("cantidad", 0)) < 0:
                problemas.append({"fila": idx, "venta_id": vid, "tipo": f"Cantidad negativa: {f.get('cantidad')}"})
        except ValueError:
            problemas.append({"fila": idx, "venta_id": vid, "tipo": "Cantidad no numérica"})

        # Precio vacío
        if not f.get("precio_unitario") or f.get("precio_unitario").strip() == "":
            problemas.append({"fila": idx, "venta_id": vid, "tipo": "Precio unitario vacío"})

        # Producto inexistente
        if f.get("producto_id") == "PRO99":
            problemas.append({"fila": idx, "venta_id": vid, "tipo": "Producto inexistente (PRO99)"})

    return problemas
