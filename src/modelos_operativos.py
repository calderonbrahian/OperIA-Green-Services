"""Modelos de IA y Analítica Operacional para OperIA (Hackatón EstudIA).

Incluye:
1. ModeloClasificacionComercial: semáforo por recencia + prioridad derivada de la cobertura.
2. ModeloPredictivoRecompra: regresión logística a 30 días (pesos leídos de metricas_modelo.json).
3. ModeloImpactoTRM: correlación y sensibilidad de ventas frente a la TRM de prueba.
4. construir_dataset_operia_completo: vista por cliente (120), consolidado de ventas y cifras
   que alimentan dashboards y documentos (una sola fuente de verdad: outputs/).
"""

from datetime import date, timedelta
from collections import defaultdict
from pathlib import Path
import csv
import json
import math
import statistics
from typing import Dict, List, Any, Tuple, Optional

import pandas as pd

from .config import DATA_RAW_DIR, OUTPUTS_DIR, load_config, verificar_datos_oficiales
from .data_loader import load_csv, load_trm, calcular_importe_cop

# ---------------------------------------------------------------------------
# Constantes de negocio (las umbrales numéricos viven en config/parametros.json)
# ---------------------------------------------------------------------------
COB_PROXIMA = "Próxima a Renovar (≤ 45d)"
COB_VIGENTE = "Vigente (> 45d)"
COB_VENCIDA = "Vencida (< 0d)"
COB_SIN = "Sin Cobertura"
ESTADOS_COBERTURA = (COB_PROXIMA, COB_VIGENTE, COB_VENCIDA, COB_SIN)

EST_FRIO = "Frío (Riesgo de Abandono)"
EST_FRECUENTE = "Frecuente (Activo)"
EST_SEGUIMIENTO = "Base Instalada (Seguimiento)"
EST_SIN_COMPRAS = "Sin Compras (Prospecto)"

ORDEN_PRIORIDAD = {"ALTA": 0, "MEDIA": 1, "NORMAL": 2, "BAJA": 3}
DIAS_SIN_HISTORIAL = 730  # valor de recencia usado SOLO por el modelo para clientes sin compras


# ---------------------------------------------------------------------------
# Cobertura
# ---------------------------------------------------------------------------
def calcular_estado_cobertura(instalaciones: List[Dict[str, Any]], fecha_corte: date,
                              dias_renovacion: int = 45) -> Tuple[str, Dict[str, int]]:
    """Clasifica la cobertura de un cliente a partir de sus contratos de base instalada.

    Reglas (una sola fuente de verdad para semáforo, dashboards y documentos):
      - Próxima a Renovar: algún contrato con 0 <= (fecha_fin - corte) <= dias_renovacion.
      - Vigente: no hay próximos, pero existe algún contrato con fin > corte + dias_renovacion.
      - Vencida: todos sus contratos tienen fecha_fin < corte.
      - Sin Cobertura: el cliente no tiene contratos iniciados al corte.
    """
    prox = vigente = vencida = 0
    for x in instalaciones:
        if date.fromisoformat(x["fecha_inicio"]) > fecha_corte:
            continue
        d = (date.fromisoformat(x["fecha_fin"]) - fecha_corte).days
        if d < 0:
            vencida += 1
        elif d <= dias_renovacion:
            prox += 1
        else:
            vigente += 1
    detalle = {"proximas": prox, "vigentes": vigente, "vencidas": vencida}
    if prox:
        return COB_PROXIMA, detalle
    if vigente:
        return COB_VIGENTE, detalle
    if vencida:
        return COB_VENCIDA, detalle
    return COB_SIN, detalle


