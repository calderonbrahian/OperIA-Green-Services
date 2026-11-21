"""Modelos de IA y Analítica Operacional para OperIA (Hackatón EstudIA).

Incluye:
1. ModeloClasificacionComercial: Semáforo inteligente (Verde/Amarillo/Rojo) y alertas de abandono.
2. ModeloPredictivoRecompra: Estimación de probabilidad de recompra a 30 días.
3. ModeloImpactoTRM: Correlación y análisis de sensibilidad de ventas frente a la TRM.
4. Exportador del Dataset Consolidado OperIA (CSV y Excel XLSX).
"""

from datetime import date, timedelta
from collections import defaultdict
from pathlib import Path
import csv
import json
import math
import statistics
from typing import Dict, List, Any, Tuple

import pandas as pd

from .config import DATA_RAW_DIR, OUTPUTS_DIR, load_config
from .data_loader import load_csv, load_trm, calcular_importe_cop

class ModeloClasificacionComercial:
    """Clasificador de clientes y generador de semáforo de llamadas prioritarias."""

    def __init__(self, dias_frecuente: int = 30, dias_frio: int = 90, dias_renovacion: int = 45):
        self.dias_frecuente = dias_frecuente
        self.dias_frio = dias_frio
        self.dias_renovacion = dias_renovacion

    def clasificar_cliente(self, dias_sin_compra: Optional[int], transacciones: int,
                            renovaciones_proximas: int, coberturas_vencidas: int) -> Tuple[str, str, str, str]:
        """Determina el estado del semáforo, prioridad de contacto y criterio exacto de decisión.
        
        Reglas estrictas de negocio:
        1. Recencia >= 90 días (o sin compras) -> 🔴 Frío (Riesgo de Abandono) | Prioridad ALTA
        2. Recencia <= 30 días -> 🟢 Frecuente (Activo) | Prioridad MEDIA (si vence póliza) o BAJA (al día)
        3. Recencia 31 a 89 días -> 🟡 Base Instalada (Seguimiento) | Prioridad MEDIA (si vence póliza) o NORMAL
        """
        if dias_sin_compra is None:
            return (
                "Frío (Riesgo de Abandono)",
                "ALTA",
                "Invitar a primera compra / Prospección inicial",
                "Sin historial transaccional previo (Cuenta no activada)"
            )

        # 1. Regla estricta de abandono (Frío >= 90 días)
        if dias_sin_compra >= self.dias_frio:
            estado = "Frío (Riesgo de Abandono)"
            prioridad = "ALTA"
            accion = "Campaña de reactivación comercial urgente (Llamada prioritaria)"
            criterio = f"Recencia crítica: {dias_sin_compra} días sin comprar (≥ {self.dias_frio}d)"

        # 2. Regla estricta de cliente frecuente / activo (Última compra <= 30 días)
        elif dias_sin_compra <= self.dias_frecuente:
            estado = "Frecuente (Activo)"
            if renovaciones_proximas > 0 or coberturas_vencidas > 0:
                prioridad = "MEDIA"
                accion = "Fidelización activa y renovación anticipada de póliza"
                criterio = f"Compra reciente ({dias_sin_compra}d ≤ {self.dias_frecuente}d) + Contrato por renovar (≤ {self.dias_renovacion}d)"
            else:
                prioridad = "BAJA"
                accion = "Fidelización y propuesta de up-selling / servicios adicionales"
                criterio = f"Compra reciente ({dias_sin_compra}d ≤ {self.dias_frecuente}d) — Cuenta sana y al día"

        # 3. Regla estricta de seguimiento intermedio (31 a 89 días)
        else:
            estado = "Base Instalada (Seguimiento)"
            if renovaciones_proximas > 0 or coberturas_vencidas > 0:
                prioridad = "MEDIA"
                accion = "Contactar para renovación de póliza / licencia de cobertura"
                criterio = f"Recencia intermedia ({dias_sin_compra}d) + Contrato por vencer en ≤ {self.dias_renovacion}d"
            else:
                prioridad = "NORMAL"
                accion = "Seguimiento periódico de cuenta y nuevas necesidades"
                criterio = f"Recencia intermedia ({dias_sin_compra}d) sin vencimiento inminente"

        return estado, prioridad, accion, criterio

