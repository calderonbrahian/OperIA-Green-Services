# 🖥️ Manual de Usuario del Dashboard y Visor Interactivo — OperIA

OperIA cuenta con **dos capas de visualización complementarias**:
1. **Dashboard en Streamlit (`app_operia.py`):** Panel interactivo con analítica avanzada en Plotly, filtros multidimensionales y exportación de datos.
2. **Visor Web Autónomo (`visor/visor.html`):** Tablero en HTML5 y Chart.js ejecutable directamente en cualquier navegador sin necesidad de levantar terminal ni servidores locales.

---

## 1. Cómo Lanzar cada Interfaz

### Lanzar el Dashboard Oficial en Streamlit
Desde la terminal en `Green_Services_Proyecto`:
```bash
python main.py --dashboard
```
O directamente:
```bash
streamlit run app_operia.py
```
> La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

### Lanzar el Visor Web Local (Sin Servidor)
Haz doble clic sobre el archivo:
📁 `Green_Services_Proyecto/visor/visor.html`
O desde la terminal:
```bash
start visor/visor.html
```

---

## 2. Anatomía del Dashboard en Streamlit (`app_operia.py`)

### 📊 Franja Superior: Tarjetas de KPIs Consolidados
* **Total Clientes:** Universo completo de clientes monitoreados (120 cuentas corporativas).
* **🟢 Frecuentes (Activos):** Cuentas con transacciones recientes ($\le 30$ días) o alto volumen ($\ge 8$ compras).
* **🟡 Base Instalada:** Cuentas con contratos de servicio activos y seguimiento de cobertura.
* **🔴 Fríos (Llamar Hoy):** Clientes con más de 90 días sin comprar; representa la lista de mayor riesgo de deserción comercial.
* **TRM Actual:** Última cotización registrada de pesos por dólar, permitiendo calibrar precios de inmediato.

---

### 📑 Pestaña 1: 🚨 Semáforo de Clientes (Llamadas Prioritarias)
Diseñado específicamente para el equipo Comercial y de Operaciones:
* **Filtro Rápido por Estado:** Selecciona con un clic solo clientes fríos, de seguimiento o frecuentes.
* **Filtro por Sector:** Filtra por sectores económicos (Tecnología, Financiero, Salud, Comercio, etc.).
* **Buscador en Tiempo Real:** Escribe cualquier parte del nombre del cliente o su ID (por ejemplo `CLI015`).
* **Tabla Inteligente:**
  * **Empresa e ID:** Nombre corporativo anonimizado.
  * **Días sin Compra:** Contador exacto de días desde la última operación.
  * **Probabilidad de Recompra (IA %):** Probabilidad estimada por el modelo de Machine Learning para los próximos 30 días.
  * **Prioridad y Acción Sugerida:** Mensaje claro para el asesor (ej: *"Campaña urgente de reactivación"* o *"Renovación anticipada de póliza"*).
* **Botón de Descarga:** Genera y descarga en un segundo el archivo CSV con la lista filtrada de clientes para cargar en llamadas o CRM.

---

### 📈 Pestaña 2: Comportamiento de Ventas vs. Variación de la TRM
* Gráfico interactivo con **doble eje $Y$**:
  * **Eje Izquierdo (Barras Azules):** Facturación total mensual en COP.
  * **Eje Derecho (Línea Roja Discontinua):** TRM promedio del mes (pesos por dólar).
* Permite al Gerente Financiero y a Operaciones observar con claridad la estacionalidad del negocio y la sensibilidad de los ingresos ante las variaciones cambiarias.

---

### 📦 Pestaña 3: Portafolio y Sectores
* **Gráfico de Dona (Familias de Producto):** Muestra el porcentaje de facturación que aporta cada familia (Software Cloud, Ciberseguridad, Gestión de Información, Infraestructura, Servicios TI).
* **Gráfico de Barras Horizontales (Sectores Económicos):** Identifica qué industrias concentran el mayor volumen de ventas para focalizar esfuerzos de prospección.

---

### 👤 Pestaña 4: Ficha 360° del Cliente
Permite hacer doble clic sobre una cuenta individual:
* Menú desplegable para seleccionar cualquier cliente.
* **Encabezado de Perfil:** Sector, ciudad, días sin compra, semáforo, probabilidad de recompra y facturación histórica acumulada.
* **Historial Detallado:** Tabla con todas las transacciones históricas confirmadas del cliente (fecha, producto comprado, cantidad, moneda original, precio unitario y valor en COP).

---

## 3. Características del Visor Web Local (`visor.html`)
Para presentaciones rápidas o computadores sin entorno de Python instalado:
* Desarrollado en HTML5 nativo con estilos modernos CSS3 e integración con **Chart.js**.
* Carga automáticamente los datos consolidados generados por el pipeline.
* Incluye buscador instantáneo, filtrado por semáforo y drawer de detalle de cliente al hacer clic sobre cualquier fila.
