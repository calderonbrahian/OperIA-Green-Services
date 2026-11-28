# Informe de Revisión, Plan MVP → Producto y Memoria de Desarrollo de OperIA

**Proyecto:** OperIA · Reto 4 "IA en Operaciones" · Green Services and Solutions SAS · Hackatón EstudIA (Capa 2)
**Fecha de la auditoría:** 28 de noviembre de 2026 · **Repositorio:** https://github.com/calderonbrahian/OperIA-Green-Services
**Alcance:** (1) auditar si el trabajo cumple los objetivos del reto, (2) plan para pasar de MVP a producto, (3) memoria de cómo y por qué se desarrolló.

> Este informe es deliberadamente honesto: separa lo que está **verificado** de lo que fue **afirmado sin evidencia** en entregas anteriores. Donde una cifra de documentos previos no se pudo reproducir, se indica.

---

## 1. Veredicto ejecutivo

**El MVP cumple el núcleo del reto, pero NO está listo para presentarse como "validado" hasta corregir 5 hallazgos.**

Lo que sí está sólido:
- Pipeline reproducible: ingesta → conversión USD/COP con TRM de la fecha → exclusión de anuladas → vista por cliente → modelo → dashboard.
- Modelo de IA real (regresión logística propia, sin dependencias) con **partición temporal** (entrena ≤ abr-2026, valida may–jun, prueba jul–sep) y **comparación contra una línea base** (compra reciente). Métricas: F1 0.659 vs 0.574, recall 78 % vs 56.7 %.
- Los 6 casos controlados oficiales pasan (6/6) y se detectan las 7 incidencias sembradas.
- Interfaz dual (Streamlit + sitio web en GitHub Pages), descargas CSV, simulador, evidencias exportables, documentación y bitácora.

Lo que impide declararlo "cumplido al 100 %":

| # | Hallazgo crítico | Gravedad |
| :-: | :--- | :-: |
| H1 | Los CSV de `data/raw` **no son los oficiales** del paquete (contenido distinto en las 6 tablas). Se regeneraron con el generador sintético. Resultado: 30 clientes fríos vs **41** en la referencia oficial; métricas no comparables con `Referencia_metricas_modelo.json`. | **Crítica** |
| H2 | El dashboard muestra **117 clientes, no 120**: 3 clientes sin compras desaparecen porque la tabla se construye desde filas de ventas. La categoría "Sin compras" exigida por la guía se pierde. | **Alta** |
| H3 | Inconsistencia semáforo/cobertura: 17 clientes con cobertura **Vigente** reciben prioridad **MEDIA** (el código cuenta *cualquier* contrato vencido, aunque tenga otro vigente). El manual de 24 casos dice BAJA/NORMAL para esos casos. | **Alta** |
| H4 | El manual de "24 casos" incluye un eje **IA (P ≥ 40 %)** que **no altera** la prioridad ni el semáforo en el código; 15 clientes con P ≥ 40 % tienen prioridad BAJA. El documento sobrevende el papel del modelo. | **Alta** |
| H5 | Afirmaciones sin evidencia: "recall 52 % con umbral 0.5", "50 cuentas frías", "TRM Oficial" (la guía prohíbe presentar la TRM como oficial), proyección Nov-2026 de \$169.87 M sin backtest. | **Media-Alta** |

Ninguno es difícil de resolver; el plan de la sección 4 los ataca en la Fase 0.

---

## 2. Auditoría contra los objetivos del reto

Fuente de objetivos: `Ficha_original_del_reto.pdf`, `Guia_estudiante_EDITABLE.md`, `Orientaciones_para_facilitadores.md`.

