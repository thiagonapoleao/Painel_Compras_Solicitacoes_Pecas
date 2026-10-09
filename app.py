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

# Oculta menus padrão do Streamlit
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

# IDs e URLs da Planilha do Google Sheets (Aba: Base de Dados gid=270834817)
SPREADSHEET_ID = "1iWjdaZLAp5hi9YIhmfSO4cPBn6fkfDjef8PAdZp1nsY"
GID_BASE = "270834817"

URL_CSV_DIRECT = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_BASE}"
URL_GVIZ_DIRECT = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_BASE}"

def buscar_dados_planilha_ao_vivo():
    """Lê diretamente da aba 'Base de Dados' do Google Sheets em tempo real."""
    df = None
    try:
        df = pd.read_csv(URL_CSV_DIRECT, dtype=str)
    except Exception:
        try:
            df = pd.read_csv(URL_GVIZ_DIRECT, dtype=str)
        except Exception:
            pass

    if df is None or df.empty:
        st.error(
            "⚠️ Não foi possível ler a planilha em tempo real. "
            "Certifique-se de que a planilha está com acesso liberado em: "
            "**Compartilhar > Qualquer pessoa com o link pode ler**."
        )
        return []

    col_a = df.columns[0]
    col_b = df.columns[1] if len(df.columns) > 1 else col_a
    col_c = df.columns[2] if len(df.columns) > 2 else col_a
    col_f = df.columns[5] if len(df.columns) > 5 else (df.columns[-1])

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

dados_catalogo = buscar_dados_planilha_ao_vivo()
catalogo_json = json.dumps(dados_catalogo, ensure_ascii=False)
total_itens_carregados = len(dados_catalogo)

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

    /* Estilos de Impressão */
    @media print {{
      body * {{
        visibility: hidden;
      }}
      #printArea, #printArea * {{
        visibility: visible;
      }}
      #printArea {{
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        background-color: #ffffff !important;
        padding: 24px;
        color: #000000 !important;
      }}
      .no-print {{
        display: none !important;
      }}
    }}
  </style>
