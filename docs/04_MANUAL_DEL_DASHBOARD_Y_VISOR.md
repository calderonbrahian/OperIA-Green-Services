# 🖥️ Manual de Usuario del Dashboard y Visor Interactivo — OperIA

OperIA cuenta con **dos capas de visualización complementarias y sincronizadas**:
1. **Dashboard Oficial en Streamlit (`app_operia.py`):** Panel interactivo avanzado con analítica en Plotly, filtros multidimensionales, probador de datos con subida de archivos CSV, explicación paso a paso de IA y exportación de evidencias.
2. **Visor Web Autónomo Online en GitHub Pages (`index.html` y `visor/visor.html`):** Tablero ejecutable directamente en cualquier navegador o en internet en [https://calderonbrahian.github.io/OperIA-Green-Services/](https://calderonbrahian.github.io/OperIA-Green-Services/) sin requerir servidores locales ni dependencias instaladas.

---

## 1. Cómo Lanzar cada Interfaz

### A. Dashboard en Streamlit
Desde la terminal en `Green_Services_Proyecto`:
```bash
python main.py --dashboard
```
O directamente:
```bash
streamlit run app_operia.py
```
> La aplicación se abre automáticamente en el navegador en `http://localhost:8501`.

### B. Visor Web Online (GitHub Pages)
Accede directamente desde cualquier dispositivo al enlace público:
🌐 **[https://calderonbrahian.github.io/OperIA-Green-Services/](https://calderonbrahian.github.io/OperIA-Green-Services/)**

### C. Visor Web Local (Sin Servidor)
Haz doble clic sobre el archivo:
📁 `Green_Services_Proyecto/visor/visor.html` o `Green_Services_Proyecto/index.html`.

---

## 2. Anatomía de las Pestañas y Módulos de OperIA

### 📊 Franja Superior: Tarjetas de KPIs y Semáforos Clickeables
* **Cartera Total (120 Clientes):** Haz clic para ver el universo total de cuentas.
* **🟢 Frecuentes (Activos):** Haz clic para filtrar solo clientes con compras recientes ($\le 30$ días).
* **🟡 Base Instalada:** Haz clic para filtrar cuentas con contratos o pólizas de servicio.
* **🔴 Clientes Fríos:** Haz clic para ver de inmediato los clientes con $\ge 90$ días sin comprar (prioridad de llamadas).
* **🔮 Proyección Nov 2026:** Facturación proyectada para el próximo mes ($169.87M COP) y cantidad de compradores esperados (70 cuentas).
* **TRM Actual:** Última cotización registrada de pesos por dólar.

---

### 📑 Pestaña 1: 🚨 Semáforo de Clientes (Llamadas Prioritarias)
Diseñado para la labor diaria del equipo de Ventas y Operaciones:
* **Botones de Clic Directo:** Filtra al instante por estado ("Ver Todos", "Solo Frecuentes", "Solo Base Instalada", "Solo Fríos").
* **Filtros Adicionales:** Por sector económico y buscador por texto/ID de cliente.
* **Tabla Inteligente:** Días sin compra, probabilidad de recompra calculada por IA, prioridad de contacto y estrategia recomendada.
* **Botones de Descarga:**
  * 📥 *Descargar Lista Comercial Filtrada (CSV)*: Para cargar en campañas de llamadas del día.
  * 📥 *Descargar Cartera Completa con Resultados (CSV)*: Auditoría integral de los 120 clientes.

---

### 🔮 Pestaña 2: Proyección Próximo Mes (Noviembre 2026)
Responde a la necesidad de mirar hacia adelante y planificar la facturación mensual:
* **Métricas Clave:** Facturación total esperada (\$169,870,345.83 COP), 70 clientes con propensión $\ge 0.40$, ticket promedio proyectado y cuentas frías a reactivar.
* **Gráfica de Tendencia y Proyección:** Evolución mensual histórica (Enero 2025 – Octubre 2026) combinada con la barra proyectada para Noviembre 2026 destacada en color violeta.
* **Cartera Priorizada:** Tabla de los 120 clientes clasificados por el ingreso esperado de Noviembre 2026 ($\text{Venta Esperada}_c = P_c \times \text{Ticket Promedio}_c$).
* **Botón de Descarga:** 📥 *Descargar Proyección Noviembre 2026 (CSV)*.

---

### 🧠 Pestaña 3: ¿Cómo Funciona el Modelo de IA? (Caja Blanca)
Demuestra rigurosamente qué hace el modelo y elimina el concepto de "caja negra":
1. **Partición Temporal Out-of-Time:** Explica la división estricta entre entrenamiento (Ene 2025 – Jun 2026) y prueba ciega (Jul 2026 – Oct 2026) para evitar fuga de datos (*data leakage*).
2. **Estandarización Z-Score:** Muestra la media ($\mu$) y desviación estándar ($\sigma$) de cada una de las 4 variables.
3. **Ecuación Logit y Pesos ($w$):** Tabla con el sesgo basal ($w_0 = -0.4225$), la penalización por recencia ($w_1 = -0.1729$), el impulso reciente ($w_2 = +0.0402$), la recurrencia trimestral ($w_3 = +0.4355$) y la lealtad histórica ($w_4 = +0.3789$).
4. **Función Sigmoide y Umbral $\theta = 0.40$:** Justificación del umbral calibrado para maximizar el Recall operativo al 78%.
5. **Desglose en Vivo de Cualquier Cliente:** Selector interactivo donde se elige cualquier empresa y se observa en pantalla el paso a paso aritmético ($X \to Z \to w \cdot Z \to Z_{\text{logit}} \to P\%$).

---

### 🧪 Pestaña 4: Simulador y Probador de Datos
Permite al usuario ingresar sus propios datos para experimentar con el modelo:
1. **Evaluador de Cliente Hipotético:** Permite modificar días sin compra, monto estimado, frecuencia de compras en 30/90 días y estado de contratos. Al pulsar *"⚡ Calcular Predicción con IA y Semáforo"*, genera la probabilidad, semáforo y sugerencia operativa.
2. **Cargador de Archivos CSV:** Arrastra o sube cualquier archivo CSV de clientes propio para previsualizarlo y auditarlo en la aplicación.

---

### 📋 Pestaña 5: Sesión de Pruebas y Evidencias
Consolida la validación técnica requerida por el reto EstudIA:
* **Matriz de Casos de Frontera (`Casos_controlados.json`):** Evaluación de las 6 reglas de negocio clave (descarte de ventas anuladas, detección de cliente frío $\ge 90$ días, cliente frecuente $\le 30$ días, renovación de contrato $\le 45$ días, normalización cambiaria con TRM exacta, y partición temporal out-of-time).
* **Auditoría de Calidad en Datos (`ventas_con_incidencias_OPCIONAL.csv`):** Identificación y aislamiento de 7 anomalías sembradas (precios negativos, TRM inexistente, clientes no registrados).
* **Botones de Descarga de Evidencias:**
  * 📥 *Descargar Evidencias de Pruebas (JSON)*: Archivo JSON firmado con métricas de aprobación (100%), fecha y matriz completa.
  * 📥 *Descargar Matriz de Casos de Frontera (CSV)*: Hoja de cálculo con el detalle de las 6 pruebas ejecutadas.

---

### 📈 Pestaña 6: Comportamiento Ventas vs. TRM
* Gráfico interactivo con doble eje $Y$ (Facturación mensual en COP vs. TRM promedio diaria en USD).
* Cálculo del coeficiente de correlación de Pearson y análisis de elasticidad cambiaria para la toma de decisiones de cobertura.

---

### 👤 Pestaña 7: Ficha 360° del Cliente
* Permite seleccionar cualquier cliente del menú desplegable para inspeccionar su perfil completo (sector, días sin compra, semáforo, prioridad de contacto, estrategia comercial y facturación total).
* Historial transaccional completo del cliente con detalle de producto, cantidad, moneda y TRM aplicada.

---

### 🎯 Pestaña 8: Objetivos y Reto Empresarial
* Contexto de la organización (Green Services and Solutions SAS) y de su fundador Jacob Arochi.
* Pregunta orientadora del reto.
* Matriz de alcance del MVP bajo metodología MoSCoW (Must, Should, Could, Won't).
* Roles del equipo de trabajo y guion del Pitch de 3 minutos para los jurados.

---

### 🔍 Pestaña 9: Explorador de Datos en Vivo
* Visor de transacciones con filtro dinámico por moneda original (Todas, COP, USD) para verificar la correcta aplicación de la TRM.
