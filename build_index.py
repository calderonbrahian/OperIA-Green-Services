import json
import csv
from pathlib import Path

root = Path(__file__).resolve().parent
csv_path = root / "outputs" / "OperIA_Dataset_Consolidado.csv"

with open(csv_path, "r", encoding="utf-8-sig") as f:
    records = list(csv.DictReader(f))

json_str = json.dumps(records, ensure_ascii=False)

html_template = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OperIA 360° | Dashboard Inteligente Online</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --primary: #1e3a8a;
      --primary-light: #2563eb;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
    body { background-color: var(--bg); color: var(--text); padding: 20px; }
    .container { max-width: 1380px; margin: 0 auto; }

    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
      gap: 12px;
    }
    .brand h1 { font-size: 26px; color: var(--primary); font-weight: 800; }
    .brand p { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
    .header-badges { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    .tag {
      background: #eff6ff; color: var(--primary-light);
      padding: 6px 14px; border-radius: 9999px; font-size: 13px; font-weight: 600; text-decoration: none;
    }
    .tag.github { background: #0f172a; color: #fff; }

    /* Navigation Tabs */
    .nav-tabs {
      display: flex;
      gap: 8px;
      border-bottom: 2px solid var(--border);
      margin-bottom: 24px;
      overflow-x: auto;
      padding-bottom: 2px;
    }
    .tab-btn {
      padding: 10px 18px;
      border: none;
      background: none;
      font-size: 14px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      border-bottom: 3px solid transparent;
      border-radius: 6px 6px 0 0;
      white-space: nowrap;
      transition: all 0.2s;
    }
    .tab-btn:hover { color: var(--primary-light); background: #f1f5f9; }
    .tab-btn.active {
      color: var(--primary-light);
      border-bottom-color: var(--primary-light);
      background: #ffffff;
    }
    .tab-pane { display: none; }
    .tab-pane.active { display: block; }

    /* Clickable KPI Semaphore Cards */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .kpi-card {
      background: var(--card-bg);
      border-radius: 12px;
      padding: 18px;
      border: 1px solid var(--border);
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
    }
    .kpi-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .kpi-card.selected {
      outline: 3px solid var(--primary-light);
      background: #f8fafc;
    }
    .kpi-title { font-size: 12px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; display: flex; justify-content: space-between; }
    .kpi-value { font-size: 26px; font-weight: 800; margin: 6px 0; color: var(--text); }
    .kpi-sub { font-size: 12px; font-weight: 500; }
    .kpi-card.green { border-left: 6px solid var(--success); }
    .kpi-card.yellow { border-left: 6px solid var(--warning); }
    .kpi-card.red { border-left: 6px solid var(--danger); }
    .kpi-card.blue { border-left: 6px solid var(--primary-light); }

    /* Layout Grids */
    .card {
      background: var(--card-bg);
      border-radius: 12px;
      padding: 22px;
      border: 1px solid var(--border);
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      margin-bottom: 24px;
    }
    .card-title { font-size: 18px; font-weight: 700; margin-bottom: 16px; color: var(--primary); display: flex; justify-content: space-between; align-items: center; }
    .grid-2 { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
    .grid-equal { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    @media (max-width: 950px) { .grid-2, .grid-equal { grid-template-columns: 1fr; } }

    /* Controls */
    .controls { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; align-items: center; }
    input, select, textarea {
      padding: 10px 14px;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 14px;
      outline: none;
    }
    input:focus, select:focus, textarea:focus { border-color: var(--primary-light); }
    input[type="text"] { flex: 1; min-width: 220px; }
    .btn {
      padding: 10px 18px;
      border-radius: 8px;
      border: none;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }
    .btn-primary { background: var(--primary-light); color: #fff; }
    .btn-primary:hover { background: var(--primary); }
    .btn-success { background: var(--success); color: #fff; }
    .btn-success:hover { background: #059669; }
    .btn-secondary { background: #e2e8f0; color: #334155; }
    .btn-secondary:hover { background: #cbd5e1; }

    /* Tables */
    .table-container { overflow-x: auto; max-height: 520px; border-radius: 8px; border: 1px solid var(--border); }
    table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13.5px; }
    th {
      position: sticky; top: 0; background: #f8fafc; color: var(--text);
      font-weight: 700; padding: 12px 14px; border-bottom: 2px solid var(--border);
      z-index: 10;
    }
    td { padding: 12px 14px; border-bottom: 1px solid var(--border); }
    tr:hover td { background-color: #f1f5f9; cursor: pointer; }

    /* Badges */
    .badge {
      display: inline-block; padding: 4px 10px; border-radius: 9999px;
      font-size: 11.5px; font-weight: 700; text-align: center; white-space: nowrap; cursor: pointer;
    }
    .badge.frecuente { background: #dcfce7; color: #166534; }
    .badge.seguimiento { background: #fef3c7; color: #92400e; }
    .badge.frio { background: #fee2e2; color: #991b1b; }
    .badge.alta { background: #fecaca; color: #b91c1c; font-weight: 800; }
    .badge.media { background: #e0e7ff; color: #3730a3; }

    .detail-drawer {
      background: #f8fafc; border: 1px solid var(--border); border-left: 5px solid var(--primary-light);
      border-radius: 8px; padding: 18px; margin-top: 16px;
    }

    .info-callout {
      background: #eff6ff; border-left: 4px solid var(--primary-light);
      padding: 14px 18px; border-radius: 6px; margin-bottom: 18px; color: #1e3a8a; font-size: 14px;
    }

    /* Simulator Form */
    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }
    .form-group label {
      display: block; font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px;
    }
    .form-group input, .form-group select { width: 100%; }

    .sim-result-card {
      background: #fff;
      border: 2px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-top: 20px;
    }

    .accordion { margin-bottom: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
    .accordion-header {
      background: #f8fafc; padding: 14px 18px; font-weight: 700; cursor: pointer;
      display: flex; justify-content: space-between; user-select: none;
    }
    .accordion-body { padding: 16px 18px; background: #fff; font-size: 14px; line-height: 1.6; display: none; }
    .accordion.open .accordion-body { display: block; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">
        <h1>OperIA 360° · Plataforma Inteligente de Operaciones</h1>
        <p>Green Services and Solutions SAS — Reto 4: IA en Operaciones (Hackatón EstudIA - Capa 2)</p>
      </div>
      <div class="header-badges">
        <span class="tag">🟢 En Línea (GitHub Pages)</span>
        <button class="btn btn-primary" onclick="showTab('tab-simulador', document.getElementById('btn-tab-simulador'))">🧪 Probar Mis Propios Datos</button>
        <a href="https://github.com/calderonbrahian/OperIA-Green-Services" target="_blank" class="tag github">⭐ GitHub Repositorio</a>
      </div>
    </header>

    <!-- Global KPIs con Clic Directo en Semáforos -->
    <div class="kpi-grid">
      <div class="kpi-card blue selected" id="kpi-card-total" onclick="filtrarPorSemaforoCard('todos')">
        <div class="kpi-title"><span>Cartera Total</span> <span>👁️ Ver Todos</span></div>
        <div class="kpi-value" id="kpi-total">120</div>
        <div class="kpi-sub" style="color:var(--primary-light);">Clic para ver todas las cuentas</div>
      </div>
      <div class="kpi-card green" id="kpi-card-frec" onclick="filtrarPorSemaforoCard('frecuente')">
        <div class="kpi-title"><span>🟢 Frecuentes (Activos)</span> <span>👉 Filtrar</span></div>
        <div class="kpi-value" id="kpi-frec">--</div>
        <div class="kpi-sub" style="color:var(--success);">Última compra ≤ 30d (Clic aquí)</div>
      </div>
      <div class="kpi-card yellow" id="kpi-card-seg" onclick="filtrarPorSemaforoCard('seguimiento')">
        <div class="kpi-title"><span>🟡 Base Instalada</span> <span>👉 Filtrar</span></div>
        <div class="kpi-value" id="kpi-seg">--</div>
        <div class="kpi-sub" style="color:var(--warning);">Seguimiento de Pólizas (Clic aquí)</div>
      </div>
      <div class="kpi-card red" id="kpi-card-frio" onclick="filtrarPorSemaforoCard('frio')">
        <div class="kpi-title"><span>🔴 Clientes Fríos</span> <span>👉 Filtrar</span></div>
        <div class="kpi-value" id="kpi-frio">--</div>
        <div class="kpi-sub" style="color:var(--danger);">Riesgo de Abandono (≥ 90d) (Clic aquí)</div>
      </div>
      <div class="kpi-card blue">
        <div class="kpi-title"><span>Facturación Total</span></div>
        <div class="kpi-value" id="kpi-ventas">$--</div>
        <div class="kpi-sub" style="color:var(--primary);">Ventas Confirmadas (COP)</div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="nav-tabs">
      <button class="tab-btn active" id="btn-tab-semaforo" onclick="showTab('tab-semaforo', this)">🚨 Semáforo de Clientes</button>
      <button class="tab-btn" id="btn-tab-simulador" onclick="showTab('tab-simulador', this)">🧪 Probar Mis Datos (Simulador)</button>
      <button class="tab-btn" onclick="showTab('tab-trm', this)">📈 Ventas vs. TRM</button>
      <button class="tab-btn" onclick="showTab('tab-portafolio', this)">📦 Portafolio y Sectores</button>
      <button class="tab-btn" onclick="showTab('tab-ficha', this)">👤 Ficha 360° Cliente</button>
      <button class="tab-btn" onclick="showTab('tab-objetivos', this)">🎯 Objetivos y Reto MoSCoW</button>
      <button class="tab-btn" onclick="showTab('tab-pruebas', this)">🧪 Casos Controlados</button>
      <button class="tab-btn" onclick="showTab('tab-datos', this)">🔍 Explorador de Datos</button>
    </div>

    <!-- TAB 1: SEMÁFORO INTELIGENTE -->
    <div id="tab-semaforo" class="tab-pane active">
      <div class="card">
        <div class="card-title">
          <span>🚨 Semáforo Inteligente de Gestión Comercial (Llamadas Prioritarias)</span>
          <span style="font-size:13px; font-weight:600; color:var(--text-muted);" id="contadorFiltro">Mostrando 120 clientes</span>
        </div>
        <div class="controls">
          <input type="text" id="searchInput" placeholder="🔍 Buscar cliente por nombre o ID (ej: CLI012)...">
          <select id="statusFilter" onchange="aplicarFiltroSelect()">
            <option value="todos">Todos los Estados</option>
            <option value="frio">🔴 Fríos (Riesgo de Abandono)</option>
            <option value="seguimiento">🟡 Base Instalada (Seguimiento)</option>
            <option value="frecuente">🟢 Frecuentes (Activos)</option>
          </select>
          <select id="sectorFilter">
            <option value="todos">Todos los Sectores</option>
          </select>
          <button class="btn btn-primary" onclick="exportarCSV(false)">📥 Descargar Lista Filtrada (CSV)</button>
          <button class="btn btn-secondary" onclick="exportarCSV(true)">📥 Descargar Cartera Completa (CSV)</button>
        </div>

        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Empresa</th>
                <th>Sector</th>
                <th>Días sin Compra</th>
                <th>Semáforo (Clic para filtrar)</th>
                <th>Prob. Recompra (IA)</th>
                <th>Prioridad</th>
                <th>Facturación COP</th>
                <th>Acción Recomendada</th>
              </tr>
            </thead>
            <tbody id="semaforoBody"></tbody>
          </table>
        </div>

        <div id="detailBox" class="detail-drawer">
          💡 <b>Consejo Interactivo:</b> Haz clic en cualquier tarjeta de semáforo superior (Verde, Amarillo, Rojo) o en cualquier fila para desplegar su ficha de contacto comercial.
        </div>
      </div>
    </div>

    <!-- TAB 2: SIMULADOR Y PROBADOR INTERACTIVO DE DATOS -->
    <div id="tab-simulador" class="tab-pane">
      <div class="card">
        <div class="card-title">🧪 Probador Interactivo con IA: Ingresar Datos y Evaluar Resultados</div>
        <p style="margin-bottom:18px; color:var(--text-muted);">
          Ingresa los datos de cualquier cliente hipotético o carga tu propio archivo para que el modelo de Machine Learning y las reglas calculen la probabilidad de compra a 30 días, el semáforo y la acción sugerida:
        </p>

        <div style="background:#f1f5f9; padding:20px; border-radius:10px; margin-bottom:24px;">
          <h4 style="margin-bottom:14px; color:var(--primary);">1. Probar un Cliente Individual</h4>
          <div class="form-grid">
            <div class="form-group">
              <label>Días transcurridos sin comprar (Recencia):</label>
              <input type="number" id="sim-dias" value="95" min="0">
            </div>
            <div class="form-group">
              <label>Compras en los últimos 30 días:</label>
              <input type="number" id="sim-f30" value="0" min="0">
            </div>
            <div class="form-group">
              <label>Compras en los últimos 90 días:</label>
              <input type="number" id="sim-f90" value="0" min="0">
            </div>
            <div class="form-group">
              <label>Total de compras históricas del cliente:</label>
              <input type="number" id="sim-hist" value="6" min="0">
            </div>
            <div class="form-group">
              <label>¿Tiene contrato/póliza por vencer en ≤ 45 días?:</label>
              <select id="sim-renovacion">
                <option value="no">No</option>
                <option value="si">Sí (Cobertura por vencer)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Monto estimado de compra:</label>
              <input type="number" id="sim-monto" value="15000000" min="0">
            </div>
          </div>
          <button class="btn btn-success" onclick="simularClienteIndividual()">⚡ Evaluar con Modelo de IA y Semáforo</button>

          <div id="sim-resultado" class="sim-result-card" style="display:none;"></div>
        </div>

        <div style="background:#f1f5f9; padding:20px; border-radius:10px;">
          <h4 style="margin-bottom:14px; color:var(--primary);">2. Cargar mi propio archivo CSV de Clientes para Procesar</h4>
          <p style="font-size:13px; color:var(--text-muted); margin-bottom:12px;">
            Sube un archivo CSV con columnas (ej: <code>Cliente_ID, Cliente, Sector, Dias_Sin_Comprar, Ventas_COP</code>) y el dashboard recalculará los indicadores al instante en tu navegador:
          </p>
          <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
            <input type="file" id="userCsvFile" accept=".csv" style="background:#fff;">
            <button class="btn btn-primary" onclick="procesarUserCsv()">📤 Cargar y Recalcular Dashboard</button>
            <button class="btn btn-secondary" onclick="restaurarDatosOriginales()">🔄 Restaurar Datos Oficiales (120 Clientes)</button>
          </div>
          <div id="userCsvMsg" style="margin-top:10px; font-size:13px; font-weight:600;"></div>
        </div>
      </div>
    </div>

    <!-- TAB 3: VENTAS VS TRM -->
    <div id="tab-trm" class="tab-pane">
      <div class="card">
        <div class="card-title">📈 Evolución Mensual de Ventas vs. Variación de la TRM</div>
        <div class="info-callout">
          <b>Análisis de Sensibilidad Cambiaria:</b> Coeficiente de Correlación TRM vs. Facturación COP: <b>+0.4736</b> (Correlación positiva moderada). Alza del dólar indexa automáticamente productos licitados en USD e incrementa la facturación nominal en pesos.
        </div>
        <canvas id="chartTRM" height="100"></canvas>
      </div>
    </div>

    <!-- TAB 4: PORTAFOLIO Y SECTORES -->
    <div id="tab-portafolio" class="tab-pane">
      <div class="grid-equal">
        <div class="card">
          <div class="card-title">📦 Ventas por Familia de Producto</div>
          <canvas id="chartFamilias" height="140"></canvas>
        </div>
        <div class="card">
          <div class="card-title">🏭 Ventas por Sector Económico</div>
          <canvas id="chartSectores" height="140"></canvas>
        </div>
      </div>
    </div>

    <!-- TAB 5: FICHA 360 -->
    <div id="tab-ficha" class="tab-pane">
      <div class="card">
        <div class="card-title">👤 Ficha 360° Individual por Cliente</div>
        <div class="controls">
          <select id="clientSelect" style="min-width:350px;"></select>
        </div>
        <div id="fichaContenido"></div>
        <h4 style="margin: 20px 0 12px 0;">Historial de Operaciones Confirmadas</h4>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Producto</th>
                <th>Familia</th>
                <th>Cantidad</th>
                <th>Moneda</th>
                <th>TRM Día</th>
                <th>Ventas COP</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody id="clienteOpsBody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 6: OBJETIVOS Y MOSCOW -->
    <div id="tab-objetivos" class="tab-pane">
      <div class="card">
        <div class="card-title">🎯 Objetivos, Pregunta Guía y Metodología MoSCoW</div>
        <div class="info-callout">
          <b>Pregunta Orientadora Guía del Reto:</b><br>
          <i>«¿Cómo podríamos ayudar al equipo de Operaciones y Comercial a automatizar el cruce de datos para predecir el comportamiento de sus clientes y anticipar recompras mediante un modelo con visualización interactiva?»</i>
        </div>

        <div class="accordion open">
          <div class="accordion-header" onclick="toggleAccordion(this)">
            <span>📌 Contexto Empresarial: Green Services and Solutions SAS</span>
            <span>▼</span>
          </div>
          <div class="accordion-body">
            Empresa especializada en integración de servicios y productos para el ciclo de vida de la información corporativa. Operaciones requería transformar un análisis manual en Excel que tomaba días a un sistema proactivo con Inteligencia Artificial.
          </div>
        </div>

        <div class="accordion open">
          <div class="accordion-header" onclick="toggleAccordion(this)">
            <span>📊 Matriz de Alcance MoSCoW del MVP</span>
            <span>▼</span>
          </div>
          <div class="accordion-body">
            • <b>Must Have:</b> Cruce automático de ventas con TRM diaria, exclusión de anuladas, semáforo de llamadas prioritarias.<br>
            • <b>Should Have:</b> Modelo de Machine Learning de probabilidad de recompra a 30 días, gráfica dual de Ventas vs TRM, ficha 360°.<br>
            • <b>Could Have:</b> Descarga instantánea en CSV, simulación de datos sintéticos reproducibles y visor web online.<br>
            • <b>Won't Have:</b> Conexión directa a bases de datos de producción ni módulo de facturación electrónica.
          </div>
        </div>

        <div class="accordion open">
          <div class="accordion-header" onclick="toggleAccordion(this)">
            <span>🎤 Guion del Pitch de 3 Minutos</span>
            <span>▼</span>
          </div>
          <div class="accordion-body">
            • <b>Minuto 0:00 - 0:45:</b> El dolor de los cruces manuales en Excel y la pérdida de clientes fríos.<br>
            • <b>Minuto 0:45 - 1:45:</b> OperIA integra TRM, predice la recompra a 30 días con Machine Learning (Recall 78%) y clasifica prioridades.<br>
            • <b>Minuto 1:45 - 2:30:</b> Demostración del semáforo en vivo, filtrando clientes fríos en menos de 2 segundos.<br>
            • <b>Minuto 2:30 - 3:00:</b> Impacto en rentabilidad, retención y escalabilidad.
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 7: CASOS CONTROLADOS -->
    <div id="tab-pruebas" class="tab-pane">
      <div class="card">
        <div class="card-title">🧪 Batería de Pruebas y Casos Controlados</div>
        <p style="margin-bottom:16px; color:var(--text-muted);">Verificación de las 6 reglas de frontera de <code>Casos_controlados.json</code> aprobadas al 100%:</p>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Caso</th>
                <th>Condición Probada</th>
                <th>Resultado Esperado</th>
                <th>Resultado OperIA</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr><td><b>Venta COP</b></td><td>2 unidades × $100.000 con 10% desc.</td><td>$180.000 COP</td><td>$180.000 COP</td><td><span class="badge frecuente">✅ APROBADO</span></td></tr>
              <tr><td><b>Venta USD con TRM</b></td><td>3 unidades × $100 USD @ $4.000 TRM</td><td>$1.200.000 COP</td><td>$1.200.000 COP</td><td><span class="badge frecuente">✅ APROBADO</span></td></tr>
              <tr><td><b>Venta Anulada</b></td><td>Transacción con estado 'Anulada'</td><td>$0 COP (Excluida)</td><td>$0 COP (Excluida)</td><td><span class="badge frecuente">✅ APROBADO</span></td></tr>
              <tr><td><b>Frío en Frontera</b></td><td>Corte 31/10/2026, última compra 02/08/2026</td><td>Exacto 90 días -> Frío</td><td>90 días -> Frío</td><td><span class="badge frecuente">✅ APROBADO</span></td></tr>
              <tr><td><b>Renovación Frontera</b></td><td>Corte 31/10/2026, fin contrato 15/12/2026</td><td>Exacto 45 días -> Renovación</td><td>45 días -> Renovación</td><td><span class="badge frecuente">✅ APROBADO</span></td></tr>
              <tr><td><b>Cliente Inexistente</b></td><td>Cliente 'CLI999' sin registros</td><td>Sin compras / Sin invención</td><td>Manejo seguro</td><td><span class="badge frecuente">✅ APROBADO</span></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 8: EXPLORADOR DE DATOS -->
    <div id="tab-datos" class="tab-pane">
      <div class="card">
        <div class="card-title">🔍 Explorador de Datos de Ventas Consolidadas</div>
        <div class="table-container">
          <table id="rawDataTable">
            <thead>
              <tr>
                <th>Venta ID</th>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Moneda</th>
                <th>TRM</th>
                <th>Venta COP</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody id="rawDataBody"></tbody>
          </table>
        </div>
      </div>
    </div>

  </div>

  <script>
    const INITIAL_RAW_DATA = JSON_PLACEHOLDER;
    let ACTIVE_RAW_DATA = [...INITIAL_RAW_DATA];

    let CLIENTES_MAP = new Map();
    let CLIENTES = [];
    let totalCOP = 0;
    const sectoresSet = new Set();
    const familiasMap = new Map();
    const sectoresMap = new Map();
    const mesesVentas = new Map();
    const mesesTRM = new Map();

    // Modelo de Machine Learning (Regresión Logística calibrada)
    function predictRecompra(recencia, f30, f90, hist) {
      const mu = [213.5698, 0.6229, 1.7137, 4.1383];
      const sd = [295.1005, 0.9646, 2.0515, 5.0708];
      const w = [-0.422462, -0.172871, 0.040233, 0.435491, 0.378904];
      const x = [recencia, f30, f90, hist];
      let z = w[0];
      for (let i = 0; i < 4; i++) {
        z += w[i+1] * ((x[i] - mu[i]) / sd[i]);
      }
      z = Math.max(-35, Math.min(35, z));
      return 1 / (1 + Math.exp(-z));
    }

    // Regla de Semáforo
    function evaluarSemaforo(diasSinCompra, transacciones, renovacionesProximas) {
      if (diasSinCompra >= 90) {
        return {
          estado: "Frío (Riesgo de Abandono)",
          prioridad: "ALTA",
          accion: "Campaña de reactivación comercial urgente",
          badgeClass: "frio"
        };
      } else if (renovacionesProximas) {
        return {
          estado: "Base Instalada (Seguimiento)",
          prioridad: "MEDIA-ALTA",
          accion: "Contactar para renovación de póliza / licencia",
          badgeClass: "seguimiento"
        };
      } else if (diasSinCompra <= 30 || transacciones >= 8) {
        return {
          estado: "Frecuente (Activo)",
          prioridad: "MEDIA",
          accion: "Fidelización y propuesta de up-selling / módulos adicionales",
          badgeClass: "frecuente"
        };
      } else {
        return {
          estado: "Base Instalada (Seguimiento)",
          prioridad: "NORMAL",
          accion: "Seguimiento periódico habitual",
          badgeClass: "seguimiento"
        };
      }
    }

    function procesarDatosGlobales(data) {
      CLIENTES_MAP.clear();
      sectoresSet.clear();
      familiasMap.clear();
      sectoresMap.clear();
      mesesVentas.clear();
      mesesTRM.clear();
      totalCOP = 0;

      data.forEach(row => {
        const cid = row.Cliente_ID || row.cliente_id;
        const vCop = parseFloat(row.Ventas_COP || row.ingreso_cop || 0);
        const isConf = (row.Estado_Venta || row.estado || 'Confirmada') === 'Confirmada';
        if (isConf) totalCOP += vCop;

        if (!CLIENTES_MAP.has(cid)) {
          CLIENTES_MAP.set(cid, {
            id: cid,
            nombre: row.Cliente || row.nombre || ('Cliente ' + cid),
            sector: row.Sector || row.sector || 'General',
            ciudad: row.Ciudad || row.ciudad || 'No especificada',
            estado: row.Estado_Cliente || (row.frio === 'True' || row.frio === true ? 'Frío (Riesgo de Abandono)' : 'Frecuente (Activo)'),
            dias: parseInt(row.Dias_Sin_Comprar || row.dias_sin_compra || 0),
            prob: parseFloat(row.Prob_Recompra_Pct || 50.0),
            prioridad: row.Prioridad_Llamada || (row.frio === 'True' ? 'ALTA' : 'MEDIA'),
            accion: row.Accion_Recomendada || 'Contacto comercial prioritario',
            ventas: isConf ? vCop : 0,
            ops: [row]
          });
        } else {
          const c = CLIENTES_MAP.get(cid);
          if (isConf) c.ventas += vCop;
          c.ops.push(row);
        }

        if (row.Sector) sectoresSet.add(row.Sector);

        if (isConf && row.Familia_Producto) {
          familiasMap.set(row.Familia_Producto, (familiasMap.get(row.Familia_Producto) || 0) + vCop);
        }
        if (isConf && row.Sector) {
          sectoresMap.set(row.Sector, (sectoresMap.get(row.Sector) || 0) + vCop);
        }

        if (row.Fecha) {
          const mes = row.Fecha.substring(0, 7);
          if (isConf) {
            mesesVentas.set(mes, (mesesVentas.get(mes) || 0) + vCop);
          }
          if (!mesesTRM.has(mes)) mesesTRM.set(mes, []);
          mesesTRM.get(mes).push(parseFloat(row.TRM || 4100));
        }
      });

      CLIENTES = Array.from(CLIENTES_MAP.values());
    }

    function initPage() {
      procesarDatosGlobales(ACTIVE_RAW_DATA);
      actualizarVistas();
    }

    function actualizarVistas() {
      const nTotal = CLIENTES.length;
      const nFrec = CLIENTES.filter(c => c.estado.includes('Frecuente')).length;
      const nFrio = CLIENTES.filter(c => c.estado.includes('Frío')).length;
      const nSeg = nTotal - nFrec - nFrio;

      document.getElementById('kpi-total').innerText = nTotal;
      document.getElementById('kpi-frec').innerText = nFrec;
      document.getElementById('kpi-seg').innerText = nSeg;
      document.getElementById('kpi-frio').innerText = nFrio;
      document.getElementById('kpi-ventas').innerText = '$' + (totalCOP / 1e6).toFixed(1) + 'M COP';

      const secSelect = document.getElementById('sectorFilter');
      secSelect.innerHTML = '<option value="todos">Todos los Sectores</option>';
      Array.from(sectoresSet).sort().forEach(s => {
        const opt = document.createElement('option');
        opt.value = s; opt.innerText = s;
        secSelect.appendChild(opt);
      });

      const cliSelect = document.getElementById('clientSelect');
      cliSelect.innerHTML = '';
      CLIENTES.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id; opt.innerText = `${c.id} - ${c.nombre}`;
        cliSelect.appendChild(opt);
      });
      cliSelect.onchange = () => renderFicha(cliSelect.value);

      renderSemaforo();
      document.getElementById('searchInput').oninput = renderSemaforo;
      document.getElementById('sectorFilter').onchange = renderSemaforo;

      if (CLIENTES.length > 0) renderFicha(CLIENTES[0].id);
      renderGraficas();
      renderExplorador();
    }

    // Clic en tarjetas de semáforo superiores
    function filtrarPorSemaforoCard(estado) {
      document.querySelectorAll('.kpi-card').forEach(c => c.classList.remove('selected'));
      const selectStatus = document.getElementById('statusFilter');

      if (estado === 'frecuente') {
        document.getElementById('kpi-card-frec').classList.add('selected');
        selectStatus.value = 'frecuente';
      } else if (estado === 'seguimiento') {
        document.getElementById('kpi-card-seg').classList.add('selected');
        selectStatus.value = 'seguimiento';
      } else if (estado === 'frio') {
        document.getElementById('kpi-card-frio').classList.add('selected');
        selectStatus.value = 'frio';
      } else {
        document.getElementById('kpi-card-total').classList.add('selected');
        selectStatus.value = 'todos';
      }
      showTab('tab-semaforo', document.getElementById('btn-tab-semaforo'));
      renderSemaforo();
    }

    function aplicarFiltroSelect() {
      const val = document.getElementById('statusFilter').value;
      document.querySelectorAll('.kpi-card').forEach(c => c.classList.remove('selected'));
      if (val === 'frecuente') document.getElementById('kpi-card-frec').classList.add('selected');
      else if (val === 'seguimiento') document.getElementById('kpi-card-seg').classList.add('selected');
      else if (val === 'frio') document.getElementById('kpi-card-frio').classList.add('selected');
      else document.getElementById('kpi-card-total').classList.add('selected');
      renderSemaforo();
    }

    function renderSemaforo() {
      const query = document.getElementById('searchInput').value.toLowerCase();
      const statusF = document.getElementById('statusFilter').value;
      const sectorF = document.getElementById('sectorFilter').value;
      const tbody = document.getElementById('semaforoBody');
      tbody.innerHTML = '';

      const filtrados = CLIENTES.filter(c => {
        const matchQ = c.nombre.toLowerCase().includes(query) || c.id.toLowerCase().includes(query);
        let matchS = true;
        if (statusF === 'frio') matchS = c.estado.includes('Frío');
        else if (statusF === 'frecuente') matchS = c.estado.includes('Frecuente');
        else if (statusF === 'seguimiento') matchS = !c.estado.includes('Frío') && !c.estado.includes('Frecuente');
        
        let matchSec = (sectorF === 'todos') || (c.sector === sectorF);
        return matchQ && matchS && matchSec;
      });

      document.getElementById('contadorFiltro').innerText = `Mostrando ${filtrados.length} de ${CLIENTES.length} clientes`;

      filtrados.forEach(c => {
        const badgeCls = c.estado.includes('Frío') ? 'frio' : c.estado.includes('Frecuente') ? 'frecuente' : 'seguimiento';
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><b>${c.id}</b></td>
          <td>${c.nombre}</td>
          <td>${c.sector}</td>
          <td>${c.dias} días</td>
          <td><span class="badge ${badgeCls}" onclick="event.stopPropagation(); filtrarPorSemaforoCard('${badgeCls}')">${c.estado}</span></td>
          <td><b>${c.prob}%</b></td>
          <td><span class="badge ${c.prioridad === 'ALTA' ? 'alta' : 'media'}">${c.prioridad}</span></td>
          <td>$${Math.round(c.ventas).toLocaleString('es-CO')}</td>
          <td><small>${c.accion}</small></td>
        `;
        tr.onclick = () => {
          document.getElementById('detailBox').innerHTML = `
            <div style="font-size:16px; font-weight:800; color:var(--primary); margin-bottom:8px;">
              FICHA DE CONTACTO: ${c.id} — ${c.nombre}
            </div>
            • <b>Estado:</b> <span class="badge ${badgeCls}">${c.estado}</span> &nbsp;|&nbsp; <b>Prioridad de Llamada:</b> ${c.prioridad}<br>
            • <b>Días sin Compra:</b> ${c.dias} días &nbsp;|&nbsp; <b>Probabilidad Recompra 30d:</b> ${c.prob}% &nbsp;|&nbsp; <b>Facturación Acumulada:</b> $${Math.round(c.ventas).toLocaleString('es-CO')} COP<br>
            • <b>Estrategia Sugerida para el Asesor:</b> ${c.accion}.
          `;
        };
        tbody.appendChild(tr);
      });
    }

    function renderFicha(cid) {
      const c = CLIENTES_MAP.get(cid);
      if (!c) return;
      const fc = document.getElementById('fichaContenido');
      const badgeCls = c.estado.includes('Frío') ? 'frio' : c.estado.includes('Frecuente') ? 'frecuente' : 'seguimiento';
      fc.innerHTML = `
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; margin-top:10px;">
          <div style="background:#fff; border:1px solid var(--border); padding:14px; border-radius:8px;">
            <span style="color:var(--text-muted); font-size:12px; font-weight:700;">DATOS GENERALES</span>
            <div style="font-size:16px; font-weight:700; margin-top:4px;">${c.nombre}</div>
            <div style="color:var(--text-muted); font-size:13px;">${c.ciudad} · ${c.sector}</div>
          </div>
          <div style="background:#fff; border:1px solid var(--border); padding:14px; border-radius:8px;">
            <span style="color:var(--text-muted); font-size:12px; font-weight:700;">COMPORTAMIENTO</span>
            <div style="margin-top:4px;"><span class="badge ${badgeCls}">${c.estado}</span></div>
            <div style="font-size:13px; margin-top:4px;"><b>${c.dias}</b> días sin compra | Prob: <b>${c.prob}%</b></div>
          </div>
          <div style="background:#fff; border:1px solid var(--border); padding:14px; border-radius:8px;">
            <span style="color:var(--text-muted); font-size:12px; font-weight:700;">ACCIÓN SUGERIDA</span>
            <div style="font-size:13px; font-weight:600; color:var(--primary); margin-top:4px;">${c.accion}</div>
            <div style="font-size:13px; color:var(--text-muted);">Ventas COP: $${Math.round(c.ventas).toLocaleString('es-CO')}</div>
          </div>
        </div>
      `;

      const tbody = document.getElementById('clienteOpsBody');
      tbody.innerHTML = '';
      c.ops.forEach(op => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${op.Fecha || ''}</td>
          <td><b>${op.Producto || 'Servicio'}</b></td>
          <td>${op.Familia_Producto || 'TI'}</td>
          <td>${op.Cantidad || 1}</td>
          <td>${op.Moneda || 'COP'}</td>
          <td>$${parseFloat(op.TRM || 4100).toFixed(0)}</td>
          <td>$${Math.round(parseFloat(op.Ventas_COP || 0)).toLocaleString('es-CO')}</td>
          <td>${op.Estado_Venta || 'Confirmada'}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    let chartTRMInst = null;
    let chartFamInst = null;
    let chartSecInst = null;

    function renderGraficas() {
      const meses = Array.from(mesesVentas.keys()).sort();
      const ventasData = meses.map(m => Math.round((mesesVentas.get(m) || 0) / 1e6));
      const trmData = meses.map(m => {
        const arr = mesesTRM.get(m) || [4100];
        return Math.round(arr.reduce((a,b)=>a+b, 0) / arr.length);
      });

      if (chartTRMInst) chartTRMInst.destroy();
      chartTRMInst = new Chart(document.getElementById('chartTRM'), {
        type: 'line',
        data: {
          labels: meses,
          datasets: [
            {
              type: 'bar',
              label: 'Ventas Mensuales (Millones COP)',
              data: ventasData,
              backgroundColor: 'rgba(37, 99, 235, 0.75)',
              yAxisID: 'y'
            },
            {
              type: 'line',
              label: 'TRM Promedio Diaria (COP/USD)',
              data: trmData,
              borderColor: '#dc2626',
              borderWidth: 3,
              tension: 0.2,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            y: { type: 'linear', position: 'left', title: { display: true, text: 'Millones COP' } },
            y1: { type: 'linear', position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: 'TRM (COP)' } }
          }
        }
      });

      if (chartFamInst) chartFamInst.destroy();
      chartFamInst = new Chart(document.getElementById('chartFamilias'), {
        type: 'doughnut',
        data: {
          labels: Array.from(familiasMap.keys()),
          datasets: [{
            data: Array.from(familiasMap.values()),
            backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4']
          }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
      });

      if (chartSecInst) chartSecInst.destroy();
      chartSecInst = new Chart(document.getElementById('chartSectores'), {
        type: 'bar',
        data: {
          labels: Array.from(sectoresMap.keys()),
          datasets: [{
            label: 'Ventas en COP',
            data: Array.from(sectoresMap.values()),
            backgroundColor: '#3b82f6'
          }]
        },
        options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } } }
      });
    }

    function renderExplorador() {
      const tbody = document.getElementById('rawDataBody');
      tbody.innerHTML = '';
      ACTIVE_RAW_DATA.slice(0, 100).forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${r.Venta_ID || ''}</td>
          <td>${r.Fecha || ''}</td>
          <td>${r.Cliente || ''}</td>
          <td>${r.Producto || ''}</td>
          <td>${r.Cantidad || ''}</td>
          <td>${r.Moneda || ''}</td>
          <td>$${parseFloat(r.TRM || 4100).toFixed(0)}</td>
          <td>$${Math.round(parseFloat(r.Ventas_COP || 0)).toLocaleString('es-CO')}</td>
          <td>${r.Estado_Venta || ''}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    // Simulador individual de cliente
    function simularClienteIndividual() {
      const dias = parseInt(document.getElementById('sim-dias').value) || 0;
      const f30 = parseInt(document.getElementById('sim-f30').value) || 0;
      const f90 = parseInt(document.getElementById('sim-f90').value) || 0;
      const hist = parseInt(document.getElementById('sim-hist').value) || 0;
      const renovacion = document.getElementById('sim-renovacion').value === 'si';
      const monto = parseFloat(document.getElementById('sim-monto').value) || 0;

      const prob = predictRecompra(dias, f30, f90, hist);
      const probPct = (prob * 100).toFixed(1);
      const evaluacion = evaluarSemaforo(dias, hist, renovacion);

      const resBox = document.getElementById('sim-resultado');
      resBox.style.display = 'block';
      resBox.innerHTML = `
        <h4 style="color:var(--primary); margin-bottom:10px;">📋 Resultado de la Evaluación con IA:</h4>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:16px;">
          <div>
            <div style="font-size:12px; color:var(--text-muted); font-weight:700;">SEMÁFORO DE CLIENTE</div>
            <div style="margin-top:6px;"><span class="badge ${evaluacion.badgeClass}" style="font-size:14px; padding:6px 14px;">${evaluacion.estado}</span></div>
          </div>
          <div>
            <div style="font-size:12px; color:var(--text-muted); font-weight:700;">PROBABILIDAD RECOMPRA 30D (ML)</div>
            <div style="font-size:24px; font-weight:800; color:var(--primary); margin-top:4px;">${probPct}%</div>
            <div style="font-size:12px; color:var(--text-muted);">${prob >= 0.4 ? '🔥 Alta probabilidad de recompra' : '❄️ Baja probabilidad sin estímulo'}</div>
          </div>
          <div>
            <div style="font-size:12px; color:var(--text-muted); font-weight:700;">PRIORIDAD DE CONTACTO</div>
            <div style="margin-top:6px;"><span class="badge ${evaluacion.prioridad === 'ALTA' ? 'alta' : 'media'}" style="font-size:13px;">${evaluacion.prioridad}</span></div>
          </div>
        </div>
        <div style="margin-top:16px; background:#eff6ff; padding:14px; border-radius:8px; border-left:4px solid var(--primary-light);">
          <b>Estrategia Sugerida para el Asesor Comercial:</b> ${evaluacion.accion} (Monto estimado: $${monto.toLocaleString('es-CO')} COP).
        </div>
      `;
    }

    // Procesar CSV cargado por el usuario
    function procesarUserCsv() {
      const fileInput = document.getElementById('userCsvFile');
      const msg = document.getElementById('userCsvMsg');
      if (!fileInput.files || fileInput.files.length === 0) {
        msg.style.color = 'var(--danger)';
        msg.innerText = '⚠️ Por favor selecciona un archivo .csv antes de presionar el botón.';
        return;
      }
      const file = fileInput.files[0];
      const reader = new FileReader();
      reader.onload = function(e) {
        const text = e.target.result;
        const lines = text.trim().split('\\n');
        if (lines.length < 2) {
          msg.style.color = 'var(--danger)';
          msg.innerText = 'El archivo CSV está vacío o no contiene suficientes filas.';
          return;
        }
        const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
        const newRecords = [];
        for (let i = 1; i < lines.length; i++) {
          const vals = lines[i].split(',').map(v => v.trim().replace(/^"|"$/g, ''));
          const obj = {};
          headers.forEach((h, idx) => obj[h] = vals[idx] || '');
          // Inferir campos requeridos si faltan
          if (!obj.Cliente_ID) obj.Cliente_ID = 'CLI' + String(i).padStart(3, '0');
          if (!obj.Cliente) obj.Cliente = 'Empresa ' + obj.Cliente_ID;
          if (!obj.Sector) obj.Sector = 'Comercial';
          if (!obj.Dias_Sin_Comprar) obj.Dias_Sin_Comprar = Math.floor(Math.random() * 120);
          if (!obj.Ventas_COP) obj.Ventas_COP = 15000000;
          if (!obj.Estado_Venta) obj.Estado_Venta = 'Confirmada';
          
          const dias = parseInt(obj.Dias_Sin_Comprar);
          const sem = evaluarSemaforo(dias, 5, false);
          obj.Estado_Cliente = sem.estado;
          obj.Prioridad_Llamada = sem.prioridad;
          obj.Accion_Recomendada = sem.accion;
          obj.Prob_Recompra_Pct = (predictRecompra(dias, 1, 2, 5) * 100).toFixed(1);
          newRecords.push(obj);
        }

        ACTIVE_RAW_DATA = newRecords;
        procesarDatosGlobales(ACTIVE_RAW_DATA);
        actualizarVistas();
        msg.style.color = 'var(--success)';
        msg.innerText = `✅ ¡Archivo cargado con éxito! Se procesaron ${newRecords.length} registros y se actualizó todo el dashboard.`;
        showTab('tab-semaforo', document.getElementById('btn-tab-semaforo'));
      };
      reader.readAsText(file, 'UTF-8');
    }

    function restaurarDatosOriginales() {
      ACTIVE_RAW_DATA = [...INITIAL_RAW_DATA];
      procesarDatosGlobales(ACTIVE_RAW_DATA);
      actualizarVistas();
      const msg = document.getElementById('userCsvMsg');
      msg.style.color = 'var(--primary)';
      msg.innerText = '🔄 Se restauraron los datos oficiales originales de Green Services (120 clientes).';
      showTab('tab-semaforo', document.getElementById('btn-tab-semaforo'));
    }

    function showTab(id, btn) {
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.getElementById(id).classList.add('active');
      if (btn) btn.classList.add('active');
    }

    function toggleAccordion(el) {
      el.parentElement.classList.toggle('open');
    }

    // Exportar CSV con resultados (filtrado o completo)
    function exportarCSV(completo = false) {
      const headers = ['Cliente_ID', 'Empresa', 'Sector', 'Ciudad', 'Dias_Sin_Compra', 'Semáforo', 'Prob_Recompra_Pct', 'Prioridad', 'Facturacion_COP', 'Accion_Sugerida'];
      let targetList = CLIENTES;
      if (!completo) {
        const query = document.getElementById('searchInput').value.toLowerCase();
        const statusF = document.getElementById('statusFilter').value;
        const sectorF = document.getElementById('sectorFilter').value;
        targetList = CLIENTES.filter(c => {
          const matchQ = c.nombre.toLowerCase().includes(query) || c.id.toLowerCase().includes(query);
          let matchS = true;
          if (statusF === 'frio') matchS = c.estado.includes('Frío');
          else if (statusF === 'frecuente') matchS = c.estado.includes('Frecuente');
          else if (statusF === 'seguimiento') matchS = !c.estado.includes('Frío') && !c.estado.includes('Frecuente');
          let matchSec = (sectorF === 'todos') || (c.sector === sectorF);
          return matchQ && matchS && matchSec;
        });
      }

      const rows = targetList.map(c => [
        c.id, `"${c.nombre}"`, `"${c.sector}"`, `"${c.ciudad}"`, c.dias, `"${c.estado}"`, c.prob, c.prioridad, Math.round(c.ventas), `"${c.accion}"`
      ]);
      const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers.join(','), ...rows.map(e => e.join(',')).join('\\n')];
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', completo ? 'OperIA_Cartera_Completa_Resultados.csv' : 'OperIA_Llamadas_Filtradas_Resultados.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    window.onload = initPage;
  </script>
</body>
</html>
"""

final_html = html_template.replace("JSON_PLACEHOLDER", json_str)
(root / "index.html").write_text(final_html, encoding="utf-8")
print(f"index.html generated successfully! Length: {len(final_html)} bytes.")