</head>
<body class="bg-slate-100 text-slate-800 min-h-screen">

  <!-- Header Superior -->
  <header class="no-print sticky top-0 z-40 bg-white/95 border-b border-slate-200 backdrop-blur-md px-6 py-3">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
      <div class="flex items-center gap-3">
        <div class="p-2.5 bg-blue-600 text-white rounded-xl shadow-lg shadow-blue-500/25">
          <i data-lucide="package-search" class="w-6 h-6"></i>
        </div>
        <div>
          <h1 class="text-xl font-bold tracking-tight text-slate-900">Painel de Compras & Ordens de Compra</h1>
          <p class="text-xs text-slate-500">Fornecedor único · Reimpressão de Pedidos · Preço de Venda (+70%)</p>
        </div>
      </div>
      
      <!-- Navegação -->
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
          <span class="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span> {total_itens_carregados} Peças (Recarregar 🔄)
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

    <!-- ==================== PÁGINA 2: FORMULÁRIO DE LANÇAMENTO ==================== -->
    <div id="pageFormulario" class="space-y-6">

      <!-- Notificação de Sucesso com Botão de Imprimir Imediato -->
      <div id="alertSuccess" class="hidden p-5 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm transition">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-emerald-600 text-white rounded-xl">
            <i data-lucide="check-circle" class="w-5 h-5"></i>
          </div>
          <div>
            <p id="alertSuccessTitle" class="text-sm font-bold">Ordem de Compra salva com sucesso!</p>
            <p id="alertSuccessSub" class="text-xs text-emerald-700">Os campos foram limpos para a próxima solicitação.</p>
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
              <h2 class="text-base font-bold text-slate-900">Formulário de Entrada: Solicitação de Compra de Peças</h2>
              <p class="text-xs text-slate-500">Fornecedor único · Múltiplas peças · Valor de Venda com <strong>+70% de margem</strong></p>
            </div>
          </div>
          <span class="text-xs font-semibold px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
            Padrão OC-AAAA-XXXX
          </span>
        </div>

        <form id="orderForm" onsubmit="handleFinalSubmit(event)" class="space-y-6">
          
          <!-- DADOS GERAIS DO CABEÇALHO DA OC (FORNECEDOR É ÚNICO NO CABEÇALHO) -->
          <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 p-5 rounded-2xl bg-slate-50/90 border border-slate-200">
            <!-- Nº Ordem de Compra (OC-AAAA-XXXX) -->
            <div>
              <label class="block text-xs font-bold text-blue-800 mb-1">Número da OC *</label>
              <input type="text" id="formNumeroOC" readonly class="w-full text-sm font-mono font-bold rounded-xl border border-blue-300 bg-white px-3.5 py-2 text-blue-700 cursor-not-allowed shadow-inner">
            </div>

            <!-- Ano -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Ano *</label>
              <select id="formAno" required onchange="atualizarProximoNumeroOC()" class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
                <option value="2026">2026</option>
                <option value="2025">2025</option>
              </select>
            </div>

            <!-- Mês -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Mês *</label>
              <select id="formMes" required class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
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
              <input type="date" id="formData" required class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
            </div>

            <!-- Solicitante (Será limpo após salvar) -->
            <div class="lg:col-span-2">
              <label class="block text-xs font-semibold text-slate-700 mb-1">Solicitante *</label>
              <input type="text" id="formSolicitante" placeholder="Ex: Willian Neves, Thiago, Flávio, Samantha" required class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-slate-800">
            </div>

            <!-- FORNECEDOR (ÚNICO POR PEDIDO - Será limpo após salvar) -->
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
              <!-- 1. CÓDIGO DA PEÇA COM PRÉ-LISTA DA COLUNA A DA PLANILHA -->
              <div>
                <label class="block text-xs font-bold text-slate-800 mb-1">
                  Código da Peça *
                </label>
                <input list="listaCodigosPecas" id="itemCodigoPeca" placeholder="Clique ou digite o código..." oninput="aoMudarCodigo()" onchange="aoMudarCodigo()" class="w-full text-sm font-mono font-bold rounded-xl border border-blue-300 bg-white px-3.5 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600">
                <datalist id="listaCodigosPecas"></datalist>
              </div>

              <!-- 2. DESCRIÇÃO DA PEÇA / PRODUTO COM PRÉ-LISTA DA COLUNA B DA PLANILHA -->
              <div class="col-span-1 md:col-span-2">
                <label class="block text-xs font-bold text-slate-800 mb-1">
                  Descrição da Peça / Produto *
                </label>
                <input list="listaDescricoesPecas" id="itemPeca" placeholder="Clique ou digite a descrição da peça..." oninput="aoMudarDescricao()" onchange="aoMudarDescricao()" class="w-full text-sm font-semibold rounded-xl border border-blue-300 bg-white px-3.5 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600">
                <datalist id="listaDescricoesPecas"></datalist>
              </div>

              <!-- Categoria -->
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1">Categoria</label>
                <input type="text" id="itemCategoria" placeholder="Ex: 8 PEÇAS, Multi Bebidas" class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
              </div>

              <!-- Quantidade Solicitada -->
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1">Quantidade Solicitada (Qt) *</label>
                <input type="number" id="itemQt" min="1" value="1" oninput="calcItemPreview()" class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
              </div>

              <!-- Custo Unitário -->
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1">Custo Unitário (R$) *</label>
                <input type="number" step="0.01" min="0" id="itemCustoUnit" placeholder="0,00" oninput="calcItemPreview()" class="w-full text-sm rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-800">
              </div>

              <!-- Valor de Venda Unitário Calculado (+70%) -->
              <div>
                <label class="block text-xs font-semibold text-emerald-700 mb-1">Valor Venda Unit. (+70%)</label>
                <input type="text" id="itemVendaUnitPreview" readonly value="R$ 0,00" class="w-full text-sm font-bold rounded-xl border border-emerald-300 bg-emerald-50/60 px-3 py-2 text-emerald-900 cursor-not-allowed">
              </div>

              <!-- Quantidade Atendida -->
              <div>
                <label class="block text-xs font-semibold text-emerald-700 mb-1">Quantidade Atendida</label>
                <input type="number" id="itemQtAprovada" min="0" value="1" oninput="calcItemPreview()" class="w-full text-sm rounded-xl border border-emerald-300 bg-emerald-50/30 px-3 py-2 text-slate-800">
              </div>

              <!-- Quantidade Não Atendida -->
              <div>
                <label class="block text-xs font-semibold text-rose-700 mb-1">Quantidade Não Atendida</label>
                <input type="number" id="itemQtNaoAprovada" min="0" value="0" class="w-full text-sm rounded-xl border border-rose-300 bg-rose-50/30 px-3 py-2 text-slate-800">
              </div>

              <!-- Subtotal Custo -->
              <div>
                <label class="block text-xs font-semibold text-amber-700 mb-1">Subtotal Custo Total</label>
                <input type="text" id="itemCustoSubtotalPreview" readonly value="R$ 0,00" class="w-full text-sm font-bold rounded-xl border border-amber-300 bg-amber-50/60 px-3 py-2 text-amber-900 cursor-not-allowed">
              </div>

              <!-- Subtotal Venda Total -->
              <div>
                <label class="block text-xs font-semibold text-indigo-700 mb-1">Subtotal Venda Total (+70%)</label>
                <input type="text" id="itemVendaSubtotalPreview" readonly value="R$ 0,00" class="w-full text-sm font-bold rounded-xl border border-indigo-300 bg-indigo-50/60 px-3 py-2 text-indigo-900 cursor-not-allowed">
              </div>

              <!-- Botão Adicionar Item -->
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
                    <th class="py-2.5 px-3 text-right text-emerald-700">Venda Unit. (+70%)</th>
                    <th class="py-2.5 px-3 text-right">Custo Total</th>
                    <th class="py-2.5 px-3 text-right text-indigo-700">Venda Total</th>
                    <th class="py-2.5 px-3 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody id="listaPecasOCTableBody" class="divide-y divide-slate-100">
                  <tr id="rowEmptyList">
                    <td colspan="10" class="text-center py-6 text-slate-400">Nenhuma peça adicionada ainda. Preencha os campos acima e clique em "Adicionar Peça à Ordem".</td>
                  </tr>
                </tbody>
                <tfoot class="bg-slate-50 font-bold text-slate-800 border-t border-slate-200">
                  <tr>
                    <td colspan="3" class="py-3 px-3 text-right uppercase text-[11px]">Totais da Ordem de Compra:</td>
                    <td id="footTotalQt" class="py-3 px-3 text-center text-blue-700 font-bold">0 un</td>
                    <td id="footTotalAtendida" class="py-3 px-3 text-center text-emerald-700 font-bold">0 un</td>
                    <td colspan="2"></td>
                    <td id="footTotalValor" class="py-3 px-3 text-right text-amber-700 font-bold text-sm">R$ 0,00</td>
                    <td id="footTotalVenda" class="py-3 px-3 text-right text-indigo-700 font-bold text-sm">R$ 0,00</td>
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
            <button type="submit" class="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 text-white text-xs font-bold shadow-lg shadow-blue-500/25 hover:bg-blue-700 transition">
              <i data-lucide="save" class="w-4 h-4"></i>
              Salvar e Emitir Ordem de Compra
            </button>
          </div>
        </form>
      </section>

      <!-- Histórico de Lançamentos Recentes com Botão de Imprimir em cada linha -->
      <section class="no-print bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 class="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
          <i data-lucide="history" class="w-4 h-4 text-slate-400"></i>
          Últimas Ordens de Compra Emitidas (Reimpressão Disponível)
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
                <th class="py-2.5 px-3 text-right text-indigo-700">Venda Total (+70%)</th>
              </tr>
            </thead>
            <tbody id="recentEntriesBody" class="divide-y divide-slate-100">
              <tr>
                <td colspan="11" class="text-center py-4 text-slate-400">Nenhum lançamento emitido na sessão ainda.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </div>

    <!-- ==================== ÁREA EXCLUSIVA DE IMPRESSÃO DA OC ==================== -->
    <div id="printArea" class="hidden">
      <div class="max-w-4xl mx-auto border-2 border-slate-800 p-8 rounded-lg bg-white text-slate-900 font-sans">
        <div class="flex justify-between items-start border-b-2 border-slate-800 pb-4 mb-6">
          <div>
            <h1 class="text-2xl font-black uppercase tracking-tight">ORDEM DE COMPRA</h1>
            <p class="text-xs text-slate-600">Controle Operacional de Peças, Suprimentos e Precificação</p>
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
              <th class="py-2 px-3 border border-slate-300">Item</th>
              <th class="py-2 px-3 border border-slate-300">Cód. Peça</th>
              <th class="py-2 px-3 border border-slate-300">Descrição do Produto</th>
              <th class="py-2 px-3 border border-slate-300 text-center">Qt Solicitada</th>
              <th class="py-2 px-3 border border-slate-300 text-center">Qt Atendida</th>
              <th class="py-2 px-3 border border-slate-300 text-right">Custo Unit.</th>
              <th class="py-2 px-3 border border-slate-300 text-right">Venda Unit. (+70%)</th>
              <th class="py-2 px-3 border border-slate-300 text-right">Custo Total</th>
              <th class="py-2 px-3 border border-slate-300 text-right">Venda Total</th>
            </tr>
          </thead>
          <tbody id="printOCTableBody"></tbody>
          <tfoot class="bg-slate-100 font-bold border-t-2 border-slate-800">
            <tr>
              <td colspan="3" class="py-2.5 px-3 text-right uppercase">Totais Gerais do Pedido:</td>
              <td id="printOCTotalQt" class="py-2.5 px-3 text-center">0 un</td>
              <td id="printOCTotalAtendida" class="py-2.5 px-3 text-center">0 un</td>
              <td colspan="2"></td>
              <td id="printOCTotalValor" class="py-2.5 px-3 text-right text-sm font-black text-amber-800">R$ 0,00</td>
              <td id="printOCTotalVenda" class="py-2.5 px-3 text-right text-sm font-black text-indigo-800">R$ 0,00</td>
            </tr>
          </tfoot>
        </table>

        <div class="grid grid-cols-2 gap-8 mt-14 pt-8 border-t border-slate-300 text-center text-xs">
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

    document.getElementById('formData').value = new Date().toISOString().split('T')[0];

    // ==============================================================
    // BASE DE DADOS CARREGADA DIRETO DA PLANILHA DO GOOGLE
    // ==============================================================
    const catalogoPecas = {catalogo_json};

    // 1. Popula Pré-lista do CÓDIGO DA PEÇA (Coluna A)
    const dlCodigos = document.getElementById('listaCodigosPecas');
    dlCodigos.innerHTML = '';
    const codigosUnicos = [...new Set(catalogoPecas.map(p => p.codigo).filter(Boolean))].sort();
    codigosUnicos.forEach(cod => {{
      const opt = document.createElement('option');
      opt.value = cod;
      dlCodigos.appendChild(opt);
    }});

    // 2. Popula Pré-lista de DESCRIÇÃO DA PEÇA / PRODUTO (Coluna B)
    const dlDescricoes = document.getElementById('listaDescricoesPecas');
    dlDescricoes.innerHTML = '';
    const descricoesUnicas = [...new Set(catalogoPecas.map(p => p.descricao).filter(Boolean))].sort();
    descricoesUnicas.forEach(desc => {{
      const opt = document.createElement('option');
      opt.value = desc;
      dlDescricoes.appendChild(opt);
    }});

    // 3. Popula Pré-lista de FORNECEDORES (Coluna F)
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

    // ==============================================================
    // CÁLCULO DE VALOR DE VENDA: 70% SOBRE O VALOR DE CUSTO
    // ==============================================================
    function calcItemPreview() {{
      const qt = parseInt(document.getElementById('itemQt').value) || 0;
      let qtAprovada = parseInt(document.getElementById('itemQtAprovada').value);
      if (isNaN(qtAprovada)) qtAprovada = qt;
      if (qtAprovada > qt) {{
        qtAprovada = qt;
        document.getElementById('itemQtAprovada').value = qt;
      }}
      document.getElementById('itemQtNaoAprovada').value = Math.max(0, qt - qtAprovada);

      const custoUnit = parseFloat(document.getElementById('itemCustoUnit').value) || 0;
      // Preço de venda com margem de 70%
      const vendaUnit = custoUnit * 1.70;
      const subtotalCusto = qtAprovada * custoUnit;
      const subtotalVenda = qtAprovada * vendaUnit;

      document.getElementById('itemVendaUnitPreview').value = formatCurrency(vendaUnit);
      document.getElementById('itemCustoSubtotalPreview').value = formatCurrency(subtotalCusto);
      document.getElementById('itemVendaSubtotalPreview').value = formatCurrency(subtotalVenda);
    }}

    // ==============================================================
    // ADIÇÃO DE MÚLTIPLAS PEÇAS COM FORNECEDOR ÚNICO
    // ==============================================================
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

      // Limpa os campos da peça adicionada
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
            <td colspan="10" class="text-center py-6 text-slate-400">Nenhuma peça adicionada ainda. Preencha os campos acima e clique em "Adicionar Peça à Ordem".</td>
          </tr>
        `;
        document.getElementById('footTotalQt').innerText = '0 un';
        document.getElementById('footTotalAtendida').innerText = '0 un';
        document.getElementById('footTotalValor').innerText = 'R$ 0,00';
        document.getElementById('footTotalVenda').innerText = 'R$ 0,00';
        return;
      }}

      let somaQt = 0;
      let somaAtendida = 0;
      let somaValor = 0;
      let somaVenda = 0;

      tbody.innerHTML = itensDaOrdemAtual.map((item, idx) => {{
        somaQt += item.qt;
        somaAtendida += item.qtAprovada;
        somaValor += item.custoTotal;
        somaVenda += item.vendaTotal;

        return `
          <tr class="hover:bg-slate-50 transition">
            <td class="py-2.5 px-3 font-mono font-bold text-blue-700">${{item.codigoPeca}}</td>
            <td class="py-2.5 px-3 font-semibold text-slate-800">${{item.peca}}</td>
            <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] bg-slate-100 text-slate-700">${{item.categoria}}</span></td>
            <td class="py-2.5 px-3 text-center font-bold">${{item.qt}} un</td>
            <td class="py-2.5 px-3 text-center font-bold text-emerald-600">${{item.qtAprovada}} un</td>
            <td class="py-2.5 px-3 text-right">${{formatCurrency(item.custoUnit)}}</td>
            <td class="py-2.5 px-3 text-right font-semibold text-emerald-700">${{formatCurrency(item.vendaUnit)}}</td>
            <td class="py-2.5 px-3 text-right font-bold text-amber-600">${{formatCurrency(item.custoTotal)}}</td>
            <td class="py-2.5 px-3 text-right font-bold text-indigo-700">${{formatCurrency(item.vendaTotal)}}</td>
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
      document.getElementById('footTotalVenda').innerText = formatCurrency(somaVenda);
      lucide.createIcons();
    }}

    function limparOCAtual() {{
      itensDaOrdemAtual = [];
      renderizarTabelaItensOC();
    }}

    // ==============================================================
    // BASE DE DADOS DE ORDENS DE COMPRA
    // ==============================================================
    let rawOrdersData = [
      {{ oc: 'OC-2025-0001', ano: '2025', mes: 'Agosto', data: '05/08/2025', solicitante: 'WILLIAN NEVES', codigoPeca: 'PEC-00101', peca: 'DISCO ROTAÇÃO DO MISTURADOR', categoria: 'Multi Bebidas', fornecedor: 'EVOCA', qt: 15, qtAprovada: 15, qtNaoAprovada: 0, custoUnit: 4.39, vendaUnit: 7.46, custoTotal: 65.85, vendaTotal: 111.90 }},
      {{ oc: 'OC-2025-0002', ano: '2025', mes: 'Agosto', data: '08/08/2025', solicitante: 'FLAVIO', codigoPeca: 'PEC-00102', peca: 'BICO DE SAIDA DO SOLUVEL PHEDRA', categoria: 'Multi Bebidas', fornecedor: 'EVOCA', qt: 12, qtAprovada: 12, qtNaoAprovada: 0, custoUnit: 8.52, vendaUnit: 14.48, custoTotal: 102.24, vendaTotal: 173.76 }},
      {{ oc: 'OC-2026-0001', ano: '2026', mes: 'Março', data: '02/03/2026', solicitante: 'DAVI', codigoPeca: '2290', peca: 'ABERTURA PLASTICA CENTRAL SAIDA', categoria: '8 PEÇAS', fornecedor: 'ANDRE MEKAR', qt: 5, qtAprovada: 5, qtNaoAprovada: 0, custoUnit: 45.00, vendaUnit: 76.50, custoTotal: 225.00, vendaTotal: 382.50 }}
    ];

    let todasOCsEmitidas = {{}}; // Armazenamento completo por número de OC para permitir reimpressão a qualquer momento

    // Preenche as OCs iniciais
    rawOrdersData.forEach(item => {{
      if (!todasOCsEmitidas[item.oc]) {{
        todasOCsEmitidas[item.oc] = {{
          oc: item.oc,
          ano: item.ano,
          mes: item.mes,
          data: item.data,
          solicitante: item.solicitante,
          fornecedor: item.fornecedor,
          itens: []
        }};
      }}
      todasOCsEmitidas[item.oc].itens.push(item);
    }});

    let ultimaOCSalva = null;

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

    // ==============================================================
    // SALVAR PEDIDO + LIMPAR SOLICITANTE E FORNECEDOR
    // ==============================================================
    function handleFinalSubmit(e) {{
      e.preventDefault();

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

      const oc = document.getElementById('formNumeroOC').value;
      const ano = document.getElementById('formAno').value;
      const mes = document.getElementById('formMes').value;
      const dataStr = document.getElementById('formData').value;
      const solicitante = document.getElementById('formSolicitante').value.toUpperCase().trim();

      // Guarda os dados completos da OC para reimpressão
      const dadosOCSalva = {{
        oc,
        ano,
        mes,
        data: dataStr,
        solicitante,
        fornecedor: fornecedorPrincipal,
        itens: JSON.parse(JSON.stringify(itensDaOrdemAtual))
      }};

      todasOCsEmitidas[oc] = dadosOCSalva;
      ultimaOCSalva = dadosOCSalva;

      // Salva os itens na base de dados
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

      const totalPecas = itensDaOrdemAtual.length;

      // 1. Limpa os itens da ordem atual
      limparOCAtual();

      // 2. LIMPA OS CAMPOS SOLICITANTE E FORNECEDOR CONFORME SOLICITADO
      document.getElementById('formSolicitante').value = '';
      document.getElementById('formFornecedor').value = '';

      // 3. Atualiza numeração da OC, tabelas e dashboard
      atualizarProximoNumeroOC();
      populateDropdowns();
      updateDashboard();
      renderizarTabelaRecentes();

      // Mostra o card de sucesso na mesma página
      const alertBox = document.getElementById('alertSuccess');
      document.getElementById('alertSuccessTitle').innerText = `✅ Ordem de Compra ${{oc}} salva com sucesso (${{totalPecas}} peças)!`;
      document.getElementById('alertSuccessSub').innerText = `Fornecedor: ${{fornecedorPrincipal}} · Solicitante: ${{solicitante}} · Campos limpos para o próximo lançamento.`;
      alertBox.classList.remove('hidden');
      alertBox.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}

    // ==============================================================
    // RENDERIZAÇÃO DA TABELA RECENTE COM BOTÃO DE IMPRIMIR NA FRENTE
    // ==============================================================
    function renderizarTabelaRecentes() {{
      const recentBody = document.getElementById('recentEntriesBody');
      if (rawOrdersData.length === 0) {{
        recentBody.innerHTML = '<tr><td colspan="11" class="text-center py-4 text-slate-400">Nenhum lançamento emitido na sessão ainda.</td></tr>';
        return;
      }}

      recentBody.innerHTML = rawOrdersData.slice(0, 15).map(item => `
        <tr class="hover:bg-slate-50 transition font-medium">
          <td class="py-2 px-3">
            <button type="button" onclick="imprimirOCEspecifica('${{item.oc}}')" title="Imprimir Ordem de Compra ${{item.oc}}" class="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-bold border border-blue-200 transition">
              <i data-lucide="printer" class="w-3.5 h-3.5"></i>
              Imprimir
            </button>
          </td>
          <td class="py-2.5 px-3 font-mono font-bold text-blue-700">${{item.oc}}</td>
          <td class="py-2.5 px-3">${{item.data}}</td>
          <td class="py-2.5 px-3 font-semibold text-slate-800">${{item.solicitante}}</td>
          <td class="py-2.5 px-3 font-bold text-blue-900">${{item.fornecedor}}</td>
          <td class="py-2.5 px-3 font-mono text-slate-600">${{item.codigoPeca}}</td>
          <td class="py-2.5 px-3 font-semibold text-slate-800">${{item.peca}}</td>
          <td class="py-2.5 px-3 text-center font-bold">${{item.qt}} un</td>
          <td class="py-2.5 px-3 text-center font-bold text-emerald-600">${{item.qtAprovada}} un</td>
          <td class="py-2.5 px-3 text-right font-bold text-amber-600">${{formatCurrency(item.custoTotal)}}</td>
          <td class="py-2.5 px-3 text-right font-bold text-indigo-700">${{formatCurrency(item.vendaTotal || (item.custoTotal * 1.70))}}</td>
        </tr>
      `).join('');
      lucide.createIcons();
    }}
    renderizarTabelaRecentes();

    // ==============================================================
    // FUNÇÕES DE IMPRESSÃO
    // ==============================================================
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
        // Constrói com base nos itens cadastrados na base
        const itens = rawOrdersData.filter(i => i.oc === numeroOC);
        if (itens.length > 0) {{
          executarImpressao({{
            oc: numeroOC,
            ano: itens[0].ano,
            mes: itens[0].mes,
            data: itens[0].data,
            solicitante: itens[0].solicitante,
            fornecedor: itens[0].fornecedor,
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
      document.getElementById('printOCData').innerText = `Data: ${{dadosOC.data}} (${{dadosOC.mes}}/${{dadosOC.ano}})`;
      document.getElementById('printOCFornecedor').innerText = dadosOC.fornecedor;
      document.getElementById('printOCSolicitante').innerText = dadosOC.solicitante;

      const tbody = document.getElementById('printOCTableBody');
      let somaQt = 0;
      let somaAtendida = 0;
      let somaCusto = 0;
      let somaVenda = 0;

      tbody.innerHTML = dadosOC.itens.map((item, idx) => {{
        somaQt += item.qt;
        somaAtendida += item.qtAprovada;
        somaCusto += item.custoTotal;
        const vTot = item.vendaTotal || (item.custoTotal * 1.70);
        const vUnit = item.vendaUnit || (item.custoUnit * 1.70);
        somaVenda += vTot;

        return `
          <tr class="border-b border-slate-200">
            <td class="py-2 px-3 border border-slate-300 font-bold">${{idx + 1}}</td>
            <td class="py-2 px-3 border border-slate-300 font-mono font-bold">${{item.codigoPeca}}</td>
            <td class="py-2 px-3 border border-slate-300">${{item.peca}}</td>
            <td class="py-2 px-3 border border-slate-300 text-center">${{item.qt}} un</td>
            <td class="py-2 px-3 border border-slate-300 text-center font-bold">${{item.qtAprovada}} un</td>
            <td class="py-2 px-3 border border-slate-300 text-right">${{formatCurrency(item.custoUnit)}}</td>
            <td class="py-2 px-3 border border-slate-300 text-right font-semibold text-emerald-800">${{formatCurrency(vUnit)}}</td>
            <td class="py-2 px-3 border border-slate-300 text-right font-bold text-amber-900">${{formatCurrency(item.custoTotal)}}</td>
            <td class="py-2 px-3 border border-slate-300 text-right font-bold text-indigo-900">${{formatCurrency(vTot)}}</td>
          </tr>
        `;
      }}).join('');

      document.getElementById('printOCTotalQt').innerText = `${{somaQt}} un`;
      document.getElementById('printOCTotalAtendida').innerText = `${{somaAtendida}} un`;
      document.getElementById('printOCTotalValor').innerText = formatCurrency(somaCusto);
      document.getElementById('printOCTotalVenda').innerText = formatCurrency(somaVenda);

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

    // Filtros e Dashboard
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

      const years = [...new Set(rawOrdersData.map(d => d.ano))].sort();
      const months = [...new Set(rawOrdersData.map(d => d.mes))];
      const categories = [...new Set(rawOrdersData.map(d => d.categoria))].sort();
      const requesters = [...new Set(rawOrdersData.map(d => d.solicitante))].sort();

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

      const totalCusto = filtered.reduce((acc, cur) => acc + cur.custoTotal, 0);
      const totalItens = filtered.reduce((acc, cur) => acc + cur.qt, 0);
      const totalAtendidas = filtered.reduce((acc, cur) => acc + cur.qtAprovada, 0);
      const totalNaoAtendidas = filtered.reduce((acc, cur) => acc + cur.qtNaoAprovada, 0);
      
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

components.html(html_code, height=2500, scrolling=True)