| Objetivo / requisito del reto | Estado | Evidencia y observación |
| :--- | :-: | :--- |
| Integrar ventas, TRM, clientes y base instalada en una vista por cliente | ✅ Cumple | `operaciones.py`, `modelos_operativos.py`; ficha 360° con historial. |
| Integrar **compras/proveedores** | ❌ No cumple | `compras.csv` y `proveedores.csv` se generan pero **no se usan** en la vista ni en el modelo (la guía advierte no cruzarlas con ventas; faltó al menos un indicador agregado, p. ej. costo de reposición por producto). |
| Convertir USD→COP con la TRM de la misma fecha; excluir anuladas | ✅ Cumple | Casos `COP`, `USD`, `Anulada` aprobados. |
| Cliente frío (≥ 90 d), renovación próxima (≤ 45 d) con bordes inclusivos | ✅ Cumple | Casos de frontera 90 d y 45 d aprobados. |
| Etiquetas **independientes** (frecuente ≥ 8 operaciones vs frío) | ⚠️ Parcial | La guía dice que alguien puede ser frecuente **y** frío. Por petición del usuario, el semáforo se redefinió por recencia (≤ 30 d = Frecuente). Decisión válida, pero se perdió la etiqueta oficial "frecuente (≥ 8 ops)": 58 clientes la cumplen y hoy no se ve. |
| Categoría separada "Sin compras" | ❌ No cumple | Ver H2 (3 clientes omitidos). |
| Prioridad transparente: frío → renovación/vencida → resto | ⚠️ Parcial | Implementada, pero con niveles extra (MEDIA/BAJA/NORMAL) y con la inconsistencia H3. |
| Modelo de IA con probabilidad de compra a 30 días | ✅ Cumple | `modelo_predictivo.py`, pesos en `metricas_modelo.json`. |
| Fotografías mensuales solo con datos conocidos al corte (sin fuga) | ✅ Cumple | Features de recencia/frecuencias calculadas ≤ corte; ventanas completas. |
| Partición: train mar-25→abr-26, ajuste may–jun-26, prueba jul–sep-26 | ✅ Cumple | Rangos idénticos en `metricas_modelo.json`. Umbral 0.40 elegido en validación. |
| Comparar con regla simple; reportar precisión, recall y **matriz de confusión** | ⚠️ Parcial | Precisión/recall/F1 sí; la matriz de confusión (TP/TN/FP/FN) está en el JSON pero **no se muestra** en el dashboard. |
| Discutir que la regresión puede perder en alguna métrica | ⚠️ Parcial | El modelo gana en recall y F1 pero **pierde en precisión** (57.1 % vs 58.2 %) y en accuracy es casi igual; no se discute el costo de falsos positivos (88 FP). |
| Pronóstico agregado con MAE vs último valor observado | ❌ No cumple | La proyección Nov-2026 (Σ P × ticket) no se valida con backtest ni MAE. Es una estimación no verificada. |
| Visualización interactiva / consulta | ✅ Cumple | Streamlit y GitHub Pages, filtros, semáforos clicables, descargas. |
| 7 incidencias de calidad: documentar corregir/aislar/pedir info por fila | ⚠️ Parcial | Se detectan y listan; falta registro por fila con la decisión tomada. |
| No presentar TRM ni datos como reales/oficiales | ❌ No cumple | Texto "TRM Oficial" en dashboard; no hay aviso permanente "datos de prueba". |
| Registrar preguntas pendientes a la empresa ("com", definición de frío, etc.) | ✅ Cumple | `05_PREGUNTAS_CLAVE_Y_BITACORA.md`. |
| Pruebas con otro equipo + mejora derivada | ⚠️ Parcial | Mejora derivada real y documentada (corrección del semáforo, H del 21-nov). Falta registro formal de una prueba con otro equipo. |
| Limitaciones y próximos pasos | ✅ Cumple | Documentados; este informe los amplía. |

**Resumen:** 9 cumplen · 6 parciales · 4 no cumplen (compras, Sin compras, pronóstico con MAE, advertencia de datos de prueba).

---

## 3. Hallazgos detallados y corrección propuesta

| ID | Causa probable | Corrección | Prueba que la valida |
| :-: | :--- | :--- | :--- |
| H1 | Probable sobrescritura de `data/raw` por el generador sintético (no se pudo confirmar el momento exacto; sí se confirma que el contenido difiere). | Restaurar los CSV oficiales (hash en `MANIFIESTO_SHA256.txt`); mover el generador a `data/synthetic/`; el pipeline debe leer solo de `data/raw` oficial y verificar el SHA-256 al iniciar. | Test: resultado = 41 fríos, 1 371 operaciones, ingreso 5 647 449 456 COP (valores de `Referencia_resumen_prueba.json`). |
| H2 | `groupby` sobre filas de ventas. | Construir la vista parte de `clientes.csv` (120 filas) con *left join*. | Test: 120 clientes y 3 con estado "Sin compras". |
| H3 | `coberturas_vencidas` suma contratos vencidos sin descontar clientes con contrato vigente. | Derivar la prioridad desde `Estado_Cobertura` (una sola fuente de verdad). | Test de tabla de verdad Semáforo × Cobertura. |
| H4 | La probabilidad no entra en la regla de prioridad. | Decisión de negocio: (a) quitar el eje IA del manual, o (b) usar P ≥ 0.40 como *desempate* dentro de cada prioridad. Se recomienda (b) y documentarlo. | Test: a igual prioridad, mayor P sube en la lista. |
| H5 | Cifras escritas a mano en textos. | Generar todas las cifras de los documentos desde `outputs/*.json`; reemplazar "TRM Oficial" por "TRM de prueba (no oficial)"; eliminar o calcular el 52 %. | Revisión automática: ninguna cifra literal sin fuente. |

