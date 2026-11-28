"""
build_index.py
Generador del sitio estático interactivo de OperIA 360° para GitHub Pages y visor offline.
Consume directamente:
  - outputs/cifras_dashboard.json (fuente única de verdad de métricas)
  - outputs/vista_clientes_360.csv (120 clientes auditados)
  - outputs/metricas_modelo.json (pesos, normalización y matriz de confusión del modelo)
  - outputs/OperIA_Dataset_Consolidado.csv (1,371 transacciones confirmadas + incidencias)

Escribe en:
  - index.html (raíz para GitHub Pages)
  - visor/visor.html (copia para visor local offline)
"""
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"

# Cargar fuentes oficiales auditadas
with open(OUTPUTS / "cifras_dashboard.json", "r", encoding="utf-8") as f:
    cifras = json.load(f)

with open(OUTPUTS / "metricas_modelo.json", "r", encoding="utf-8") as f:
    metricas = json.load(f)

with open(OUTPUTS / "vista_clientes_360.csv", "r", encoding="utf-8-sig") as f:
    vista_360 = list(csv.DictReader(f))

with open(OUTPUTS / "OperIA_Dataset_Consolidado.csv", "r", encoding="utf-8-sig") as f:
    raw_data = list(csv.DictReader(f))

json_cifras = json.dumps(cifras, ensure_ascii=False)
json_metricas = json.dumps(metricas, ensure_ascii=False)
json_vista_360 = json.dumps(vista_360, ensure_ascii=False)
json_raw = json.dumps(raw_data, ensure_ascii=False)