class ModeloPredictivoRecompra:
    """Regresión logística calibrada temporalmente para predicción de probabilidad a 30 días."""

    def __init__(self):
        self.w = [0.0] * 5
        self.mu = [0.0] * 4
        self.sd = [1.0] * 4
        self.fields = ["recencia_dias", "frecuencia_30d", "frecuencia_90d", "historial_n"]
        self.threshold = 0.4
        self._entrenado = False

    def entrenar(self, ventas: List[Dict[str, Any]], clientes: List[Dict[str, Any]]):
        hist = defaultdict(list)
        for v in ventas:
            if v["estado"] == "Confirmada":
                hist[v["cliente_id"]].append(date.fromisoformat(v["fecha"]))

        rows = []
        for year in [2025, 2026]:
            for month in range(1, 13):
                nxt = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
                cut = nxt - timedelta(days=1)
                if cut < date(2025, 3, 31) or cut > date(2026, 9, 30):
                    continue
                for c in clientes:
                    if date.fromisoformat(c["fecha_alta"]) > cut:
                        continue
                    ds = [d for d in hist[c["cliente_id"]] if d <= cut]
                    rec = (cut - max(ds)).days if ds else 730
                    f30 = sum(0 <= (cut - d).days < 30 for d in ds)
                    f90 = sum(0 <= (cut - d).days < 90 for d in ds)
                    label = int(any(cut < d <= cut + timedelta(days=30) for d in hist[c["cliente_id"]]))
                    rows.append({
                        "recencia_dias": rec,
                        "frecuencia_30d": f30,
                        "frecuencia_90d": f90,
                        "historial_n": len(ds),
                        "corte": str(cut),
                        "compra_30d": label
                    })

        train = [x for x in rows if x["corte"] <= "2026-04-30"]
        self.mu = [statistics.mean(x[f] for x in train) for f in self.fields]
        self.sd = [statistics.pstdev(x[f] for x in train) or 1.0 for f in self.fields]

        def vec(x):
            return [1.0] + [(x[f] - m) / s for f, m, s in zip(self.fields, self.mu, self.sd)]

        def sig(z):
            return 1.0 / (1.0 + math.exp(-max(-35, min(35, z))))

        w = [0.0] * 5
        lr = 0.1
        for _ in range(600):
            g = [0.0] * 5
            for row in train:
                a = vec(row)
                pred = sig(sum(k * v for k, v in zip(w, a)))
                err = pred - row["compra_30d"]
                for j in range(5):
                    g[j] += err * a[j]
            w = [v - lr * (g[j] / len(train) + (0.001 * v if j else 0.0)) for j, v in enumerate(w)]
        self.w = w
        self._entrenado = True

    def predecir_probabilidad(self, recencia: int, f30: int, f90: int, historial: int) -> float:
        if not self._entrenado:
            return 0.5
        vals = [recencia, f30, f90, historial]
        vec = [1.0] + [(v - m) / s for v, m, s in zip(vals, self.mu, self.sd)]
        z = sum(k * v for k, v in zip(self.w, vec))
        return 1.0 / (1.0 + math.exp(-max(-35, min(35, z))))

