import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd

# Configuração da página Streamlit em modo Wide
st.set_page_config(
    page_title="Gestão de Peças & Solicitações de Compras",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Oculta menus e bordas padrão do Streamlit
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

# URL para exportação direta em CSV da aba 'Base de Dados' (gid=270834817)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1iWjdaZLAp5hi9YIhmfSO4cPBn6fkfDjef8PAdZp1nsY/export?format=csv&gid=270834817"

@st.cache_data(ttl=300)
def carregar_base_de_dados():
    """Tenta ler online diretamente da planilha. Se não conseguir acesso, usa a base fiel extraída da aba."""
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        col_cod = df.columns[0]   # Coluna A: Produto / Código
        col_desc = df.columns[1]  # Coluna B: Descrição
        col_cat = df.columns[2]   # Coluna C: Grupo
        col_forn = df.columns[5]  # Coluna F: FORNECEDOR

        lista = []
        for _, row in df.iterrows():
            c = str(row[col_cod]).strip() if pd.notna(row[col_cod]) else ""
            d = str(row[col_desc]).strip() if pd.notna(row[col_desc]) else ""
            f = str(row[col_forn]).strip() if pd.notna(row[col_forn]) else "EVOCA"
            g = str(row[col_cat]).strip() if pd.notna(row[col_cat]) else "8 PEÇAS"
            
            if c and d and c.lower() != "nan" and d.lower() != "nan":
                lista.append({
                    "codigo": c,
                    "descricao": d,
                    "fornecedor": f,
                    "categoria": g
                })
        if len(lista) > 0:
            return lista
    except Exception:
        pass

    # Base oficial extraída diretamente da aba 'Base de Dados' (gid=270834817)
    return [
        {"codigo": "2290", "descricao": "ABERTURA PLASTICA CENTRAL SAIDA", "categoria": "8 PEÇAS", "fornecedor": "ANDRE MEKAR"},
        {"codigo": "534", "descricao": "ABRACADEIRA PEQUENA - INCANTO/ODEA/TALEA", "categoria": "8 PEÇAS", "fornecedor": "ANGELO OCS"},
        {"codigo": "534-INOX", "descricao": "ABRACADEIRA PEQUENA - INCANTO/ODEA/TALEA ( INOX )", "categoria": "8 PEÇAS", "fornecedor": "AUTO ELETRICA 3C"},
        {"codigo": "700", "descricao": "ACABABAMENTO TUBO DO VAPOR PRETO", "categoria": "8 PEÇAS", "fornecedor": "BIANCHI FERNANDO"},
        {"codigo": "1442", "descricao": "MAQUINA DE CAFE SOFIA 2 GRUPOS", "categoria": "MÁQUINAS DE CAFÉ", "fornecedor": "BIANCHI VENDING BRASIL S.A"},
        {"codigo": "2672", "descricao": "MAQ. CAFE EXPRESSO OPERA", "categoria": "MÁQUINAS DE CAFÉ", "fornecedor": "EVOCA BRAZIL"},
        {"codigo": "2617", "descricao": "MAQ. CAFE EXPRESSO KIKKO 220V", "categoria": "MÁQUINAS DE CAFÉ", "fornecedor": "EVOCA"},
        {"codigo": "PEC-00101", "descricao": "DISCO ROTAÇÃO DO MISTURADOR", "categoria": "Multi Bebidas", "fornecedor": "EVOCA"},
        {"codigo": "PEC-00102", "descricao": "BICO DE SAIDA DO SOLUVEL PHEDRA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA"},
        {"codigo": "PEC-00103", "descricao": "MOTOR DE MIXER COMPLETO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA"},
        {"codigo": "PEC-00104", "descricao": "TORNEIRA 3/4", "categoria": "Acessorios", "fornecedor": "LUCAS"},
        {"codigo": "PEC-00105", "descricao": "REMOVE GRUDE", "categoria": "Snaks", "fornecedor": "FABIO"},
        {"codigo": "PEC-00106", "descricao": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT"},
        {"codigo": "PEC-00107", "descricao": "BOMBA DE AGUA ULKA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT"},
        {"codigo": "PEC-00108", "descricao": "SPRAY COLORART PRATA LUNAR", "categoria": "Acessorios", "fornecedor": "MGC"},
        {"codigo": "PEC-00109", "descricao": "CONECTOR MACHO 8MM X1/2", "categoria": "Hidraulica", "fornecedor": "IMELKRON"},
        {"codigo": "PEC-00110", "descricao": "NUCLEO SOLUVEL SOLISTA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA"},
        {"codigo": "PEC-00111", "descricao": "GAXETA DE SILICONE", "categoria": "Acessorios", "fornecedor": "EVOCA"},
        {"codigo": "PEC-00112", "descricao": "MOTOR DO CARROSSEL PINO LONGO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA"},
        {"codigo": "PEC-00113", "descricao": "ANEL DO BICO CALDEIRA 70", "categoria": "Acessorios", "fornecedor": "PARAMOUNT"},
        {"codigo": "PEC-00114", "descricao": "ANEL BICO CALDEIRA 69", "categoria": "Acessorios", "fornecedor": "PARAMOUNT"},
        {"codigo": "PEC-00115", "descricao": "SUPORTE DE MAQUINA", "categoria": "Acessorios", "fornecedor": "LUCAS"},
        {"codigo": "PEC-00116", "descricao": "PINCEL DE LIMPEZA", "categoria": "Multi Bebidas", "fornecedor": "WILLIAN NEVES"},
        {"codigo": "PEC-00117", "descricao": "FILTRO BANANINHA C ENGATE RAPIDO", "categoria": "Hidraulica", "fornecedor": "PARAMOUNT"},
        {"codigo": "PEC-00118", "descricao": "PRODUTO ROSA DESENGRAXANTE", "categoria": "Multi Bebidas", "fornecedor": "TAIS MICHELE"},
        {"codigo": "PEC-00119", "descricao": "TORNEIRA METALICA", "categoria": "Acessorios", "fornecedor": "LUCAS"},
        {"codigo": "PEC-00120", "descricao": "CONTADOR VOLUMETRICO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA"},
        {"codigo": "PEC-00121", "descricao": "NUCLEO DA CALDEIRA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA"},
        {"codigo": "PEC-00122", "descricao": "MOTOR DO MOINHO 110V", "categoria": "Multi Bebidas", "fornecedor": "EVOCA"}
    ]

dados_catalogo = carregar_base_de_dados()
dados_catalogo_json = json.dumps(dados_catalogo, ensure_ascii=False)

html_code = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard Executivo - Solicitações & Ordens de Compra de Peças</title>
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
  </style>
</head>
<body class="bg-slate-100 text-slate-800 min-h-screen">

  <!-- Header Superior -->
  <header class="sticky top-0 z-40 bg-white/95 border-b border-slate-200 backdrop-blur-md px-6 py-3">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
      <div class="flex items-center gap-3">
        <div class="p-2.5 bg-blue-600 text-white rounded-xl shadow-lg shadow-blue-500/25">
          <i data-lucide="package-search" class="w-6 h-6"></i>
        </div>
        <div>
          <h1 class="text-xl font-bold tracking-tight text-slate-900">Painel de Compras & Solicitações de Peças</h1>
          <p class="text-xs text-slate-500">Aba: Base de Dados (Col A: Código | Col B: Descrição | Col F: Fornecedor)</p>
        </div>
      </div>
      
      <!-- Navegação -->
      <div class="flex items-center gap-2 bg-slate-100 p-1.5 rounded-2xl border border-slate-200">
        <button id="navDashboard" class="nav-btn active flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition" onclick="switchPage('dashboard')">
          <i data-lucide="layout-dashboard" class="w-4 h-4"></i>
          Dashboard Executivo
        </button>
        <button id="navForm" class="nav-btn inactive flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition" onclick="switchPage('formulario')">
          <i data-lucide="plus-circle" class="w-4 h-4"></i>
          Nova Solicitação (OC)
        </button>
        <span class="inline-flex items-center px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300 ml-1">
          <span class="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span> {len(dados_catalogo)} Itens na Base
        </span>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">

    <!-- ==================== PÁGINA 1: DASHBOARD ==================== -->
    <div id="pageDashboard" class="space-y-6">

      <!-- Filtros Dinâmicos -->
      <section class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <i data-lucide="sliders" class="w-4 h-4 text-blue-500"></i>
            <span>Filtros do Painel</span>
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
            <span class="p-1.5 rounded-lg bg-amber-50 text-amber-600">
              <i data-lucide="badge-dollar-sign" class="w-4 h-4"></i>
            </span>
          </div>
          <div class="mt-3">
            <span id="kpiTotalCost" class="text-xl font-bold tracking-tight text-amber-600">R$ 0,00</span>
            <p class="text-[11px] text-slate-400 mt-0.5">Soma da coluna Custo</p>
          </div>
        </div>

        <div class="kpi-card p-4 rounded-2xl shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total de Pedidos</span>
            <span class="p-1.5 rounded-lg bg-blue-50 text-blue-600">
              <i data-lucide="clipboard-list" class="w-4 h-4"></i>
            </span>
          </div>
          <div class="mt-3">
            <span id="kpiTotalRequests" class="text-xl font-bold tracking-tight text-slate-800">0</span>
            <p class="text-[11px] text-slate-400 mt-0.5">Ordens registradas</p>
          </div>
        </div>

        <div class="kpi-card p-4 rounded-2xl shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Qtde Solicitada</span>
            <span class="p-1.5 rounded-lg bg-indigo-50 text-indigo-600">
              <i data-lucide="boxes" class="w-4 h-4"></i>
            </span>
          </div>
          <div class="mt-3">
            <span id="kpiItemsQty" class="text-xl font-bold tracking-tight text-slate-800">0 un</span>
            <p class="text-[11px] text-slate-400 mt-0.5">Peças pedidas</p>
          </div>
        </div>

        <div class="kpi-card p-4 rounded-2xl shadow-sm flex flex-col justify-between border-emerald-200">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-emerald-600 uppercase tracking-wider">Peças Atendidas</span>
            <span class="p-1.5 rounded-lg bg-emerald-50 text-emerald-600">
              <i data-lucide="check-circle-2" class="w-4 h-4"></i>
            </span>
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
            <span class="p-1.5 rounded-lg bg-rose-50 text-rose-600">
              <i data-lucide="x-circle" class="w-4 h-4"></i>
            </span>
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
            <span class="p-1.5 rounded-lg bg-cyan-50 text-cyan-600">
              <i data-lucide="calculator" class="w-4 h-4"></i>
            </span>
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
          <div class="relative h-64">
            <canvas id="chartTopAgosto"></canvas>
          </div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 class="font-bold text-base text-slate-800 mb-2">Top 5 Solicitantes — Setembro</h3>
          <div class="relative h-64">
            <canvas id="chartTopSetembro"></canvas>
          </div>
        </div>
      </section>

      <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 class="font-bold text-base text-slate-800 mb-2">Distribuição por Categoria</h3>
          <div class="relative h-64">
            <canvas id="chartCategoryDist"></canvas>
          </div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 class="font-bold text-base text-slate-800 mb-2">Soma de Custo por Fornecedor (R$)</h3>
          <div class="relative h-64">
            <canvas id="chartSupplierCost"></canvas>
          </div>
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
            <p class="text-xs text-slate-500">Consolidado com Códigos (Coluna A), Nomes (Coluna B) e Custo</p>
          </div>

          <div class="flex items-center gap-3">
            <div class="relative">
              <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-2.5"></i>
              <input type="text" id="tableSearch" placeholder="Buscar código ou descrição..." class="text-xs pl-9 pr-3 py-2 rounded-xl border border-slate-300 bg-slate-50 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 w-56 sm:w-72">
            </div>
            <span id="tableCountBadge" class="text-xs px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 font-semibold">
              0 itens
            </span>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-600">
            <thead class="bg-slate-50 uppercase font-semibold text-slate-500">
              <tr>
                <th class="py-3 px-4 rounded-l-lg">Cód. Peça (Col A)</th>
                <th class="py-3 px-4">Descrição da Peça / Produto (Col B)</th>
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

    <!-- ==================== PÁGINA 2: FORMULÁRIO ==================== -->
    <div id="pageFormulario" class="hidden space-y-6">
      
      <section class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div class="flex items-center justify-between pb-4 mb-6 border-b border-slate-100">
          <div class="flex items-center gap-3">
            <div class="p-2.5 bg-blue-600 text-white rounded-xl shadow-lg shadow-blue-500/25">
              <i data-lucide="file-plus" class="w-6 h-6"></i>
            </div>
            <div>
              <h2 class="text-base font-bold text-slate-900">Formulário de Entrada: Solicitação & Ordem de Compra</h2>
              <p class="text-xs text-slate-500">Selecione uma peça na lista de pesquisa para preencher código, descrição e fornecedor automaticamente</p>
            </div>
          </div>
          <span class="text-xs font-semibold px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
            Padrão OC-AAAA-XXXX
          </span>
        </div>

        <form id="orderForm" onsubmit="handleFormSubmit(event)" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            
            <!-- Nº Ordem de Compra (OC-AAAA-XXXX) -->
            <div class="bg-blue-50/70 p-3 rounded-xl border border-blue-200">
              <label class="block text-xs font-bold text-blue-800 mb-1">Número da OC *</label>
              <input type="text" id="formNumeroOC" readonly class="w-full text-sm font-mono font-bold rounded-lg border border-blue-300 bg-white px-3 py-2 text-blue-700 cursor-not-allowed">
              <span class="text-[10px] text-blue-500 mt-1 block">Sequencial automático por ano</span>
            </div>

            <!-- Ano -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Ano *</label>
              <select id="formAno" required onchange="atualizarProximoNumeroOC()" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-slate-800">
                <option value="2026">2026</option>
                <option value="2025">2025</option>
              </select>
            </div>

            <!-- Mês -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Mês *</label>
              <select id="formMes" required class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-slate-800">
                <option value="Agosto">Agosto</option>
                <option value="Setembro">Setembro</option>
                <option value="Outubro" selected>Outubro</option>
                <option value="Novembro">Novembro</option>
                <option value="Dezembro">Dezembro</option>
                <option value="Janeiro">Janeiro</option>
                <option value="Fevereiro">Fevereiro</option>
                <option value="Março">Março</option>
                <option value="Abril">Abril</option>
                <option value="Maio">Maio</option>
                <option value="Junho">Junho</option>
                <option value="Julho">Julho</option>
              </select>
            </div>

            <!-- Data da Solicitação -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Data da Solicitação *</label>
              <input type="date" id="formData" required class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-slate-800">
            </div>

            <!-- Solicitante -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Solicitante / Setor *</label>
              <input type="text" id="formSolicitante" placeholder="Ex: Willian Neves, Thiago, Flávio, Samantha" required class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-slate-800">
            </div>

            <!-- CAMPO DE PESQUISA COM AUTOCOMPLETAR DA PLANILHA -->
            <div class="col-span-1 md:col-span-3 bg-slate-50 p-4 rounded-xl border-2 border-blue-300">
              <label class="block text-xs font-bold text-blue-900 mb-1">
                🔍 Pesquisar Peça a ser Solicitada (Planilha Base de Dados) *
              </label>
              <input list="listaPecasCadastradas" id="formPesquisaPeca" placeholder="Clique duas vezes ou comece a digitar o código (ex: 2290, 534) ou descrição..." onchange="selecionarPecaPredefinida()" oninput="selecionarPecaPredefinida()" class="w-full text-sm rounded-xl border border-blue-400 bg-white px-3.5 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600 font-semibold shadow-sm">
              <datalist id="listaPecasCadastradas"></datalist>
              <p class="text-[11px] text-slate-500 mt-1">Ao selecionar uma peça, os campos abaixo (Código, Descrição e Fornecedor) serão preenchidos na hora.</p>
            </div>

            <!-- Código da Peça (Coluna A) -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Código da Peça (Coluna A) *</label>
              <input type="text" id="formCodigoPeca" placeholder="Ex: 2290" required class="w-full text-sm font-mono font-bold rounded-xl border border-slate-300 bg-slate-100 px-3.5 py-2.5 text-slate-800">
            </div>

            <!-- Descrição da Peça / Produto (Coluna B) -->
            <div class="col-span-1 md:col-span-2">
              <label class="block text-xs font-semibold text-slate-700 mb-1">Descrição da Peça / Produto (Coluna B) *</label>
              <input type="text" id="formPeca" placeholder="Ex: ABERTURA PLASTICA CENTRAL SAIDA" required class="w-full text-sm font-semibold rounded-xl border border-slate-300 bg-slate-100 px-3.5 py-2.5 text-slate-800">
            </div>

            <!-- Fornecedor (Coluna F) -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Fornecedor (Coluna F) *</label>
              <input type="text" id="formFornecedor" placeholder="Ex: EVOCA, PARAMOUNT, ANDRE MEKAR" required class="w-full text-sm font-semibold rounded-xl border border-slate-300 bg-slate-100 px-3.5 py-2.5 text-slate-800">
            </div>

            <!-- Categoria -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Categoria *</label>
              <input type="text" id="formCategoria" placeholder="Ex: 8 PEÇAS, Multi Bebidas" required class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-slate-800">
            </div>

            <!-- Quantidade Solicitada -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Quantidade Solicitada (Qt) *</label>
              <input type="number" id="formQt" min="1" value="1" required oninput="calcQuantidades()" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-slate-800">
            </div>

            <!-- Custo Unitário -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Custo Unitário (R$) *</label>
              <input type="number" step="0.01" min="0" id="formCustoUnit" placeholder="Ex: 195,00" required oninput="calcQuantidades()" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-slate-800">
            </div>

            <!-- Quantidade Atendida -->
            <div>
              <label class="block text-xs font-semibold text-emerald-700 mb-1">Quantidade Atendida</label>
              <input type="number" id="formQtAprovada" min="0" value="1" oninput="calcQuantidades()" class="w-full text-sm rounded-xl border border-emerald-300 bg-emerald-50/30 px-3.5 py-2.5 text-slate-800">
            </div>

            <!-- Quantidade Não Atendida -->
            <div>
              <label class="block text-xs font-semibold text-rose-700 mb-1">Quantidade Não Atendida</label>
              <input type="number" id="formQtNaoAprovada" min="0" value="0" class="w-full text-sm rounded-xl border border-rose-300 bg-rose-50/30 px-3.5 py-2.5 text-slate-800">
            </div>

            <!-- Custo Total Previsto -->
            <div class="col-span-1 md:col-span-3">
              <label class="block text-xs font-semibold text-amber-700 mb-1">Custo Total Previsto (Coluna Custo)</label>
              <input type="text" id="formCustoTotalPreview" readonly value="R$ 0,00" class="w-full text-base font-bold rounded-xl border border-amber-300 bg-amber-50/50 px-3.5 py-2.5 text-amber-800 cursor-not-allowed">
            </div>

          </div>

          <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
            <button type="button" onclick="switchPage('dashboard')" class="px-5 py-2.5 rounded-xl border border-slate-300 bg-white text-xs font-semibold text-slate-600 hover:bg-slate-50 transition">
              Cancelar
            </button>
            <button type="submit" class="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 text-white text-xs font-bold shadow-lg shadow-blue-500/25 hover:bg-blue-700 transition">
              <i data-lucide="check" class="w-4 h-4"></i>
              Emitir e Lançar Ordem de Compra
            </button>
          </div>
        </form>
      </section>

      <!-- Histórico de Lançamentos Recentes -->
      <section class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
          <i data-lucide="history" class="w-4 h-4 text-slate-400"></i>
          Últimas Ordens de Compra Emitidas nesta Sessão
        </h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-600">
            <thead class="bg-slate-50 uppercase font-semibold text-slate-500">
              <tr>
                <th class="py-2.5 px-3">Nº OC</th>
                <th class="py-2.5 px-3">Data</th>
                <th class="py-2.5 px-3">Solicitante</th>
                <th class="py-2.5 px-3">Cód. Peça</th>
                <th class="py-2.5 px-3">Peça / Produto</th>
                <th class="py-2.5 px-3">Fornecedor</th>
                <th class="py-2.5 px-3 text-center">Qt Pedida</th>
                <th class="py-2.5 px-3 text-center text-emerald-600">Atendida</th>
                <th class="py-2.5 px-3 text-right">Custo Total</th>
              </tr>
            </thead>
            <tbody id="recentEntriesBody" class="divide-y divide-slate-100">
              <tr>
                <td colspan="9" class="text-center py-4 text-slate-400">Nenhum lançamento emitido na sessão ainda.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </div>

  </main>

  <script>
    lucide.createIcons();
    Chart.register(ChartDataLabels);

    document.getElementById('formData').value = new Date().toISOString().split('T')[0];

    // ==========================================
    // CARREGA BASE DE DADOS (COLUNAS A, B e F)
    // ==========================================
    const catalogoPecasPreCriada = {dados_catalogo_json};

    // Monta as opções do datalist pesquisável
    const datalist = document.getElementById('listaPecasCadastradas');
    datalist.innerHTML = '';
    catalogoPecasPreCriada.forEach(item => {{
      const opt = document.createElement('option');
      opt.value = `${{item.codigo}} | ${{item.descricao}} | ${{item.fornecedor}}`;
      datalist.appendChild(opt);
    }});

    // Função que preenche Código (A), Descrição (B) e Fornecedor (F)
    function selecionarPecaPredefinida() {{
      const val = document.getElementById('formPesquisaPeca').value.trim();
      if (!val) return;

      const valLower = val.toLowerCase();
      const achado = catalogoPecasPreCriada.find(item => {{
        const fullString = `${{item.codigo}} | ${{item.descricao}} | ${{item.fornecedor}}`.toLowerCase();
        return (
          item.codigo.toLowerCase() === valLower ||
          item.descricao.toLowerCase() === valLower ||
          fullString === valLower ||
          fullString.startsWith(valLower) ||
          fullString.includes(valLower)
        );
      }});

      if (achado) {{
        document.getElementById('formCodigoPeca').value = achado.codigo;
        document.getElementById('formPeca').value = achado.descricao;
        document.getElementById('formFornecedor').value = achado.fornecedor;
        document.getElementById('formCategoria').value = achado.categoria || '8 PEÇAS';
        calcQuantidades();
      }}
    }}

    // Dados de Ordens de Compra
    let rawOrdersData = [
      {{ oc: 'OC-2025-0001', ano: '2025', mes: 'Agosto', data: '05/08/2025', solicitante: 'WILLIAN NEVES', codigoPeca: 'PEC-00101', peca: 'DISCO ROTAÇÃO DO MISTURADOR', categoria: 'Multi Bebidas', fornecedor: 'EVOCA', qt: 15, qtAprovada: 15, qtNaoAprovada: 0, custoUnit: 4.39 }},
      {{ oc: 'OC-2025-0002', ano: '2025', mes: 'Agosto', data: '08/08/2025', solicitante: 'FLAVIO', codigoPeca: 'PEC-00102', peca: 'BICO DE SAIDA DO SOLUVEL PHEDRA', categoria: 'Multi Bebidas', fornecedor: 'EVOCA', qt: 12, qtAprovada: 12, qtNaoAprovada: 0, custoUnit: 8.52 }},
      {{ oc: 'OC-2025-0003', ano: '2025', mes: 'Agosto', data: '12/08/2025', solicitante: 'WILLIAN NEVES', codigoPeca: 'PEC-00103', peca: 'MOTOR DE MIXER COMPLETO', categoria: 'Multi Bebidas', fornecedor: 'EVOCA', qt: 4, qtAprovada: 4, qtNaoAprovada: 0, custoUnit: 334.00 }},
      {{ oc: 'OC-2025-0004', ano: '2025', mes: 'Agosto', data: '14/08/2025', solicitante: 'NAPOLEAO', codigoPeca: 'PEC-00104', peca: 'TORNEIRA 3/4', categoria: 'Acessorios', fornecedor: 'LUCAS', qt: 8, qtAprovada: 7, qtNaoAprovada: 1, custoUnit: 75.18 }},
      {{ oc: 'OC-2025-0005', ano: '2025', mes: 'Agosto', data: '18/08/2025', solicitante: 'FABIO', codigoPeca: 'PEC-00105', peca: 'REMOVE GRUDE', categoria: 'Snaks', fornecedor: 'FABIO', qt: 10, qtAprovada: 10, qtNaoAprovada: 0, custoUnit: 72.00 }},
      {{ oc: 'OC-2025-0006', ano: '2025', mes: 'Agosto', data: '20/08/2025', solicitante: 'LUCAS', codigoPeca: 'PEC-00106', peca: 'BOMBA DE AGUA 220V', categoria: 'Multi Bebidas', fornecedor: 'PARAMOUNT', qt: 6, qtAprovada: 5, qtNaoAprovada: 1, custoUnit: 180.00 }},
      {{ oc: 'OC-2025-0007', ano: '2025', mes: 'Agosto', data: '22/08/2025', solicitante: 'WILLIAN NEVES', codigoPeca: 'PEC-00108', peca: 'SPRAY COLORART PRATA LUNAR', categoria: 'Acessorios', fornecedor: 'MGC', qt: 20, qtAprovada: 20, qtNaoAprovada: 0, custoUnit: 26.50 }},
      {{ oc: 'OC-2025-0008', ano: '2025', mes: 'Agosto', data: '25/08/2025', solicitante: 'FLAVIO', codigoPeca: 'PEC-00109', peca: 'CONECTOR MACHO 8MM X1/2', categoria: 'Hidraulica', fornecedor: 'IMELKRON', qt: 30, qtAprovada: 25, qtNaoAprovada: 5, custoUnit: 10.50 }},
      {{ oc: 'OC-2025-0009', ano: '2025', mes: 'Agosto', data: '28/08/2025', solicitante: 'NAPOLEAO', codigoPeca: 'PEC-00110', peca: 'NUCLEO SOLUVEL SOLISTA', categoria: 'Multi Bebidas', fornecedor: 'EVOCA', qt: 5, qtAprovada: 5, qtNaoAprovada: 0, custoUnit: 91.04 }},
      {{ oc: 'OC-2025-0010', ano: '2025', mes: 'Setembro', data: '02/09/2025', solicitante: 'THIAGO', codigoPeca: 'PEC-00107', peca: 'BOMBA DE AGUA ULKA 220V', categoria: 'Multi Bebidas', fornecedor: 'PARAMOUNT', qt: 18, qtAprovada: 18, qtNaoAprovada: 0, custoUnit: 195.00 }},
      {{ oc: 'OC-2025-0011', ano: '2025', mes: 'Setembro', data: '05/09/2025', solicitante: 'SAMANTHA', codigoPeca: 'PEC-00111', peca: 'GAXETA DE SILICONE', categoria: 'Acessorios', fornecedor: 'EVOCA', qt: 25, qtAprovada: 22, qtNaoAprovada: 3, custoUnit: 18.50 }},
      {{ oc: 'OC-2026-0001', ano: '2026', mes: 'Março', data: '02/03/2026', solicitante: 'DAVI', codigoPeca: '2290', peca: 'ABERTURA PLASTICA CENTRAL SAIDA', categoria: '8 PEÇAS', fornecedor: 'ANDRE MEKAR', qt: 5, qtAprovada: 5, qtNaoAprovada: 0, custoUnit: 45.00 }},
      {{ oc: 'OC-2026-0002', ano: '2026', mes: 'Março', data: '07/03/2026', solicitante: 'DAVI', codigoPeca: '534', peca: 'ABRACADEIRA PEQUENA - INCANTO/ODEA/TALEA', categoria: '8 PEÇAS', fornecedor: 'ANGELO OCS', qt: 10, qtAprovada: 10, qtNaoAprovada: 0, custoUnit: 12.50 }},
      {{ oc: 'OC-2026-0003', ano: '2026', mes: 'Agosto', data: '14/08/2026', solicitante: 'WILLIAN NEVES', codigoPeca: 'PEC-00106', peca: 'BOMBA DE AGUA 220V', categoria: 'Multi Bebidas', fornecedor: 'PARAMOUNT', qt: 12, qtAprovada: 12, qtNaoAprovada: 0, custoUnit: 195.00 }},
      {{ oc: 'OC-2026-0004', ano: '2026', mes: 'Setembro', data: '11/09/2026', solicitante: 'THIAGO', codigoPeca: 'PEC-00106', peca: 'BOMBA DE AGUA 220V', categoria: 'Multi Bebidas', fornecedor: 'PARAMOUNT', qt: 14, qtAprovada: 14, qtNaoAprovada: 0, custoUnit: 195.00 }}
    ];

    function recalcularCustos() {{
      rawOrdersData.forEach(item => {{
        item.custoTotal = item.qtAprovada * item.custoUnit;
      }});
    }}
    recalcularCustos();

    // ==========================================
    // GERADOR DO NÚMERO DE OC (OC-AAAA-XXXX)
    // ==========================================
    function gerarNumeroOC(anoSelecionado) {{
      const pedidosDoAno = rawOrdersData.filter(d => d.ano === anoSelecionado);
      let maiorSequencial = 0;
      pedidosDoAno.forEach(item => {{
        if (item.oc && item.oc.startsWith(`OC-${{anoSelecionado}}-`)) {{
          const partes = item.oc.split('-');
          const seq = parseInt(partes[2]);
          if (!isNaN(seq) && seq > maiorSequencial) {{
            maiorSequencial = seq;
          }}
        }}
      }});
      const proximoSeq = String(maiorSequencial + 1).padStart(4, '0');
      return `OC-${{anoSelecionado}}-${{proximoSeq}}`;
    }}

    function atualizarProximoNumeroOC() {{
      const anoSelecionado = document.getElementById('formAno').value;
      document.getElementById('formNumeroOC').value = gerarNumeroOC(anoSelecionado);
    }}
    atualizarProximoNumeroOC();

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

    function calcQuantidades() {{
      const qt = parseInt(document.getElementById('formQt').value) || 0;
      let qtAprovada = parseInt(document.getElementById('formQtAprovada').value);
      if (isNaN(qtAprovada)) qtAprovada = qt;

      if (qtAprovada > qt) {{
        qtAprovada = qt;
        document.getElementById('formQtAprovada').value = qt;
      }}

      const qtNao = Math.max(0, qt - qtAprovada);
      document.getElementById('formQtNaoAprovada').value = qtNao;

      const custoUnit = parseFloat(document.getElementById('formCustoUnit').value) || 0;
      const custoTotal = qtAprovada * custoUnit;
      document.getElementById('formCustoTotalPreview').value = formatCurrency(custoTotal);
    }}

    function handleFormSubmit(e) {{
      e.preventDefault();

      const oc = document.getElementById('formNumeroOC').value;
      const ano = document.getElementById('formAno').value;
      const mes = document.getElementById('formMes').value;
      const dataStr = document.getElementById('formData').value;
      const solicitante = document.getElementById('formSolicitante').value.toUpperCase().trim();
      const codigoPeca = document.getElementById('formCodigoPeca').value.toUpperCase().trim();
      const peca = document.getElementById('formPeca').value.toUpperCase().trim();
      const categoria = document.getElementById('formCategoria').value;
      const fornecedor = document.getElementById('formFornecedor').value.toUpperCase().trim();
      const qt = parseInt(document.getElementById('formQt').value) || 0;
      const qtAprovada = parseInt(document.getElementById('formQtAprovada').value) || 0;
      const qtNaoAprovada = parseInt(document.getElementById('formQtNaoAprovada').value) || 0;
      const custoUnit = parseFloat(document.getElementById('formCustoUnit').value) || 0;

      const novoRegistro = {{
        oc,
        ano,
        mes,
        data: dataStr,
        solicitante,
        codigoPeca,
        peca,
        categoria,
        fornecedor,
        qt,
        qtAprovada,
        qtNaoAprovada,
        custoUnit,
        custoTotal: qtAprovada * custoUnit
      }};

      rawOrdersData.unshift(novoRegistro);

      const recentBody = document.getElementById('recentEntriesBody');
      const emptyRow = recentBody.querySelector('td[colspan="9"]');
      if (emptyRow) recentBody.innerHTML = '';

      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-50 transition font-medium';
      tr.innerHTML = `
        <td class="py-2.5 px-3 font-mono font-bold text-blue-700">${{novoRegistro.oc}}</td>
        <td class="py-2.5 px-3">${{novoRegistro.data}}</td>
        <td class="py-2.5 px-3 font-semibold text-slate-800">${{novoRegistro.solicitante}}</td>
        <td class="py-2.5 px-3 font-mono text-slate-600">${{novoRegistro.codigoPeca}}</td>
        <td class="py-2.5 px-3 font-semibold text-slate-800">${{novoRegistro.peca}}</td>
        <td class="py-2.5 px-3">${{novoRegistro.fornecedor}}</td>
        <td class="py-2.5 px-3 text-center font-bold">${{novoRegistro.qt}} un</td>
        <td class="py-2.5 px-3 text-center font-bold text-emerald-600">${{novoRegistro.qtAprovada}} un</td>
        <td class="py-2.5 px-3 text-right font-bold text-amber-600">${{formatCurrency(novoRegistro.custoTotal)}}</td>
      `;
      recentBody.prepend(tr);

      // Limpar formulário
      document.getElementById('formPesquisaPeca').value = '';
      document.getElementById('formCodigoPeca').value = '';
      document.getElementById('formPeca').value = '';
      document.getElementById('formFornecedor').value = '';
      document.getElementById('formQt').value = '1';
      document.getElementById('formQtAprovada').value = '1';
      document.getElementById('formQtNaoAprovada').value = '0';
      document.getElementById('formCustoUnit').value = '';
      document.getElementById('formCustoTotalPreview').value = 'R$ 0,00';

      atualizarProximoNumeroOC();
      populateDropdowns();
      updateDashboard();

      alert(`✅ Ordem de Compra ${{novoRegistro.oc}} gerada e salva com sucesso!`);
      switchPage('dashboard');
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

    function formatCurrency(val) {{
      return val.toLocaleString('pt-BR', {{ style: 'currency', currency: 'BRL' }});
    }}

    function populateDropdowns() {{
      const currentYear = filterYear.value;
      const currentMonth = filterMonth.value;
      const currentCat = filterCategory.value;
      const currentReq = filterRequester.value;

      filterYear.innerHTML = '<option value="ALL">Todos os Anos</option>';
      filterMonth.innerHTML = '<option value="ALL">Todos os Meses</option>';
      filterCategory.innerHTML = '<option value="ALL">Todas as Categorias</option>';
      filterRequester.innerHTML = '<option value="ALL">Todos os Solicitantes</option>';

      const years = [...new Set(rawOrdersData.map(d => d.ano))].sort();
      const months = [...new Set(rawOrdersData.map(d => d.mes))];
      const categories = [...new Set(rawOrdersData.map(d => d.categoria))].sort();
      const requesters = [...new Set(rawOrdersData.map(d => d.solicitante))].sort();

      years.forEach(y => {{
        const opt = document.createElement('option');
        opt.value = y;
        opt.textContent = y;
        filterYear.appendChild(opt);
      }});

      months.forEach(m => {{
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        filterMonth.appendChild(opt);
      }});

      categories.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        filterCategory.appendChild(opt);
      }});

      requesters.forEach(r => {{
        const opt = document.createElement('option');
        opt.value = r;
        opt.textContent = r;
        filterRequester.appendChild(opt);
      }});

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

      const totalCusto = filtered.reduce((acc, cur) => acc + cur.custoTotal, 0);
      const totalItens = filtered.reduce((acc, cur) => acc + cur.qt, 0);
      const totalAtendidas = filtered.reduce((acc, cur) => acc + cur.qtAprovada, 0);
      const totalNaoAtendidas = filtered.reduce((acc, cur) => acc + cur.qtNaoAprovada, 0);
      const totalPedidos = filtered.length;
      const avgCost = totalPedidos > 0 ? (totalCusto / totalPedidos) : 0;

      const pctAtendidas = totalItens > 0 ? Math.round((totalAtendidas / totalItens) * 100) : 0;
      const pctNaoAtendidas = totalItens > 0 ? (100 - pctAtendidas) : 0;

      kpiTotalCost.innerText = formatCurrency(totalCusto);
      kpiTotalRequests.innerText = totalPedidos;
      kpiItemsQty.innerText = `${{totalItens.toLocaleString('pt-BR')}} un`;
      kpiApprovedQty.innerText = `${{totalAtendidas.toLocaleString('pt-BR')}} un`;
      kpiApprovedPercent.innerText = `${{pctAtendidas}}%`;
      kpiUnapprovedQty.innerText = `${{totalNaoAtendidas.toLocaleString('pt-BR')}} un`;
      kpiUnapprovedPercent.innerText = `${{pctNaoAtendidas}}%`;
      kpiAvgCost.innerText = formatCurrency(avgCost);

      const agostoItems = rawOrdersData.filter(d => (yearVal === 'ALL' || d.ano === yearVal) && d.mes === 'Agosto');
      const setembroItems = rawOrdersData.filter(d => (yearVal === 'ALL' || d.ano === yearVal) && d.mes === 'Setembro');

      function getTop5(items) {{
        const counts = {{}};
        items.forEach(d => counts[d.solicitante] = (counts[d.solicitante] || 0) + d.qt);
        return Object.entries(counts).map(([name, qt]) => ({{ name, qt }})).sort((a, b) => b.qt - a.qt).slice(0, 5);
      }}

      const topAgosto = getTop5(agostoItems);
      chartAgosto.data.labels = topAgosto.map(d => d.name);
      chartAgosto.data.datasets[0].data = topAgosto.map(d => d.qt);
      chartAgosto.update();

      const topSetembro = getTop5(setembroItems);
      chartSetembro.data.labels = topSetembro.map(d => d.name);
      chartSetembro.data.datasets[0].data = topSetembro.map(d => d.qt);
      chartSetembro.update();

      const catCounts = {{}};
      filtered.forEach(d => catCounts[d.categoria] = (catCounts[d.categoria] || 0) + d.qt);
      chartCategory.data.labels = Object.keys(catCounts);
      chartCategory.data.datasets[0].data = Object.values(catCounts);
      chartCategory.update();

      const supplierCosts = {{}};
      filtered.forEach(d => supplierCosts[d.fornecedor] = (supplierCosts[d.fornecedor] || 0) + d.custoTotal);
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
        grouped[key].qtTotal += item.qt;
        grouped[key].qtAtendida += item.qtAprovada;
        grouped[key].qtNaoAtendida += item.qtNaoAprovada;
        grouped[key].pedidosCount += 1;
        grouped[key].custoTotal += item.custoTotal;
      }});

      let itemsArray = Object.values(grouped);
      if (searchTerm) {{
        itemsArray = itemsArray.filter(i => 
          i.peca.toLowerCase().includes(searchTerm) || 
          i.codigoPeca.toLowerCase().includes(searchTerm) ||
          i.categoria.toLowerCase().includes(searchTerm)
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

components.html(html_code, height=2200, scrolling=True)