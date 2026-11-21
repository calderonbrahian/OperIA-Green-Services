# 📋 Respuestas a Preguntas Clave, Bitácora y Guion del Pitch — OperIA

## 1. Resolución a las 8 Preguntas Fundamentales del Reto

Estas respuestas resuelven con exactitud los puntos planteados en las tarjetas del papelógrafo y en la ficha del reto empresarial de Green Services and Solutions SAS:

### Mitad 1: Contexto Empresarial
1. **¿Qué organización es y a qué sector pertenece?**  
   *Respuesta:* Green Services and Solutions SAS, perteneciente al sector de Tecnología y Software, especializada en integrar soluciones y servicios para la gestión integral del ciclo de vida de la información corporativa. Contacto: Jacob Arochi (Fundador).
2. **¿Qué ocurre hoy y cómo gestionan la situación?**  
   *Respuesta:* La información de ventas, compras, contratos de la base instalada y TRM reside dispersa en varias plataformas. Se consolida manualmente cada mes en hojas de Excel. Esto provoca un análisis netamente reactivo y tardío.
3. **¿Por qué necesita resolverla y a quién afecta?**  
   *Respuesta:* Para acelerar la toma de decisiones y transformar la atención al cliente de reactiva a proactiva. Afecta directamente al equipo de **Operaciones** (desgaste en tareas repetitivas), al equipo **Comercial** (pérdida de cuentas por falta de visión 360) y a la **Gerencia Financiera** (reportes desfasados frente a la TRM).
4. **¿Dónde ocurre y con qué frecuencia?**  
   *Respuesta:* En el área de Operaciones, con periodicidad crítica mensual (durante los cierres de facturación y generación de reportes).

### Mitad 2: Definición del Reto
5. **¿Cuál es el reto y quién vive el problema?**  
   *Respuesta:* Automatizar el cruce de datos y aplicar modelos de Machine Learning para clasificar clientes y predecir ventanas de recompra a 30 días, entregando un visualizador con semáforo inteligente de llamadas.
6. **¿Qué sabemos con evidencia y qué suponemos?**  
   *Respuesta:*  
   * *Evidencia:* Se trabaja en Excel, la periodicidad es mensual y se cuenta con transacciones de ventas, clientes, catálogo y serie de TRM.  
   * *Supuestos Didácticos:* Cliente frío definido a partir de $\ge 90$ días sin compras; renovación próxima entre 0 y 45 días; TRM modelada para fines del ejercicio de prueba.
7. **¿Qué preguntas siguen sin resolver para la empresa real?**  
   *Respuesta:*  
   * ¿A qué corresponde exactamente el recurso identificado en la ficha técnica como «com»?  
   * ¿Cuáles son los umbrales oficiales y contractuales de cliente frío y periodos de gracia de renovación de pólizas?  
   * ¿Qué permisos y mecanismos de integración (APIs o vistas SQL) habilitará la empresa para conectar los datos reales de producción?
8. **¿Qué resultado necesita el usuario?**  
   *Respuesta:* Una visión consolidada 360° del cliente y un semáforo interactivo que le diga al asesor comercial exactamente a quién llamar hoy, por qué motivo y qué producto ofrecerle.

---

