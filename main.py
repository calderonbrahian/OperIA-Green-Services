#!/usr/bin/env python3
"""Punto de entrada principal para el proyecto Green Services / OperIA (EstudIA - Capa 2)."""
import argparse
import json
import sys
from pathlib import Path

# Asegurar importación del paquete src
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.operaciones import procesar_operaciones
from src.modelo_predictivo import entrenar_y_evaluar_modelo
from src.validador import validar_casos_controlados, analizar_incidencias_opcionales
from src.generador_datos_sinteticos import GeneradorDatosSinteticos
from src.modelos_operativos import (
    ModeloImpactoTRM,
    construir_dataset_operia_completo
)
from src.data_loader import load_csv, load_trm
from src.config import OUTPUTS_DIR, VISOR_DIR, DATA_RAW_DIR

def actualizar_visor_html(resumen_clientes):
    """Actualiza los datos del visor HTML con la última corrida generada."""
    visor_file = VISOR_DIR / "visor.html"
    if not visor_file.exists():
        return
    with open(visor_file, "r", encoding="utf-8") as f:
        content = f.read()

    marker_start = "const data="
    marker_end = ";const q=document.getElementById"
    if marker_start in content and marker_end in content:
        idx1 = content.find(marker_start) + len(marker_start)
        idx2 = content.find(marker_end)
        json_data = json.dumps(resumen_clientes, ensure_ascii=False)
        nuevo_html = content[:idx1] + json_data + content[idx2:]
        with open(visor_file, "w", encoding="utf-8") as f:
            f.write(nuevo_html)
        print("  ✓ Visor HTML sincronizado con los últimos datos calculados.")

def main():
    parser = argparse.ArgumentParser(description="Green Services / OperIA - IA en Operaciones")
    parser.add_argument("--operaciones", action="store_true", help="Calcular operaciones y clientes")
    parser.add_argument("--modelo", action="store_true", help="Entrenar y evaluar modelo predictivo de compra")
    parser.add_argument("--validar", action="store_true", help="Ejecutar validación de casos controlados y calidad")
    parser.add_argument("--consolidar", action="store_true", help="Generar dataset unificado OperIA (CSV y Excel)")
    parser.add_argument("--generar-datos", action="store_true", help="Generar nuevos datos sintéticos reproducibles")
    parser.add_argument("--dashboard", action="store_true", help="Iniciar el Dashboard Interactivo de Streamlit")
    parser.add_argument("--all", action="store_true", help="Ejecutar todo el flujo completo")

    args = parser.parse_args()

    # Si se pide el dashboard
    if args.dashboard:
        import subprocess
        app_path = PROJECT_ROOT / "app_operia.py"
        print(f"\n🚀 Iniciando Dashboard OperIA en Streamlit ({app_path})...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])
        return

    # Si no hay argumentos específicos, ejecutar flujo estándar
    if not (args.operaciones or args.modelo or args.validar or args.consolidar or args.generar_datos or args.all):
        args.all = True

    print("=" * 70)
    print("   GREEN SERVICES AND SOLUTIONS SAS - PROYECTO OPERIA")
    print("   IA en Operaciones | Hackatón EstudIA (Capa 2)")
    print("=" * 70)

    if args.generar_datos:
        print("\n[Módulo Generador] Creando datos sintéticos de prueba con semilla reproducible...")
        gen = GeneradorDatosSinteticos(seed=212026)
        conteo = gen.guardar_dataset_completo(DATA_RAW_DIR)
        for archivo, cant in conteo.items():
            print(f"  ✓ {archivo}: {cant} registros generados.")

    if args.operaciones or args.all:
        print("\n[1/4] Procesando datos operativos y visión 360 de clientes...")
        resumen, kpis = procesar_operaciones()
        print(f"  ✓ Clientes analizados: {kpis['total_clientes']}")
        print(f"  ✓ Transacciones confirmadas: {kpis['transacciones_confirmadas']} | Facturación: ${kpis['ingreso_total_cop']:,.2f} COP")
        print(f"  ✓ Clientes fríos detectados: {kpis['clientes_frios']}")
        actualizar_visor_html(resumen)

    if args.modelo or args.all:
        print("\n[2/4] Ejecutando modelos predictivos de Machine Learning...")
        res_modelo = entrenar_y_evaluar_modelo()
        m_test = res_modelo["metricas_prueba_modelo"]
        m_base = res_modelo["metricas_prueba_linea_base_compra_reciente"]
        print(f"  ✓ Modelo Recompra a 30 días: F1={m_test['F1']} | Recall={m_test['recall']} | Precision={m_test['precision']}")
        print(f"  ✓ Línea Base Comparativa:   F1={m_base['F1']} | Recall={m_base['recall']} | Precision={m_base['precision']}")

        # Análisis de impacto TRM
        ventas = [v for v in load_csv(DATA_RAW_DIR / "ventas.csv") if v["estado"] == "Confirmada"]
        rates = load_trm(DATA_RAW_DIR)
        res_trm = ModeloImpactoTRM.analizar_impacto(ventas, rates)
        print(f"  ✓ Correlación TRM vs Ventas COP: {res_trm['correlacion_trm_ventas']} ({res_trm['interpretacion']})")

    if args.consolidar or args.all:
        print("\n[3/4] Generando dataset consolidado OperIA (CSV + Excel XLSX)...")
        csv_path, xlsx_path = construir_dataset_operia_completo()
        print(f"  ✓ CSV Consolidado generado en: {csv_path.name}")
        print(f"  ✓ Excel XLSX generado en:     {xlsx_path.name}")

    if args.validar or args.all:
        print("\n[4/4] Ejecutando batería de validación y control de calidad...")
        casos = validar_casos_controlados()
        for c in casos:
            status = "APROBADO" if c["aprobado"] else "FALLÓ"
            print(f"  [{status}] Caso '{c['caso']}'")
        
        incidencias = analizar_incidencias_opcionales()
        if incidencias:
            print(f"  ✓ Calidad de datos: {len(incidencias)} incidencias sembradas identificadas y aisladas.")

    print("\n" + "=" * 70)
    print("   FLUJO EJECUTADO EXITOSAMENTE")
    print(f"   Outputs disponibles en: {OUTPUTS_DIR}")
    print(f"   Visor interactivo en:   {VISOR_DIR / 'visor.html'}")
    print("   Para abrir el Dashboard en Streamlit:")
    print("     python main.py --dashboard  (o streamlit run app_operia.py)")
    print("=" * 70)

if __name__ == "__main__":
    main()
