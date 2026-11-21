"""Modelo predictivo de probabilidad de compra a 30 días."""
from datetime import date, timedelta
from collections import defaultdict
import csv
import json
import math
import statistics
from typing import Dict, Any

from .config import DATA_RAW_DIR, OUTPUTS_DIR
from .data_loader import load_csv

def entrenar_y_evaluar_modelo() -> Dict[str, Any]:
    """Entrena regresión logística didáctica con partición temporal y calcula métricas."""
    sales = load_csv(DATA_RAW_DIR / "ventas.csv")
    clients = load_csv(DATA_RAW_DIR / "clientes.csv")

    hist = defaultdict(list)
    for v in sales:
        if v["estado"] == "Confirmada":
            hist[v["cliente_id"]].append(date.fromisoformat(v["fecha"]))

    # Generar fotografías temporales mensuales
    rows = []
    for year in [2025, 2026]:
        for month in range(1, 13):
            nxt = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
            cut = nxt - timedelta(days=1)
            # Solo cortes con ventana futura completa observable
            if cut < date(2025, 3, 31) or cut > date(2026, 9, 30):
                continue
            
            for c in clients:
                if date.fromisoformat(c["fecha_alta"]) > cut:
                    continue
                ds = [d for d in hist[c["cliente_id"]] if d <= cut]
                rec = (cut - max(ds)).days if ds else 730
                f30 = sum(0 <= (cut - d).days < 30 for d in ds)
                f90 = sum(0 <= (cut - d).days < 90 for d in ds)
                label = int(any(cut < d <= cut + timedelta(days=30) for d in hist[c["cliente_id"]]))
                rows.append({
                    "cliente_id": c["cliente_id"],
                    "corte": str(cut),
                    "recencia_dias": rec,
                    "frecuencia_30d": f30,
                    "frecuencia_90d": f90,
                    "historial_n": len(ds),
                    "compra_30d": label
                })

    train = [x for x in rows if x["corte"] <= "2026-04-30"]
    valid = [x for x in rows if "2026-05-01" <= x["corte"] <= "2026-06-30"]
    test = [x for x in rows if x["corte"] >= "2026-07-01"]

    fields = ["recencia_dias", "frecuencia_30d", "frecuencia_90d", "historial_n"]
    mu = [statistics.mean(x[f] for x in train) for f in fields]
    sd = [statistics.pstdev(x[f] for x in train) or 1 for f in fields]

    def vec(x):
        return [1.0] + [(x[f] - m) / s for f, m, s in zip(fields, mu, sd)]

    def sig(z):
        return 1.0 / (1.0 + math.exp(-max(-35, min(35, z))))

    # Descenso de gradiente con regularización L2
    w = [0.0] * 5
    lr = 0.1
    epochs = 600
    for _ in range(epochs):
        g = [0.0] * 5
        for row in train:
            a = vec(row)
            pred = sig(sum(k * v for k, v in zip(w, a)))
            error = pred - row["compra_30d"]
            for j in range(5):
                g[j] += error * a[j]
        w = [v - lr * (g[j] / len(train) + (0.001 * v if j else 0.0)) for j, v in enumerate(w)]

    def prob(x):
        return sig(sum(k * v for k, v in zip(w, vec(x))))

    def calc_metrics(data, predict_fn):
        tp = tn = fp = fn = 0
        for x in data:
            y = x["compra_30d"]
            p = predict_fn(x)
            if p and y: tp += 1
            elif not p and not y: tn += 1
            elif p and not y: fp += 1
            elif not p and y: fn += 1
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        accuracy = (tp + tn) / len(data) if data else 0.0
        return {
            "n": len(data),
            "TP": tp, "TN": tn, "FP": fp, "FN": fn,
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "F1": round(f1, 4)
        }

    # Selección óptima de umbral usando SOLO conjunto de validación
    thresholds = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    best_threshold = max(thresholds, key=lambda t: calc_metrics(valid, lambda x: prob(x) >= t)["F1"])

    metrics_valid = calc_metrics(valid, lambda x: prob(x) >= best_threshold)
    metrics_test_model = calc_metrics(test, lambda x: prob(x) >= best_threshold)
    metrics_test_baseline = calc_metrics(test, lambda x: x["frecuencia_30d"] > 0)

    results = {
        "modelo": "Regresión Logística Didáctica (sin dependencias externas)",
        "entrenamiento_rango": "hasta 2026-04-30",
        "validacion_rango": "2026-05-01 a 2026-06-30",
        "prueba_rango": "2026-07-01 a 2026-09-30",
        "ventana_objetivo_dias": 30,
        "umbral_seleccionado": best_threshold,
        "variables": fields,
        "medias_escalado": mu,
        "desviaciones_escalado": sd,
        "pesos_modelo": [round(val, 6) for val in w],
        "metricas_validacion": metrics_valid,
        "metricas_prueba_modelo": metrics_test_model,
        "metricas_prueba_linea_base_compra_reciente": metrics_test_baseline,
        "advertencia": "Datos de prueba; valida metodología temporal antes de aplicar en producción."
    }

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUTS_DIR / "metricas_modelo.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Exportar fotografías y predicciones de prueba
    with open(OUTPUTS_DIR / "fotografias_modelo.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    test_predictions = [
        dict(x, probabilidad=round(prob(x), 4), prediccion=int(prob(x) >= best_threshold))
        for x in test
    ]
    with open(OUTPUTS_DIR / "predicciones_prueba.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(test_predictions[0].keys()))
        writer.writeheader()
        writer.writerows(test_predictions)

    return results
