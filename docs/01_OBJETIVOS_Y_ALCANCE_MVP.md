# 🎯 Objetivos, Contexto Empresarial y Alcance del MVP — OperIA

## 1. Contexto de la Organización y el Reto
* **Organización Aliada:** Green Services and Solutions SAS
* **Sector:** Tecnología y Software — Especialistas en servicios y productos para el ciclo de vida de la información.
* **Reto:** Reto Empresarial 4: *IA en Operaciones* (Hackatón EstudIA - Capa 2).
* **Contacto Institucional:** Jacob Arochi (Fundador) — [greencss.com](https://greencss.com).

---

## 2. El Problema de Negocio y Pregunta Orientadora

### Situación Inicial
El equipo de Operaciones de Green Services gestionaba mensualmente de manera manual múltiples fuentes de datos en hojas de cálculo de Excel: compras a proveedores, ventas en distintas monedas (COP y USD), oscilaciones diarias de la Tasa Representativa del Mercado (TRM), recurrencia de pedidos y contratos vigentes en la base instalada.

### Consecuencias Críticas
1. **Desgaste Operativo:** Horas de trabajo consumidas en cruces manuales de tablas propensos a errores humanos.
2. **Desfase Financiero:** Dificultad para cuantificar el impacto real del dólar (TRM) sobre los márgenes en ventas en pesos colombianos.
3. **Pérdida de Clientes (Enfriamiento):** El área comercial actuaba de forma 100% reactiva; los clientes se "enfriaban" (más de 90 días sin comprar o con pólizas vencidas) sin que nadie recibiera una alerta temprana.

### ❓ Pregunta Orientadora Guía
> **«¿Cómo podríamos ayudar al equipo de Operaciones y Comercial a automatizar el cruce de datos para predecir el comportamiento de sus clientes y anticipar recompras mediante un modelo con visualización interactiva?»**

---

## 3. Objetivos del Proyecto OperIA

### Objetivo General
Desarrollar un Producto Mínimo Viable (MVP) que automatice la integración de datos operacionales y aplique inteligencia artificial/machine learning para predecir el comportamiento comercial, clasificar a los clientes mediante un semáforo de llamadas prioritarias y visualizar el impacto de la TRM en un panel interactivo.

### Objetivos Específicos
1. **Automatización e Integración:** Estandarizar y cruzar ventas, TRM diaria, compras, productos y base instalada en un solo pipeline automatizado.
2. **Modelo Predictivo de Recompra:** Entrenar un modelo de Machine Learning con partición temporal estricta para estimar la probabilidad de que un cliente compre en los próximos 30 días.
3. **Semáforo de Acción Comercial:** Clasificar a cada cuenta en Verde (Activo), Amarillo (Seguimiento / Renovación) o Rojo (Frío / Riesgo de Abandono) con sugerencias accionables.
4. **Visualización y Monitoreo TRM:** Desplegar un dashboard ejecutivo interactivo en Streamlit y un visor web autónomo en HTML que permitan filtrar clientes y monitorear la correlación cambiaria.
5. **Control de Calidad y Validación:** Implementar pruebas unitarias sobre casos controlados y detección de anomalías en los datos.

---

## 4. Alcance del MVP bajo Metodología MoSCoW

| Categoría MoSCoW | Descripción | Funcionalidades Entregadas en OperIA |
| :--- | :--- | :--- |
| **Must Have**<br>*(Imprescindible)* | Indispensable para que el MVP opere y se valide. | 1. Ingesta y normalización de archivos de datos.<br>2. Cruce y conversión dinámica de USD a COP según la TRM de cada fecha.<br>3. Semáforo inteligente de clientes (Frecuente, Seguimiento, Frío).<br>4. Exclusión automática de transacciones anuladas.<br>5. Identificación de contratos con renovación próxima ($\le 45$ días) o vencidos. |
| **Should Have**<br>*(Importante)* | Aporta alto valor analítico y comercial. | 1. Modelo de Machine Learning con predicción porcentual de recompra a 30 días.<br>2. Gráfica interactiva de tendencia de ventas históricas vs. variación de la TRM en doble eje.<br>3. Buscador en tiempo real por nombre de cliente o ID.<br>4. Ficha 360° por cliente con historial y desglose por producto. |
| **Could Have**<br>*(Deseable)* | Valor agregado implementado. | 1. Botón de descarga directa a CSV/Excel con las llamadas prioritarias del día.<br>2. Generador de datos sintéticos reproducibles (`seed=212026`) para pruebas y simulaciones.<br>3. Doble interfaz: Dashboard en Streamlit (`app_operia.py`) y Visor web local (`visor.html`). |
| **Won't Have**<br>*(Fuera de alcance)* | Excluido deliberadamente para asegurar entrega ágil. | 1. Conexión por API en tiempo real al ERP/CRM de producción de la empresa.<br>2. Autenticación multiusuario con contraseñas complejas y roles de base de datos.<br>3. Pasarela de pagos o facturación electrónica en línea. |

---

## 5. Roles y Responsabilidades del Equipo

* **Coordinador(a):** Gestión del repositorio en GitHub, control de versiones, orquestación del código fuente y cumplimiento del cronograma de entrega.
* **Investigador(a):** Validación del diccionario de datos, verificación de claves foráneas, reglas de TRM y formulación de umbrales comerciales.
* **Diseñador(a):** Experiencia de usuario (UX/UI), maquetación del dashboard en Streamlit (`app_operia.py`), diseño de tarjetas KPI y paleta cromática del semáforo.
* **Documentador(a):** Redacción técnica, estructuración de manuales en `docs/`, registro de bitácora y recopilación de evidencias.
* **Comunicador(a):** Preparación del Pitch de 3 minutos, guion de demostración y sustentación ante jurados y mentores.