class ModeloImpactoTRM:
    """Modelo de correlación y análisis de elasticidad TRM vs Ventas en COP."""

    @staticmethod
    def analizar_impacto(ventas_confirmadas: List[Dict[str, Any]], rates: Dict[str, float]) -> Dict[str, Any]:
        ventas_mensuales = defaultdict(lambda: {"ventas_cop": 0.0, "trm_suma": 0.0, "conteo_dias": 0})
        trm_mensual_dias = defaultdict(list)

        for fecha_str, trm_val in rates.items():
            mes = fecha_str[:7]
            trm_mensual_dias[mes].append(trm_val)

        for v in ventas_confirmadas:
            mes = v["fecha"][:7]
            imp = calcular_importe_cop(v, rates)
            ventas_mensuales[mes]["ventas_cop"] += imp

        meses = sorted(set(ventas_mensuales.keys()) & set(trm_mensual_dias.keys()))
        if len(meses) < 3:
            return {"correlacion": 0.0, "tendencia": "Datos insuficientes"}

        x = [statistics.mean(trm_mensual_dias[m]) for m in meses]
        y = [ventas_mensuales[m]["ventas_cop"] for m in meses]

        # Coeficiente de correlación de Pearson
        n = len(meses)
        mx = statistics.mean(x)
        my = statistics.mean(y)
        cov = sum((a - mx) * (b - my) for a, b in zip(x, y)) / (n - 1)
        sx = statistics.stdev(x) or 1.0
        sy = statistics.stdev(y) or 1.0
        corr = cov / (sx * sy)

        # Regresión lineal simple: y = beta * x + alpha
        beta = cov / (sx ** 2) if sx > 0 else 0.0
        alpha = my - beta * mx

        return {
            "meses_analizados": n,
            "correlacion_trm_ventas": round(corr, 4),
            "pendiente_beta": round(beta, 2),
            "intercepto_alpha": round(alpha, 2),
            "interpretacion": (
                "Correlación positiva: a mayor TRM se incrementan las ventas facturadas en COP (por indexación en USD)."
                if corr > 0.2 else
                "Correlación neutra o independiente de la TRM."
            )
        }

