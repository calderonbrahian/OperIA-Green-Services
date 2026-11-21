"""Cálculo de indicadores operativos y visión 360 del cliente."""
from datetime import date
from collections import defaultdict
import csv
import json
from typing import Dict, Any, Tuple, List

from .config import DATA_RAW_DIR, OUTPUTS_DIR, load_config
from .data_loader import load_csv, load_trm, calcular_importe_cop

def procesar_operaciones() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Integra ventas, clientes y base instalada para generar indicadores operativos."""
    cfg = load_config()
    fecha_corte = date.fromisoformat(cfg["fecha_corte"])
    rates = load_trm(DATA_RAW_DIR)

    ventas = load_csv(DATA_RAW_DIR / "ventas.csv")
    clientes = load_csv(DATA_RAW_DIR / "clientes.csv")
    base_instalada = load_csv(DATA_RAW_DIR / "base_instalada.csv")

    # Agrupar ventas confirmadas hasta la fecha de corte
    ventas_por_cliente = defaultdict(list)
    for v in ventas:
        if v["estado"] == "Confirmada" and date.fromisoformat(v["fecha"]) <= fecha_corte:
            ventas_por_cliente[v["cliente_id"]].append(v)

    # Agrupar base instalada vigente o iniciada hasta la fecha de corte
    instalaciones_por_cliente = defaultdict(list)
    for bi in base_instalada:
        if date.fromisoformat(bi["fecha_inicio"]) <= fecha_corte:
            instalaciones_por_cliente[bi["cliente_id"]].append(bi)

    resumen_clientes = []
    for c in clientes:
        cid = c["cliente_id"]
        v_cli = ventas_por_cliente[cid]
        fechas_ventas = sorted(date.fromisoformat(v["fecha"]) for v in v_cli)
        
        ultima_compra_str = str(fechas_ventas[-1]) if fechas_ventas else ""
        dias_sin_compra = (fecha_corte - fechas_ventas[-1]).days if fechas_ventas else None
        
        es_frecuente = len(v_cli) >= cfg["frecuente_min_transacciones"]
        es_frio = (dias_sin_compra is not None) and (dias_sin_compra >= cfg["frio_dias_sin_compra"])
        sin_compras = len(v_cli) == 0

        instals = instalaciones_por_cliente[cid]
        renovaciones_proximas = sum(
            0 <= (date.fromisoformat(x["fecha_fin"]) - fecha_corte).days <= cfg["renovacion_dias"]
            for x in instals
        )
        coberturas_vencidas = sum(
            date.fromisoformat(x["fecha_fin"]) < fecha_corte
            for x in instals
        )

        # Regla de asignación de prioridad transparente
        if es_frio:
            prioridad = "Revisar cliente frío"
        elif renovaciones_proximas > 0 or coberturas_vencidas > 0:
            prioridad = "Revisar cobertura"
        else:
            prioridad = "Seguimiento habitual"

        total_ingreso = sum(calcular_importe_cop(v, rates) for v in v_cli)
        productos_hist = sorted({v["producto_id"] for v in v_cli})

        resumen_clientes.append({
            "cliente_id": cid,
            "nombre": c.get("nombre_prueba", ""),
            "sector": c.get("sector_prueba", ""),
            "ciudad": c.get("ciudad_prueba", ""),
            "fecha_corte": str(fecha_corte),
            "transacciones_confirmadas": len(v_cli),
            "ingreso_cop": round(total_ingreso, 2),
            "ultima_compra": ultima_compra_str,
            "dias_sin_compra": dias_sin_compra if dias_sin_compra is not None else "",
            "frecuente": es_frecuente,
            "frio": es_frio,
            "sin_compras": sin_compras,
            "renovaciones_proximas": renovaciones_proximas,
            "coberturas_vencidas": coberturas_vencidas,
            "productos_historicos": "|".join(productos_hist),
            "prioridad_regla": prioridad,
            "naturaleza": "Resultado de prueba; línea base calculada"
        })

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Exportar resumen_clientes.csv
    csv_path = OUTPUTS_DIR / "resumen_clientes.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(resumen_clientes[0].keys()))
        writer.writeheader()
        writer.writerows(resumen_clientes)

    # Resumen ejecutivo en JSON
    kpis = {
        "fecha_corte": str(fecha_corte),
        "total_clientes": len(resumen_clientes),
        "clientes_con_compras": sum(1 for x in resumen_clientes if not x["sin_compras"]),
        "clientes_sin_compras": sum(1 for x in resumen_clientes if x["sin_compras"]),
        "transacciones_confirmadas": sum(x["transacciones_confirmadas"] for x in resumen_clientes),
        "ingreso_total_cop": round(sum(x["ingreso_cop"] for x in resumen_clientes), 2),
        "clientes_frecuentes": sum(1 for x in resumen_clientes if x["frecuente"]),
        "clientes_frios": sum(1 for x in resumen_clientes if x["frio"]),
        "clientes_con_renovaciones_proximas": sum(1 for x in resumen_clientes if x["renovaciones_proximas"] > 0),
        "clientes_con_coberturas_vencidas": sum(1 for x in resumen_clientes if x["coberturas_vencidas"] > 0),
        "nota": "Cálculo basado en reglas y parámetros de prueba."
    }

    json_path = OUTPUTS_DIR / "resumen_general.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(kpis, f, ensure_ascii=False, indent=2)

    return resumen_clientes, kpis
