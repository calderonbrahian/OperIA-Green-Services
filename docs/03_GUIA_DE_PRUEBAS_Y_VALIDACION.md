# 🧪 Guía de Pruebas, Validación y Calidad de Datos — OperIA

## 1. Comandos Rápidos para Lanzar las Pruebas

Desde la raíz del proyecto (`Green_Services_Proyecto`):

### Prueba 1: Batería Completa de Casos Controlados y Calidad
```bash
python main.py --validar
```
*Ejecuta la validación de las 6 reglas de negocio y audita las anomalías sembradas en el archivo de calidad.*

### Prueba 2: Suite Automatizada de Pruebas Unitarias (`unittest`)
```bash
python -m unittest tests/test_casos_controlados.py
```
*Pruebas unitarias de software formales para aserciones matemáticas y aislamiento de anuladas.*

### Prueba 3: Ejecución de Punto a Punto (End-to-End)
```bash
python main.py
```
*Ejecuta operaciones, modelo predictivo, consolidación a Excel/CSV y validación en un solo comando.*

---

## 2. Los 6 Casos Controlados Oficiales (`Casos_controlados.json`)

El sistema cuenta con un motor de validación contra casos de frontera predefinidos:

| Caso | Parámetros de Entrada | Resultado Esperado | Resultado OperIA | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **1. Venta en COP** | Cantidad: 2, Precio: \$100.000, Descuento: 10%, Moneda: COP | \$180.000 COP | \$180.000 COP | ✅ APROBADO |
| **2. Venta en USD con TRM** | Cantidad: 3, Precio: \$100 USD, Descuento: 0%, TRM: \$4.000 | \$1.200.000 COP | \$1.200.000 COP | ✅ APROBADO |
| **3. Venta Anulada** | Estado: `Anulada`, Cantidad: 10, Precio: \$50.000 | No sumar a facturación ni a frecuencia (\$0 COP) | \$0 COP (Excluida) | ✅ APROBADO |
| **4. Frío en Frontera** | Corte: `2026-10-31`, Última compra: `2026-08-02` | Exactamente 90 días $\rightarrow$ `es_frio = True` | 90 días $\rightarrow$ `es_frio = True` | ✅ APROBADO |
| **5. Renovación en Frontera** | Corte: `2026-10-31`, Fecha fin cobertura: `2026-12-15` | Exactamente 45 días $\rightarrow$ `renovacion_proxima = True` | 45 días $\rightarrow$ `renovacion_proxima = True` | ✅ APROBADO |
| **6. Cliente Inexistente** | Cliente: `CLI999` (sin registros) | Manejo seguro sin inventar historial ni compras | Fila no creada / Sin compras | ✅ APROBADO |

---

## 3. Protocolo de Prueba Oficial de la Hackatón (Paso a Paso)

Este protocolo replica exactamente la prueba descrita en el documento de la sesión del 21 de noviembre:

1. **Paso 1: Lanzar la aplicación:**
   ```bash
   python main.py --dashboard
   ```
2. **Paso 2: Medir tiempo de respuesta:**
   * Criterio: La interfaz y el semáforo deben responder y procesar los 120 clientes en **menos de 5 segundos**.
   * Resultado: Procesamiento instantáneo en memoria local (< 1.2 segundos).
3. **Paso 3: Identificar clientes en riesgo (Rojo):**
   * En el filtro de semáforo, seleccionar: `🔴 Fríos (Riesgo de Abandono)`.
   * Verificar que se listen las empresas que superan los 90 días sin comprar.
   * Tomar captura de pantalla de los 3 clientes más fríos para la evidencia de la bitácora.
4. **Paso 4: Inspeccionar la curva de TRM vs. Ventas:**
   * Pasar a la pestaña *📈 Comportamiento Ventas vs. TRM*.
   * Verificar que la curva de TRM promedio mensual acompañe las barras de facturación en COP.
5. **Paso 5: Descarga comercial:**
   * Hacer clic en *📥 Descargar Lista de Contacto Filtrada (CSV)* y comprobar que genere el archivo descargable con las llamadas prioritarias.

---

## 4. Auditoría de Calidad de Datos (Detección de Incidencias Sembradas)

Para demostrar robustez en ingeniería de datos, el módulo `validador.py` inspecciona el archivo de pruebas `ventas_con_incidencias_OPCIONAL.csv` y detecta con éxito las **7 anomalías sembradas** sin corromper el pipeline principal:

| Tipo de Incidencia Sembrada | Registro Afectado | Detección por OperIA | Tratamiento Aplicado |
| :--- | :--- | :--- | :--- |
| **ID de Venta Duplicado** | Clave primaria duplicada | Detectada (ID repetido) | Se descarta la copia redundante |
| **Cliente Inexistente** | `cliente_id = 'CLI999'` | Detectada (clave foránea huérfana) | Se aísla para verificación con CRM |
| **Fecha Inválida** | `fecha = '2026-02-30'` | Detectada (error de formato de fecha) | Se rechaza por fecha no gregoriana |
| **Moneda No Soportada** | `moneda = 'EUR'` | Detectada (fuera de TRM COP/USD) | Se aísla para requerir tasa oficial |
| **Cantidad Negativa** | `cantidad = -2` | Detectada (valor no admisible) | Se excluye de cálculo de ventas |
| **Precio Unitario Vacío** | `precio_unitario = ''` | Detectada (valor nulo) | Se marca como registro incompleto |
| **Producto Inexistente** | `producto_id = 'PRO99'` | Detectada (clave foránea inexistente) | Se aísla para revisión de catálogo |