---

## 4. Plan para pasar de MVP a producto final

### 4.1 Principios
1. **Datos reales primero:** nada de ML nuevo hasta validar esquemas y permisos con Green Services.
2. **Una sola fuente de verdad** para reglas (parámetros en config, no en código ni en HTML).
3. **Explicable por diseño:** cada recomendación cita variables, corte y regla.
4. **Humano en el circuito:** el sistema prioriza y sugiere; no contacta ni promete ventas.

### 4.2 Hoja de ruta por fases

| Fase | Objetivo | Entregables clave | Duración estimada* |
| :-: | :--- | :--- | :-: |
| **0. Cierre del MVP** | Corregir H1–H5 y cerrar brechas de la sección 2 | Datos oficiales restaurados; 120 clientes; prioridad desde cobertura; matriz de confusión visible; MAE de pronóstico; aviso "datos de prueba"; tests de reglas y no-fuga | 3–5 días |
| **1. Datos y gobierno** | Ingesta de datos reales y calidad | Contratos de datos (esquema, tipos, claves); validaciones automáticas por tabla; registro por fila de incidencias (corrige/aísla/solicita); TRM oficial (fuente Banco de la República/SFC) con fallback; autorización de uso y Ley 1581 (habeas data) | 2–3 semanas |
| **2. Modelo robusto** | Pasar de logística didáctica a modelo evaluado | Validación temporal con múltiples cortes (*rolling origin*); cohortes de clientes nuevos; calibración de probabilidades; comparación con gradiente boosting; *feature store* (incluir compras/proveedores y producto); monitoreo de *drift*; umbral por costo-beneficio acordado con Comercial | 3–4 semanas |
| **3. Plataforma** | De scripts a servicio | Base de datos (PostgreSQL) y capa API (FastAPI); tareas programadas (corte diario/semanal); autenticación y roles (Gerencia, Comercial, Operaciones); auditoría de accesos; despliegue en contenedor; sustituir `visor.html` embebido por un front que consuma la API | 4–6 semanas |
| **4. Experiencia y ciclo de feedback** | Adopción real | Cola diaria de llamadas con responsable y estado; botón "resultado de la gestión" (compró / no contesta / no interesa) que alimenta el reentrenamiento; alertas por correo/Teams; integración con CRM; exportes a Excel con formato corporativo | 3–4 semanas |
| **5. Operación y mejora continua** | Confiabilidad | CI/CD con tests; observabilidad (logs, métricas, alertas); runbook; backups; revisión trimestral de umbrales y del modelo; medición de impacto | continuo |

\* Estimaciones orientativas para 1–2 personas; deben ajustarse con la disponibilidad real del equipo y de Green Services.

### 4.3 Qué falta detallar (brechas de definición, no de código)
- **Definición real de cliente frío** y si varía por familia de producto (recurrente vs único).
- **Periodicidad de renovación** y política ante contratos vencidos con cliente activo.
- **Indicadores de éxito** acordados: p. ej. % de renovaciones a tiempo, reducción de clientes fríos, tasa de conversión de llamadas.
- **Significado del recurso «com»** (la ficha no lo precisa; no se ha interpretado).
- **Costo de un falso positivo vs falso negativo** para fijar el umbral con datos de negocio.
- **Calidad y profundidad histórica** de los datos reales (con 20 meses no hay estacionalidad anual comprobable).
- **Permisos y privacidad** de los datos de clientes.

### 4.4 Indicadores de éxito propuestos

