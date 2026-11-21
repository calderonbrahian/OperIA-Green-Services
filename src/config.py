"""Módulo de configuración y rutas para Green Services."""
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_DIR = PROJECT_ROOT / "config"
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_VAL_DIR = PROJECT_ROOT / "data" / "validation"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
VISOR_DIR = PROJECT_ROOT / "visor"

DEFAULT_PARAMS = {
    "fecha_corte": "2026-10-31",
    "frecuente_min_transacciones": 8,
    "frio_dias_sin_compra": 90,
    "renovacion_dias": 45,
    "horizonte_prediccion_dias": 30,
    "nota": "Supuestos didácticos editables."
}

def load_config() -> dict:
    cfg_file = CONFIG_DIR / "parametros.json"
    if cfg_file.exists():
        with open(cfg_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {**DEFAULT_PARAMS, **data}
    return DEFAULT_PARAMS