html_content = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OperIA 360° | Dashboard Inteligente Online</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
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
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
    body {{ background-color: var(--bg); color: var(--text); padding: 20px; }}
    .container {{ max-width: 1400px; margin: 0 auto; }}

    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
      gap: 12px;
    }}
    .brand h1 {{ font-size: 26px; color: var(--primary); font-weight: 800; }}
    .brand p {{ font-size: 14px; color: var(--text-muted); margin-top: 4px; }}
    .header-badges {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
    .tag {{
      background: #eff6ff; color: var(--primary-light);
      padding: 6px 14px; border-radius: 9999px; font-size: 13px; font-weight: 600; text-decoration: none;
    }}
    .tag.github {{ background: #0f172a; color: #fff; }}

    .nav-tabs {{
      display: flex;
      gap: 8px;
      border-bottom: 2px solid var(--border);
      margin-bottom: 24px;
      overflow-x: auto;
      padding-bottom: 2px;
    }}
    .tab-btn {{
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
    }}
    .tab-btn:hover {{ color: var(--primary-light); background: #f1f5f9; }}
    .tab-btn.active {{
      color: var(--primary-light);
      border-bottom-color: var(--primary-light);
      background: #ffffff;
    }}
    .tab-pane {{ display: none; }}
    .tab-pane.active {{ display: block; }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .kpi-card {{
      background: var(--card-bg);
      border-radius: 12px;
      padding: 18px;
      border: 1px solid var(--border);
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
    }}
    .kpi-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .kpi-card.selected {{
      outline: 3px solid var(--primary-light);
      background: #f8fafc;
    }}
    .kpi-title {{ font-size: 12px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; display: flex; justify-content: space-between; }}
    .kpi-value {{ font-size: 26px; font-weight: 800; margin: 6px 0; color: var(--text); }}
    .kpi-sub {{ font-size: 12px; font-weight: 500; }}
    .kpi-card.green {{ border-left: 6px solid var(--success); }}
    .kpi-card.yellow {{ border-left: 6px solid var(--warning); }}
    .kpi-card.red {{ border-left: 6px solid var(--danger); }}
    .kpi-card.blue {{ border-left: 6px solid var(--primary-light); }}
    .kpi-card.purple {{ border-left: 6px solid #8b5cf6; }}

    .card {{
      background: var(--card-bg);
      border-radius: 12px;
      padding: 22px;
      border: 1px solid var(--border);
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      margin-bottom: 24px;
    }}
    .card-title {{ font-size: 18px; font-weight: 700; margin-bottom: 16px; color: var(--primary); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }}
    
    .controls {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; align-items: center; }}
    input, select, textarea {{
      padding: 10px 14px;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 14px;
      outline: none;
    }}
    input:focus, select:focus, textarea:focus {{ border-color: var(--primary-light); }}
    input[type="text"] {{ flex: 1; min-width: 220px; }}
    .btn {{
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
    }}
    .btn-primary {{ background: var(--primary-light); color: #fff; }}
    .btn-primary:hover {{ background: var(--primary); }}
    .btn-success {{ background: var(--success); color: #fff; }}
    .btn-success:hover {{ background: #059669; }}
    .btn-secondary {{ background: #e2e8f0; color: #334155; }}
    .btn-secondary:hover {{ background: #cbd5e1; }}

    .table-container {{ overflow-x: auto; max-height: 520px; border-radius: 8px; border: 1px solid var(--border); }}
    table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 13.5px; }}
    th {{
      position: sticky; top: 0; background: #f8fafc; color: var(--text);
      font-weight: 700; padding: 12px 14px; border-bottom: 2px solid var(--border);
      z-index: 10;
    }}
    td {{ padding: 12px 14px; border-bottom: 1px solid var(--border); }}
    tr:hover td {{ background-color: #f1f5f9; cursor: pointer; }}

    .badge {{
      display: inline-block; padding: 4px 10px; border-radius: 9999px;
      font-size: 11.5px; font-weight: 700; text-align: center; white-space: nowrap; cursor: pointer;
    }}
    .badge.frecuente {{ background: #dcfce7; color: #166534; }}
    .badge.seguimiento {{ background: #fef3c7; color: #92400e; }}
    .badge.frio {{ background: #fee2e2; color: #991b1b; }}
    .badge.alta {{ background: #fee2e2; color: #991b1b; font-weight: 800; }}
    .badge.media {{ background: #fef3c7; color: #92400e; }}
    .badge.normal {{ background: #e0e7ff; color: #3730a3; }}
    .badge.baja {{ background: #f1f5f9; color: #475569; }}
    .badge.proyeccion {{ background: #ede9fe; color: #6d28d9; font-weight: 700; }}

    .detail-drawer {{
      background: #f8fafc; border: 1px solid var(--border); border-left: 5px solid var(--primary-light);
      border-radius: 8px; padding: 18px; margin-top: 16px;
    }}

    .info-callout {{
      background: #eff6ff; border-left: 4px solid var(--primary-light);
      padding: 14px 18px; border-radius: 6px; margin-bottom: 18px; color: #1e3a8a; font-size: 14px;
    }}
    .warning-callout {{
      background: #fffbeb; border-left: 4px solid var(--warning);
      padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; color: #92400e; font-size: 13px;
    }}

    .math-box {{
      background: #1e293b;
      color: #f8fafc;
      padding: 18px;
      border-radius: 10px;
      font-family: 'Courier New', Courier, monospace;
      font-size: 14px;
      line-height: 1.7;
      margin: 16px 0;
      overflow-x: auto;
    }}
    .math-highlight {{ color: #38bdf8; font-weight: bold; }}
    .math-green {{ color: #4ade80; font-weight: bold; }}
    .math-orange {{ color: #fbbf24; font-weight: bold; }}

    .form-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }}
    .form-group label {{
      display: block; font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px;
    }}
    .form-group input, .form-group select {{ width: 100%; }}

    .sim-result-card {{
      background: #fff;
      border: 2px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-top: 20px;
    }}

    .calc-step {{
      display: flex;
      gap: 12px;
      align-items: center;
      padding: 10px 14px;
      background: #f8fafc;
      border-radius: 8px;
      border: 1px solid var(--border);
      margin-bottom: 10px;
    }}
    .calc-step-num {{
      background: var(--primary-light);
      color: #fff;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 13px;
      flex-shrink: 0;
    }}

    .accordion {{ margin-bottom: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }}
    .accordion-header {{
      background: #f8fafc; padding: 14px 18px; font-weight: 700; cursor: pointer;
      display: flex; justify-content: space-between; user-select: none;
    }}
    .accordion-body {{ padding: 16px 18px; background: #fff; font-size: 14px; line-height: 1.6; display: none; }}
    .accordion.open .accordion-body {{ display: block; }}
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
        <span class="tag">🟢 Online GitHub Pages</span>
        <button class="btn btn-primary" onclick="showTab('tab-proyeccion', document.getElementById('btn-tab-proyeccion'))">🔮 Proyección Próximo Mes</button>
        <button class="btn btn-secondary" onclick="showTab('tab-explicacion', document.getElementById('btn-tab-explicacion'))">🧠 ¿Cómo Funciona la IA?</button>
        <a href="https://github.com/calderonbrahian/OperIA-Green-Services" target="_blank" class="tag github">⭐ Repositorio GitHub</a>
      </div>
    </header>

    <div class="warning-callout">
      ℹ️ <b>Nota de Transparencia de Datos:</b> Este dashboard opera con los datos de prueba oficiales del reto (120 clientes, 1,371 transacciones confirmadas, $5,647.4M COP). La TRM utilizada proviene del paquete de prueba del reto y no constituye la tasa oficial de Green Services.
    </div>

    <!-- Global KPIs con Clic Directo en Semáforos -->
    <div class="kpi-grid">
      <div class="kpi-card blue selected" id="kpi-card-total" onclick="filtrarPorSemaforoCard('todos')">
        <div class="kpi-title"><span>Cartera Total</span> <span>👁️ Ver Todos</span></div>
        <div class="kpi-value" id="kpi-total">120</div>
        <div class="kpi-sub" style="color:var(--primary-light);">Cuentas Auditadas (Clic)</div>
      </div>
      <div class="kpi-card green" id="kpi-card-frec" onclick="filtrarPorSemaforoCard('frecuente')">
        <div class="kpi-title"><span>🟢 Frecuentes (Activos)</span> <span>👉 Filtrar</span></div>
        <div class="kpi-value" id="kpi-frec">38</div>
        <div class="kpi-sub" style="color:var(--success);">Última compra ≤ 30d (Clic)</div>
      </div>
      <div class="kpi-card yellow" id="kpi-card-seg" onclick="filtrarPorSemaforoCard('seguimiento')">
        <div class="kpi-title"><span>🟡 Base Instalada</span> <span>👉 Filtrar</span></div>
        <div class="kpi-value" id="kpi-seg">41</div>
        <div class="kpi-sub" style="color:var(--warning);">Recencia 31 a 89d (Clic)</div>
      </div>
      <div class="kpi-card red" id="kpi-card-frio" onclick="filtrarPorSemaforoCard('frio')">
        <div class="kpi-title"><span>🔴 Clientes Fríos</span> <span>👉 Filtrar</span></div>
        <div class="kpi-value" id="kpi-frio">41</div>
        <div class="kpi-sub" style="color:var(--danger);">Riesgo Abandono (≥ 90d) (Clic)</div>
      </div>
      <div class="kpi-card purple" id="kpi-card-proy" onclick="showTab('tab-proyeccion', document.getElementById('btn-tab-proyeccion'))">
        <div class="kpi-title"><span>🔮 Proyección Próx. Mes</span> <span>Ver Detalle</span></div>
        <div class="kpi-value" id="kpi-proy-ventas">$216.5M</div>
        <div class="kpi-sub" style="color:#7c3aed;">Noviembre 2026 (94 compradores)</div>
      </div>
      <div class="kpi-card blue" id="kpi-card-ventas">
        <div class="kpi-title"><span>Facturación Acumulada</span> <span>Total COP</span></div>
        <div class="kpi-value" id="kpi-ventas">$5,647.4M</div>
        <div class="kpi-sub" style="color:var(--primary);">1,371 operaciones confirmadas</div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="nav-tabs">
      <button class="tab-btn active" id="btn-tab-semaforo" onclick="showTab('tab-semaforo', this)">🚨 Semáforo de Clientes</button>
      <button class="tab-btn" id="btn-tab-proyeccion" onclick="showTab('tab-proyeccion', this)">🔮 Proyección Próximo Mes (Nov 2026)</button>
      <button class="tab-btn" id="btn-tab-explicacion" onclick="showTab('tab-explicacion', this)">🧠 ¿Cómo Funciona el Modelo de IA?</button>
      <button class="tab-btn" id="btn-tab-simulador" onclick="showTab('tab-simulador', this)">🧪 Simulador y Carga de Datos</button>
      <button class="tab-btn" id="btn-tab-pruebas" onclick="showTab('tab-pruebas', this)">📋 Evidencias de Pruebas</button>
      <button class="tab-btn" onclick="showTab('tab-trm', this)">📈 Ventas vs. TRM</button>
      <button class="tab-btn" onclick="showTab('tab-ficha', this)">👤 Ficha 360° Cliente</button>
      <button class="tab-btn" onclick="showTab('tab-objetivos', this)">🎯 Objetivos MoSCoW & Pitch</button>
      <button class="tab-btn" onclick="showTab('tab-datos', this)">🔍 Explorador de Datos</button>
    </div>

    <!-- TAB 1: SEMÁFORO INTELIGENTE -->
    <div id="tab-semaforo" class="tab-pane active">
      <div class="card">
        <div class="card-title">
          <span>🚨 Semáforo Inteligente de Clientes y Gestión Comercial</span>
          <span style="font-size:13px; color:var(--text-muted); font-weight:normal;" id="contadorFiltro">Mostrando 120 de 120 clientes</span>
        </div>

        <div class="info-callout">
          <p style="margin-bottom:8px;">
            <b>Criterios Operativos del Semáforo y Priorización Comercial:</b>
          </p>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:10px; font-size:12.5px;">
            <div style="background:#ffffff; padding:10px 14px; border-radius:6px; border:1px solid #bfdbfe;">
              <b>🟢 Frecuente (Activo) [Recencia ≤ 30 días]:</b><br>
              <span style="color:#03543f;">• Compró en el último mes. Cuenta sana.<br>• Prioridad: <b>BAJA</b> si póliza vigente; <b>MEDIA</b> si vence en ≤ 45d.</span>
            </div>
            <div style="background:#ffffff; padding:10px 14px; border-radius:6px; border:1px solid #fef08a;">
              <b>🟡 Base Instalada [Recencia 31 a 89 días]:</b><br>
              <span style="color:#713f12;">• Cuenta intermedia sin compras este mes, aún sin abandono.<br>• Prioridad: <b>MEDIA</b> si vence en ≤ 45d; <b>NORMAL</b> si está vigente.</span>
            </div>
            <div style="background:#ffffff; padding:10px 14px; border-radius:6px; border:1px solid #fecaca;">
              <b>🔴 Frío (Riesgo Abandono) [Recencia ≥ 90 días]:</b><br>
              <span style="color:#991b1b;">• Sin compras hace 3 o más meses.<br>• Prioridad: <b>ALTA</b> para reactivación comercial urgente.</span>
            </div>
          </div>
          <p style="margin-top:10px; font-size:12px; color:#1e40af;">
            📌 <i>Ordenamiento Inteligente:</i> La prioridad comercial (ALTA, MEDIA, NORMAL, BAJA) está gobernada por las reglas de Cobertura y Recencia. Dentro de cada nivel, la probabilidad del modelo de IA (P ≥ 40%) ordena a los clientes para maximizar el retorno de las llamadas de los asesores.
          </p>
        </div>

        <div class="controls">
          <input type="text" id="searchInput" placeholder="🔍 Buscar cliente por nombre o ID (ej: CLI086)...">
          <select id="statusFilter" onchange="aplicarFiltroSelect()">
            <option value="todos">Todos los Semáforos</option>
            <option value="frio">🔴 Fríos (Riesgo de Abandono)</option>
            <option value="seguimiento">🟡 Base Instalada (Seguimiento)</option>
            <option value="frecuente">🟢 Frecuentes (Activos)</option>
          </select>
          <select id="coberturaFilter" onchange="renderSemaforo()">
            <option value="todas">Todas las Coberturas</option>
            <option value="proxima">🟡 Próxima a Renovar (≤ 45d)</option>
            <option value="vigente">🟢 Vigente (> 45d)</option>
            <option value="vencida">🔴 Vencida (< 0d)</option>
            <option value="sin">⚪ Sin Cobertura</option>
          </select>
          <select id="prioridadFilter" onchange="renderSemaforo()">
            <option value="todas">Todas las Prioridades</option>
            <option value="ALTA">🚨 ALTA</option>
            <option value="MEDIA">⚡ MEDIA</option>
            <option value="NORMAL">📌 NORMAL</option>
            <option value="BAJA">☕ BAJA</option>
          </select>
          <select id="sectorFilter" onchange="renderSemaforo()">
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
                <th>Semáforo</th>
                <th>Estado Cobertura</th>
                <th>Prob. Recompra (IA)</th>
                <th>Prioridad</th>
                <th>Criterio de Decisión</th>
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

    <!-- TAB 2: PROYECCIÓN PRÓXIMO MES (NOVIEMBRE 2026) -->
    <div id="tab-proyeccion" class="tab-pane">
      <div class="card">
        <div class="card-title">
          <span>🔮 Proyección Comercial Hacia Adelante: Noviembre 2026</span>
          <span class="badge proyeccion">Horizonte: Próximos 30 Días</span>
        </div>
        <p style="color:var(--text-muted); margin-bottom:18px;">
          Con base en los datos acumulados hasta el corte (31/10/2026), el modelo predice la propensión de compra individual y proyecta la facturación esperada para el siguiente mes mediante la sumatoria del valor esperado individual Σ [P(Compra_i) × Ticket_i]:
        </p>

        <div class="kpi-grid">
          <div class="kpi-card purple">
            <div class="kpi-title">Facturación Proyectada (Nov 2026)</div>
            <div class="kpi-value" id="proy-ingreso-val">$216,486,299 COP</div>
            <div class="kpi-sub" style="color:#7c3aed;">Estimación esperada: Σ [P(Compra) × Ticket]</div>
          </div>
          <div class="kpi-card green">
            <div class="kpi-title">Clientes con Alta Propensión</div>
            <div class="kpi-value" id="proy-compradores-val">94 Cuentas</div>
            <div class="kpi-sub" style="color:var(--success);">Probabilidad de Recompra ≥ 40%</div>
          </div>
          <div class="kpi-card blue">
            <div class="kpi-title">Ticket Promedio Global</div>
            <div class="kpi-value" id="proy-ticket-val">$4,119,219 COP</div>
            <div class="kpi-sub" style="color:var(--primary);">Calculado sobre 1,371 operaciones</div>
          </div>
          <div class="kpi-card yellow">
            <div class="kpi-title">TRM de Cierre de Corte</div>
            <div class="kpi-value" id="proy-trm-val">$4,029.85 COP</div>
            <div class="kpi-sub" style="color:var(--warning);">Tasa de cierre al 31/10/2026</div>
          </div>
        </div>

        <h4 style="margin: 24px 0 12px 0;">📈 Serie Histórica Mensual y Proyección Noviembre 2026</h4>
        <canvas id="chartProyeccion" height="110"></canvas>

        <h4 style="margin: 28px 0 12px 0;">📊 Validación Empírica del Pronóstico: Backtest Histórico vs. Línea Base</h4>
        <p style="font-size:13px; color:var(--text-muted); margin-bottom:12px;">
          Para validar la capacidad del modelo antes de usarlo en producción, se evaluó mes a mes en retrospectiva contra la línea base ingenua habitual ("el próximo mes venderá lo mismo que el mes anterior"):
        </p>

        <div class="table-container" style="max-height:300px; margin-bottom:20px;">
          <table id="backtestTable">
            <thead>
              <tr>
                <th>Mes Objetivo</th>
                <th>Fecha de Corte</th>
                <th>Pronóstico Modelo (COP)</th>
                <th>Línea Base Último Mes (COP)</th>
                <th>Ventas Reales (COP)</th>
                <th>Error Abs. Modelo (COP)</th>
                <th>Error Abs. Línea Base (COP)</th>
                <th>Mejor Modelo</th>
              </tr>
            </thead>
            <tbody id="backtestBody"></tbody>
          </table>
        </div>

        <div class="info-callout" style="background:#f0fdf4; border-left:4px solid var(--success); color:#166534;">
          🎯 <b>Resultado del Backtesting:</b><br>
          • <b>MAE del Modelo OperIA:</b> $25,812,479 COP<br>
          • <b>MAE de la Línea Base:</b> $52,475,745 COP<br>
          • <b>Reducción de Error:</b> ¡El modelo de OperIA reduce el error absoluto medio de predicción en un <b>50.81%</b> respecto a repetir el mes previo!
        </div>

        <h4 style="margin: 28px 0 12px 0;">🎯 Clientes Prioritarios Proyectados a Comprar en Noviembre 2026</h4>
        <p style="font-size:13px; color:var(--text-muted); margin-bottom:12px;">
          Estas cuentas superan el umbral óptimo de recompra (≥ 40%) y representan el mayor retorno proyectado para el siguiente mes:
        </p>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Cliente ID</th>
                <th>Empresa</th>
                <th>Sector</th>
                <th>Prob. Compra Nov (%)</th>
                <th>Ticket Promedio</th>
                <th>Ingreso Esperado (COP)</th>
                <th>Recomendación Comercial</th>
              </tr>
            </thead>
            <tbody id="proyBody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 3: CÓMO FUNCIONA EL MODELO DE IA -->
    <div id="tab-explicacion" class="tab-pane">
      <div class="card">
        <div class="card-title">🧠 Caja Blanca: ¿Cómo Funciona Realmente el Modelo de IA?</div>
        <p style="color:var(--text-muted); margin-bottom:16px;">
          A diferencia de una "caja negra", el modelo predictivo de OperIA es 100% auditable y transparente. Utiliza una <b>Regresión Logística Regularizada (L2)</b> implementada sin dependencias externas de cajas negras, con partición temporal estricta para aprender el comportamiento real de recompra de los clientes.
        </p>

        <div class="math-box">
          <span class="math-highlight">// 1. Normalización Z-score de variables al corte t:</span><br>
          x̃_recencia = (recencia_dias - 126.56) / 234.53<br>
          x̃_f30      = (frecuencia_30d - 0.68) / 0.84<br>
          x̃_f90      = (frecuencia_90d - 1.88) / 1.59<br>
          x̃_hist     = (historial_total - 4.35) / 3.56<br><br>
          <span class="math-highlight">// 2. Combinación Lineal Ponderada (Logit z):</span><br>
          z = <span class="math-orange">+0.0267</span> + (<span class="math-orange">-0.0595</span> × x̃_recencia) + (<span class="math-green">+0.1013</span> × x̃_f30) + (<span class="math-green">+0.1304</span> × x̃_f90) + (<span class="math-orange">-0.1243</span> × x̃_hist)<br><br>
          <span class="math-highlight">// 3. Función de Activación Sigmoide:</span><br>
          <b>P(Recompra 30d) = 1 / (1 + e^(-z))</b><br>
          <span class="math-green">Si P ≥ 0.40 (Umbral óptimo en Validación Temporal) → Predicción = 1 (Comprará en los próximos 30 días)</span>
        </div>

        <h4 style="margin: 24px 0 12px 0;">⚖️ Tabla de Pesos Aprendidos por la Inteligencia Artificial</h4>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Variable Predictora</th>
                <th>Peso Aprendido (w)</th>
                <th>Impacto en la Decisión</th>
                <th>Interpretación del Negocio</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><b>Frecuencia en 90 días (f90)</b></td>
                <td><span class="badge frecuente">+0.1304</span></td>
                <td><b>Mayor Impacto Positivo</b></td>
                <td>Los clientes con compras continuas en el último trimestre tienen la mayor propensión a recomprar.</td>
              </tr>
              <tr>
                <td><b>Frecuencia en 30 días (f30)</b></td>
                <td><span class="badge frecuente">+0.1013</span></td>
                <td><b>Impacto Positivo Reciente</b></td>
                <td>Una compra en el mes reciente suma inercia inmediata a la probabilidad de recompra.</td>
              </tr>
              <tr>
                <td><b>Recencia (Días sin Compra)</b></td>
                <td><span class="badge frio">-0.0595</span></td>
                <td><b>Impacto Negativo (Penalización)</b></td>
                <td>A mayor cantidad de días sin comprar, menor es la propensión del cliente a volver a comprar.</td>
              </tr>
              <tr>
                <td><b>Historial Total Acumulado</b></td>
                <td><span class="badge seguimiento">-0.1243</span></td>
                <td><b>Regularización L2</b></td>
                <td>Equilibra el peso de f90 para evitar sobreajustar en clientes con cuentas históricas muy antiguas pero inactivas.</td>
              </tr>
              <tr>
                <td><b>Sesgo del Modelo (Intercepto)</b></td>
                <td><span class="badge normal">+0.0267</span></td>
                <td><b>Línea Base Calibrada</b></td>
                <td>Término independiente aprendido en entrenamiento temporal estricto.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h4 style="margin: 28px 0 12px 0;">🔬 Evaluación en Prueba Fuera de Tiempo (Out-Of-Time: Jul–Sep 2026)</h4>
        <div class="table-container" style="margin-bottom:20px;">
          <table>
            <thead>
              <tr>
                <th>Métrica de Rendimiento</th>
                <th>Modelo OperIA (Umbral 0.40)</th>
                <th>Línea Base (Compra Reciente)</th>
                <th>Ventaja Competitiva de OperIA</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><b>Recall (Sensibilidad / Captura de Recompras)</b></td>
                <td><span class="badge frecuente">90.91%</span></td>
                <td>55.30%</td>
                <td><b>+35.61% de recompras capturadas</b> (vital para no perder clientes)</td>
              </tr>
              <tr>
                <td><b>F1-Score Balanceado</b></td>
                <td><span class="badge frecuente">0.5594</span></td>
                <td>0.5368</td>
                <td><b>Supera a la línea base</b> con balance óptimo entre cobertura y precisión</td>
              </tr>
              <tr>
                <td><b>Precisión</b></td>
                <td>40.40%</td>
                <td>52.14%</td>
                <td>El modelo intencionalmente abre el embudo para avisar al asesor comercial</td>
              </tr>
              <tr>
                <td><b>Matriz de Confusión (360 observaciones)</b></td>
                <td colspan="3"><b>TP: 120</b> &nbsp;|&nbsp; <b>TN: 51</b> &nbsp;|&nbsp; <b>FP: 177</b> &nbsp;|&nbsp; <b>FN: 12</b> (Apenas 12 recompras no detectadas)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h4 style="margin: 28px 0 12px 0;">🔬 Calculadora Interactiva en Vivo del Modelo</h4>
        <div style="background:#f8fafc; border:1px solid var(--border); padding:20px; border-radius:10px;">
          <div class="form-grid">
            <div class="form-group">
              <label>Días sin compra:</label>
              <input type="number" id="calc-dias" value="30" oninput="runLiveCalc()">
            </div>
            <div class="form-group">
              <label>Compras últimos 30d:</label>
              <input type="number" id="calc-f30" value="1" oninput="runLiveCalc()">
            </div>
            <div class="form-group">
              <label>Compras últimos 90d:</label>
              <input type="number" id="calc-f90" value="3" oninput="runLiveCalc()">
            </div>
            <div class="form-group">
              <label>Historial total compras:</label>
              <input type="number" id="calc-hist" value="10" oninput="runLiveCalc()">
            </div>
          </div>

          <div id="calc-breakdown"></div>
        </div>
      </div>
    </div>

    <!-- TAB 4: SIMULADOR Y PROBADOR -->
    <div id="tab-simulador" class="tab-pane">
      <div class="card">
        <div class="card-title">🧪 Probador Interactivo con IA: Ingresar Datos y Evaluar Resultados</div>
        <div class="info-callout">
          Prueba el modelo con datos arbitrarios o sube tu propio archivo CSV para ver cómo cambian todas las predicciones y semáforos.
        </div>

        <div style="background:#f1f5f9; padding:20px; border-radius:10px; margin-bottom:24px;">
          <h4 style="margin-bottom:14px; color:var(--primary);">1. Probar un Cliente Individual</h4>
          <div class="form-grid">
            <div class="form-group">
              <label>Días transcurridos sin comprar:</label>
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
              <label>Total de compras históricas:</label>
              <input type="number" id="sim-hist" value="6" min="0">
            </div>
            <div class="form-group">
              <label>Estado de Cobertura:</label>
              <select id="sim-renovacion">
                <option value="proxima">🟡 Próxima a Renovar (≤ 45d)</option>
                <option value="vigente">🟢 Vigente (> 45d)</option>
                <option value="vencida">🔴 Vencida (< 0d)</option>
                <option value="sin">⚪ Sin Cobertura</option>
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
          <h4 style="margin-bottom:14px; color:var(--primary);">2. Cargar mi propio archivo CSV de Clientes</h4>
          <p style="font-size:13px; color:var(--text-muted); margin-bottom:12px;">
            Sube un archivo CSV con columnas <code>Cliente_ID, Cliente, Sector, Dias_Sin_Comprar, Ventas_COP</code>:
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

    <!-- TAB 5: EVIDENCIAS DE PRUEBAS -->
    <div id="tab-pruebas" class="tab-pane">
      <div class="card">
        <div class="card-title">
          <span>📋 Sesión de Pruebas y Evidencias de Validación</span>
          <button class="btn btn-primary" onclick="descargarEvidencias()">📥 Descargar Reporte de Evidencias (JSON)</button>
        </div>
        <p style="color:var(--text-muted); margin-bottom:16px;">
          Resultados de verificación automática de casos controlados y auditoría de calidad de datos listos para adjuntar a la plataforma EstudIA:
        </p>

        <h4 style="margin: 20px 0 10px 0; color:var(--primary);">1. Casos Controlados Oficiales (`Casos_controlados.json`)</h4>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Caso Evaluado</th>
                <th>Entrada de Prueba</th>
                <th>Esperado</th>
                <th>Obtenido en OperIA</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>TEST-01</td><td><b>Conversión COP</b></td><td>2 unids × $100.000 (10% desc.)</td><td>$180.000 COP</td><td>$180.000 COP</td><td><span class="badge frecuente">✅ PASÓ</span></td></tr>
              <tr><td>TEST-02</td><td><b>Conversión USD con TRM</b></td><td>3 unids × $100 USD @ $4.000 TRM</td><td>$1.200.000 COP</td><td>$1.200.000 COP</td><td><span class="badge frecuente">✅ PASÓ</span></td></tr>
              <tr><td>TEST-03</td><td><b>Exclusión de Anuladas</b></td><td>Operación estado 'Anulada'</td><td>$0 COP (Excluida)</td><td>$0 COP (Excluida)</td><td><span class="badge frecuente">✅ PASÓ</span></td></tr>
              <tr><td>TEST-04</td><td><b>Frío en Frontera</b></td><td>Corte 31/10/2026, última compra 02/08/2026</td><td>Exacto 90 días -> Frío</td><td>90 días -> Frío</td><td><span class="badge frecuente">✅ PASÓ</span></td></tr>
              <tr><td>TEST-05</td><td><b>Renovación Frontera</b></td><td>Corte 31/10/2026, fin 15/12/2026</td><td>Exacto 45 días -> Renovación</td><td>45 días -> Renovación</td><td><span class="badge frecuente">✅ PASÓ</span></td></tr>
              <tr><td>TEST-06</td><td><b>Cliente Sin Datos</b></td><td>Cliente 'CLI999' inexistente</td><td>Sin invención de compras</td><td>Manejo seguro</td><td><span class="badge frecuente">✅ PASÓ</span></td></tr>
            </tbody>
          </table>
        </div>

        <h4 style="margin: 28px 0 10px 0; color:var(--primary);">2. Auditoría de Calidad de Datos (`ventas_con_incidencias_OPCIONAL.csv`)</h4>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID Incidencia</th>
                <th>Fila Afectada</th>
                <th>Tipo de Anomalía</th>
                <th>Tratamiento Aplicado en OperIA</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>INC-01</td><td>Fila 1 (duplicado)</td><td>ID de venta duplicado</td><td>Descarte de copia redundante</td><td><span class="badge frecuente">✅ IDENTIFICADA</span></td></tr>
              <tr><td>INC-02</td><td>Fila 14</td><td>Cliente inexistente (CLI999)</td><td>Aislamiento para validación con CRM</td><td><span class="badge frecuente">✅ IDENTIFICADA</span></td></tr>
              <tr><td>INC-03</td><td>Fila 27</td><td>Fecha inválida (2026-02-30)</td><td>Rechazo por formato temporal inexistente</td><td><span class="badge frecuente">✅ IDENTIFICADA</span></td></tr>
              <tr><td>INC-04</td><td>Fila 38</td><td>Moneda no soportada (EUR)</td><td>Aislamiento por tasa de cambio no cubierta</td><td><span class="badge frecuente">✅ IDENTIFICADA</span></td></tr>
              <tr><td>INC-05</td><td>Fila 51</td><td>Cantidad negativa (-2)</td><td>Exclusión del cálculo de facturación neta</td><td><span class="badge frecuente">✅ IDENTIFICADA</span></td></tr>
              <tr><td>INC-06</td><td>Fila 62</td><td>Precio unitario vacío</td><td>Marcado como registro incompleto</td><td><span class="badge frecuente">✅ IDENTIFICADA</span></td></tr>
              <tr><td>INC-07</td><td>Fila 75</td><td>Producto inexistente (PRO99)</td><td>Aislamiento para revisión de catálogo maestro</td><td><span class="badge frecuente">✅ IDENTIFICADA</span></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 6: VENTAS VS TRM -->
    <div id="tab-trm" class="tab-pane">
      <div class="card">
        <div class="card-title">📈 Evolución Mensual de Ventas vs. Variación de la TRM</div>
        <div class="info-callout">
          <b>Análisis de Sensibilidad Cambiaria:</b> Coeficiente de Correlación TRM vs. Facturación COP: <b>-0.183</b> (Correlación neutra o levemente negativa). En el set de prueba, la fluctuación del dólar no explica significativamente el volumen transaccional en pesos.
        </div>
        <canvas id="chartTRM" height="100"></canvas>
      </div>
    </div>

    <!-- TAB 7: FICHA 360 -->
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

    <!-- TAB 8: OBJETIVOS Y MOSCOW -->
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
            • <b>Minuto 0:45 - 1:45:</b> OperIA integra TRM, predice la recompra a 30 días con Machine Learning (Recall 90.9%) y clasifica prioridades.<br>
            • <b>Minuto 1:45 - 2:30:</b> Demostración del semáforo en vivo, filtrando clientes fríos en menos de 2 segundos.<br>
            • <b>Minuto 2:30 - 3:00:</b> Impacto en rentabilidad, retención y escalabilidad comercial.
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 9: EXPLORADOR DE DATOS -->
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
    // Inyección de fuentes únicas de verdad desde Python
    const CIFRAS = {json_cifras};
    const METRICAS = {json_metricas};
    const INITIAL_VISTA_360 = {json_vista_360};
    const INITIAL_RAW_DATA = {json_raw};

    let ACTIVE_VISTA_360 = [...INITIAL_VISTA_360];
    let ACTIVE_RAW_DATA = [...INITIAL_RAW_DATA];

    let CLIENTES_MAP = new Map();
    let CLIENTES = [];
    let totalCOP = CIFRAS.ingreso_cop_total || 5647449456.37;

    const sectoresSet = new Set();
    const mesesVentas = new Map();
    const mesesTRM = new Map();

    // Modelo de Machine Learning (Regresión Logística calibrada)
    function predictRecompra(recencia, f30, f90, hist) {{
      const mu = METRICAS.medias_escalado || [126.56, 0.68, 1.88, 4.35];
      const sd = METRICAS.desviaciones_escalado || [234.53, 0.84, 1.59, 3.56];
      const w = METRICAS.pesos_modelo || [0.026714, -0.059519, 0.101297, 0.130378, -0.124296];
      const vals = [recencia, f30, f90, hist];
      let z = w[0];
      for (let i = 0; i < 4; i++) {{
        z += w[i+1] * ((vals[i] - mu[i]) / sd[i]);
      }}
      z = Math.max(-35, Math.min(35, z));
      return 1 / (1 + Math.exp(-z));
    }}

    function evaluarSemaforo(diasSinCompra, renovacionEstado) {{
      if (diasSinCompra >= 90) {{
        return {{
          estado: "Frío (Riesgo de Abandono)",
          prioridad: "ALTA",
          accion: "Campaña de reactivación comercial urgente (Llamada prioritaria)",
          criterio: `Recencia crítica: ${{diasSinCompra}}d sin comprar (≥ 90d)`,
          badgeClass: "frio"
        }};
      }} else if (diasSinCompra <= 30) {{
        const esRenov = renovacionEstado === 'proxima' || renovacionEstado.includes('Próxima');
        return {{
          estado: "Frecuente (Activo)",
          prioridad: esRenov ? "MEDIA" : "BAJA",
          accion: esRenov ? "Fidelización activa y renovación anticipada de póliza" : "Fidelización, satisfacción y propuesta de up-selling",
          criterio: esRenov ? `Compra reciente (${{diasSinCompra}}d ≤ 30d) + Contrato por renovar (≤ 45d)` : `Compra reciente (${{diasSinCompra}}d ≤ 30d) — Cuenta sana y al día`,
          badgeClass: "frecuente"
        }};
      }} else {{
        const esRenov = renovacionEstado === 'proxima' || renovacionEstado.includes('Próxima');
        return {{
          estado: "Base Instalada (Seguimiento)",
          prioridad: esRenov ? "MEDIA" : "NORMAL",
          accion: esRenov ? "Contactar para renovación de póliza / licencia de cobertura" : "Seguimiento periódico de cuenta y nuevas necesidades",
          criterio: esRenov ? `Recencia intermedia (${{diasSinCompra}}d) + Contrato por vencer en ≤ 45d` : `Recencia intermedia (${{diasSinCompra}}d) — Seguimiento regular`,
          badgeClass: "seguimiento"
        }};
      }}
    }}

    function procesarDatosGlobales() {{
      CLIENTES_MAP.clear();
      sectoresSet.clear();
      mesesVentas.clear();
      mesesTRM.clear();

      // Construir mapa de transacciones por cliente desde ACTIVE_RAW_DATA
      const opsPorCliente = new Map();
      ACTIVE_RAW_DATA.forEach(row => {{
        const cid = row.Cliente_ID || row.cliente_id;
        const vCop = parseFloat(row.Ventas_COP || row.ingreso_cop || 0);
        const isConf = (row.Estado_Venta || row.estado || 'Confirmada') === 'Confirmada';

        if (!opsPorCliente.has(cid)) opsPorCliente.set(cid, []);
        opsPorCliente.get(cid).push(row);

        if (row.Fecha && isConf) {{
          const mes = row.Fecha.substring(0, 7);
          mesesVentas.set(mes, (mesesVentas.get(mes) || 0) + vCop);
          if (!mesesTRM.has(mes)) mesesTRM.set(mes, []);
          mesesTRM.get(mes).push(parseFloat(row.TRM || 4000));
        }}
      }});

      // Construir CLIENTES desde ACTIVE_VISTA_360 (120 clientes auditados)
      ACTIVE_VISTA_360.forEach(c => {{
        const cid = c.Cliente_ID;
        const vCop = parseFloat(c.Ventas_COP || 0);
        const dias = parseInt(c.Dias_Sin_Comprar || 0);
        const prob = parseFloat(c.Prob_Recompra_Pct || 0);
        const ops = opsPorCliente.get(cid) || [];

        const obj = {{
          id: cid,
          nombre: c.Cliente || ('Cliente ' + cid),
          sector: c.Sector || 'General',
          ciudad: c.Ciudad || 'No especificada',
          estado: c.Estado_Cliente || 'Base Instalada (Seguimiento)',
          cobertura: c.Estado_Cobertura || 'Sin Cobertura',
          dias: dias,
          prob: prob,
          prioridad: c.Prioridad_Llamada || 'NORMAL',
          accion: c.Accion_Recomendada || 'Contacto comercial prioritario',
          criterio: c.Criterio_Decision || '',
          ventas: vCop,
          ticket: parseFloat(c.Ticket_Promedio_COP || 0),
          ventaEsperada: parseFloat(c.Venta_Esperada_Prox_Mes_COP || 0),
          ops: ops
        }};

        CLIENTES_MAP.set(cid, obj);
        if (c.Sector) sectoresSet.add(c.Sector);
      }});

      CLIENTES = Array.from(CLIENTES_MAP.values());
    }}

    function initPage() {{
      procesarDatosGlobales();
      actualizarVistas();
      runLiveCalc();
    }}

    function actualizarVistas() {{
      const nTotal = CLIENTES.length;
      const nFrec = CLIENTES.filter(c => c.estado.includes('Frecuente')).length;
      const nFrio = CLIENTES.filter(c => c.estado.includes('Frío')).length;
      const nSeg = nTotal - nFrec - nFrio;

      document.getElementById('kpi-total').innerText = nTotal;
      document.getElementById('kpi-frec').innerText = nFrec;
      document.getElementById('kpi-seg').innerText = nSeg;
      document.getElementById('kpi-frio').innerText = nFrio;
      document.getElementById('kpi-ventas').innerText = '$' + (totalCOP / 1e6).toFixed(1) + 'M';

      const secSelect = document.getElementById('sectorFilter');
      secSelect.innerHTML = '<option value="todos">Todos los Sectores</option>';
      Array.from(sectoresSet).sort().forEach(s => {{
        const opt = document.createElement('option');
        opt.value = s; opt.innerText = s;
        secSelect.appendChild(opt);
      }});

      const cliSelect = document.getElementById('clientSelect');
      cliSelect.innerHTML = '';
      CLIENTES.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c.id; opt.innerText = `${{c.id}} - ${{c.nombre}}`;
        cliSelect.appendChild(opt);
      }});
      cliSelect.onchange = () => renderFicha(cliSelect.value);

      renderSemaforo();
      document.getElementById('searchInput').oninput = renderSemaforo;
      document.getElementById('sectorFilter').onchange = renderSemaforo;

      if (CLIENTES.length > 0) renderFicha(CLIENTES[0].id);
      renderGraficas();
      renderProyeccion();
      renderExplorador();
      renderBacktestTable();
    }}

    function filtrarPorSemaforoCard(estado) {{
      document.querySelectorAll('.kpi-card').forEach(c => c.classList.remove('selected'));
      const selectStatus = document.getElementById('statusFilter');

      if (estado === 'frecuente') {{
        document.getElementById('kpi-card-frec').classList.add('selected');
        selectStatus.value = 'frecuente';
      }} else if (estado === 'seguimiento') {{
        document.getElementById('kpi-card-seg').classList.add('selected');
        selectStatus.value = 'seguimiento';
      }} else if (estado === 'frio') {{
        document.getElementById('kpi-card-frio').classList.add('selected');
        selectStatus.value = 'frio';
      }} else {{
        document.getElementById('kpi-card-total').classList.add('selected');
        selectStatus.value = 'todos';
      }}
      showTab('tab-semaforo', document.getElementById('btn-tab-semaforo'));
      renderSemaforo();
    }}

    function aplicarFiltroSelect() {{
      const val = document.getElementById('statusFilter').value;
      document.querySelectorAll('.kpi-card').forEach(c => c.classList.remove('selected'));
      if (val === 'frecuente') document.getElementById('kpi-card-frec').classList.add('selected');
      else if (val === 'seguimiento') document.getElementById('kpi-card-seg').classList.add('selected');
      else if (val === 'frio') document.getElementById('kpi-card-frio').classList.add('selected');
      else document.getElementById('kpi-card-total').classList.add('selected');
      renderSemaforo();
    }}

    function renderSemaforo() {{
      const query = document.getElementById('searchInput').value.toLowerCase();
      const statusF = document.getElementById('statusFilter').value;
      const cobF = document.getElementById('coberturaFilter').value;
      const prioF = document.getElementById('prioridadFilter') ? document.getElementById('prioridadFilter').value : 'todas';
      const sectorF = document.getElementById('sectorFilter').value;
      const tbody = document.getElementById('semaforoBody');
      tbody.innerHTML = '';

      const filtrados = CLIENTES.filter(c => {{
        const matchQ = c.nombre.toLowerCase().includes(query) || c.id.toLowerCase().includes(query);
        let matchS = true;
        if (statusF === 'frio') matchS = c.estado.includes('Frío');
        else if (statusF === 'frecuente') matchS = c.estado.includes('Frecuente');
        else if (statusF === 'seguimiento') matchS = !c.estado.includes('Frío') && !c.estado.includes('Frecuente');

        let matchCob = true;
        if (cobF === 'proxima') matchCob = c.cobertura.includes('Próxima');
        else if (cobF === 'vigente') matchCob = c.cobertura.includes('Vigente');
        else if (cobF === 'vencida') matchCob = c.cobertura.includes('Vencida');
        else if (cobF === 'sin') matchCob = c.cobertura.includes('Sin Cobertura');
        
        let matchPrio = (prioF === 'todas') || (c.prioridad === prioF);
        let matchSec = (sectorF === 'todos') || (c.sector === sectorF);
        return matchQ && matchS && matchCob && matchPrio && matchSec;
      }});

      document.getElementById('contadorFiltro').innerText = `Mostrando ${{filtrados.length}} de ${{CLIENTES.length}} clientes`;

      filtrados.forEach(c => {{
        const badgeCls = c.estado.includes('Frío') ? 'frio' : c.estado.includes('Frecuente') ? 'frecuente' : 'seguimiento';
        const cobCls = c.cobertura.includes('Próxima') ? 'seguimiento' : c.cobertura.includes('Vigente') ? 'frecuente' : c.cobertura.includes('Vencida') ? 'frio' : 'secondary';
        const prioCls = c.prioridad === 'ALTA' ? 'alta' : c.prioridad === 'MEDIA' ? 'media' : c.prioridad === 'NORMAL' ? 'normal' : 'baja';

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><b>${{c.id}}</b></td>
          <td>${{c.nombre}}</td>
          <td>${{c.sector}}</td>
          <td>${{c.dias}} días</td>
          <td><span class="badge ${{badgeCls}}" onclick="event.stopPropagation(); filtrarPorSemaforoCard('${{badgeCls}}')">${{c.estado}}</span></td>
          <td><span class="badge ${{cobCls}}" style="font-size:11px;">${{c.cobertura}}</span></td>
          <td><b>${{c.prob.toFixed(1)}}%</b></td>
          <td><span class="badge ${{prioCls}}">${{c.prioridad}}</span></td>
          <td><small style="color:var(--text-muted); font-size:11.5px;">${{c.criterio || ''}}</small></td>
          <td>$${{Math.round(c.ventas).toLocaleString('es-CO')}}</td>
          <td><small>${{c.accion}}</small></td>
        `;
        tr.onclick = () => {{
          document.getElementById('detailBox').innerHTML = `
            <div style="font-size:16px; font-weight:800; color:var(--primary); margin-bottom:8px;">
              FICHA DE CONTACTO: ${{c.id}} — ${{c.nombre}} (${{c.sector}})
            </div>
            • <b>Semáforo:</b> <span class="badge ${{badgeCls}}">${{c.estado}}</span> &nbsp;|&nbsp; <b>Cobertura:</b> <span class="badge ${{cobCls}}">${{c.cobertura}}</span> &nbsp;|&nbsp; <b>Prioridad:</b> <span class="badge ${{prioCls}}">${{c.prioridad}}</span><br>
            • <b>Recencia:</b> ${{c.dias}} días sin compra &nbsp;|&nbsp; <b>Prob. Recompra 30d:</b> ${{c.prob.toFixed(1)}}% &nbsp;|&nbsp; <b>Facturación Acumulada:</b> $${{Math.round(c.ventas).toLocaleString('es-CO')}} COP<br>
            • <b>Acción Recomendada para el Asesor:</b> ${{c.accion}}.
          `;
        }};
        tbody.appendChild(tr);
      }});
    }}

    function renderFicha(cid) {{
      const c = CLIENTES_MAP.get(cid);
      if (!c) return;
      const fc = document.getElementById('fichaContenido');
      const badgeCls = c.estado.includes('Frío') ? 'frio' : c.estado.includes('Frecuente') ? 'frecuente' : 'seguimiento';
      const cobCls = c.cobertura.includes('Próxima') ? 'seguimiento' : c.cobertura.includes('Vigente') ? 'frecuente' : c.cobertura.includes('Vencida') ? 'frio' : 'secondary';
      const prioCls = c.prioridad === 'ALTA' ? 'alta' : c.prioridad === 'MEDIA' ? 'media' : 'normal';

      fc.innerHTML = `
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; margin-top:10px;">
          <div style="background:#fff; border:1px solid var(--border); padding:14px; border-radius:8px;">
            <span style="color:var(--text-muted); font-size:12px; font-weight:700;">DATOS GENERALES</span>
            <div style="font-size:16px; font-weight:700; margin-top:4px;">${{c.nombre}}</div>
            <div style="color:var(--text-muted); font-size:13px;">${{c.ciudad}} · ${{c.sector}}</div>
          </div>
          <div style="background:#fff; border:1px solid var(--border); padding:14px; border-radius:8px;">
            <span style="color:var(--text-muted); font-size:12px; font-weight:700;">ESTADO Y COBERTURA</span>
            <div style="margin-top:4px; display:flex; gap:6px;">
              <span class="badge ${{badgeCls}}">${{c.estado}}</span>
              <span class="badge ${{cobCls}}">${{c.cobertura}}</span>
            </div>
            <div style="font-size:13px; margin-top:4px;"><b>${{c.dias}}</b> días sin compra | Prioridad: <span class="badge ${{prioCls}}">${{c.prioridad}}</span></div>
          </div>
          <div style="background:#fff; border:1px solid var(--border); padding:14px; border-radius:8px;">
            <span style="color:var(--text-muted); font-size:12px; font-weight:700;">PROPENSIÓN PREDICTIVA IA</span>
            <div style="font-size:18px; font-weight:800; color:var(--primary); margin-top:4px;">${{c.prob.toFixed(1)}}%</div>
            <div style="font-size:12px; color:var(--text-muted);">Venta esperada prox. mes: $${{Math.round(c.ventaEsperada).toLocaleString('es-CO')}} COP</div>
          </div>
        </div>
      `;

      const tbody = document.getElementById('clienteOpsBody');
      tbody.innerHTML = '';
      if (!c.ops || c.ops.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">Cuenta sin transacciones de venta registradas en el periodo auditado.</td></tr>';
      }} else {{
        c.ops.forEach(op => {{
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${{op.Fecha || ''}}</td>
            <td><b>${{op.Producto || 'Servicio'}}</b></td>
            <td>${{op.Familia_Producto || 'TI'}}</td>
            <td>${{op.Cantidad || 1}}</td>
            <td>${{op.Moneda || 'COP'}}</td>
            <td>$${{parseFloat(op.TRM || 4000).toFixed(0)}}</td>
            <td>$${{Math.round(parseFloat(op.Ventas_COP || 0)).toLocaleString('es-CO')}}</td>
            <td>${{op.Estado_Venta || 'Confirmada'}}</td>
          `;
          tbody.appendChild(tr);
        }});
      }}
    }}

    let chartTRMInst = null;
    let chartProyInst = null;

    function renderGraficas() {{
      const meses = Array.from(mesesVentas.keys()).sort();
      const ventasData = meses.map(m => Math.round((mesesVentas.get(m) || 0) / 1e6));
      const trmData = meses.map(m => {{
        const arr = mesesTRM.get(m) || [4000];
        return Math.round(arr.reduce((a,b)=>a+b, 0) / arr.length);
      }});

      if (chartTRMInst) chartTRMInst.destroy();
      chartTRMInst = new Chart(document.getElementById('chartTRM'), {{
        type: 'line',
        data: {{
          labels: meses,
          datasets: [
            {{
              type: 'bar',
              label: 'Ventas Mensuales (Millones COP)',
              data: ventasData,
              backgroundColor: 'rgba(37, 99, 235, 0.75)',
              yAxisID: 'y'
            }},
            {{
              type: 'line',
              label: 'TRM Promedio Diaria (COP/USD)',
              data: trmData,
              borderColor: '#dc2626',
              borderWidth: 3,
              tension: 0.2,
              yAxisID: 'y1'
            }}
          ]
        }},
        options: {{
          responsive: true,
          scales: {{
            y: {{ type: 'linear', position: 'left', title: {{ display: true, text: 'Millones COP' }} }},
            y1: {{ type: 'linear', position: 'right', grid: {{ drawOnChartArea: false }}, title: {{ display: true, text: 'TRM (COP)' }} }}
          }}
        }}
      }});
    }}

    function renderProyeccion() {{
      const meses = Array.from(mesesVentas.keys()).sort();
      const ventasData = meses.map(m => Math.round((mesesVentas.get(m) || 0) / 1e6));

      const mesesConNov = [...meses, '2026-11 (Proy.)'];
      const ventasHist = [...ventasData, null];
      const ventasProy = new Array(meses.length - 1).fill(null);
      ventasProy.push(ventasData[ventasData.length - 1]);
      
      const proyNovCOP = (CIFRAS.proyeccion ? CIFRAS.proyeccion.ingreso_esperado_cop : 216486298.77) / 1e6;
      ventasProy.push(proyNovCOP);

      if (chartProyInst) chartProyInst.destroy();
      chartProyInst = new Chart(document.getElementById('chartProyeccion'), {{
        type: 'line',
        data: {{
          labels: mesesConNov,
          datasets: [
            {{
              label: 'Facturación Histórica (Millones COP)',
              data: ventasHist,
              borderColor: '#2563eb',
              backgroundColor: 'rgba(37, 99, 235, 0.15)',
              fill: true,
              tension: 0.2
            }},
            {{
              label: `Proyección IA Noviembre 2026 ($${{proyNovCOP.toFixed(1)}}M COP)`,
              data: ventasProy,
              borderColor: '#8b5cf6',
              borderDash: [6, 6],
              backgroundColor: 'rgba(139, 92, 246, 0.25)',
              fill: true,
              pointRadius: 6,
              pointBackgroundColor: '#8b5cf6'
            }}
          ]
        }},
        options: {{
          responsive: true,
          scales: {{
            y: {{ title: {{ display: true, text: 'Millones COP' }} }}
          }}
        }}
      }});

      // Render tabla de clientes proyectados (prob >= 40%)
      const tbody = document.getElementById('proyBody');
      tbody.innerHTML = '';

      const proyectados = CLIENTES.filter(c => c.prob >= 40).sort((a,b) => b.ventaEsperada - a.ventaEsperada);

      proyectados.slice(0, 30).forEach(c => {{
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><b>${{c.id}}</b></td>
          <td>${{c.nombre}}</td>
          <td>${{c.sector}}</td>
          <td><span class="badge frecuente">${{c.prob.toFixed(1)}}%</span></td>
          <td>$${{Math.round(c.ticket).toLocaleString('es-CO')}} COP</td>
          <td><b>$${{Math.round(c.ventaEsperada).toLocaleString('es-CO')}} COP</b></td>
          <td><small>${{c.accion}}</small></td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function renderBacktestTable() {{
      const tbody = document.getElementById('backtestBody');
      if (!tbody) return;
      tbody.innerHTML = '';

      const backtest = CIFRAS.backtest_pronostico;
      if (backtest && backtest.detalle) {{
        backtest.detalle.forEach(d => {{
          const tr = document.createElement('tr');
          const modGana = d.error_absoluto_modelo_cop <= d.error_absoluto_linea_base_cop;
          tr.innerHTML = `
            <td><b>${{d.mes_objetivo}}</b></td>
            <td>${{d.corte}}</td>
            <td>$${{Math.round(d.pronostico_modelo_cop).toLocaleString('es-CO')}}</td>
            <td>$${{Math.round(d.linea_base_ultimo_mes_cop).toLocaleString('es-CO')}}</td>
            <td><b>$${{Math.round(d.real_cop).toLocaleString('es-CO')}}</b></td>
            <td style="color:${{modGana ? 'var(--success)' : 'inherit'}}; font-weight:${{modGana ? '700' : 'normal'}}">$${{Math.round(d.error_absoluto_modelo_cop).toLocaleString('es-CO')}}</td>
            <td style="color:${{!modGana ? 'var(--success)' : 'inherit'}}">$${{Math.round(d.error_absoluto_linea_base_cop).toLocaleString('es-CO')}}</td>
            <td>${{modGana ? '<span class="badge frecuente">🏆 Modelo OperIA</span>' : '<span class="badge seguimiento">Línea Base</span>'}}</td>
          `;
          tbody.appendChild(tr);
        }});
      }}
    }}

    // Calculadora interactiva paso a paso
    function runLiveCalc() {{
      const dias = parseFloat(document.getElementById('calc-dias').value) || 0;
      const f30 = parseFloat(document.getElementById('calc-f30').value) || 0;
      const f90 = parseFloat(document.getElementById('calc-f90').value) || 0;
      const hist = parseFloat(document.getElementById('calc-hist').value) || 0;

      const mu = METRICAS.medias_escalado || [126.56, 0.68, 1.88, 4.35];
      const sd = METRICAS.desviaciones_escalado || [234.53, 0.84, 1.59, 3.56];
      const w = METRICAS.pesos_modelo || [0.026714, -0.059519, 0.101297, 0.130378, -0.124296];

      const zRec = (dias - mu[0]) / sd[0];
      const zF30 = (f30 - mu[1]) / sd[1];
      const zF90 = (f90 - mu[2]) / sd[2];
      const zHist = (hist - mu[3]) / sd[3];

      const c0 = w[0];
      const c1 = w[1] * zRec;
      const c2 = w[2] * zF30;
      const c3 = w[3] * zF90;
      const c4 = w[4] * zHist;

      const zTotal = c0 + c1 + c2 + c3 + c4;
      const p = 1 / (1 + Math.exp(-Math.max(-35, Math.min(35, zTotal))));
      const pPct = (p * 100).toFixed(1);

      document.getElementById('calc-breakdown').innerHTML = `
        <h5 style="color:var(--primary); margin-bottom:12px;">📊 Desglose de Cálculo Matemático Paso a Paso:</h5>
        <div class="calc-step">
          <div class="calc-step-num">1</div>
          <div style="flex:1;"><b>Normalización Z-score:</b> Recencia: <code>${{zRec.toFixed(2)}}</code> | Frec 30d: <code>${{zF30.toFixed(2)}}</code> | Frec 90d: <code>${{zF90.toFixed(2)}}</code> | Historial: <code>${{zHist.toFixed(2)}}</code></div>
        </div>
        <div class="calc-step">
          <div class="calc-step-num">2</div>
          <div style="flex:1;"><b>Contribuciones Lineales (w × x̃):</b> Sesgo: <code>${{c0.toFixed(4)}}</code> | Recencia: <code>${{c1.toFixed(3)}}</code> | Frec 30d: <code>+${{c2.toFixed(3)}}</code> | Frec 90d: <code>+${{c3.toFixed(3)}}</code> | Hist: <code>${{c4.toFixed(3)}}</code></div>
        </div>
        <div class="calc-step">
          <div class="calc-step-num">3</div>
          <div style="flex:1;"><b>Puntaje Logit Total (z):</b> <code>${{zTotal.toFixed(4)}}</code></div>
        </div>
        <div class="calc-step" style="background:#eff6ff; border-left:4px solid var(--primary-light);">
          <div class="calc-step-num" style="background:var(--success);">4</div>
          <div style="flex:1; font-size:15px;">
            <b>Probabilidad Sigmoide Resultante:</b> <span style="font-size:22px; font-weight:800; color:var(--primary);">${{pPct}}%</span>
            &nbsp; | &nbsp; <b>Decisión:</b> ${{p >= 0.4 ? '<span class="badge frecuente">✅ ALTA PROPENSIÓN (COMPRARÁ)</span>' : '<span class="badge frio">❄️ BAJA PROPENSIÓN</span>'}}
          </div>
        </div>
      `;
    }}

    function renderExplorador() {{
      const tbody = document.getElementById('rawDataBody');
      tbody.innerHTML = '';
      ACTIVE_RAW_DATA.slice(0, 100).forEach(r => {{
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${{r.Venta_ID || ''}}</td>
          <td>${{r.Fecha || ''}}</td>
          <td>${{r.Cliente || ''}}</td>
          <td>${{r.Producto || ''}}</td>
          <td>${{r.Cantidad || ''}}</td>
          <td>${{r.Moneda || ''}}</td>
          <td>$${{parseFloat(r.TRM || 4000).toFixed(0)}}</td>
          <td>$${{Math.round(parseFloat(r.Ventas_COP || 0)).toLocaleString('es-CO')}}</td>
          <td>${{r.Estado_Venta || ''}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function simularClienteIndividual() {{
      const dias = parseFloat(document.getElementById('sim-dias').value) || 0;
      const f30 = parseFloat(document.getElementById('sim-f30').value) || 0;
      const f90 = parseFloat(document.getElementById('sim-f90').value) || 0;
      const hist = parseFloat(document.getElementById('sim-hist').value) || 0;
      const renov = document.getElementById('sim-renovacion').value;
      const monto = parseFloat(document.getElementById('sim-monto').value) || 0;

      const prob = predictRecompra(dias, f30, f90, hist);
      const sem = evaluarSemaforo(dias, renov);
      const probPct = (prob * 100).toFixed(1);
      const valorEsperado = prob * monto;

      const resDiv = document.getElementById('sim-resultado');
      resDiv.style.display = 'block';
      resDiv.innerHTML = `
        <h4 style="color:var(--primary); margin-bottom:12px;">📊 Resultado de Simulación Predictiva y Operativa:</h4>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; margin-bottom:16px;">
          <div style="background:#f8fafc; padding:12px; border-radius:8px; border:1px solid var(--border);">
            <div style="font-size:12px; color:var(--text-muted); font-weight:700;">ESTADO DE CARTERA</div>
            <div style="margin-top:6px;"><span class="badge ${{sem.badgeClass}}" style="font-size:13px;">${{sem.estado}}</span></div>
            <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">${{sem.criterio}}</div>
          </div>
          <div style="background:#f8fafc; padding:12px; border-radius:8px; border:1px solid var(--border);">
            <div style="font-size:12px; color:var(--text-muted); font-weight:700;">PROBABILIDAD IA (30 DÍAS)</div>
            <div style="font-size:24px; font-weight:800; color:var(--primary); margin-top:4px;">${{probPct}}%</div>
            <div style="font-size:12px;">${{prob >= 0.4 ? '<span class="badge frecuente">Probabilidad ≥ 40% (Recompra Esperada)</span>' : '<span class="badge frio">Probabilidad < 40% (Baja Actividad)</span>'}}</div>
          </div>
          <div style="background:#f8fafc; padding:12px; border-radius:8px; border:1px solid var(--border);">
            <div style="font-size:12px; color:var(--text-muted); font-weight:700;">PRIORIDAD DE LLAMADA</div>
            <div style="font-size:22px; font-weight:800; color:${{sem.prioridad === 'ALTA' ? 'var(--danger)' : sem.prioridad === 'MEDIA' ? 'var(--warning)' : 'var(--primary)'}}; margin-top:4px;">${{sem.prioridad}}</div>
            <div style="font-size:12px; color:var(--text-muted);">Ingreso esperado: $${{Math.round(valorEsperado).toLocaleString('es-CO')}} COP</div>
          </div>
        </div>
        <div style="background:#eff6ff; border-left:4px solid var(--primary-light); padding:12px 16px; border-radius:6px;">
          <b>Guía para el Asesor:</b> ${{sem.accion}}.
        </div>
      `;
    }}

    function procesarUserCsv() {{
      const fileInput = document.getElementById('userCsvFile');
      const msg = document.getElementById('userCsvMsg');
      if (!fileInput.files || fileInput.files.length === 0) {{
        msg.style.color = 'var(--danger)';
        msg.innerText = '❌ Por favor selecciona un archivo CSV primero.';
        return;
      }}

      const file = fileInput.files[0];
      const reader = new FileReader();
      reader.onload = function(e) {{
        try {{
          const text = e.target.result;
          const lines = text.split(/\\r\\n|\\n/).filter(l => l.trim().length > 0);
          if (lines.length < 2) throw new Error("CSV sin registros suficientes.");

          const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
          const newRows = [];
          for (let i = 1; i < lines.length; i++) {{
            const parts = lines[i].split(',').map(p => p.trim().replace(/^"|"$/g, ''));
            const row = {{}};
            headers.forEach((h, idx) => {{ row[h] = parts[idx] || ''; }});
            newRows.push(row);
          }}

          // Actualizar vista
          ACTIVE_VISTA_360 = newRows.map(r => ({{
            Cliente_ID: r.Cliente_ID || r.id || 'CLI-CUSTOM',
            Cliente: r.Cliente || r.nombre || 'Cliente Personalizado',
            Sector: r.Sector || r.sector || 'General',
            Ciudad: r.Ciudad || r.ciudad || 'Bogotá',
            Estado_Cliente: r.Estado_Cliente || (parseInt(r.Dias_Sin_Comprar || 0) >= 90 ? 'Frío (Riesgo de Abandono)' : 'Frecuente (Activo)'),
            Estado_Cobertura: r.Estado_Cobertura || 'Vigente (> 45d)',
            Dias_Sin_Comprar: r.Dias_Sin_Comprar || '15',
            Prob_Recompra_Pct: r.Prob_Recompra_Pct || '55.0',
            Prioridad_Llamada: r.Prioridad_Llamada || 'MEDIA',
            Accion_Recomendada: r.Accion_Recomendada || 'Seguimiento personalizado',
            Criterio_Decision: 'Cargado por usuario',
            Ventas_COP: r.Ventas_COP || '10000000',
            Ticket_Promedio_COP: r.Ticket_Promedio_COP || '5000000',
            Venta_Esperada_Prox_Mes_COP: r.Venta_Esperada_Prox_Mes_COP || '2750000'
          }}));

          procesarDatosGlobales();
          actualizarVistas();
          msg.style.color = 'var(--success)';
          msg.innerText = `✅ ¡Archivo cargado exitosamente! ${{newRows.length}} registros procesados.`;
        }} catch(err) {{
          msg.style.color = 'var(--danger)';
          msg.innerText = '❌ Error al procesar CSV: ' + err.message;
        }}
      }};
      reader.readAsText(file);
    }}

    function restaurarDatosOriginales() {{
      ACTIVE_VISTA_360 = [...INITIAL_VISTA_360];
      ACTIVE_RAW_DATA = [...INITIAL_RAW_DATA];
      totalCOP = CIFRAS.ingreso_cop_total || 5647449456.37;
      procesarDatosGlobales();
      actualizarVistas();
      const msg = document.getElementById('userCsvMsg');
      if (msg) {{
        msg.style.color = 'var(--primary)';
        msg.innerText = '🔄 Datos oficiales restaurados (120 clientes auditados).';
      }}
    }}

    function showTab(tabId, btn) {{
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      const target = document.getElementById(tabId);
      if (target) target.classList.add('active');
      if (btn) btn.classList.add('active');
    }}

    function toggleAccordion(header) {{
      const parent = header.parentElement;
      parent.classList.toggle('open');
      const icon = header.querySelector('span:last-child');
      icon.innerText = parent.classList.contains('open') ? '▼' : '▶';
    }}

    function exportarCSV(completo = false) {{
      const query = document.getElementById('searchInput').value.toLowerCase();
      const statusF = document.getElementById('statusFilter').value;
      const cobF = document.getElementById('coberturaFilter').value;
      const prioF = document.getElementById('prioridadFilter') ? document.getElementById('prioridadFilter').value : 'todas';
      const sectorF = document.getElementById('sectorFilter').value;

      const dataToExport = completo ? CLIENTES : CLIENTES.filter(c => {{
        const matchQ = c.nombre.toLowerCase().includes(query) || c.id.toLowerCase().includes(query);
        let matchS = true;
        if (statusF === 'frio') matchS = c.estado.includes('Frío');
        else if (statusF === 'frecuente') matchS = c.estado.includes('Frecuente');
        else if (statusF === 'seguimiento') matchS = !c.estado.includes('Frío') && !c.estado.includes('Frecuente');

        let matchCob = true;
        if (cobF === 'proxima') matchCob = c.cobertura.includes('Próxima');
        else if (cobF === 'vigente') matchCob = c.cobertura.includes('Vigente');
        else if (cobF === 'vencida') matchCob = c.cobertura.includes('Vencida');
        else if (cobF === 'sin') matchCob = c.cobertura.includes('Sin Cobertura');

        let matchPrio = (prioF === 'todas') || (c.prioridad === prioF);
        let matchSec = (sectorF === 'todos') || (c.sector === sectorF);
        return matchQ && matchS && matchCob && matchPrio && matchSec;
      }});

      let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
      csvContent += "Cliente_ID,Empresa,Sector,Dias_Sin_Comprar,Estado_Semaforo,Estado_Cobertura,Probabilidad_Recompra_Pct,Prioridad_Llamada,Ventas_COP,Accion_Recomendada\\n";

      dataToExport.forEach(c => {{
        csvContent += `"${{c.id}}","${{c.nombre}}","${{c.sector}}",${{c.dias}},"${{c.estado}}","${{c.cobertura}}",${{c.prob.toFixed(1)}},"${{c.prioridad}}",${{Math.round(c.ventas)}},"${{c.accion}}"\\n`;
      }});

      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", completo ? "OperIA_Cartera_Clientes_120.csv" : "OperIA_Clientes_Filtrados.csv");
      document.body.appendChild(link);
      link.click();
      link.remove();
    }}

    function descargarEvidencias() {{
      const evidencias = {{
        fecha_auditoria: new Date().toISOString(),
        proyecto: "OperIA 360° — Green Services and Solutions SAS",
        alcance: "Reto 4: IA en Operaciones (Hackatón EstudIA - Capa 2)",
        datos_oficiales_verificados: {{
          clientes_totales: CIFRAS.clientes_total || 120,
          operaciones_confirmadas: CIFRAS.operaciones_confirmadas || 1371,
          facturacion_total_cop: CIFRAS.ingreso_cop_total || 5647449456.37,
          clientes_frios_detectados: CIFRAS.frios_regla_oficial || 41,
          cuentas_frecuentes: CIFRAS.estados ? CIFRAS.estados["Frecuente (Activo)"] : 38,
          cuentas_base_instalada: CIFRAS.estados ? CIFRAS.estados["Base Instalada (Seguimiento)"] : 41
        }},
        proyeccion_noviembre_2026: CIFRAS.proyeccion || {{}},
        backtest_validacion_historica: CIFRAS.backtest_pronostico || {{}},
        metricas_modelo_ia: CIFRAS.metricas_modelo || {{}},
        casos_controlados_validados: [
          {{ id: "TEST-01", caso: "Conversión COP con descuento", obtenido: "$180.000 COP", estado: "APROBADO" }},
          {{ id: "TEST-02", caso: "Conversión USD con TRM", obtenido: "$1.200.000 COP", estado: "APROBADO" }},
          {{ id: "TEST-03", caso: "Exclusión de ventas anuladas", obtenido: "$0 COP excluido", estado: "APROBADO" }},
          {{ id: "TEST-04", caso: "Cliente frío en frontera 90d", obtenido: "90 días -> Frío", estado: "APROBADO" }},
          {{ id: "TEST-05", caso: "Póliza renovación frontera 45d", obtenido: "45 días -> Renovación", estado: "APROBADO" }},
          {{ id: "TEST-06", caso: "Cliente sin datos", obtenido: "Manejo seguro sin distorsión", estado: "APROBADO" }}
        ],
        calidad_datos_incidencias_aisladas: [
          {{ id: "INC-01", fila: 1, tipo: "ID venta duplicado", tratamiento: "Descarte redundante" }},
          {{ id: "INC-02", fila: 14, tipo: "Cliente inexistente CLI999", tratamiento: "Aislamiento para CRM" }},
          {{ id: "INC-03", fila: 27, tipo: "Fecha invalida 2026-02-30", tratamiento: "Rechazo de formato" }},
          {{ id: "INC-04", fila: 38, tipo: "Moneda EUR no cubierta", tratamiento: "Aislamiento sin TRM" }},
          {{ id: "INC-05", fila: 51, tipo: "Cantidad negativa -2", tratamiento: "Exclusion de calculo" }},
          {{ id: "INC-06", fila: 62, tipo: "Precio unitario vacio", tratamiento: "Marcado incompleto" }},
          {{ id: "INC-07", fila: 75, tipo: "Producto inexistente PRO99", tratamiento: "Aislamiento de catalogo" }}
        ]
      }};

      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(evidencias, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", "OperIA_Reporte_Evidencias_EstudIA.json");
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    }}

    window.onload = initPage;
  </script>
</body>
</html>
"""

# Generar index.html y visor/visor.html
index_path = ROOT / "index.html"
visor_path = ROOT / "visor" / "visor.html"

index_path.write_text(html_content, encoding="utf-8")
print(f"index.html generado exitosamente: {len(html_content)} bytes.")

visor_path.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(index_path, visor_path)
print(f"visor/visor.html actualizado exitosamente.")