# ---------------------------------------------------------------------------
# Semáforo
# ---------------------------------------------------------------------------
class ModeloClasificacionComercial:
    """Semáforo por recencia; la prioridad nace de la cobertura (no de la IA).

    Estado (por días sin compra): >= dias_frio Frío · <= dias_frecuente Frecuente · resto Seguimiento.
    Sin compras es una categoría separada.
    Prioridad: Frío = ALTA; con cobertura Próxima o Vencida = MEDIA; resto = BAJA (frecuente) / NORMAL.
    La probabilidad de la IA NO cambia la prioridad: solo ordena dentro de cada prioridad.
    """

    _ACCION_BASE = {
        EST_FRIO: "Reactivación comercial urgente",
        EST_FRECUENTE: "Fidelización y propuesta de up-selling",
        EST_SEGUIMIENTO: "Seguimiento periódico de la cuenta",
        EST_SIN_COMPRAS: "Validar si es prospecto y ofrecer primera compra",
    }
    _ACCION_COB = {
        COB_PROXIMA: "Renovar la póliza antes del vencimiento",
        COB_VENCIDA: "Regularizar la cobertura vencida",
        COB_SIN: "Ofrecer póliza de soporte",
    }

    def __init__(self, dias_frecuente: int = 30, dias_frio: int = 90, dias_renovacion: int = 45):
        self.dias_frecuente = dias_frecuente
        self.dias_frio = dias_frio
        self.dias_renovacion = dias_renovacion

    def clasificar_cliente(self, dias_sin_compra: Optional[int], transacciones: int,
                           estado_cobertura: str) -> Tuple[str, str, str, str]:
        """Retorna (estado, prioridad, acción, criterio) con el motivo en texto claro."""
        if dias_sin_compra is None:
            estado = EST_SIN_COMPRAS
            regla = "Sin compras confirmadas al corte"
        elif dias_sin_compra >= self.dias_frio:
            estado = EST_FRIO
            regla = f"{dias_sin_compra} d sin comprar (≥ {self.dias_frio} d)"
        elif dias_sin_compra <= self.dias_frecuente:
            estado = EST_FRECUENTE
            regla = f"{dias_sin_compra} d sin comprar (≤ {self.dias_frecuente} d)"
        else:
            estado = EST_SEGUIMIENTO
            regla = f"{dias_sin_compra} d sin comprar (entre {self.dias_frecuente + 1} y {self.dias_frio - 1} d)"

        requiere_cobertura = estado_cobertura in (COB_PROXIMA, COB_VENCIDA)
        if estado == EST_FRIO:
            prioridad = "ALTA"
        elif requiere_cobertura:
            prioridad = "MEDIA"
        elif estado == EST_FRECUENTE:
            prioridad = "BAJA"
        else:
            prioridad = "NORMAL"

        accion = self._ACCION_BASE[estado]
        if estado_cobertura in self._ACCION_COB:
            accion += " · " + self._ACCION_COB[estado_cobertura]
        criterio = f"Recencia: {regla} · Cobertura: {estado_cobertura} → prioridad {prioridad}"
        return estado, prioridad, accion, criterio


def ordenar_cartera(clientes: List[Dict[str, Any]], clave_prioridad="prioridad", clave_prob="prob") -> List[Dict[str, Any]]:
    """Orden operativo: prioridad (ALTA→BAJA) y, dentro de ella, mayor probabilidad de recompra primero."""
    return sorted(clientes, key=lambda c: (ORDEN_PRIORIDAD.get(c[clave_prioridad], 9), -float(c[clave_prob])))


# ---------------------------------------------------------------------------
# Modelo predictivo
# ---------------------------------------------------------------------------
def features_en_corte(fechas: List[date], corte: date) -> Tuple[int, int, int, int]:
    """(recencia, compras 30d, compras 90d, historial) usando SOLO fechas <= corte (sin fuga del futuro)."""
    ds = [d for d in fechas if d <= corte]
    rec = (corte - max(ds)).days if ds else DIAS_SIN_HISTORIAL
    f30 = sum(0 <= (corte - d).days < 30 for d in ds)
    f90 = sum(0 <= (corte - d).days < 90 for d in ds)
    return rec, f30, f90, len(ds)