| Indicador | Línea base (MVP) | Meta de producto |
| :--- | :-: | :-: |
| Recall de recompra a 30 d (prueba temporal) | 78 % (datos de prueba) | ≥ 75 % en datos reales |
| Precisión | 57 % | ≥ 65 % tras calibración y umbral por costo |
| Error absoluto medio del pronóstico mensual | no medido | menor que "último valor observado" |
| Tiempo de preparación del reporte comercial | manual (días) | < 5 min automático |
| Clientes fríos recuperados / contactados | n/d | definir con Comercial |

### 4.5 Riesgos principales

| Riesgo | Mitigación |
| :--- | :--- |
| Datos reales distintos de los de prueba: el modelo no generaliza | Reentrenar y re-evaluar antes de usar; no reutilizar umbral de prueba |
| Reglas de negocio no aceptadas por la empresa | Parámetros editables + validación con Comercial en Fase 1 |
| Falsos positivos (88 en prueba) saturan al equipo comercial | Limitar cola diaria y ordenar por valor esperado × probabilidad |
| Uso indebido de datos personales | Minimización, roles, auditoría y consentimiento documentado |
| Dependencia de un solo desarrollador | Documentación, pruebas automáticas y CI |

---

## 5. Memoria de desarrollo: qué se hizo, cómo y por qué

### 5.1 Cronología (repositorio Git, 21-nov-2026)

| Hora | Commit | Qué se hizo |
| :-: | :--- | :--- |
| 10:34 | `4f91b86` | MVP base: ingesta, TRM, vista 360, modelos, generador sintético, pruebas, CLI |
| 10:42 | `e60925c` | Documentación 01–05 (objetivos MoSCoW, arquitectura, pruebas, manual, bitácora) |
| 10:48 | `239da26` | Streamlit completo: explorador, objetivos, batería de pruebas en vivo |
| 10:51 | `6254434` | `index.html` autónomo para GitHub Pages |
| 10:57 | `7eab543` | Semáforos clicables, simulador, carga de CSV, descargas |
| 11:06 | `c516241` | Proyección Nov-2026, "caja blanca" del modelo, evidencias de pruebas |
| 11:21 | `44332cf` | Corrección del semáforo por recencia; criterio auditable por cliente |
| 11:29 | `2088c2d` | Variable `Estado_Cobertura`, manual Word de decisiones |

### 5.2 Arquitectura

```
data/raw (CSV) ─► data_loader (TRM, COP) ─► operaciones (vista 360, reglas)
                                         └► modelo_predictivo (fotos mensuales, logística)
                         ▼
        modelos_operativos (semáforo, cobertura, prob., TRM) ─► outputs/*.csv|json|xlsx
                         ▼
        app_operia.py (Streamlit)      build_index.py ─► index.html (GitHub Pages)
        validador.py + tests/  ◄── Casos_controlados.json
```

### 5.3 Decisiones de diseño y su justificación

| Decisión | Alternativa descartada | Razón | Consecuencia / deuda |
| :--- | :--- | :--- | :--- |
| Python estándar para el núcleo (csv, datetime) | Todo en pandas | Reproducible sin cuentas ni instalación (requisito de la guía) | Streamlit sí exige pandas/plotly |
| Regresión logística propia con descenso de gradiente | scikit-learn / boosting | Explicable, auditable, sin dependencias; la guía pide un modelo simple y comparable | Rendimiento limitado; modelo único para todos los productos |
| Partición temporal por cortes mensuales | Muestreo aleatorio | Evita fuga de información del futuro | Los mismos clientes reaparecen en distintos meses: mide seguimiento, no generalización a clientes nuevos (advertencia oficial) |
| Umbral 0.40 elegido en validación | 0.50 estándar | Priorizar recall (detectar recompras) | Más falsos positivos (88/360); no está justificado con costos reales |
| Línea base "compra en los últimos 30 d" | Sin comparación | Exigido por el reto: separar regla de IA | Gana en precisión por poco |
| Semáforo por recencia (≤ 30 / 31–89 / ≥ 90 d) | Etiquetas independientes de la guía | Petición del usuario tras detectar clientes con 0 días en "seguimiento" | Se perdió la etiqueta oficial "frecuente ≥ 8 ops" (ver sección 2) |
| `Estado_Cobertura` (Vigente / Próxima ≤ 45 d / Vencida / Sin cobertura) | Contadores sueltos de renovaciones | Responde a la petición de una variable clara | Debe gobernar la prioridad (H3) |
| Prioridad ALTA/MEDIA/NORMAL/BAJA | "MEDIA-ALTA" | Eliminar ambigüedad pedida por el usuario | Falta que el modelo influya en el orden (H4) |
| Dos interfaces (Streamlit + HTML estático) | Solo Streamlit | Streamlit requiere servidor; GitHub Pages permite verlo en línea | Duplicación de lógica en JS: riesgo de divergencia |
| Parámetros del modelo incrustados en dashboard | Leerlos de `metricas_modelo.json` | Rapidez | Deben leerse del JSON (deuda) |
| Datos sintéticos con `seed=212026` | Solo datos oficiales | Petición del usuario ("modelos para generar datos") | Contaminó `data/raw` (H1) |