## 2. Textos Listos para Diligenciar la Bitácora Oficial
*(Plataforma: [https://estudia-seguimiento.vercel.app/hackaton](https://estudia-seguimiento.vercel.app/hackaton))*

* **Nombre del equipo:** Equipo Reto 4 — OperIA (EstudIA)
* **Reto empresarial asignado:** Reto 4: IA en Operaciones — Green Services and Solutions SAS
* **Avance logrado hoy (21 de Noviembre):**  
  > *«Construcción exitosa y validación del MVP 'OperIA'. Se desarrolló el pipeline automatizado de ingesta y normalización de monedas (USD a COP con TRM diaria), el modelo de Machine Learning para predicción de recompra a 30 días con partición temporal (F1=0.6592, Recall=78%), el semáforo inteligente de clientes en riesgo de abandono y el dashboard ejecutivo interactivo en Streamlit con visualización de TRM vs. Ventas.»*
* **Pruebas realizadas:**  
  > *«Se ejecutaron las pruebas unitarias y de validación sobre los 6 casos controlados oficiales (cálculo COP, TRM, exclusión de anuladas, fronteras de 90 días y manejo sin invención de clientes inexistentes) con 100% de aprobación. La aplicación cargó y procesó el universo de 120 clientes en menos de 2 segundos, filtrando de inmediato a las cuentas frías.»*
* **Dificultades y ajustes:**  
  > *«Para evitar la fuga de información temporal (data leakage), se implementó una partición estricta por bloques cronológicos en lugar de un muestreo aleatorio. Se integró una gráfica de doble eje para evidenciar la correlación entre la variación del dólar y la facturación en pesos.»*
* **Compromiso para el siguiente encuentro:**  
  > *«Validar con el facilitador y la organización los umbrales de cliente frío y ensayar la demostración en vivo del dashboard ante el panel de evaluación.»*

---

## 3. Guion del Pitch de 3 Minutos para la Sustentación

### Minuto 0:00 - 0:45 | El Problema (Hook & Dolor)
> *"Buenos días, jurados y compañeros. En Green Services and Solutions SAS, la información de clientes, ventas, compras y TRM vive dispersa en múltiples plataformas. Cada mes, el equipo de Operaciones pierde valiosas horas cruzando manualmente tablas de Excel. ¿El resultado? Un análisis tardío y reactivo: clientes clave que dejan de comprar sin que nadie lo note y cotizaciones desfasadas frente a la subida del dólar.  
> Por eso nos preguntamos: **¿Cómo podríamos automatizar este cruce y predecir el comportamiento comercial para pasar de apagar incendios a anticiparnos al mercado?**"*

### Minuto 0:45 - 1:45 | La Solución: OperIA (Arquitectura e IA)
> *"Nuestra respuesta es **OperIA**, una solución integral que combina ingeniería de datos, Machine Learning y visualización ejecutiva:  
> Primero, nuestro motor integra automáticamente las ventas, excluye operaciones anuladas y convierte transacciones en dólares a pesos utilizando la TRM exacta de cada día.  
> Segundo, entrenamos un modelo de Machine Learning con partición temporal estricta que predice la probabilidad de compra en los siguientes 30 días con un Recall del 78%, superando con creces la regla tradicional.  
> Y tercero, clasificamos a cada cliente en un semáforo de llamadas prioritarias: Verde para activos, Amarillo para renovaciones próximas de cobertura y Rojo para clientes en riesgo de abandono."*

### Minuto 1:45 - 2:30 | Demostración en Vivo del Dashboard
> *(Señalar la pantalla de Streamlit)*  
> *"Aquí vemos el centro de mando de OperIA. En la parte superior, los directivos ven de un vistazo los clientes fríos y la TRM actual.  
> Si entramos al semáforo de clientes y filtramos por 'Clientes Fríos', en menos de dos segundos el asesor comercial tiene la lista exacta de las empresas que llevan más de 90 días sin comprar, su probabilidad de recompra y la acción recomendada, con un botón para descargar la lista en Excel para llamar de inmediato.  
> Además, en nuestra gráfica de TRM vs. Ventas, la Gerencia Financiera puede monitorear con claridad cómo el alza del dólar impacta la facturación mensual."*

### Minuto 2:30 - 3:00 | Impacto y Cierre
> *"OperIA convierte un proceso manual de días en un sistema inteligente de segundos. Elimina el desgaste en Excel, protege los ingresos frente a la TRM y le devuelve al equipo comercial la capacidad de anticiparse y retener a sus clientes.  
> El código está probado, documentado y publicado en GitHub listo para escalar. ¡Muchas gracias!"*
