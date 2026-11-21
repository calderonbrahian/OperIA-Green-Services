# Green Services | IA en Operaciones (EstudIA - Capa 2)

Proyecto modular y ejecutable para la integración operativa, análisis de clientes y modelo predictivo de compra en **Green Services and Solutions SAS**.

---

## 📁 Estructura del Proyecto

```text
Green_Services_Proyecto/
│
├── config/
│   └── parametros.json          # Parámetros editables de negocio (umbrales de corte, días de cliente frío, etc.)
│
├── data/
│   ├── raw/                     # Datos limpios originales (clientes, ventas, compras, productos, trm, etc.)
│   └── validation/              # Casos controlados y archivos de incidencias para calidad de datos
│
├── outputs/                     # Resultados generados automáticamente tras la ejecución
│   ├── resumen_clientes.csv     # Vista agregada y clasificación por cliente
│   ├── resumen_general.json     # KPIs consolidados
│   ├── metricas_modelo.json     # Evaluación y comparación del modelo vs línea base
│   ├── predicciones_prueba.csv  # Probabilidades estimadas para el conjunto de prueba
│   └── fotografias_modelo.csv   # Historial mensual temporal para entrenamiento/prueba
│
├── src/                         # Código fuente modular
│   ├── config.py                # Rutas y parámetros
│   ├── data_loader.py           # Lectura de CSVs, conversión TRM y cálculo de importes
│   ├── operaciones.py           # Reglas de negocio (visión 360 de clientes y prioridades)
│   ├── modelo_predictivo.py     # Regresión logística con partición temporal
│   └── validador.py             # Verificación de casos controlados y calidad de datos
│
├── tests/
│   └── test_casos_controlados.py# Pruebas unitarias automatizadas (unittest)
│
├── visor/
│   └── visor.html               # Tablero interactivo local en HTML (abre directo en navegador)
│
├── app_operia.py                # Dashboard Ejecutivo en Streamlit (oficial del MVP Hackatón)
├── main.py                      # Script principal ejecutable
└── README.md                    # Documentación del proyecto
```

---

## 🚀 Cómo Ejecutar

### 1. Iniciar el Dashboard Interactivo (OperIA):
Puedes iniciarlo de cualquiera de estas dos formas:
```bash
python main.py --dashboard
```
O directamente con Streamlit:
```bash
streamlit run app_operia.py
```
> El dashboard incluye semáforo interactivo, filtros, predicción de recompra a 30 días, gráfica de ventas vs TRM en doble eje y ficha 360° por cliente con botón para descargar el listado filtrado para el equipo comercial.

### 2. Ejecutar el flujo de modelos y procesamiento:
```bash
python main.py
```
O con `py`:
```bash
py main.py
```

### 2. Ejecutar módulos específicos:
* **Solo operaciones y resumen de clientes:**
  ```bash
  python main.py --operaciones
  ```
* **Solo modelo predictivo:**
  ```bash
  python main.py --modelo
  ```
* **Solo validación de casos y calidad:**
  ```bash
  python main.py --validar
  ```

### 3. Ejecutar pruebas unitarias automatizadas:
```bash
python -m unittest tests/test_casos_controlados.py
```

### 4. Abrir el Visor Interactivo:
Abre el archivo `visor/visor.html` en cualquier navegador web (Google Chrome, Edge, etc.) para consultar los clientes, filtrar fríos o coberturas próximas y revisar detalles.

---

## 📊 Reglas de Negocio Implementadas
1. **Conversión de Moneda:**
   - Moneda COP: Se toma directamente.
   - Moneda USD: Se multiplica por la TRM correspondiente a la fecha exacta de la venta.
   - Ventas `Anulada`: Se excluyen de la facturación y la frecuencia.
2. **Clasificación de Clientes:**
   - **Cliente Frecuente:** $\ge 8$ transacciones confirmadas.
   - **Cliente Frío:** $\ge 90$ días sin compras confirmadas desde la fecha de corte (`2026-10-31`).
   - **Renovación Próxima:** Vencimiento de cobertura entre 0 y 45 días posteriores al corte.
   - **Cobertura Vencida:** Fin de cobertura anterior al corte.
3. **Modelo Predictivo:**
   - Clasificación de probabilidad de compra a 30 días.
   - Partición temporal sin fuga de datos futuros (entrenamiento $\le$ 2026-04-30, validación mayo-junio 2026, prueba julio-septiembre 2026).
   - Umbral de decisión optimizado sobre el conjunto de validación y evaluado contra la línea base de compra reciente.
