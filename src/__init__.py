"""Paquete principal de Green Services y OperIA."""
from .config import load_config, PROJECT_ROOT, DATA_RAW_DIR, OUTPUTS_DIR
from .data_loader import load_csv, load_trm, calcular_importe_cop
from .operaciones import procesar_operaciones
from .modelo_predictivo import entrenar_y_evaluar_modelo
from .validador import validar_casos_controlados, analizar_incidencias_opcionales
from .generador_datos_sinteticos import GeneradorDatosSinteticos
from .modelos_operativos import (
    ModeloClasificacionComercial,
    ModeloPredictivoRecompra,
    ModeloImpactoTRM,
    construir_dataset_operia_completo
)

__all__ = [
    "load_config",
    "PROJECT_ROOT",
    "DATA_RAW_DIR",
    "OUTPUTS_DIR",
    "load_csv",
    "load_trm",
    "calcular_importe_cop",
    "procesar_operaciones",
    "entrenar_y_evaluar_modelo",
    "validar_casos_controlados",
    "analizar_incidencias_opcionales",
    "GeneradorDatosSinteticos",
    "ModeloClasificacionComercial",
    "ModeloPredictivoRecompra",
    "ModeloImpactoTRM",
    "construir_dataset_operia_completo"
]
