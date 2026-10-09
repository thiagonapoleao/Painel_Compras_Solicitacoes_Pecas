import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd
import re
import os
import base64

# Link oficial do Web App do Google Apps Script
APPS_SCRIPT_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbyEr_l9ulBrh04iFybET96bMlLRydzF3epQSMZXBBr5rAbqBm2M4jW_zPrR3dDcqiUZGg/exec"

st.set_page_config(
    page_title="Gestão de Peças & Solicitações de Compras",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CARREGAMENTO DO ARQUIVO "Logotipo.PNG" NA MESMA PASTA DO APP.PY
# ==============================================================================
def obter_logo_base64():
    pastas_busca = [
        os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "",
        os.getcwd(),
        "."
    ]
    
    nomes_alvo = [
        "Logotipo.PNG", "Logotipo.png", "logotipo.PNG", "logotipo.png",
        "LOGOTIPO.PNG", "logo.PNG", "logo.png"
    ]
    
    caminho_encontrado = None
    for pasta in pastas_busca:
        if not pasta:
            continue
        for nome in nomes_alvo:
            candidato = os.path.join(pasta, nome)
            if os.path.isfile(candidato):
                caminho_encontrado = candidato
                break
        if caminho_encontrado:
            break
            
    if not caminho_encontrado:
        for pasta in pastas_busca:
            if not pasta or not os.path.isdir(pasta):
                continue
            for arq in os.listdir(pasta):
                if arq.lower() in ["logotipo.png", "logotipo.jpg", "logotipo.jpeg"]:
                    caminho_encontrado = os.path.join(pasta, arq)
                    break
            if caminho_encontrado:
                break

    if caminho_encontrado and os.path.exists(caminho_encontrado):
        ext = os.path.splitext(caminho_encontrado)[1].lower().replace(".", "")
        mime = "jpeg" if ext in ["jpg", "jpeg"] else "png"
        with open(caminho_encontrado, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/{mime};base64,{encoded}"
            
    return ""

logo_base64_src = obter_logo_base64()

SPREADSHEET_ID = "1iWjdaZLAp5hi9YIhmfSO4cPBn6fkfDjef8PAdZp1nsY"
GID_BASE_PECAS = "270834817"      # Aba: Base de Dados (catálogo)
GID_ORDEM_COMPRA = "643448898"     # Aba: Ordem de Compra(Peças)

URL_CSV_CATALOGO = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_BASE_PECAS}"
URL_CSV_ORDENS = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_ORDEM_COMPRA}"

@st.cache_data(ttl=30)
def carregar_catalogo_planilha():
    df = None
    try:
        df = pd.read_csv(URL_CSV_CATALOGO, dtype=str)
    except Exception:
        pass

    if df is None or df.empty:
        return []

    col_a = df.columns[0]
    col_b = df.columns[1] if len(df.columns) > 1 else col_a
    col_c = df.columns[2] if len(df.columns) > 2 else col_a
    col_f = df.columns[5] if len(df.columns) > 5 else df.columns[-1]

    catalogo = []
    for _, row in df.iterrows():
        cod = str(row[col_a]).strip() if pd.notna(row[col_a]) else ""
        desc = str(row[col_b]).strip() if pd.notna(row[col_b]) else ""
        cat = str(row[col_c]).strip() if pd.notna(row[col_c]) else "Geral"
        forn = str(row[col_f]).strip() if pd.notna(row[col_f]) else ""

        if cod and desc and cod.lower() not in ["nan", "produto", "código", "codigo"]:
            catalogo.append({
                "codigo": cod,
                "descricao": desc,
                "categoria": cat,
                "fornecedor": forn
            })
    return catalogo

def obter_dados_ordens_e_proxima_oc():
    df = None
    try:
        df = pd.read_csv(URL_CSV_ORDENS, dtype=str)
    except Exception:
        pass

    ocs_existentes = []
    maior_por_ano = {}

    if df is not None and not df.empty:
        col_oc = df.columns[0]
        col_cod = df.columns[1] if len(df.columns) > 1 else ""
        col_prod = df.columns[2] if len(df.columns) > 2 else ""
        col_cat = df.columns[3] if len(df.columns) > 3 else ""
        col_data = df.columns[4] if len(df.columns) > 4 else ""
        col_custo = df.columns[6] if len(df.columns) > 6 else ""
        col_qt = df.columns[7] if len(df.columns) > 7 else ""
        col_qt_aprov = df.columns[8] if len(df.columns) > 8 else ""
        col_venda = df.columns[10] if len(df.columns) > 10 else ""
        col_forn = df.columns[11] if len(df.columns) > 11 else ""
        col_obs = df.columns[13] if len(df.columns) > 13 else ""

        for _, r in df.iterrows():
            oc_val = str(r[col_oc]).strip() if pd.notna(r[col_oc]) else ""
            if not oc_val or oc_val.lower() in ["nan", "ordem de compra"]:
                continue

            match = re.search(r'OC-(\d{4})-(\d+)', oc_val, re.IGNORECASE)
            if match:
                ano_str = match.group(1)
                seq_num = int(match.group(2))
                maior_por_ano[ano_str] = max(maior_por_ano.get(ano_str, 0), seq_num)

            obs_val = str(r[col_obs]) if pd.notna(r[col_obs]) else ""
            solic = obs_val.replace("Solicitante:", "").strip() if "Solicitante:" in obs_val else ""

            def to_float(val):
                if not val or pd.isna(val): return 0.0
                s = str(val).replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                try: return float(s)
                except: return 0.0

            custo_u = to_float(r.get(col_custo, 0))
            qt_val = int(to_float(r.get(col_qt, 1)))
            qt_ap = int(to_float(r.get(col_qt_aprov, qt_val)))
            venda_u = to_float(r.get(col_venda, 0))

            ocs_existentes.append({
                "oc": oc_val,
                "data": str(r.get(col_data, "")).strip(),
                "solicitante": solic,
                "fornecedor": str(r.get(col_forn, "")).strip(),
                "codigoPeca": str(r.get(col_cod, "")).strip(),
                "peca": str(r.get(col_prod, "")).strip(),
                "categoria": str(r.get(col_cat, "")).strip(),
                "qt": qt_val,
                "qtAprovada": qt_ap,
                "qtNaoAprovada": max(0, qt_val - qt_ap),
                "custoUnit": custo_u,
                "vendaUnit": venda_u if venda_u > 0 else (custo_u * 1.70),
                "custoTotal": qt_ap * custo_u
            })

    return ocs_existentes, maior_por_ano

catalogo_pecas = carregar_catalogo_planilha()
catalogo_json = json.dumps(catalogo_pecas, ensure_ascii=False)
total_itens_carregados = len(catalogo_pecas)

ocs_planilha, max_seq_anos = obter_dados_ordens_e_proxima_oc()
ocs_planilha_json = json.dumps(ocs_planilha, ensure_ascii=False)
max_seq_anos_json = json.dumps(max_seq_anos, ensure_ascii=False)

html_code = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard Executivo - Solicitações & Ordens de Compra</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    body {{ 
      font-family: 'Inter', system-ui, -apple-system, sans-serif; 
      background-color: #f1f5f9; 
      color: #1e293b; 
    }}
    .kpi-card {{
      background-color: #ffffff;
      border: 1px solid #e2e8f0;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .kpi-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}
    .nav-btn.active {{ 
      background-color: #0284c7; 
      color: #ffffff; 
      box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.25);
    }}
    .nav-btn.inactive {{ 
      background-color: #ffffff; 
      color: #64748b; 
      border: 1px solid #e2e8f0; 
    }}
    @media print {{
      body * {{ visibility: hidden; }}
      #printArea, #printArea * {{ visibility: visible; }}
      #printArea {{ 
        position: absolute; 
        left: 0; 
        top: 0; 
        width: 100%; 
        padding: 24px; 
        background: #ffffff !important; 
        color: #000000 !important;
      }}
      .no-print {{ display: none !important; }}
    }}
  </style>
