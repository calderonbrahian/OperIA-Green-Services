"""Carga y transformación de datos."""
import csv
from pathlib import Path
from typing import List, Dict, Any

def load_csv(file_path: Path) -> List[Dict[str, Any]]:
    """Carga un archivo CSV retornando una lista de diccionarios con codificación utf-8-sig."""
    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    with open(file_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_trm(raw_dir: Path) -> Dict[str, float]:
    """Carga la tasa de cambio diaria desde trm_prueba.csv."""
    trm_list = load_csv(raw_dir / "trm_prueba.csv")
    return {row["fecha"]: float(row["cop_por_usd"]) for row in trm_list}

def calcular_importe_cop(venta: Dict[str, Any], rates: Dict[str, float]) -> float:
    """Calcula el importe neto en COP de una venta confirmada aplicando descuento y TRM."""
    if venta.get("estado") != "Confirmada":
        return 0.0
    
    cantidad = int(venta["cantidad"])
    precio_unitario = float(venta["precio_unitario"])
    descuento_pct = float(venta.get("descuento_pct", 0.0))
    monto_origen = cantidad * precio_unitario * (1.0 - (descuento_pct / 100.0))
    
    moneda = venta["moneda"]
    if moneda == "COP":
        return monto_origen
    elif moneda == "USD":
        fecha = venta["fecha"]
        if fecha not in rates:
            raise KeyError(f"Tasa de cambio no encontrada para la fecha: {fecha}")
        return monto_origen * rates[fecha]
    else:
        raise ValueError(f"Moneda no admitida: {moneda}")