class ModeloPredictivoRecompra:
    """Regresión logística: los pesos se leen de outputs/metricas_modelo.json (única fuente de verdad)."""

    CAMPOS = ["recencia_dias", "frecuencia_30d", "frecuencia_90d", "historial_n"]

    def __init__(self):
        self.w = [0.0] * 5
        self.mu = [0.0] * 4
        self.sd = [1.0] * 4
        self.threshold = 0.4
        self._entrenado = False

    @classmethod
    def desde_metricas(cls, ruta: Path = None) -> "ModeloPredictivoRecompra":
        ruta = ruta or (OUTPUTS_DIR / "metricas_modelo.json")
        with open(ruta, "r", encoding="utf-8") as f:
            m = json.load(f)
        mod = cls()
        mod.w = m["pesos_modelo"]
        mod.mu = m["medias_escalado"]
        mod.sd = m["desviaciones_escalado"]
        mod.threshold = m["umbral_seleccionado"]
        mod._entrenado = True
        return mod

    def predecir_probabilidad(self, recencia: int, f30: int, f90: int, historial: int) -> float:
        if not self._entrenado:
            raise RuntimeError("Modelo sin pesos: ejecute entrenar_y_evaluar_modelo() primero.")
        vals = [recencia, f30, f90, historial]
        z = self.w[0] + sum(k * (v - m) / s for k, v, m, s in zip(self.w[1:], vals, self.mu, self.sd))
        return 1.0 / (1.0 + math.exp(-max(-35, min(35, z))))

    def predecir_en_corte(self, fechas: List[date], corte: date) -> float:
        return self.predecir_probabilidad(*features_en_corte(fechas, corte))


# ---------------------------------------------------------------------------
# TRM
# ---------------------------------------------------------------------------
class ModeloImpactoTRM:
    """Correlación y sensibilidad de ventas en COP frente a la TRM de prueba (no oficial)."""

    @staticmethod
    def analizar_impacto(ventas_confirmadas: List[Dict[str, Any]], rates: Dict[str, float]) -> Dict[str, Any]:
        ventas_mensuales = defaultdict(float)
        trm_mensual_dias = defaultdict(list)
        for fecha_str, trm_val in rates.items():
            trm_mensual_dias[fecha_str[:7]].append(trm_val)
        for v in ventas_confirmadas:
            ventas_mensuales[v["fecha"][:7]] += calcular_importe_cop(v, rates)

        meses = sorted(set(ventas_mensuales) & set(trm_mensual_dias))
        if len(meses) < 3:
            return {"correlacion_trm_ventas": 0.0, "interpretacion": "Datos insuficientes"}

        x = [statistics.mean(trm_mensual_dias[m]) for m in meses]
        y = [ventas_mensuales[m] for m in meses]
        n = len(meses)
        mx, my = statistics.mean(x), statistics.mean(y)
        cov = sum((a - mx) * (b - my) for a, b in zip(x, y)) / (n - 1)
        sx, sy = statistics.stdev(x) or 1.0, statistics.stdev(y) or 1.0
        corr = cov / (sx * sy)
        beta = cov / (sx ** 2) if sx > 0 else 0.0
        return {
            "meses_analizados": n,
            "correlacion_trm_ventas": round(corr, 4),
            "pendiente_beta": round(beta, 2),
            "intercepto_alpha": round(my - beta * mx, 2),
            "interpretacion": (
                "Correlación positiva: a mayor TRM de prueba se incrementan las ventas facturadas en COP (por productos en USD)."
                if corr > 0.2 else "Correlación neutra o independiente de la TRM de prueba."
            )
        }


