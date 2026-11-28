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

DATA_SYNTH_DIR = PROJECT_ROOT / "data" / "synthetic"


def verificar_datos_oficiales(raw_dir: Path = DATA_RAW_DIR) -> list:
    """Compara el SHA-256 de cada CSV de data/raw con el manifiesto oficial.

    Retorna la lista de archivos alterados o ausentes (vacía = datos íntegros).
    Normaliza finales de línea para que Windows y Linux den el mismo resultado.
    """
    import hashlib
    ref_file = CONFIG_DIR / "sha256_datos_oficiales.json"
    if not ref_file.exists():
        return []
    with open(ref_file, "r", encoding="utf-8") as f:
        esperado = json.load(f)
    problemas = []
    for nombre, h in esperado.items():
        p = raw_dir / nombre
        if not p.exists():
            problemas.append(f"{nombre}: ausente")
            continue
        contenido = p.read_bytes()
        if (hashlib.sha256(contenido).hexdigest() != h and
                hashlib.sha256(contenido.replace(b"\r\n", b"\n")).hexdigest() != h):
            problemas.append(f"{nombre}: contenido distinto al oficial")
    return problemas
