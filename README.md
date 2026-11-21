# 🟢 OperIA — Centro de Mando Inteligente de Operaciones
### Green Services and Solutions SAS · Reto 4: IA en Operaciones (Hackatón EstudIA - Capa 2)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit Dashboard](https://img.shields.io/badge/streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Machine Learning](https://img.shields.io/badge/ML-Logistic%20Regression%20Temporal-brightgreen.svg)]()
[![Repository](https://img.shields.io/badge/GitHub-OperIA--Green--Services-blue.svg)](https://github.com/calderonbrahian/OperIA-Green-Services)

> **OperIA** es una solución analítica integral que transforma la gestión operativa y comercial de Green Services and Solutions SAS: automatiza el cruce de datos, predice recompras a 30 días con Machine Learning, asigna prioridades de llamada mediante un semáforo inteligente y monitorea la sensibilidad de las ventas frente a las variaciones de la TRM.

---

## 📚 Índice de Documentación Oficial del Proyecto

Hemos estructurado la documentación técnica y de negocio en 5 manuales detallados dentro de la carpeta [`docs/`](file:///c:/Users/Brahian/OneDrive/Desktop/EstuDIA/Green_Services_Proyecto/docs):

1. **[01. Objetivos, Contexto Empresarial y Alcance del MVP (MoSCoW)](file:///c:/Users/Brahian/OneDrive/Desktop/EstuDIA/Green_Services_Proyecto/docs/01_OBJETIVOS_Y_ALCANCE_MVP.md):**
   * Definición del problema, justificación, pregunta orientadora y matriz de alcance MoSCoW.
   * Roles y responsabilidades del equipo de trabajo (Coordinador, Investigador, Diseñador, Documentador, Comunicador).
2. **[02. Arquitectura de la Solución y Modelos de Inteligencia Artificial](file:///c:/Users/Brahian/OneDrive/Desktop/EstuDIA/Green_Services_Proyecto/docs/02_ARQUITECTURA_Y_MODELOS_IA.md):**
   * Diagrama Mermaid de flujo de datos y reglas de negocio monetarias (TRM).
   * Modelo predictivo de recompra a 30 días: partición temporal estricta sin fuga de datos (`data leakage`), formulación matemática y métricas (F1=0.6592, Recall=78.0%).
   * Modelo de correlación y elasticidad cambiaria TRM vs. Ventas en COP.
3. **[03. Guía de Pruebas, Validación y Calidad de Datos](file:///c:/Users/Brahian/OneDrive/Desktop/EstuDIA/Green_Services_Proyecto/docs/03_GUIA_DE_PRUEBAS_Y_VALIDACION.md):**
   * Comandos de ejecución para pruebas unitarias (`unittest`) y de negocio.
   * Los 6 casos controlados de frontera aprobados al 100%.
   * Auditoría y tratamiento de las 7 incidencias de calidad de datos sembradas.
4. **[04. Manual de Usuario del Dashboard y Visor Interactivo](file:///c:/Users/Brahian/OneDrive/Desktop/EstuDIA/Green_Services_Proyecto/docs/04_MANUAL_DEL_DASHBOARD_Y_VISOR.md):**
   * Guía completa de uso del Dashboard en Streamlit (`app_operia.py`) y del Visor Web local (`visor.html`).
   * Explicación de los 4 paneles: Semáforo de clientes, Ventas vs. TRM, Portafolio/Sectores y Ficha 360°.
5. **[05. Respuestas a Preguntas Clave, Bitácora y Guion del Pitch](file:///c:/Users/Brahian/OneDrive/Desktop/EstuDIA/Green_Services_Proyecto/docs/05_PREGUNTAS_CLAVE_Y_BITACORA.md):**
   * Respuestas a las 8 preguntas del papelógrafo y de la ficha empresarial.
   * Textos listos para copiar y pegar en la bitácora de la plataforma EstudIA.
   * Guion cronometrado para el Pitch de 3 minutos ante los jurados y mentores.

---

## 📁 Estructura del Repositorio

```text
OperIA-Green-Services/
│
├── config/
│   └── parametros.json             # Parámetros editables (días de cliente frío, corte, etc.)
│
├── data/
│   ├── raw/                        # Datos base limpios (clientes, ventas, productos, compras, trm)
│   └── validation/                 # Casos controlados y archivos de prueba de incidencias
│
├── docs/                           # Documentación completa y manuales de la Hackatón
│   ├── 01_OBJETIVOS_Y_ALCANCE_MVP.md
│   ├── 02_ARQUITECTURA_Y_MODELOS_IA.md
│   ├── 03_GUIA_DE_PRUEBAS_Y_VALIDACION.md
│   ├── 04_MANUAL_DEL_DASHBOARD_Y_VISOR.md
│   ├── 05_PREGUNTAS_CLAVE_Y_BITACORA.md
│   ├── Documento_MVP_OperIA.docx
│   ├── Presentacion_OperIA.pptx
│   ├── Tarea_21_Noviembre_Construir_y_Probar_MVP.docx
│   └── Tarjetas_Recortables_Papelografo.docx
│
├── outputs/                        # Datasets consolidados y métricas generadas
│   ├── OperIA_Dataset_Consolidado.xlsx   # Archivo maestro para Excel o Power BI
│   ├── OperIA_Dataset_Consolidado.csv    # Dataset plano enriquecido con IA
│   ├── metricas_modelo.json              # Evaluación del modelo de Machine Learning
│   └── resumen_clientes.csv              # Vista agregada 360° por cliente
│
├── src/                            # Código fuente modular
│   ├── __init__.py
│   ├── config.py                   # Carga de rutas y parámetros
│   ├── data_loader.py              # Ingesta, TRM y conversión COP
│   ├── generador_datos_sinteticos.py # Motor de simulación y generación de datos
│   ├── operaciones.py              # Reglas de negocio y KPIs
│   ├── modelo_predictivo.py        # Algoritmo de ML con corte temporal
│   ├── modelos_operativos.py       # Semáforo comercial, recompra y TRM
│   └── validador.py                # Verificación de casos y calidad de datos
│
├── tests/
│   └── test_casos_controlados.py   # Suite de pruebas unitarias automatizadas
│
├── visor/
│   └── visor.html                  # Tablero web interactivo autónomo (abre directo en navegador)
│
├── app_operia.py                   # Dashboard Ejecutivo en Streamlit y Plotly
├── main.py                         # Orquestador por línea de comandos
├── requirements.txt                # Dependencias del proyecto
├── .gitignore
└── README.md
```

---

## 🚀 Guía de Inicio Rápido

### 1. Iniciar el Dashboard Ejecutivo (Streamlit)
```bash
python main.py --dashboard
```
O directamente con Streamlit:
```bash
streamlit run app_operia.py
```

### 2. Abrir el Visor Web Autónomo (Sin Servidor)
Haz doble clic sobre el archivo [`visor/visor.html`](file:///c:/Users/Brahian/OneDrive/Desktop/EstuDIA/Green_Services_Proyecto/visor/visor.html) para abrirlo en Chrome, Edge o tu navegador preferido.

### 3. Ejecutar el Pipeline Completo de Modelos
```bash
python main.py
```
*Procesa las operaciones, entrena el modelo de IA, genera el dataset consolidado en Excel y valida las reglas.*

### 4. Lanzar las Pruebas Unitarias
```bash
python -m unittest tests/test_casos_controlados.py
```

### 5. Regenerar Datos Sintéticos de Prueba
```bash
python main.py --generar-datos
```

---

## 👥 Equipo de Trabajo
* **Proyecto:** OperIA (Reto 4: IA en Operaciones)
* **Convocatoria:** Hackatón EstudIA — Capa 2 (Alcaldía de Medellín)
* **Organización:** Green Services and Solutions SAS
* **Autor / Desarrollador:** Brahian Calderón ([@calderonbrahian](https://github.com/calderonbrahian))