def construir_dataset_operia_completo() -> Tuple[Path, Path]:
    """Genera el dataset consolidado OperIA en formato CSV y Excel (.xlsx) listo para visualización."""
    cfg = load_config()
    fecha_corte = date.fromisoformat(cfg["fecha_corte"])
    rates = load_trm(DATA_RAW_DIR)

    ventas = load_csv(DATA_RAW_DIR / "ventas.csv")
    clientes = load_csv(DATA_RAW_DIR / "clientes.csv")
    productos = load_csv(DATA_RAW_DIR / "productos.csv")
    base_instalada = load_csv(DATA_RAW_DIR / "base_instalada.csv")

    cli_map = {c["cliente_id"]: c for c in clientes}
    prod_map = {p["producto_id"]: p for p in productos}

    # Entrenar modelo predictivo
    mod_pred = ModeloPredictivoRecompra()
    mod_pred.entrenar(ventas, clientes)

    # Entrenar clasificador
    clasificador = ModeloClasificacionComercial(
        dias_frecuente=30,
        dias_frio=cfg["frio_dias_sin_compra"],
        dias_renovacion=cfg["renovacion_dias"]
    )

    # Agrupar historial por cliente hasta la fecha de corte
    ventas_por_cliente = defaultdict(list)
    for v in ventas:
        if v["estado"] == "Confirmada" and date.fromisoformat(v["fecha"]) <= fecha_corte:
            ventas_por_cliente[v["cliente_id"]].append(v)

    instalaciones_por_cliente = defaultdict(list)
    for bi in base_instalada:
        if date.fromisoformat(bi["fecha_inicio"]) <= fecha_corte:
            instalaciones_por_cliente[bi["cliente_id"]].append(bi)

    # Mapeo por cliente de semáforo y predicción
    cliente_meta = {}
    for cid, c in cli_map.items():
        v_cli = ventas_por_cliente[cid]
        fechas = sorted(date.fromisoformat(v["fecha"]) for v in v_cli)
        dias_sin_compra = (fecha_corte - fechas[-1]).days if fechas else None
        
        inst = instalaciones_por_cliente[cid]
        renov_prox = sum(0 <= (date.fromisoformat(x["fecha_fin"]) - fecha_corte).days <= cfg["renovacion_dias"] for x in inst)
        cobert_venc = sum(date.fromisoformat(x["fecha_fin"]) < fecha_corte for x in inst)
        cobert_vig = sum((date.fromisoformat(x["fecha_fin"]) - fecha_corte).days > cfg["renovacion_dias"] for x in inst)

        if len(inst) == 0:
            estado_cobertura = "Sin Cobertura"
        elif renov_prox > 0:
            estado_cobertura = "Próxima a Renovar (≤ 45d)"
        elif cobert_venc > 0 and cobert_vig == 0:
            estado_cobertura = "Vencida (< 0d)"
        else:
            estado_cobertura = "Vigente (> 45d)"

        estado, prioridad, accion, criterio = clasificador.clasificar_cliente(
            dias_sin_compra, len(v_cli), renov_prox, cobert_venc
        )

        f30 = sum(0 <= (fecha_corte - d).days < 30 for d in fechas)
        f90 = sum(0 <= (fecha_corte - d).days < 90 for d in fechas)
        prob_recompra = mod_pred.predecir_probabilidad(
            dias_sin_compra if dias_sin_compra is not None else 730,
            f30, f90, len(fechas)
        )

        cliente_meta[cid] = {
            "dias_sin_compra": dias_sin_compra if dias_sin_compra is not None else "",
            "estado_semaforo": estado,
            "estado_cobertura": estado_cobertura,
            "prioridad_llamada": prioridad,
            "accion_sugerida": accion,
            "criterio_decision": criterio,
            "probabilidad_recompra_30d": round(prob_recompra * 100, 1),
            "renovaciones_proximas": renov_prox,
            "coberturas_vencidas": cobert_venc
        }

    # Construir filas consolidadas
    filas_consolidadas = []
    for v in ventas:
        cid = v["cliente_id"]
        pid = v["producto_id"]
        c_info = cli_map.get(cid, {})
        p_info = prod_map.get(pid, {})
        c_meta = cliente_meta.get(cid, {})

        imp_cop = calcular_importe_cop(v, rates)
        trm_dia = rates.get(v["fecha"], 0.0)

        filas_consolidadas.append({
            "Venta_ID": v["venta_id"],
            "Fecha": v["fecha"],
            "Cliente_ID": cid,
            "Cliente": c_info.get("nombre_prueba", cid),
            "Sector": c_info.get("sector_prueba", "No especificado"),
            "Ciudad": c_info.get("ciudad_prueba", "No especificada"),
            "Producto_ID": pid,
            "Producto": p_info.get("nombre_prueba", pid),
            "Familia_Producto": p_info.get("familia_prueba", "General"),
            "Tipo_Producto": p_info.get("tipo_prueba", "Único"),
            "Cantidad": int(v["cantidad"]),
            "Moneda": v["moneda"],
            "Precio_Unitario": float(v["precio_unitario"]),
            "Descuento_Pct": float(v["descuento_pct"]),
            "TRM": trm_dia,
            "Ventas_COP": round(imp_cop, 2),
            "Estado_Venta": v["estado"],
            "Dias_Sin_Comprar": c_meta.get("dias_sin_compra", ""),
            "Estado_Cliente": c_meta.get("estado_semaforo", ""),
            "Estado_Cobertura": c_meta.get("estado_cobertura", "Sin Cobertura"),
            "Prob_Recompra_Pct": c_meta.get("probabilidad_recompra_30d", 0.0),
            "Prioridad_Llamada": c_meta.get("prioridad_llamada", "NORMAL"),
            "Accion_Recomendada": c_meta.get("accion_sugerida", ""),
            "Criterio_Decision": c_meta.get("criterio_decision", "")
        })

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_out = OUTPUTS_DIR / "OperIA_Dataset_Consolidado.csv"
    xlsx_out = OUTPUTS_DIR / "OperIA_Dataset_Consolidado.xlsx"

    # Exportar CSV
    with open(csv_out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(filas_consolidadas[0].keys()))
        writer.writeheader()
        writer.writerows(filas_consolidadas)

    # Exportar Excel con Pandas
    df = pd.DataFrame(filas_consolidadas)
    df.to_excel(xlsx_out, index=False, engine="openpyxl")

    return csv_out, xlsx_out