</head>
<body class="bg-slate-100 min-h-screen">

  <!-- Header Superior com Apenas o Logotipo -->
  <header class="no-print sticky top-0 z-40 bg-white/95 border-b border-slate-200 backdrop-blur-md px-6 py-3">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
      <div class="flex items-center gap-4">
        <!-- Renderização do Logotipo sem o texto "Master Café" -->
        <div class="flex items-center justify-center p-1 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden" style="height: 54px; min-width: 54px;">
          <img id="headerLogoImg" src="{logo_base64_src}" alt="Logotipo" class="max-h-12 w-auto object-contain" onerror="this.style.display='none'; document.getElementById('headerFallbackIcon').style.display='flex';">
          <div id="headerFallbackIcon" style="display: {'none' if logo_base64_src else 'flex'};" class="w-10 h-10 bg-amber-700 text-white rounded-lg items-center justify-center font-black text-sm">
            ☕
          </div>
        </div>
        <div>
          <h1 class="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Painel de Gestão de Peças & Compras
          </h1>
          <p class="text-xs text-slate-500">Controle Operacional, Ordens de Serviço & Estoque · {total_itens_carregados} peças na base</p>
        </div>
      </div>
      
      <div class="flex items-center gap-2 bg-slate-100 p-1.5 rounded-2xl border border-slate-200">
        <button id="navDashboard" class="nav-btn inactive flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition" onclick="switchPage('dashboard')">
          <i data-lucide="layout-dashboard" class="w-4 h-4"></i>
          Dashboard
        </button>
        <button id="navForm" class="nav-btn active flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition" onclick="switchPage('formulario')">
          <i data-lucide="plus-circle" class="w-4 h-4"></i>
          Nova Solicitação (OC)
        </button>
        <button onclick="window.parent.location.reload()" title="Clique para recarregar da planilha" class="inline-flex items-center px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300 hover:bg-emerald-100 cursor-pointer transition">
          <span class="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span> Sincronizar 🔄
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">

    <!-- ==================== PÁGINA 1: DASHBOARD ==================== -->
    <div id="pageDashboard" class="hidden space-y-6">

      <!-- Filtros Dinâmicos -->
      <section class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <i data-lucide="sliders" class="w-4 h-4 text-blue-500"></i>
            <span>Filtros do Painel de Solicitações</span>
          </div>
          <span id="activeFilterBadge" class="text-xs font-medium text-slate-500">Filtrando: Todos os registros</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Ano</label>
            <select id="filterYear" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-800">
              <option value="ALL">Todos os Anos</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Mês</label>
            <select id="filterMonth" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-800">
              <option value="ALL">Todos os Meses</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Categoria de Peças</label>
            <select id="filterCategory" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-800">
              <option value="ALL">Todas as Categorias</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Solicitante</label>
            <select id="filterRequester" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-800">
              <option value="ALL">Todos os Solicitantes</option>
            </select>
          </div>

          <div class="flex items-end">
            <button id="resetFilters" class="w-full py-2 px-4 rounded-xl border border-slate-300 bg-slate-100 text-xs font-semibold text-slate-600 hover:bg-slate-200 transition flex items-center justify-center gap-1.5">
              <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i>
              Limpar Filtros
            </button>
          </div>
        </div>
      </section>

      <!-- CARDS DE KPIS -->
      <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <div class="kpi-card p-4 rounded-2xl shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Valor Compras (Custo)</span>
            <span class="p-1.5 rounded-lg bg-amber-50 text-amber-600"><i data-lucide="badge-dollar-sign" class="w-4 h-4"></i></span>
          </div>
          <div class="mt-3">
            <span id="kpiTotalCost" class="text-xl font-bold tracking-tight text-amber-600">R$ 0,00</span>
            <p class="text-[11px] text-slate-400 mt-0.5">Soma da coluna Custo</p>
          </div>
        </div>

        <div class="kpi-card p-4 rounded-2xl shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total de Pedidos</span>
            <span class="p-1.5 rounded-lg bg-blue-50 text-blue-600"><i data-lucide="clipboard-list" class="w-4 h-4"></i></span>
          </div>
          <div class="mt-3">
            <span id="kpiTotalRequests" class="text-xl font-bold tracking-tight text-slate-800">0</span>
            <p class="text-[11px] text-slate-400 mt-0.5">Ordens registradas</p>
          </div>
        </div>

        <div class="kpi-card p-4 rounded-2xl shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Qtde Solicitada</span>
            <span class="p-1.5 rounded-lg bg-indigo-50 text-indigo-600"><i data-lucide="boxes" class="w-4 h-4"></i></span>
          </div>
          <div class="mt-3">
            <span id="kpiItemsQty" class="text-xl font-bold tracking-tight text-slate-800">0 un</span>
            <p class="text-[11px] text-slate-400 mt-0.5">Peças pedidas</p>
          </div>
        </div>

        <div class="kpi-card p-4 rounded-2xl shadow-sm flex flex-col justify-between border-emerald-200">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-emerald-600 uppercase tracking-wider">Peças Atendidas</span>
            <span class="p-1.5 rounded-lg bg-emerald-50 text-emerald-600"><i data-lucide="check-circle-2" class="w-4 h-4"></i></span>
          </div>
          <div class="mt-3 flex items-baseline justify-between">
            <div>
              <span id="kpiApprovedQty" class="text-xl font-bold tracking-tight text-emerald-600">0 un</span>
              <p class="text-[11px] text-slate-400 mt-0.5">Aprovadas</p>
            </div>
            <span id="kpiApprovedPercent" class="text-xs font-semibold px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800">0%</span>
          </div>
        </div>

        <div class="kpi-card p-4 rounded-2xl shadow-sm flex flex-col justify-between border-rose-200">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-rose-600 uppercase tracking-wider">Não Atendidas</span>
            <span class="p-1.5 rounded-lg bg-rose-50 text-rose-600"><i data-lucide="x-circle" class="w-4 h-4"></i></span>
          </div>
          <div class="mt-3 flex items-baseline justify-between">
            <div>
              <span id="kpiUnapprovedQty" class="text-xl font-bold tracking-tight text-rose-600">0 un</span>
              <p class="text-[11px] text-slate-400 mt-0.5">Pendentes</p>
            </div>
            <span id="kpiUnapprovedPercent" class="text-xs font-semibold px-2 py-0.5 rounded-md bg-rose-100 text-rose-800">0%</span>
          </div>
        </div>

        <div class="kpi-card p-4 rounded-2xl shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Custo Médio / OC</span>
            <span class="p-1.5 rounded-lg bg-cyan-50 text-cyan-600"><i data-lucide="calculator" class="w-4 h-4"></i></span>
          </div>
          <div class="mt-3">
            <span id="kpiAvgCost" class="text-xl font-bold tracking-tight text-slate-800">R$ 0,00</span>
            <p class="text-[11px] text-slate-400 mt-0.5">Média por pedido</p>
          </div>
        </div>
      </section>

      <!-- Gráficos -->
      <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 class="font-bold text-base text-slate-800 mb-2">Top 5 Solicitantes — Agosto</h3>
          <div class="relative h-64"><canvas id="chartTopAgosto"></canvas></div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 class="font-bold text-base text-slate-800 mb-2">Top 5 Solicitantes — Setembro</h3>
          <div class="relative h-64"><canvas id="chartTopSetembro"></canvas></div>
        </div>
      </section>

      <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 class="font-bold text-base text-slate-800 mb-2">Distribuição por Categoria</h3>
          <div class="relative h-64"><canvas id="chartCategoryDist"></canvas></div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 class="font-bold text-base text-slate-800 mb-2">Soma de Custo por Fornecedor (R$)</h3>
          <div class="relative h-64"><canvas id="chartSupplierCost"></canvas></div>
        </div>
      </section>

      <!-- TABELA RESUMO -->
      <section class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4 pb-3 border-b border-slate-100">
          <div>
            <h2 class="text-base font-bold flex items-center gap-2 text-slate-800">
              <i data-lucide="table" class="w-4 h-4 text-blue-500"></i>
              Resumo Detalhado por Peça Solicitada
            </h2>
            <p class="text-xs text-slate-500">Consolidado com Código da Peça, Descrição e Custo Total</p>
          </div>

          <div class="flex items-center gap-3">
            <div class="relative">
              <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-2.5"></i>
              <input type="text" id="tableSearch" placeholder="Buscar código ou descrição..." class="text-xs pl-9 pr-3 py-2 rounded-xl border border-slate-300 bg-slate-50 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 w-56 sm:w-72">
            </div>
            <span id="tableCountBadge" class="text-xs px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 font-semibold">0 itens</span>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-600">
            <thead class="bg-slate-50 uppercase font-semibold text-slate-500">
              <tr>
                <th class="py-3 px-4 rounded-l-lg">Código da Peça</th>
                <th class="py-3 px-4">Descrição da Peça / Produto</th>
                <th class="py-3 px-4">Categoria</th>
                <th class="py-3 px-4 text-center">Qtde Total</th>
                <th class="py-3 px-4 text-center text-emerald-600">Atendidas</th>
                <th class="py-3 px-4 text-center text-rose-600">Não Atendidas</th>
                <th class="py-3 px-4 text-center">Nº Pedidos</th>
                <th class="py-3 px-4 text-right rounded-r-lg">Custo Total (R$)</th>
              </tr>
            </thead>
            <tbody id="tableBody" class="divide-y divide-slate-100"></tbody>
          </table>
        </div>
      </section>

    </div>

    <!-- ==================== PÁGINA 2: FORMULÁRIO DE LANÇAMENTO / EDIÇÃO ==================== -->
    <div id="pageFormulario" class="space-y-6">

      <!-- Alerta de Modo de Edição Ativo -->
      <div id="alertEditMode" class="hidden p-4 rounded-2xl bg-amber-50 border border-amber-300 text-amber-900 flex justify-between items-center shadow-sm">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-amber-500 text-white rounded-xl"><i data-lucide="edit-3" class="w-5 h-5"></i></div>
          <div>
            <p class="text-sm font-bold">Modo de Edição Ativo: <span id="labelEditOC" class="font-mono text-amber-800">OC-0000-0000</span></p>
            <p class="text-xs text-amber-700">Você está alterando esta Ordem de Compra. Ao clicar em atualizar, os dados antigos serão substituídos.</p>
          </div>
        </div>
        <button type="button" onclick="cancelarEdicao()" class="px-3 py-1.5 bg-amber-200 hover:bg-amber-300 rounded-xl text-xs font-bold text-amber-900 transition">
          Cancelar Edição ✕
        </button>
      </div>

      <!-- Notificação de Sucesso com Botão de Imprimir Imediato -->
      <div id="alertSuccess" class="hidden p-5 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm transition">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-emerald-600 text-white rounded-xl">
            <i data-lucide="check-circle" class="w-5 h-5"></i>
          </div>
          <div>
            <p id="alertSuccessTitle" class="text-sm font-bold">Ordem de Compra salva com sucesso!</p>
            <p id="alertSuccessSub" class="text-xs text-emerald-700">Enviada para a planilha e pronta para impressão.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button type="button" onclick="imprimirUltimaOC()" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-700 text-white text-xs font-bold hover:bg-emerald-800 shadow-md shadow-emerald-700/20 transition">
            <i data-lucide="printer" class="w-4 h-4"></i>
            Imprimir Pedido de Compra
          </button>
          <button type="button" onclick="document.getElementById('alertSuccess').classList.add('hidden')" class="px-3 py-2 rounded-xl hover:bg-emerald-100 text-xs font-semibold text-emerald-800 transition">
            Fechar
          </button>
        </div>
      </div>
      
      <section class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div class="flex items-center justify-between pb-4 mb-6 border-b border-slate-100">
          <div class="flex items-center gap-3">
            <div class="p-2.5 bg-blue-600 text-white rounded-xl shadow-lg shadow-blue-500/25">
              <i data-lucide="file-plus" class="w-6 h-6"></i>
            </div>
            <div>
              <h2 id="formTitleText" class="text-base font-bold text-slate-900">Formulário de Entrada: Solicitação de Compra de Peças</h2>
              <p class="text-xs text-slate-500">Fornecedor único · Múltiplas peças · Sequência controlada diretamente pela planilha</p>
            </div>
          </div>
          <span class="text-xs font-semibold px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
            Padrão OC-AAAA-XXXX
          </span>
        </div>

        <form id="orderForm" onsubmit="handleFinalSubmit(event)" class="space-y-6">
          
          <!-- CABEÇALHO DA OC -->
          <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 p-5 rounded-2xl bg-slate-50/90 border border-slate-200">
            <div>
              <label class="block text-xs font-bold text-blue-800 mb-1">Número da OC *</label>
              <input type="text" id="formNumeroOC" readonly class="w-full text-sm font-mono font-bold rounded-xl border border-blue-300 bg-white px-3.5 py-2 text-blue-700 cursor-not-allowed shadow-inner">
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Ano *</label>
              <select id="formAno" required onchange="aoMudarAnoForm()" class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
                <option value="2026">2026</option>
                <option value="2025">2025</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Mês *</label>
              <select id="formMes" required class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
                <option value="Janeiro">Janeiro</option><option value="Fevereiro">Fevereiro</option><option value="Março">Março</option><option value="Abril">Abril</option><option value="Maio">Maio</option><option value="Junho">Junho</option><option value="Julho">Julho</option><option value="Agosto">Agosto</option><option value="Setembro">Setembro</option><option value="Outubro" selected>Outubro</option><option value="Novembro">Novembro</option><option value="Dezembro">Dezembro</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Data da Solicitação *</label>
              <input type="date" id="formData" required class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
            </div>

            <div class="lg:col-span-2">
              <label class="block text-xs font-semibold text-slate-700 mb-1">Solicitante *</label>
              <input type="text" id="formSolicitante" placeholder="Ex: Willian Neves, Thiago, Flávio, Samantha" required class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-slate-800">
            </div>

            <!-- FORNECEDOR ÚNICO -->
            <div class="md:col-span-3 lg:col-span-6 bg-blue-50/60 p-3.5 rounded-xl border border-blue-200">
              <label class="block text-xs font-bold text-blue-900 mb-1">
                Fornecedor (Único para este Pedido de Compra) *
              </label>
              <input list="listaFornecedores" id="formFornecedor" placeholder="Selecione ou digite o Fornecedor exclusivo desta OC..." required onchange="aoMudarFornecedorPrincipal()" class="w-full text-sm font-semibold rounded-xl border border-blue-400 bg-white px-3.5 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600 shadow-sm">
              <datalist id="listaFornecedores"></datalist>
              <span class="text-[11px] text-blue-600 font-medium mt-1 block">📌 O fornecedor escolhido aqui será associado a todas as peças desta Ordem de Compra.</span>
            </div>
          </div>

          <!-- ÁREA PARA ADICIONAR PEÇAS À ORDEM -->
          <div class="p-5 rounded-2xl border-2 border-blue-200 bg-blue-50/20 space-y-4">
            <div class="flex items-center justify-between pb-2 border-b border-blue-100">
              <h3 class="text-xs font-bold uppercase tracking-wider text-blue-900 flex items-center gap-2">
                <i data-lucide="plus-circle" class="w-4 h-4 text-blue-600"></i>
                Adicionar Peça à Ordem de Compra
              </h3>
              <span class="text-[11px] text-slate-500">Pré-listas conectadas à Coluna A e B da planilha</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              <div>
                <label class="block text-xs font-bold text-slate-800 mb-1">Código da Peça *</label>
                <input list="listaCodigosPecas" id="itemCodigoPeca" placeholder="Clique ou digite o código..." oninput="aoMudarCodigo()" onchange="aoMudarCodigo()" class="w-full text-sm font-mono font-bold rounded-xl border border-blue-300 bg-white px-3.5 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600">
                <datalist id="listaCodigosPecas"></datalist>
              </div>

              <div class="col-span-1 md:col-span-2">
                <label class="block text-xs font-bold text-slate-800 mb-1">Descrição da Peça / Produto *</label>
                <input list="listaDescricoesPecas" id="itemPeca" placeholder="Clique ou digite a descrição da peça..." oninput="aoMudarDescricao()" onchange="aoMudarDescricao()" class="w-full text-sm font-semibold rounded-xl border border-blue-300 bg-white px-3.5 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600">
                <datalist id="listaDescricoesPecas"></datalist>
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1">Categoria</label>
                <input type="text" id="itemCategoria" placeholder="Ex: 8 PEÇAS, Multi Bebidas" class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1">Quantidade Solicitada (Qt) *</label>
                <input type="number" id="itemQt" min="1" value="1" oninput="calcItemPreview()" class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1">Custo Unitário (R$) *</label>
                <input type="number" step="0.01" min="0" id="itemCustoUnit" placeholder="0,00" oninput="calcItemPreview()" class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
              </div>

              <div>
                <label class="block text-xs font-semibold text-emerald-700 mb-1">Valor Venda Unit. (+70%) [Interno]</label>
                <input type="text" id="itemVendaUnitPreview" readonly value="R$ 0,00" class="w-full text-sm font-bold rounded-xl border border-emerald-300 bg-emerald-50/60 px-3 py-2 text-emerald-900 cursor-not-allowed">
              </div>

              <div>
                <label class="block text-xs font-semibold text-emerald-700 mb-1">Quantidade Atendida</label>
                <input type="number" id="itemQtAprovada" min="0" value="1" oninput="calcItemPreview()" class="w-full text-sm rounded-xl border border-emerald-300 bg-emerald-50/30 px-3 py-2 text-slate-800">
              </div>

              <div>
                <label class="block text-xs font-semibold text-rose-700 mb-1">Quantidade Não Atendida</label>
                <input type="number" id="itemQtNaoAprovada" min="0" value="0" class="w-full text-sm rounded-xl border border-rose-300 bg-rose-50/30 px-3 py-2 text-slate-800">
              </div>

              <div class="col-span-1 md:col-span-2">
                <label class="block text-xs font-semibold text-amber-700 mb-1">Subtotal Custo Total</label>
                <input type="text" id="itemCustoSubtotalPreview" readonly value="R$ 0,00" class="w-full text-sm font-bold rounded-xl border border-amber-300 bg-amber-50/60 px-3 py-2 text-amber-900 cursor-not-allowed">
              </div>

              <div class="col-span-1 md:col-span-1">
                <label class="block text-xs font-semibold text-indigo-700 mb-1">Subtotal Venda (+70%) [Interno]</label>
                <input type="text" id="itemVendaSubtotalPreview" readonly value="R$ 0,00" class="w-full text-sm font-bold rounded-xl border border-indigo-300 bg-indigo-50/60 px-3 py-2 text-indigo-900 cursor-not-allowed">
              </div>

              <div class="col-span-1 md:col-span-3 lg:col-span-4 flex justify-end">
                <button type="button" onclick="adicionarItemNaLista()" class="py-2.5 px-6 rounded-xl bg-blue-700 text-white text-xs font-bold hover:bg-blue-800 transition flex items-center justify-center gap-1.5 shadow-md shadow-blue-500/20">
                  <i data-lucide="plus" class="w-4 h-4"></i>
                  Adicionar Peça à Ordem
                </button>
              </div>
            </div>
          </div>

          <!-- TABELA DE PEÇAS ADICIONADAS ANTES DE SALVAR -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                <i data-lucide="shopping-cart" class="w-4 h-4 text-blue-600"></i>
                Peças Selecionadas para esta Ordem de Compra
              </h4>
              <span id="badgeTotalItensOC" class="text-xs px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 font-bold">0 peça(s)</span>
            </div>

            <div class="overflow-x-auto border border-slate-200 rounded-2xl bg-white shadow-sm">
              <table class="w-full text-left text-xs text-slate-600">
                <thead class="bg-slate-50 uppercase font-semibold text-slate-500">
                  <tr>
                    <th class="py-2.5 px-3">Código</th>
                    <th class="py-2.5 px-3">Descrição da Peça</th>
                    <th class="py-2.5 px-3">Categoria</th>
                    <th class="py-2.5 px-3 text-center">Qt Pedida</th>
                    <th class="py-2.5 px-3 text-center text-emerald-600">Atendida</th>
                    <th class="py-2.5 px-3 text-right">Custo Unit.</th>
                    <th class="py-2.5 px-3 text-right">Custo Total</th>
                    <th class="py-2.5 px-3 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody id="listaPecasOCTableBody" class="divide-y divide-slate-100">
                  <tr id="rowEmptyList">
                    <td colspan="8" class="text-center py-6 text-slate-400">Nenhuma peça adicionada ainda. Preencha os campos acima e clique em "Adicionar Peça à Ordem".</td>
                  </tr>
                </tbody>
                <tfoot class="bg-slate-50 font-bold text-slate-800 border-t border-slate-200">
                  <tr>
                    <td colspan="3" class="py-3 px-3 text-right uppercase text-[11px]">Totais da Ordem de Compra (Custo):</td>
                    <td id="footTotalQt" class="py-3 px-3 text-center text-blue-700 font-bold">0 un</td>
                    <td id="footTotalAtendida" class="py-3 px-3 text-center text-emerald-700 font-bold">0 un</td>
                    <td></td>
                    <td id="footTotalValor" class="py-3 px-3 text-right text-amber-700 font-bold text-sm">R$ 0,00</td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- BOTÕES FINAIS -->
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
            <button type="button" onclick="limparOCAtual()" class="px-5 py-2.5 rounded-xl border border-slate-300 bg-white text-xs font-semibold text-slate-600 hover:bg-slate-50 transition">
              Limpar Ordem
            </button>
            <button type="submit" id="btnSalvarOC" class="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 text-white text-xs font-bold shadow-lg shadow-blue-500/25 hover:bg-blue-700 transition">
              <i data-lucide="save" class="w-4 h-4"></i>
              <span id="btnSalvarText">Salvar e Emitir Ordem de Compra</span>
            </button>
          </div>
        </form>
      </section>

      <!-- Histórico de Lançamentos Recentes com Botão de Imprimir e Editar -->
      <section class="no-print bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
          <i data-lucide="history" class="w-4 h-4 text-slate-400"></i>
          Últimas Ordens de Compra Emitidas (Edição & Impressão)
        </h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-600">
            <thead class="bg-slate-50 uppercase font-semibold text-slate-500">
              <tr>
                <th class="py-2.5 px-3">Ações</th>
                <th class="py-2.5 px-3">Nº OC</th>
                <th class="py-2.5 px-3">Data</th>
                <th class="py-2.5 px-3">Solicitante</th>
                <th class="py-2.5 px-3">Fornecedor</th>
                <th class="py-2.5 px-3">Código</th>
                <th class="py-2.5 px-3">Descrição da Peça</th>
                <th class="py-2.5 px-3 text-center">Qt Pedida</th>
                <th class="py-2.5 px-3 text-center text-emerald-600">Atendida</th>
                <th class="py-2.5 px-3 text-right">Custo Total</th>
              </tr>
            </thead>
            <tbody id="recentEntriesBody" class="divide-y divide-slate-100">
              <tr>
                <td colspan="10" class="text-center py-4 text-slate-400">Nenhum lançamento emitido na sessão ainda.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </div>

    <!-- ==================== ÁREA EXCLUSIVA DE IMPRESSÃO DA OC (COM LOGO E SEM TEXTO MASTER CAFÉ) ==================== -->
    <div id="printArea" class="hidden">
      <div class="max-w-4xl mx-auto border-2 border-slate-800 p-8 rounded-lg bg-white text-slate-900 font-sans">
        
        <!-- Topo da Impressão: Somente o Logotipo e Identificação da OC -->
        <div class="flex justify-between items-center border-b-2 border-slate-800 pb-4 mb-6">
          <div class="flex items-center gap-4">
            <img id="printLogoImg" src="{logo_base64_src}" alt="Logotipo" class="max-h-16 w-auto object-contain" onerror="this.style.display='none';">
            <div>
              <h1 class="text-2xl font-black uppercase tracking-tight">ORDEM DE COMPRA</h1>
              <p class="text-xs text-slate-600 font-bold uppercase tracking-wider">Peças & Suprimentos</p>
            </div>
          </div>
          <div class="text-right">
            <span id="printOCNumero" class="text-xl font-mono font-black text-blue-800">OC-0000-0000</span>
            <p id="printOCData" class="text-xs font-semibold text-slate-600 mt-1">Data: --/--/----</p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 p-4 bg-slate-100 rounded-lg mb-6 text-xs">
          <div>
            <p><strong class="uppercase text-slate-600">Fornecedor:</strong></p>
            <p id="printOCFornecedor" class="text-sm font-bold text-slate-900 mt-0.5">NOME DO FORNECEDOR</p>
          </div>
          <div>
            <p><strong class="uppercase text-slate-600">Solicitante / Setor:</strong></p>
            <p id="printOCSolicitante" class="text-sm font-bold text-slate-900 mt-0.5">NOME DO SOLICITANTE</p>
          </div>
        </div>

        <table class="w-full text-left text-xs border border-slate-300 mb-6">
          <thead class="bg-slate-200 uppercase font-bold text-slate-800">
            <tr>
              <th class="py-2.5 px-3 border border-slate-300">Item</th>
              <th class="py-2.5 px-3 border border-slate-300">Cód. Peça</th>
              <th class="py-2.5 px-3 border border-slate-300">Descrição do Produto</th>
              <th class="py-2.5 px-3 border border-slate-300 text-center">Qt Solicitada</th>
              <th class="py-2.5 px-3 border border-slate-300 text-center">Qt Atendida</th>
              <th class="py-2.5 px-3 border border-slate-300 text-right">Custo Unitário (R$)</th>
              <th class="py-2.5 px-3 border border-slate-300 text-right">Custo Total (R$)</th>
            </tr>
          </thead>
          <tbody id="printOCTableBody"></tbody>
          <tfoot class="bg-slate-100 font-bold border-t-2 border-slate-800">
            <tr>
              <td colspan="3" class="py-3 px-3 text-right uppercase text-xs">Total Geral da Ordem de Compra (Custo):</td>
              <td id="printOCTotalQt" class="py-3 px-3 text-center">0 un</td>
              <td id="printOCTotalAtendida" class="py-3 px-3 text-center">0 un</td>
              <td></td>
              <td id="printOCTotalValor" class="py-3 px-3 text-right text-base font-black text-slate-900">R$ 0,00</td>
            </tr>
          </tfoot>
        </table>

        <div class="grid grid-cols-2 gap-8 mt-16 pt-8 border-t border-slate-300 text-center text-xs">
          <div>
            <div class="border-t border-slate-500 w-3/4 mx-auto mb-1"></div>
            <p class="font-bold">Aprovação / Responsável Compras</p>
          </div>
          <div>
            <div class="border-t border-slate-500 w-3/4 mx-auto mb-1"></div>
            <p class="font-bold">Recebimento / Almoxarifado</p>
          </div>
        </div>
      </div>
    </div>

  </main>

  <script>
    lucide.createIcons();
    Chart.register(ChartDataLabels);

    const APPS_SCRIPT_URL = "{APPS_SCRIPT_WEBAPP_URL}";
    document.getElementById('formData').value = new Date().toISOString().split('T')[0];

    const catalogoPecas = {catalogo_json};

    let rawOrdersData = {ocs_planilha_json};
    let maxSeqAnosPlanilha = {max_seq_anos_json};

    // Popula Datalists
    const dlCodigos = document.getElementById('listaCodigosPecas');
    dlCodigos.innerHTML = '';
    const codigosUnicos = [...new Set(catalogoPecas.map(p => p.codigo).filter(Boolean))].sort();
    codigosUnicos.forEach(cod => {{
      const opt = document.createElement('option');
      opt.value = cod;
      dlCodigos.appendChild(opt);
    }});

    const dlDescricoes = document.getElementById('listaDescricoesPecas');
    dlDescricoes.innerHTML = '';
    const descricoesUnicas = [...new Set(catalogoPecas.map(p => p.descricao).filter(Boolean))].sort();
    descricoesUnicas.forEach(desc => {{
      const opt = document.createElement('option');
      opt.value = desc;
      dlDescricoes.appendChild(opt);
    }});

    const dlFornecedores = document.getElementById('listaFornecedores');
    dlFornecedores.innerHTML = '';
    const fornecedoresUnicos = [...new Set(catalogoPecas.map(p => p.fornecedor).filter(Boolean))].sort();
    fornecedoresUnicos.forEach(forn => {{
      const opt = document.createElement('option');
      opt.value = forn;
      dlFornecedores.appendChild(opt);
    }});

    function aoMudarFornecedorPrincipal() {{
      const forn = document.getElementById('formFornecedor').value.trim();
      if (forn && itensDaOrdemAtual.length > 0) {{
        const divergente = itensDaOrdemAtual.some(i => i.fornecedor && i.fornecedor.toUpperCase() !== forn.toUpperCase());
        if (divergente) {{
          if (confirm('Atenção: Ao alterar o fornecedor principal do pedido, todas as peças desta OC serão atualizadas para ' + forn + '. Deseja continuar?')) {{
            itensDaOrdemAtual.forEach(i => i.fornecedor = forn.toUpperCase());
            renderizarTabelaItensOC();
          }}
        }}
      }}
    }}

    function aoMudarCodigo() {{
      const codDigitado = document.getElementById('itemCodigoPeca').value.trim();
      if (!codDigitado) return;

      const itemAchado = catalogoPecas.find(p => p.codigo.toLowerCase() === codDigitado.toLowerCase());
      if (itemAchado) {{
        document.getElementById('itemPeca').value = itemAchado.descricao;
        if (itemAchado.categoria) document.getElementById('itemCategoria').value = itemAchado.categoria;

        const formForn = document.getElementById('formFornecedor');
        if (!formForn.value.trim() && itemAchado.fornecedor) {{
          formForn.value = itemAchado.fornecedor;
        }}
        calcItemPreview();
      }}
    }}

    function aoMudarDescricao() {{
      const descDigitada = document.getElementById('itemPeca').value.trim();
      if (!descDigitada) return;

      const itemAchado = catalogoPecas.find(p => p.descricao.toLowerCase() === descDigitada.toLowerCase());
      if (itemAchado) {{
        document.getElementById('itemCodigoPeca').value = itemAchado.codigo;
        if (itemAchado.categoria) document.getElementById('itemCategoria').value = itemAchado.categoria;

        const formForn = document.getElementById('formFornecedor');
        if (!formForn.value.trim() && itemAchado.fornecedor) {{
          formForn.value = itemAchado.fornecedor;
        }}
        calcItemPreview();
      }}
    }}

    function calcItemPreview() {{
      const qt = parseInt(document.getElementById('itemQt').value) || 0;
      let qtAprovada = parseInt(document.getElementById('itemQtAprovada').value);
      if (isNaN(qtAprovada) || qtAprovada > qt) qtAprovada = qt;
      document.getElementById('itemQtNaoAprovada').value = Math.max(0, qt - qtAprovada);

      const custoUnit = parseFloat(document.getElementById('itemCustoUnit').value) || 0;
      const vendaUnit = custoUnit * 1.70;
      const subtotalCusto = qtAprovada * custoUnit;
      const subtotalVenda = qtAprovada * vendaUnit;

      document.getElementById('itemVendaUnitPreview').value = formatCurrency(vendaUnit);
      document.getElementById('itemCustoSubtotalPreview').value = formatCurrency(subtotalCusto);
      document.getElementById('itemVendaSubtotalPreview').value = formatCurrency(subtotalVenda);
    }}

    let itensDaOrdemAtual = [];

    function adicionarItemNaLista() {{
      const fornecedorPrincipal = document.getElementById('formFornecedor').value.trim().toUpperCase();
      if (!fornecedorPrincipal) {{
        alert('Por favor, informe primeiro o Fornecedor Principal no cabeçalho do pedido de compra.');
        document.getElementById('formFornecedor').focus();
        return;
      }}

      const codigoPeca = document.getElementById('itemCodigoPeca').value.trim().toUpperCase();
      const peca = document.getElementById('itemPeca').value.trim().toUpperCase();
      const categoria = document.getElementById('itemCategoria').value.trim() || 'Geral';
      const qt = parseInt(document.getElementById('itemQt').value) || 0;
      const qtAprovada = parseInt(document.getElementById('itemQtAprovada').value) || 0;
      const qtNaoAprovada = parseInt(document.getElementById('itemQtNaoAprovada').value) || 0;
      const custoUnit = parseFloat(document.getElementById('itemCustoUnit').value) || 0;
      const vendaUnit = custoUnit * 1.70;

      if (!codigoPeca || !peca) {{
        alert('Por favor, informe ao menos o Código e a Descrição da Peça.');
        return;
      }}
      if (qt <= 0) {{
        alert('A Quantidade Solicitada deve ser maior que zero.');
        return;
      }}

      itensDaOrdemAtual.push({{
        codigoPeca,
        peca,
        fornecedor: fornecedorPrincipal,
        categoria,
        qt,
        qtAprovada,
        qtNaoAprovada,
        custoUnit,
        vendaUnit,
        custoTotal: qtAprovada * custoUnit,
        vendaTotal: qtAprovada * vendaUnit
      }});

      document.getElementById('itemCodigoPeca').value = '';
      document.getElementById('itemPeca').value = '';
      document.getElementById('itemCategoria').value = '';
      document.getElementById('itemQt').value = '1';
      document.getElementById('itemQtAprovada').value = '1';
      document.getElementById('itemQtNaoAprovada').value = '0';
      document.getElementById('itemCustoUnit').value = '';
      document.getElementById('itemVendaUnitPreview').value = 'R$ 0,00';
      document.getElementById('itemCustoSubtotalPreview').value = 'R$ 0,00';
      document.getElementById('itemVendaSubtotalPreview').value = 'R$ 0,00';

      renderizarTabelaItensOC();
    }}

    function removerItemDaLista(index) {{
      itensDaOrdemAtual.splice(index, 1);
      renderizarTabelaItensOC();
    }}

    function renderizarTabelaItensOC() {{
      const tbody = document.getElementById('listaPecasOCTableBody');
      const badge = document.getElementById('badgeTotalItensOC');
      badge.innerText = `${{itensDaOrdemAtual.length}} peça(s)`;

      if (itensDaOrdemAtual.length === 0) {{
        tbody.innerHTML = `
          <tr id="rowEmptyList">
            <td colspan="8" class="text-center py-6 text-slate-400">Nenhuma peça adicionada ainda. Preencha os campos acima e clique em "Adicionar Peça à Ordem".</td>
          </tr>
        `;
        document.getElementById('footTotalQt').innerText = '0 un';
        document.getElementById('footTotalAtendida').innerText = '0 un';
        document.getElementById('footTotalValor').innerText = 'R$ 0,00';
        return;
      }}

      let somaQt = 0;
      let somaAtendida = 0;
      let somaValor = 0;

      tbody.innerHTML = itensDaOrdemAtual.map((item, idx) => {{
        somaQt += item.qt;
        somaAtendida += item.qtAprovada;
        somaValor += item.custoTotal;

        return `
          <tr class="hover:bg-slate-50 transition">
            <td class="py-2.5 px-3 font-mono font-bold text-blue-700">${{item.codigoPeca}}</td>
            <td class="py-2.5 px-3 font-semibold text-slate-800">${{item.peca}}</td>
            <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] bg-slate-100 text-slate-700">${{item.categoria}}</span></td>
            <td class="py-2.5 px-3 text-center font-bold">${{item.qt}} un</td>
            <td class="py-2.5 px-3 text-center font-bold text-emerald-600">${{item.qtAprovada}} un</td>
            <td class="py-2.5 px-3 text-right">${{formatCurrency(item.custoUnit)}}</td>
            <td class="py-2.5 px-3 text-right font-bold text-amber-600">${{formatCurrency(item.custoTotal)}}</td>
            <td class="py-2.5 px-3 text-center">
              <button type="button" onclick="removerItemDaLista(${{idx}})" title="Remover Peça" class="text-rose-500 hover:text-rose-700 p-1 rounded-md hover:bg-rose-50">
                <i data-lucide="trash-2" class="w-4 h-4"></i>
              </button>
            </td>
          </tr>
        `;
      }}).join('');

      document.getElementById('footTotalQt').innerText = `${{somaQt}} un`;
      document.getElementById('footTotalAtendida').innerText = `${{somaAtendida}} un`;
      document.getElementById('footTotalValor').innerText = formatCurrency(somaValor);
      lucide.createIcons();
    }}

    function limparOCAtual() {{
      itensDaOrdemAtual = [];
      renderizarTabelaItensOC();
    }}

    let todasOCsEmitidas = {{}};
    let ultimaOCSalva = null;
    let ocEmEdicao = null;

    rawOrdersData.forEach(item => {{
      if (!todasOCsEmitidas[item.oc]) {{
        todasOCsEmitidas[item.oc] = {{
          oc: item.oc,
          data: item.data,
          solicitante: item.solicitante,
          fornecedor: item.fornecedor,
          itens: []
        }};
      }}
      todasOCsEmitidas[item.oc].itens.push(item);
    }});

    function gerarNumeroOC(anoSelecionado) {{
      let maior = maxSeqAnosPlanilha[anoSelecionado] || 0;

      rawOrdersData.forEach(item => {{
        if (item.oc) {{
          const match = item.oc.match(new RegExp('OC-' + anoSelecionado + '-(\\\\d+)', 'i'));
          if (match) {{
            const seq = parseInt(match[1]);
            if (seq > maior) maior = seq;
          }}
        }}
      }});

      const proximoSeq = String(maior + 1).padStart(4, '0');
      return `OC-${{anoSelecionado}}-${{proximoSeq}}`;
    }}

    function atualizarProximoNumeroOC() {{
      if (ocEmEdicao) return;
      const anoSelecionado = document.getElementById('formAno').value;
      document.getElementById('formNumeroOC').value = gerarNumeroOC(anoSelecionado);
    }}
    atualizarProximoNumeroOC();

    function aoMudarAnoForm() {{
      if (!ocEmEdicao) {{
        atualizarProximoNumeroOC();
      }}
    }}

    function editarOCEspecifica(numeroOC) {{
      const ocData = todasOCsEmitidas[numeroOC];
      if (!ocData) {{
        alert('Dados da Ordem de Compra ' + numeroOC + ' não localizados.');
        return;
      }}

      switchPage('formulario');
      ocEmEdicao = numeroOC;

      document.getElementById('formNumeroOC').value = ocData.oc;
      if (ocData.solicitante) document.getElementById('formSolicitante').value = ocData.solicitante;
      if (ocData.fornecedor) document.getElementById('formFornecedor').value = ocData.fornecedor;

      itensDaOrdemAtual = JSON.parse(JSON.stringify(ocData.itens));
      renderizarTabelaItensOC();

      document.getElementById('alertEditMode').classList.remove('hidden');
      document.getElementById('labelEditOC').innerText = ocData.oc;
      document.getElementById('formTitleText').innerText = 'Edição da Ordem de Compra: ' + ocData.oc;
      document.getElementById('btnSalvarText').innerText = 'Atualizar Ordem de Compra';
      document.getElementById('orderForm').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}

    function cancelarEdicao() {{
      ocEmEdicao = null;
      document.getElementById('alertEditMode').classList.add('hidden');
      document.getElementById('formTitleText').innerText = 'Formulário de Entrada: Solicitação de Compra de Peças';
      document.getElementById('btnSalvarText').innerText = 'Salvar e Emitir Ordem de Compra';
      
      limparOCAtual();
      document.getElementById('formSolicitante').value = '';
      document.getElementById('formFornecedor').value = '';
      atualizarProximoNumeroOC();
    }}

    let enviandoAgora = false;

    function handleFinalSubmit(e) {{
      e.preventDefault();

      if (enviandoAgora) return;

      const fornecedorPrincipal = document.getElementById('formFornecedor').value.trim().toUpperCase();
      if (!fornecedorPrincipal) {{
        alert('Por favor, informe o Fornecedor Principal da Ordem de Compra.');
        document.getElementById('formFornecedor').focus();
        return;
      }}

      if (itensDaOrdemAtual.length === 0) {{
        alert('Atenção: Adicione pelo menos uma peça na ordem antes de salvar!');
        return;
      }}

      enviandoAgora = true;

      const oc = document.getElementById('formNumeroOC').value;
      const ano = document.getElementById('formAno').value;
      const mes = document.getElementById('formMes').value;
      const dataStr = document.getElementById('formData').value;
      const solicitante = document.getElementById('formSolicitante').value.toUpperCase().trim();
      const ehEdicao = (ocEmEdicao !== null);

      const dadosOCSalva = {{
        oc,
        ano,
        mes,
        data: dataStr,
        solicitante,
        fornecedor: fornecedorPrincipal,
        acao: ehEdicao ? "editar" : "inserir",
        itens: JSON.parse(JSON.stringify(itensDaOrdemAtual))
      }};

      todasOCsEmitidas[oc] = dadosOCSalva;
      ultimaOCSalva = dadosOCSalva;

      const btnSalvar = document.getElementById('btnSalvarOC');
      btnSalvar.disabled = true;
      btnSalvar.innerText = ehEdicao ? 'Atualizando na planilha...' : 'Gravando na planilha...';

      try {{
        const jsonEncoded = encodeURIComponent(JSON.stringify(dadosOCSalva));
        const beaconUrl = APPS_SCRIPT_URL + "?data=" + jsonEncoded;
        const img = new Image();
        img.src = beaconUrl;
      }} catch (errBeacon) {{
        console.error("Erro no envio:", errBeacon);
      }}

      setTimeout(() => {{
        enviandoAgora = false;
        btnSalvar.disabled = false;
        btnSalvar.innerHTML = '<i data-lucide="save" class="w-4 h-4"></i> <span id="btnSalvarText">' + 
          (ehEdicao ? 'Atualizar Ordem de Compra' : 'Salvar e Emitir Ordem de Compra') + '</span>';
      }}, 800);

      if (ehEdicao) {{
        rawOrdersData = rawOrdersData.filter(item => item.oc !== oc);
      }}

      itensDaOrdemAtual.forEach(item => {{
        const novoRegistro = {{
          oc,
          ano,
          mes,
          data: dataStr,
          solicitante,
          codigoPeca: item.codigoPeca,
          peca: item.peca,
          categoria: item.categoria,
          fornecedor: fornecedorPrincipal,
          qt: item.qt,
          qtAprovada: item.qtAprovada,
          qtNaoAprovada: item.qtNaoAprovada,
          custoUnit: item.custoUnit,
          vendaUnit: item.vendaUnit,
          custoTotal: item.custoTotal,
          vendaTotal: item.vendaTotal
        }};
        rawOrdersData.unshift(novoRegistro);
      }});

      const match = oc.match(new RegExp('OC-' + ano + '-(\\\\d+)', 'i'));
      if (match) {{
        const seqSalvo = parseInt(match[1]);
        maxSeqAnosPlanilha[ano] = Math.max(maxSeqAnosPlanilha[ano] || 0, seqSalvo);
      }}

      const totalPecas = itensDaOrdemAtual.length;

      if (ehEdicao) {{
        ocEmEdicao = null;
        document.getElementById('alertEditMode').classList.add('hidden');
        document.getElementById('formTitleText').innerText = 'Formulário de Entrada: Solicitação de Compra de Peças';
        document.getElementById('btnSalvarText').innerText = 'Salvar e Emitir Ordem de Compra';
      }}

      limparOCAtual();
      document.getElementById('formSolicitante').value = '';
      document.getElementById('formFornecedor').value = '';

      atualizarProximoNumeroOC();
      populateDropdowns();
      updateDashboard();
      renderizarTabelaRecentes();

      const alertBox = document.getElementById('alertSuccess');
      document.getElementById('alertSuccessTitle').innerText = ehEdicao ? 
        `✅ Ordem de Compra ${{oc}} atualizada com sucesso (${{totalPecas}} peças)!` :
        `✅ Ordem de Compra ${{oc}} salva com sucesso (${{totalPecas}} peças)!`;
      document.getElementById('alertSuccessSub').innerText = `Fornecedor: ${{fornecedorPrincipal}} · Solicitante: ${{solicitante}} · Dados gravados na planilha Google Sheets.`;
      alertBox.classList.remove('hidden');
      alertBox.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      lucide.createIcons();
    }}

    function renderizarTabelaRecentes() {{
      const recentBody = document.getElementById('recentEntriesBody');
      if (rawOrdersData.length === 0) {{
        recentBody.innerHTML = '<tr><td colspan="10" class="text-center py-4 text-slate-400">Nenhum lançamento emitido na sessão ainda.</td></tr>';
        return;
      }}

      recentBody.innerHTML = rawOrdersData.slice(0, 25).map(item => `
        <tr class="hover:bg-slate-50 transition font-medium">
          <td class="py-2 px-3 whitespace-nowrap">
            <div class="flex items-center gap-1.5">
              <button type="button" onclick="editarOCEspecifica('${{item.oc}}')" title="Editar Ordem de Compra ${{item.oc}}" class="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-700 text-xs font-bold border border-amber-300 transition">
                <i data-lucide="edit-2" class="w-3 h-3"></i>
                Editar
              </button>
              <button type="button" onclick="imprimirOCEspecifica('${{item.oc}}')" title="Imprimir Ordem de Compra ${{item.oc}}" class="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-bold border border-blue-200 transition">
                <i data-lucide="printer" class="w-3 h-3"></i>
                Imprimir
              </button>
            </div>
          </td>
          <td class="py-2.5 px-3 font-mono font-bold text-blue-700">${{item.oc}}</td>
          <td class="py-2.5 px-3">${{item.data}}</td>
          <td class="py-2.5 px-3 font-semibold text-slate-800">${{item.solicitante || '-'}}</td>
          <td class="py-2.5 px-3 font-bold text-blue-900">${{item.fornecedor || '-'}}</td>
          <td class="py-2.5 px-3 font-mono text-slate-600">${{item.codigoPeca}}</td>
          <td class="py-2.5 px-3 font-semibold text-slate-800">${{item.peca}}</td>
          <td class="py-2.5 px-3 text-center font-bold">${{item.qt}} un</td>
          <td class="py-2.5 px-3 text-center font-bold text-emerald-600">${{item.qtAprovada}} un</td>
          <td class="py-2.5 px-3 text-right font-bold text-amber-600">${{formatCurrency(item.custoTotal)}}</td>
        </tr>
      `).join('');
      lucide.createIcons();
    }}
    renderizarTabelaRecentes();

    function imprimirUltimaOC() {{
      if (!ultimaOCSalva) {{
        alert('Nenhuma ordem de compra recente disponível para impressão.');
        return;
      }}
      executarImpressao(ultimaOCSalva);
    }}

    function imprimirOCEspecifica(numeroOC) {{
      const ocData = todasOCsEmitidas[numeroOC];
      if (!ocData) {{
        const itens = rawOrdersData.filter(i => i.oc === numeroOC);
        if (itens.length > 0) {{
          executarImpressao({{
            oc: numeroOC,
            ano: itens[0].ano || '2026',
            mes: itens[0].mes || '',
            data: itens[0].data || '',
            solicitante: itens[0].solicitante || '',
            fornecedor: itens[0].fornecedor || '',
            itens: itens
          }});
          return;
        }}
        alert('Dados da Ordem de Compra ' + numeroOC + ' não localizados.');
        return;
      }}
      executarImpressao(ocData);
    }}

    function executarImpressao(dadosOC) {{
      document.getElementById('printOCNumero').innerText = dadosOC.oc;
      document.getElementById('printOCData').innerText = `Data: ${{dadosOC.data}}`;
      document.getElementById('printOCFornecedor').innerText = dadosOC.fornecedor;
      document.getElementById('printOCSolicitante').innerText = dadosOC.solicitante;

      const tbody = document.getElementById('printOCTableBody');
      let somaQt = 0;
      let somaAtendida = 0;
      let somaCusto = 0;

      tbody.innerHTML = dadosOC.itens.map((item, idx) => {{
        somaQt += item.qt;
        somaAtendida += item.qtAprovada;
        somaCusto += item.custoTotal;

        return `
          <tr class="border-b border-slate-200">
            <td class="py-2 px-3 border border-slate-300 font-bold">${{idx + 1}}</td>
            <td class="py-2 px-3 border border-slate-300 font-mono font-bold">${{item.codigoPeca}}</td>
            <td class="py-2 px-3 border border-slate-300">${{item.peca}}</td>
            <td class="py-2 px-3 border border-slate-300 text-center">${{item.qt}} un</td>
            <td class="py-2 px-3 border border-slate-300 text-center font-bold">${{item.qtAprovada}} un</td>
            <td class="py-2.5 px-3 border border-slate-300 text-right">${{formatCurrency(item.custoUnit)}}</td>
            <td class="py-2.5 px-3 border border-slate-300 text-right font-bold">${{formatCurrency(item.custoTotal)}}</td>
          </tr>
        `;
      }}).join('');

      document.getElementById('printOCTotalQt').innerText = `${{somaQt}} un`;
      document.getElementById('printOCTotalAtendida').innerText = `${{somaAtendida}} un`;
      document.getElementById('printOCTotalValor').innerText = formatCurrency(somaCusto);

      const printArea = document.getElementById('printArea');
      printArea.classList.remove('hidden');

      setTimeout(() => {{
        window.print();
        printArea.classList.add('hidden');
      }}, 300);
    }}

    function switchPage(page) {{
      const pageDash = document.getElementById('pageDashboard');
      const pageForm = document.getElementById('pageFormulario');
      const btnDash = document.getElementById('navDashboard');
      const btnForm = document.getElementById('navForm');

      if (page === 'dashboard') {{
        pageDash.classList.remove('hidden');
        pageForm.classList.add('hidden');
        btnDash.classList.add('active');
        btnDash.classList.remove('inactive');
        btnForm.classList.remove('active');
        btnForm.classList.add('inactive');
        updateDashboard();
      }} else {{
        pageDash.classList.add('hidden');
        pageForm.classList.remove('hidden');
        btnForm.classList.add('active');
        btnForm.classList.remove('inactive');
        btnDash.classList.remove('active');
        btnDash.classList.add('inactive');
        atualizarProximoNumeroOC();
      }}
      lucide.createIcons();
    }}

    function formatCurrency(val) {{
      return (val || 0).toLocaleString('pt-BR', {{ style: 'currency', currency: 'BRL' }});
    }}

    const filterYear = document.getElementById('filterYear');
    const filterMonth = document.getElementById('filterMonth');
    const filterCategory = document.getElementById('filterCategory');
    const filterRequester = document.getElementById('filterRequester');
    const resetFiltersBtn = document.getElementById('resetFilters');
    const activeFilterBadge = document.getElementById('activeFilterBadge');

    const kpiTotalCost = document.getElementById('kpiTotalCost');
    const kpiTotalRequests = document.getElementById('kpiTotalRequests');
    const kpiItemsQty = document.getElementById('kpiItemsQty');
    const kpiApprovedQty = document.getElementById('kpiApprovedQty');
    const kpiApprovedPercent = document.getElementById('kpiApprovedPercent');
    const kpiUnapprovedQty = document.getElementById('kpiUnapprovedQty');
    const kpiUnapprovedPercent = document.getElementById('kpiUnapprovedPercent');
    const kpiAvgCost = document.getElementById('kpiAvgCost');

    const tableBody = document.getElementById('tableBody');
    const tableSearch = document.getElementById('tableSearch');
    const tableCountBadge = document.getElementById('tableCountBadge');

    function populateDropdowns() {{
      const currentYear = filterYear.value;
      const currentMonth = filterMonth.value;
      const currentCat = filterCategory.value;
      const currentReq = filterRequester.value;

      filterYear.innerHTML = '<option value="ALL">Todos os Anos</option>';
      filterMonth.innerHTML = '<option value="ALL">Todos os Meses</option>';
      filterCategory.innerHTML = '<option value="ALL">Todas as Categorias</option>';
      filterRequester.innerHTML = '<option value="ALL">Todos os Solicitantes</option>';

      const years = [...new Set(rawOrdersData.map(d => d.ano).filter(Boolean))].sort();
      const months = [...new Set(rawOrdersData.map(d => d.mes).filter(Boolean))];
      const categories = [...new Set(rawOrdersData.map(d => d.categoria).filter(Boolean))].sort();
      const requesters = [...new Set(rawOrdersData.map(d => d.solicitante).filter(Boolean))].sort();

      years.forEach(y => {{ const opt = document.createElement('option'); opt.value = y; opt.textContent = y; filterYear.appendChild(opt); }});
      months.forEach(m => {{ const opt = document.createElement('option'); opt.value = m; opt.textContent = m; filterMonth.appendChild(opt); }});
      categories.forEach(c => {{ const opt = document.createElement('option'); opt.value = c; opt.textContent = c; filterCategory.appendChild(opt); }});
      requesters.forEach(r => {{ const opt = document.createElement('option'); opt.value = r; opt.textContent = r; filterRequester.appendChild(opt); }});

      if (years.includes(currentYear)) filterYear.value = currentYear;
      if (months.includes(currentMonth)) filterMonth.value = currentMonth;
      if (categories.includes(currentCat)) filterCategory.value = currentCat;
      if (requesters.includes(currentReq)) filterRequester.value = currentReq;
    }}
    populateDropdowns();

    function getChartTheme(type = 'bar') {{
      const textColor = '#64748b';
      const labelColor = '#0f172a';
      const gridColor = 'rgba(226, 232, 240, 0.8)';
      return {{
        responsive: true,
        maintainAspectRatio: false,
        layout: {{ padding: {{ top: 22, bottom: 6, left: 6, right: 6 }} }},
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{ backgroundColor: '#ffffff', titleColor: '#0f172a', bodyColor: '#334155', borderColor: '#e2e8f0', borderWidth: 1, padding: 10 }},
          datalabels: {{
            anchor: 'end',
            align: 'top',
            offset: 2,
            color: labelColor,
            font: {{ family: 'Inter', weight: 'bold', size: 11 }},
            formatter: (v) => v ? v.toLocaleString('pt-BR') : ''
          }}
        }},
        scales: type === 'bar' ? {{
          x: {{ grid: {{ color: gridColor }}, ticks: {{ color: textColor, font: {{ size: 10 }} }} }},
          y: {{ grid: {{ color: gridColor }}, ticks: {{ color: textColor, font: {{ size: 10 }} }}, beginAtZero: true }}
        }} : undefined
      }};
    }}

    const chartAgosto = new Chart(document.getElementById('chartTopAgosto').getContext('2d'), {{
      type: 'bar',
      data: {{ labels: [], datasets: [{{ data: [], backgroundColor: 'rgba(2, 132, 199, 0.85)', borderRadius: 8 }}] }},
      options: getChartTheme('bar')
    }});

    const chartSetembro = new Chart(document.getElementById('chartTopSetembro').getContext('2d'), {{
      type: 'bar',
      data: {{ labels: [], datasets: [{{ data: [], backgroundColor: 'rgba(6, 182, 212, 0.85)', borderRadius: 8 }}] }},
      options: getChartTheme('bar')
    }});

    const chartCategory = new Chart(document.getElementById('chartCategoryDist').getContext('2d'), {{
      type: 'doughnut',
      data: {{ labels: [], datasets: [{{ data: [], backgroundColor: ['#0284c7', '#06b6d4', '#f59e0b', '#6366f1', '#10b981'], borderWidth: 2, borderColor: '#ffffff' }}] }},
      options: {{ responsive: true, maintainAspectRatio: false, cutout: '62%' }}
    }});

    const chartSupplier = new Chart(document.getElementById('chartSupplierCost').getContext('2d'), {{
      type: 'bar',
      data: {{ labels: [], datasets: [{{ data: [], backgroundColor: 'rgba(245, 158, 11, 0.85)', borderRadius: 8 }}] }},
      options: getChartTheme('bar')
    }});

    function updateDashboard() {{
      const yearVal = filterYear.value;
      const monthVal = filterMonth.value;
      const catVal = filterCategory.value;
      const reqVal = filterRequester.value;
      const searchVal = tableSearch.value.trim().toLowerCase();

      const filtered = rawOrdersData.filter(item => {{
        const matchYear = (yearVal === 'ALL' || item.ano === yearVal);
        const matchMonth = (monthVal === 'ALL' || item.mes === monthVal);
        const matchCat = (catVal === 'ALL' || item.categoria === catVal);
        const matchReq = (reqVal === 'ALL' || item.solicitante === reqVal);
        return matchYear && matchMonth && matchCat && matchReq;
      }});

      activeFilterBadge.innerText = `Filtrando: Ano [${{yearVal}}] · Mês [${{monthVal}}] · Categoria [${{catVal}}]`;

      const totalCusto = filtered.reduce((acc, cur) => acc + (cur.custoTotal || 0), 0);
      const totalItens = filtered.reduce((acc, cur) => acc + (cur.qt || 0), 0);
      const totalAtendidas = filtered.reduce((acc, cur) => acc + (cur.qtAprovada || 0), 0);
      const totalNaoAtendidas = filtered.reduce((acc, cur) => acc + (cur.qtNaoAprovada || 0), 0);
      
      const ocsUnicas = new Set(filtered.map(f => f.oc)).size;
      const avgCost = ocsUnicas > 0 ? (totalCusto / ocsUnicas) : 0;

      const pctAtendidas = totalItens > 0 ? Math.round((totalAtendidas / totalItens) * 100) : 0;
      const pctNaoAtendidas = totalItens > 0 ? (100 - pctAtendidas) : 0;

      kpiTotalCost.innerText = formatCurrency(totalCusto);
      kpiTotalRequests.innerText = ocsUnicas;
      kpiItemsQty.innerText = `${{totalItens.toLocaleString('pt-BR')}} un`;
      kpiApprovedQty.innerText = `${{totalAtendidas.toLocaleString('pt-BR')}} un`;
      kpiApprovedPercent.innerText = `${{pctAtendidas}}%`;
      kpiUnapprovedQty.innerText = `${{totalNaoAtendidas.toLocaleString('pt-BR')}} un`;
      kpiUnapprovedPercent.innerText = `${{pctNaoAtendidas}}%`;
      kpiAvgCost.innerText = formatCurrency(avgCost);

      const catCounts = {{}};
      filtered.forEach(d => {{ if(d.categoria) catCounts[d.categoria] = (catCounts[d.categoria] || 0) + (d.qt || 0); }});
      chartCategory.data.labels = Object.keys(catCounts);
      chartCategory.data.datasets[0].data = Object.values(catCounts);
      chartCategory.update();

      const supplierCosts = {{}};
      filtered.forEach(d => {{ if(d.fornecedor) supplierCosts[d.fornecedor] = (supplierCosts[d.fornecedor] || 0) + (d.custoTotal || 0); }});
      chartSupplier.data.labels = Object.keys(supplierCosts);
      chartSupplier.data.datasets[0].data = Object.values(supplierCosts);
      chartSupplier.update();

      renderTable(filtered, searchVal);
    }}

    function renderTable(dataList, searchTerm) {{
      const grouped = {{}};
      dataList.forEach(item => {{
        const key = item.codigoPeca || item.peca;
        if (!grouped[key]) {{
          grouped[key] = {{
            codigoPeca: item.codigoPeca || '—',
            peca: item.peca,
            categoria: item.categoria,
            qtTotal: 0,
            qtAtendida: 0,
            qtNaoAtendida: 0,
            pedidosCount: 0,
            custoTotal: 0
          }};
        }}
        grouped[key].qtTotal += (item.qt || 0);
        grouped[key].qtAtendida += (item.qtAprovada || 0);
        grouped[key].qtNaoAtendida += (item.qtNaoAprovada || 0);
        grouped[key].pedidosCount += 1;
        grouped[key].custoTotal += (item.custoTotal || 0);
      }});

      let itemsArray = Object.values(grouped);
      if (searchTerm) {{
        itemsArray = itemsArray.filter(i => 
          (i.peca && i.peca.toLowerCase().includes(searchTerm)) || 
          (i.codigoPeca && i.codigoPeca.toLowerCase().includes(searchTerm)) ||
          (i.categoria && i.categoria.toLowerCase().includes(searchTerm))
        );
      }}

      itemsArray.sort((a, b) => b.custoTotal - a.custoTotal);
      tableCountBadge.innerText = `${{itemsArray.length}} itens`;

      if (itemsArray.length === 0) {{
        tableBody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-400">Nenhuma peça encontrada.</td></tr>`;
        return;
      }}

      tableBody.innerHTML = itemsArray.map(item => `
        <tr class="hover:bg-slate-50 transition">
          <td class="py-3 px-4 font-mono font-semibold text-blue-600">${{item.codigoPeca}}</td>
          <td class="py-3 px-4 font-semibold text-slate-800">${{item.peca}}</td>
          <td class="py-3 px-4"><span class="inline-block px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 text-slate-700">${{item.categoria}}</span></td>
          <td class="py-3 px-4 text-center font-bold text-slate-700">${{item.qtTotal.toLocaleString('pt-BR')}} un</td>
          <td class="py-3 px-4 text-center font-semibold text-emerald-600">${{item.qtAtendida.toLocaleString('pt-BR')}} un</td>
          <td class="py-3 px-4 text-center font-semibold text-rose-500">${{item.qtNaoAtendida.toLocaleString('pt-BR')}} un</td>
          <td class="py-3 px-4 text-center text-slate-500">${{item.pedidosCount}}</td>
          <td class="py-3 px-4 text-right font-bold text-amber-600">${{formatCurrency(item.custoTotal)}}</td>
        </tr>
      `).join('');
    }}

    [filterYear, filterMonth, filterCategory, filterRequester].forEach(select => select.addEventListener('change', updateDashboard));
    tableSearch.addEventListener('input', updateDashboard);
    resetFiltersBtn.addEventListener('click', () => {{
      filterYear.value = 'ALL';
      filterMonth.value = 'ALL';
      filterCategory.value = 'ALL';
      filterRequester.value = 'ALL';
      tableSearch.value = '';
      updateDashboard();
    }});

    updateDashboard();
  </script>
</body>
</html>
"""

components.html(html_code, height=2500, scrolling=True)