### 5.4 Cómo funciona el cálculo (resumen reproducible)

1. **Importe:** `cantidad × precio × (1 − descuento/100)`; si USD, × TRM de la fecha; anuladas = 0.
2. **Recencia:** `corte (2026-10-31) − última compra confirmada`.
3. **Cobertura:** días entre `fecha_fin` y el corte → Próxima (0–45), Vigente (> 45), Vencida (< 0), Sin cobertura (sin contrato).
4. **Semáforo:** ≥ 90 d Frío (ALTA) · ≤ 30 d Frecuente · 31–89 d Base instalada; renovación/vencida eleva a MEDIA.
5. **Modelo:** z-score de [recencia, compras 30 d, compras 90 d, historial] → logit con pesos entrenados → sigmoide → P(compra en 30 d); decisión con θ = 0.40.
6. **Proyección:** Σ (P × ticket promedio) — *estimación no validada* (ver H5).

### 5.5 Errores encontrados y cómo se resolvieron

| Error | Solución |
| :--- | :--- |
| Clientes con 0 días en "seguimiento"; con muchos días en "frecuentes" | Reordenar la regla: la recencia decide el color; contratos solo modulan prioridad |
| Etiqueta "MEDIA-ALTA" ambigua | Escala simplificada |
| Puerto 8501 ocupado | Terminar el proceso y relanzar |
| Scripts largos en PowerShell fallaban | Generadores en Python (`build_index.py`, `generar_documento_word.py`) |
| Lectura de PDF del reto | Lectura por OCR/visión |
| Advertencias de escape en cadenas de Streamlit | Cadenas *raw* |

### 5.6 Mapa de archivos

| Ruta | Función |
| :--- | :--- |
| `src/data_loader.py` · `operaciones.py` | Ingesta, TRM, vista 360 |
| `src/modelo_predictivo.py` | Fotografías mensuales, entrenamiento y evaluación temporal |
| `src/modelos_operativos.py` | Semáforo, cobertura, probabilidad, consolidado |
| `src/validador.py` · `tests/` | Casos controlados e incidencias |
| `src/generador_datos_sinteticos.py` | Datos de prueba reproducibles |
| `app_operia.py` · `build_index.py` | Streamlit y sitio estático |
| `docs/01–07` y `.docx` | Documentación |

### 5.7 Cómo ejecutar y probar

```
pip install -r requirements.txt
python main.py --consolidar          # pipeline completo
python main.py --validar             # 6 casos + 7 incidencias
python -m unittest discover tests    # pruebas
streamlit run app_operia.py          # dashboard local
python build_index.py                # regenera el sitio estático
```

### 5.8 Limitaciones honestas
- Todos los resultados son sobre **datos de prueba**; no demuestran rendimiento real (así lo exige el paquete).
- No hay prueba independiente de "no ver el futuro" más allá de la construcción por cortes; falta un test automático.
- La proyección de noviembre no está validada.
- El modelo no usa producto, compras ni base instalada como variables.

---

## 6. Próximos pasos inmediatos (orden recomendado)
1. Restaurar datos oficiales y verificar hashes (H1).
2. Construir la vista desde `clientes.csv`; añadir "Sin compras" (H2).
3. Unificar prioridad en `Estado_Cobertura` y decidir el rol de la IA (H3, H4).
4. Generar todas las cifras desde `outputs/`; corregir "TRM Oficial" (H5).
5. Mostrar matriz de confusión y añadir backtest MAE del pronóstico.
6. Agregar tests de reglas, no-fuga temporal y 120 clientes.
7. Sesión de validación con Green Services para cerrar las preguntas de la sección 4.3.