# ---------------------------------------------------------------------------
# Construcción de la vista 360 y consolidados
# ---------------------------------------------------------------------------
def construir_dataset_operia_completo() -> Tuple[Path, Path]:
    """Genera vista por cliente (120), consolidado de ventas (CSV/XLSX) y cifras del dashboard."""
    from .modelo_predictivo import entrenar_y_evaluar_modelo
    from .pronostico import proyectar_mes_siguiente, backtest_pronostico

    problemas = verificar_datos_oficiales(DATA_RAW_DIR)
    cfg = load_config()
    fecha_corte = date.fromisoformat(cfg["fecha_corte"])
    rates = load_trm(DATA_RAW_DIR)

    ventas = load_csv(DATA_RAW_DIR / "ventas.csv")
    clientes = load_csv(DATA_RAW_DIR / "clientes.csv")
    productos = load_csv(DATA_RAW_DIR / "productos.csv")
    base_instalada = load_csv(DATA_RAW_DIR / "base_instalada.csv")
    cli_map = {c["cliente_id"]: c for c in clientes}
    prod_map = {p["producto_id"]: p for p in productos}

    if not (OUTPUTS_DIR / "metricas_modelo.json").exists():
        entrenar_y_evaluar_modelo()
    modelo = ModeloPredictivoRecompra.desde_metricas()

    clasificador = ModeloClasificacionComercial(
        dias_frecuente=30, dias_frio=cfg["frio_dias_sin_compra"], dias_renovacion=cfg["renovacion_dias"])

    conf_por_cliente = defaultdict(list)
    for v in ventas:
        if v["estado"] == "Confirmada" and date.fromisoformat(v["fecha"]) <= fecha_corte:
            conf_por_cliente[v["cliente_id"]].append(v)
    inst_por_cliente = defaultdict(list)
    for bi in base_instalada:
        inst_por_cliente[bi["cliente_id"]].append(bi)

    vista = []
    for cid, c in cli_map.items():
        v_cli = conf_por_cliente[cid]
        fechas = sorted(date.fromisoformat(v["fecha"]) for v in v_cli)
        dias = (fecha_corte - fechas[-1]).days if fechas else None
        cobertura, det = calcular_estado_cobertura(inst_por_cliente[cid], fecha_corte, cfg["renovacion_dias"])
        estado, prioridad, accion, criterio = clasificador.clasificar_cliente(dias, len(v_cli), cobertura)
        prob = modelo.predecir_en_corte(fechas, fecha_corte) if fechas else 0.0
        total = sum(calcular_importe_cop(v, rates) for v in v_cli)
        ticket = total / len(v_cli) if v_cli else 0.0
        _, f30, f90, hist = features_en_corte(fechas, fecha_corte)
        vista.append({
            "Cliente_ID": cid,
            "Cliente": c.get("nombre_prueba", cid),
            "Sector": c.get("sector_prueba", "No especificado"),
            "Ciudad": c.get("ciudad_prueba", "No especificada"),
            "Estado_Cliente": estado,
            "Es_Frecuente_8ops": int(len(v_cli) >= cfg["frecuente_min_transacciones"]),
            "Es_Frio": int(dias is not None and dias >= cfg["frio_dias_sin_compra"]),
            "Estado_Cobertura": cobertura,
            "Dias_Sin_Comprar": dias if dias is not None else "",
            "Ultima_Compra": str(fechas[-1]) if fechas else "",
            "Compras_30d": f30,
            "Compras_90d": f90,
            "Transacciones": len(v_cli),
            "Prob_Recompra_Pct": round(prob * 100, 1),
            "Prioridad_Llamada": prioridad,
            "Accion_Recomendada": accion,
            "Criterio_Decision": criterio,
            "Ventas_COP": round(total, 2),
            "Ticket_Promedio_COP": round(ticket, 2),
            "Venta_Esperada_Prox_Mes_COP": round(prob * ticket, 2),
            "Productos_Historicos": "|".join(sorted({v["producto_id"] for v in v_cli})),
        })

    vista.sort(key=lambda r: (ORDEN_PRIORIDAD[r["Prioridad_Llamada"]], -r["Prob_Recompra_Pct"], r["Cliente_ID"]))
    meta = {r["Cliente_ID"]: r for r in vista}

    filas = []
    for v in ventas:
        cid, pid = v["cliente_id"], v["producto_id"]
        c_info, p_info, m = cli_map.get(cid, {}), prod_map.get(pid, {}), meta.get(cid, {})
        filas.append({
            "Venta_ID": v["venta_id"], "Fecha": v["fecha"], "Cliente_ID": cid,
            "Cliente": c_info.get("nombre_prueba", cid),
            "Sector": c_info.get("sector_prueba", "No especificado"),
            "Ciudad": c_info.get("ciudad_prueba", "No especificada"),
            "Producto_ID": pid, "Producto": p_info.get("nombre_prueba", pid),
            "Familia_Producto": p_info.get("familia_prueba", "General"),
            "Tipo_Producto": p_info.get("tipo_prueba", "Único"),
            "Cantidad": int(v["cantidad"]), "Moneda": v["moneda"],
            "Precio_Unitario": float(v["precio_unitario"]),
            "Descuento_Pct": float(v["descuento_pct"]),
            "TRM": rates.get(v["fecha"], 0.0),
            "Ventas_COP": round(calcular_importe_cop(v, rates), 2),
            "Estado_Venta": v["estado"],
            "Dias_Sin_Comprar": m.get("Dias_Sin_Comprar", ""),
            "Estado_Cliente": m.get("Estado_Cliente", ""),
            "Estado_Cobertura": m.get("Estado_Cobertura", COB_SIN),
            "Prob_Recompra_Pct": m.get("Prob_Recompra_Pct", 0.0),
            "Prioridad_Llamada": m.get("Prioridad_Llamada", "NORMAL"),
            "Accion_Recomendada": m.get("Accion_Recomendada", ""),
            "Criterio_Decision": m.get("Criterio_Decision", ""),
        })

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    vista_path = OUTPUTS_DIR / "vista_clientes_360.csv"
    with open(vista_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(vista[0].keys()))
        w.writeheader()
        w.writerows(vista)

    csv_out = OUTPUTS_DIR / "OperIA_Dataset_Consolidado.csv"
    xlsx_out = OUTPUTS_DIR / "OperIA_Dataset_Consolidado.xlsx"
    with open(csv_out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    pd.DataFrame(filas).to_excel(xlsx_out, index=False, engine="openpyxl")

    # ----- Cifras únicas para dashboards y documentos -----
    with open(OUTPUTS_DIR / "metricas_modelo.json", "r", encoding="utf-8") as f:
        metricas = json.load(f)
    proy = proyectar_mes_siguiente(vista, fecha_corte, rates, modelo, conf_por_cliente)
    bt = backtest_pronostico(clientes, ventas, rates, modelo)
    ventas_ok = [v for v in ventas if v["estado"] == "Confirmada" and date.fromisoformat(v["fecha"]) <= fecha_corte]
    cuenta = lambda k, val: sum(1 for r in vista if r[k] == val)
    cifras = {
        "fecha_corte": str(fecha_corte),
        "datos_oficiales_integros": not problemas,
        "datos_alterados": problemas,
        "clientes_total": len(vista),
        "operaciones_confirmadas": len(ventas_ok),
        "ingreso_cop_total": round(sum(calcular_importe_cop(v, rates) for v in ventas_ok), 2),
        "estados": {e: cuenta("Estado_Cliente", e) for e in (EST_FRECUENTE, EST_SEGUIMIENTO, EST_FRIO, EST_SIN_COMPRAS)},
        "coberturas": {e: cuenta("Estado_Cobertura", e) for e in ESTADOS_COBERTURA},
        "prioridades": {p: cuenta("Prioridad_Llamada", p) for p in ORDEN_PRIORIDAD},
        "frecuentes_8ops": sum(r["Es_Frecuente_8ops"] for r in vista),
        "frios_regla_oficial": sum(r["Es_Frio"] for r in vista),
        "alta_propension_40": sum(1 for r in vista if r["Prob_Recompra_Pct"] >= metricas["umbral_seleccionado"] * 100),
        "proyeccion": proy,
        "backtest_pronostico": bt,
        "metricas_modelo": metricas,
        "trm": ModeloImpactoTRM.analizar_impacto([v for v in ventas if v["estado"] == "Confirmada"], rates),
        "trm_ultima": rates[max(rates)] if rates else None,
        "advertencia": "Datos y TRM de prueba del paquete del reto; no son datos ni tasa oficial de Green Services.",
    }
    with open(OUTPUTS_DIR / "cifras_dashboard.json", "w", encoding="utf-8") as f:
        json.dump(cifras, f, ensure_ascii=False, indent=2)

    return csv_out, xlsx_out
