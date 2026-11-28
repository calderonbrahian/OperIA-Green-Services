"""Proyección del mes siguiente y su backtest honesto.

Método: ingreso esperado = Σ_clientes P(compra en 30 d) × ticket promedio del cliente.
Es una estimación simple; el backtest la compara con la línea base «repetir el último mes
observado» usando el error absoluto medio (MAE), como pide la guía del reto.
"""
from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List, Any

from .data_loader import calcular_importe_cop


def _fin_de_mes(d: date) -> date:
    nxt = date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)
    return nxt - timedelta(days=1)


def proyectar_mes_siguiente(vista, fecha_corte, rates, modelo, conf_por_cliente) -> Dict[str, Any]:
    """Proyección del mes posterior al corte con ticket propio de cada cliente."""
    total = sum(r["Venta_Esperada_Prox_Mes_COP"] for r in vista)
    umbral = modelo.threshold * 100
    compradores = sum(1 for r in vista if r["Prob_Recompra_Pct"] >= umbral)
    ticket_global = (sum(r["Ventas_COP"] for r in vista) / max(1, sum(r["Transacciones"] for r in vista)))
    mes = _fin_de_mes(fecha_corte + timedelta(days=1))
    return {
        "mes_objetivo": mes.strftime("%Y-%m"),
        "ingreso_esperado_cop": round(total, 2),
        "compradores_esperados": compradores,
        "ticket_promedio_global_cop": round(ticket_global, 2),
        "metodo": "Σ P(compra 30d) × ticket promedio propio del cliente",
        "nota": "Estimación no calibrada; ver backtest_pronostico para su error frente a la línea base.",
    }


def backtest_pronostico(clientes, ventas, rates, modelo, cortes=("2026-07-31", "2026-08-31", "2026-09-30")) -> Dict[str, Any]:
    """Para cada corte pronostica el mes siguiente con solo datos ≤ corte y lo compara con lo ocurrido."""
    conf = [v for v in ventas if v["estado"] == "Confirmada"]
    cop = [(date.fromisoformat(v["fecha"]), v["cliente_id"], calcular_importe_cop(v, rates)) for v in conf]
    detalle = []
    for corte_s in cortes:
        corte = date.fromisoformat(corte_s)
        fin_obj = _fin_de_mes(corte + timedelta(days=1))
        ini_obj = corte + timedelta(days=1)
        ini_ult = date(corte.year, corte.month, 1)
        por_cli = defaultdict(list)
        for d, cid, imp in cop:
            if d <= corte:
                por_cli[cid].append((d, imp))
        pronostico = 0.0
        for c in clientes:
            if date.fromisoformat(c["fecha_alta"]) > corte:
                continue
            hist = por_cli.get(c["cliente_id"], [])
            if not hist:
                continue
            ticket = sum(i for _, i in hist) / len(hist)
            pronostico += modelo.predecir_en_corte([d for d, _ in hist], corte) * ticket
        real = sum(imp for d, _, imp in cop if ini_obj <= d <= fin_obj)
        ultimo = sum(imp for d, _, imp in cop if ini_ult <= d <= corte)
        detalle.append({
            "corte": corte_s, "mes_objetivo": fin_obj.strftime("%Y-%m"),
            "pronostico_modelo_cop": round(pronostico, 2),
            "linea_base_ultimo_mes_cop": round(ultimo, 2),
            "real_cop": round(real, 2),
        })
    mae_m = sum(abs(x["pronostico_modelo_cop"] - x["real_cop"]) for x in detalle) / len(detalle)
    mae_b = sum(abs(x["linea_base_ultimo_mes_cop"] - x["real_cop"]) for x in detalle) / len(detalle)
    return {
        "detalle": detalle,
        "mae_modelo_cop": round(mae_m, 2),
        "mae_linea_base_cop": round(mae_b, 2),
        "gana_modelo": mae_m < mae_b,
        "conclusion": ("El pronóstico del modelo supera a «repetir el último mes»." if mae_m < mae_b else
                       "El pronóstico del modelo NO supera a «repetir el último mes»: úselo solo como referencia orientativa."),
    }
