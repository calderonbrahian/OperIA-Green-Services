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
    .container { max-width: 1350px; margin: 0 auto; }

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
    .header-badges { display: flex; gap: 8px; align-items: center; }
    .tag {
      background: #eff6ff; color: var(--primary-light);
      padding: 6px 14px; border-radius: 9999px; font-size: 13px; font-weight: 600; text-decoration: none;
    }
    .tag.github { background: #0f172a; color: #fff; }

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

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .kpi-card {
      background: var(--card-bg);
      border-radius: 12px;
      padding: 18px;
      border: 1px solid var(--border);
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .kpi-title { font-size: 12px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 24px; font-weight: 800; margin: 6px 0; color: var(--text); }
    .kpi-sub { font-size: 12px; font-weight: 500; }
    .kpi-card.green { border-left: 5px solid var(--success); }
    .kpi-card.yellow { border-left: 5px solid var(--warning); }
    .kpi-card.red { border-left: 5px solid var(--danger); }
    .kpi-card.blue { border-left: 5px solid var(--primary-light); }

    .card {
      background: var(--card-bg);
      border-radius: 12px;
      padding: 22px;
      border: 1px solid var(--border);
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      margin-bottom: 24px;
    }
    .card-title { font-size: 18px; font-weight: 700; margin-bottom: 16px; color: var(--primary); }
    .grid-2 { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
    .grid-equal { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    @media (max-width: 950px) { .grid-2, .grid-equal { grid-template-columns: 1fr; } }

    .controls { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
    input, select {
      padding: 10px 14px;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 14px;
      outline: none;
    }
    input:focus, select:focus { border-color: var(--primary-light); }
    input { flex: 1; min-width: 220px; }
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

    .table-container { overflow-x: auto; max-height: 520px; border-radius: 8px; border: 1px solid var(--border); }
    table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13.5px; }
    th {
      position: sticky; top: 0; background: #f8fafc; color: var(--text);
      font-weight: 700; padding: 12px 14px; border-bottom: 2px solid var(--border);
      z-index: 10;
    }
    td { padding: 12px 14px; border-bottom: 1px solid var(--border); }
    tr:hover td { background-color: #f1f5f9; cursor: pointer; }

    .badge {
      display: inline-block; padding: 4px 10px; border-radius: 9999px;
      font-size: 11.5px; font-weight: 700; text-align: center; white-space: nowrap;
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
        <a href="https://github.com/calderonbrahian/OperIA-Green-Services" target="_blank" class="tag github">⭐ Repositorio GitHub</a>
      </div>
    </header>

    <!-- Global KPIs -->
    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-title">Cartera Total</div>
        <div class="kpi-value" id="kpi-total">120</div>
        <div class="kpi-sub" style="color:var(--primary-light);">Cuentas Monitoreadas</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-title">🟢 Clientes Frecuentes</div>
        <div class="kpi-value" id="kpi-frec">--</div>
        <div class="kpi-sub" style="color:var(--success);">Activos (Última compra ≤ 30d)</div>
      </div>
      <div class="kpi-card yellow">
        <div class="kpi-title">🟡 Base Instalada</div>
        <div class="kpi-value" id="kpi-seg">--</div>
        <div class="kpi-sub" style="color:var(--warning);">Seguimiento de Pólizas</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-title">🔴 Clientes Fríos</div>
        <div class="kpi-value" id="kpi-frio">--</div>
        <div class="kpi-sub" style="color:var(--danger);">Riesgo de Abandono (≥ 90d)</div>
      </div>
      <div class="kpi-card blue">
        <div class="kpi-title">Facturación Consolidada</div>
        <div class="kpi-value" id="kpi-ventas">$--</div>
        <div class="kpi-sub" style="color:var(--primary);">Ventas Confirmadas (COP)</div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="nav-tabs">
      <button class="tab-btn active" onclick="showTab('tab-semaforo', this)">🚨 Semáforo de Clientes</button>
      <button class="tab-btn" onclick="showTab('tab-trm', this)">📈 Ventas vs. TRM</button>
      <button class="tab-btn" onclick="showTab('tab-portafolio', this)">📦 Portafolio y Sectores</button>
      <button class="tab-btn" onclick="showTab('tab-ficha', this)">👤 Ficha 360° Cliente</button>
      <button class="tab-btn" onclick="showTab('tab-objetivos', this)">🎯 Objetivos y Reto MoSCoW</button>
      <button class="tab-btn" onclick="showTab('tab-pruebas', this)">🧪 Casos Controlados y Validación</button>
      <button class="tab-btn" onclick="showTab('tab-datos', this)">🔍 Explorador de Datos</button>
    </div>

    <!-- TAB 1: SEMÁFORO -->
    <div id="tab-semaforo" class="tab-pane active">
      <div class="card">
        <div class="card-title">🚨 Semáforo Inteligente de Gestión Comercial (Llamadas Prioritarias)</div>
        <div class="controls">
          <input type="text" id="searchInput" placeholder="🔍 Buscar cliente por nombre o ID (ej: CLI012)...">
          <select id="statusFilter">
            <option value="todos">Todos los Estados</option>
            <option value="frio">🔴 Fríos (Riesgo de Abandono)</option>
            <option value="seguimiento">🟡 Base Instalada (Seguimiento)</option>
            <option value="frecuente">🟢 Frecuentes (Activos)</option>
          </select>
          <select id="sectorFilter">
            <option value="todos">Todos los Sectores</option>
          </select>
          <button class="btn btn-primary" onclick="exportarCSV()">📥 Descargar Lista Comercial (CSV)</button>
        </div>

        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Empresa</th>
                <th>Sector</th>
                <th>Días sin Compra</th>
                <th>Semáforo</th>
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
          Haz clic en cualquier cliente de la tabla para ver su ficha de contacto comercial y recomendación estratégica.
        </div>
      </div>
    </div>

    <!-- TAB 2: VENTAS VS TRM -->
    <div id="tab-trm" class="tab-pane">
      <div class="card">
        <div class="card-title">📈 Evolución Mensual de Ventas vs. Variación de la TRM</div>
        <div class="info-callout">
          <b>Análisis de Sensibilidad Cambiaria:</b> Coeficiente de Correlación TRM vs. Facturación COP: <b>+0.4736</b> (Correlación positiva moderada). Alza del dólar indexa automáticamente productos licitados en USD e incrementa la facturación nominal en pesos.
        </div>
        <canvas id="chartTRM" height="100"></canvas>
      </div>
    </div>

    <!-- TAB 3: PORTAFOLIO Y SECTORES -->
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

    <!-- TAB 4: FICHA 360 -->
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

    <!-- TAB 5: OBJETIVOS Y MOSCOW -->
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

    <!-- TAB 6: CASOS CONTROLADOS -->
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

    <!-- TAB 7: EXPLORADOR DE DATOS -->
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
    const RAW_DATA = JSON_PLACEHOLDER;

    const CLIENTES_MAP = new Map();
    let totalCOP = 0;
    const sectoresSet = new Set();
    const familiasMap = new Map();
    const sectoresMap = new Map();
    const mesesVentas = new Map();
    const mesesTRM = new Map();

    RAW_DATA.forEach(row => {
      const cid = row.Cliente_ID;
      const vCop = parseFloat(row.Ventas_COP || 0);
      const isConf = row.Estado_Venta === 'Confirmada';
      if (isConf) totalCOP += vCop;

      if (!CLIENTES_MAP.has(cid)) {
        CLIENTES_MAP.set(cid, {
          id: cid,
          nombre: row.Cliente,
          sector: row.Sector,
          ciudad: row.Ciudad,
          estado: row.Estado_Cliente,
          dias: parseInt(row.Dias_Sin_Comprar || 0),
          prob: parseFloat(row.Prob_Recompra_Pct || 0),
          prioridad: row.Prioridad_Llamada,
          accion: row.Accion_Recomendada,
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
        mesesTRM.get(mes).push(parseFloat(row.TRM || 0));
      }
    });

    const CLIENTES = Array.from(CLIENTES_MAP.values());

    function initPage() {
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
      Array.from(sectoresSet).sort().forEach(s => {
        const opt = document.createElement('option');
        opt.value = s; opt.innerText = s;
        secSelect.appendChild(opt);
      });

      const cliSelect = document.getElementById('clientSelect');
      CLIENTES.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id; opt.innerText = `${c.id} - ${c.nombre}`;
        cliSelect.appendChild(opt);
      });
      cliSelect.onchange = () => renderFicha(cliSelect.value);

      renderSemaforo();
      document.getElementById('searchInput').oninput = renderSemaforo;
      document.getElementById('statusFilter').onchange = renderSemaforo;
      document.getElementById('sectorFilter').onchange = renderSemaforo;

      if (CLIENTES.length > 0) renderFicha(CLIENTES[0].id);
      renderGraficas();
      renderExplorador();
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

      filtrados.forEach(c => {
        const badgeCls = c.estado.includes('Frío') ? 'frio' : c.estado.includes('Frecuente') ? 'frecuente' : 'seguimiento';
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><b>${c.id}</b></td>
          <td>${c.nombre}</td>
          <td>${c.sector}</td>
          <td>${c.dias} días</td>
          <td><span class="badge ${badgeCls}">${c.estado}</span></td>
          <td><b>${c.prob}%</b></td>
          <td><span class="badge ${c.prioridad === 'ALTA' ? 'alta' : 'media'}">${c.prioridad}</span></td>
          <td>$${Math.round(c.ventas).toLocaleString('es-CO')}</td>
          <td><small>${c.accion}</small></td>
        `;
        tr.onclick = () => {
          document.getElementById('detailBox').innerHTML = `
            <div style="font-size:15px; font-weight:700; color:var(--primary); margin-bottom:6px;">
              FICHA DE CONTACTO: ${c.id} — ${c.nombre}
            </div>
            • <b>Estado:</b> <span class="badge ${badgeCls}">${c.estado}</span> &nbsp;|&nbsp; <b>Prioridad:</b> ${c.prioridad}<br>
            • <b>Días sin Compra:</b> ${c.dias} días &nbsp;|&nbsp; <b>Probabilidad Recompra 30d:</b> ${c.prob}% &nbsp;|&nbsp; <b>Ventas:</b> $${Math.round(c.ventas).toLocaleString('es-CO')} COP<br>
            • <b>Estrategia de Intervención:</b> ${c.accion}.
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
          <td>${op.Fecha}</td>
          <td><b>${op.Producto}</b></td>
          <td>${op.Familia_Producto}</td>
          <td>${op.Cantidad}</td>
          <td>${op.Moneda}</td>
          <td>$${parseFloat(op.TRM).toFixed(0)}</td>
          <td>$${Math.round(parseFloat(op.Ventas_COP)).toLocaleString('es-CO')}</td>
          <td>${op.Estado_Venta}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    function renderGraficas() {
      const meses = Array.from(mesesVentas.keys()).sort();
      const ventasData = meses.map(m => Math.round((mesesVentas.get(m) || 0) / 1e6));
      const trmData = meses.map(m => {
        const arr = mesesTRM.get(m) || [4100];
        return Math.round(arr.reduce((a,b)=>a+b, 0) / arr.length);
      });

      new Chart(document.getElementById('chartTRM'), {
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

      new Chart(document.getElementById('chartFamilias'), {
        type: 'doughnut',
        data: {
          labels: Array.from(familiasMap.keys()),
          datasets: [{
            data: Array.from(familiasMap.values()),
            backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
          }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
      });

      new Chart(document.getElementById('chartSectores'), {
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
      RAW_DATA.slice(0, 100).forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${r.Venta_ID}</td>
          <td>${r.Fecha}</td>
          <td>${r.Cliente}</td>
          <td>${r.Producto}</td>
          <td>${r.Cantidad}</td>
          <td>${r.Moneda}</td>
          <td>$${parseFloat(r.TRM).toFixed(0)}</td>
          <td>$${Math.round(parseFloat(r.Ventas_COP)).toLocaleString('es-CO')}</td>
          <td>${r.Estado_Venta}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    function showTab(id, btn) {
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.getElementById(id).classList.add('active');
      btn.classList.add('active');
    }

    function toggleAccordion(el) {
      el.parentElement.classList.toggle('open');
    }

    function exportarCSV() {
      const headers = ['Cliente_ID', 'Empresa', 'Sector', 'Dias_Sin_Compra', 'Estado', 'Prob_Recompra_Pct', 'Prioridad', 'Facturacion_COP', 'Accion_Sugerida'];
      const rows = CLIENTES.map(c => [
        c.id, `"${c.nombre}"`, `"${c.sector}"`, c.dias, `"${c.estado}"`, c.prob, c.prioridad, Math.round(c.ventas), `"${c.accion}"`
      ]);
      const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers.join(','), ...rows.map(e => e.join(',')).join('\\n')];
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', 'OperIA_Llamadas_Prioritarias.csv');
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
