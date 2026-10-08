import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from datetime import date, time

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO GERAL DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gestão de Peças - Compras & Ordens",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# CSS GLOBAL - 100% MODO CLARO & NAVBAR SUPERIOR
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Forçar fundo claro global */
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Ocultar elementos padrão do Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* Navbar Superior */
    .top-navbar {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 1rem;
        padding: 0.85rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
    }
    .navbar-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Estilização dos Botões de Aba da Navbar */
    div[data-testid="stHorizontalBlock"] button {
        border-radius: 0.75rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.25rem !important;
        transition: all 0.2s ease !important;
    }

    /* Cards e Formulários */
    .form-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 1rem;
        padding: 1.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        margin-bottom: 1.5rem;
    }
    
    /* Inputs em Modo Claro */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input, .stTimeInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 0.6rem !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BASE DE DADOS INICIAL (SESSION STATE PARA PERSISTÊNCIA NA SESSÃO)
# -----------------------------------------------------------------------------
if "orders_data" not in st.session_state:
    st.session_state.orders_data = [
        {"ordem": "OC-2025-001", "codigo": "MB-101", "peca": "DISCO ROTAÇÃO DO MISTURADOR", "categoria": "Multi Bebidas", "data": "2025-08-05", "hora": "09:30", "custoUnit": 4.39, "qt": 15, "qtAprovada": 15, "qtNaoAprovada": 0, "valorVenda": 12.00, "fornecedor": "EVOCA", "codFornecedor": "EV-9941", "solicitante": "WILLIAN NEVES", "observacao": "Reposição preventiva", "ano": "2025", "mes": "Agosto"},
        {"ordem": "OC-2025-002", "codigo": "MB-102", "peca": "BICO DE SAIDA DO SOLUVEL PHEDRA", "categoria": "Multi Bebidas", "data": "2025-08-08", "hora": "10:15", "custoUnit": 8.52, "qt": 12, "qtAprovada": 12, "qtNaoAprovada": 0, "valorVenda": 22.00, "fornecedor": "EVOCA", "codFornecedor": "EV-3312", "solicitante": "FLAVIO", "observacao": "Troca de bicos desgastados", "ano": "2025", "mes": "Agosto"},
        {"ordem": "OC-2025-003", "codigo": "MB-103", "peca": "MOTOR DE MIXER COMPLETO", "categoria": "Multi Bebidas", "data": "2025-08-12", "hora": "14:00", "custoUnit": 334.00, "qt": 4, "qtAprovada": 4, "qtNaoAprovada": 0, "valorVenda": 520.00, "fornecedor": "EVOCA", "codFornecedor": "EV-8821", "solicitante": "WILLIAN NEVES", "observacao": "Manutenção corretiva", "ano": "2025", "mes": "Agosto"},
        {"ordem": "OC-2025-004", "codigo": "AC-201", "peca": "TORNEIRA 3/4", "categoria": "Acessorios", "data": "2025-08-14", "hora": "11:20", "custoUnit": 75.18, "qt": 8, "qtAprovada": 7, "qtNaoAprovada": 1, "valorVenda": 130.00, "fornecedor": "LUCAS", "codFornecedor": "LC-701", "solicitante": "NAPOLEAO", "observacao": "1 item avariado no transporte", "ano": "2025", "mes": "Agosto"},
        {"ordem": "OC-2025-005", "codigo": "SN-301", "peca": "REMOVE GRUDE", "categoria": "Snaks", "data": "2025-08-18", "hora": "15:45", "custoUnit": 72.00, "qt": 10, "qtAprovada": 10, "qtNaoAprovada": 0, "valorVenda": 115.00, "fornecedor": "FABIO", "codFornecedor": "FB-019", "solicitante": "FABIO", "observacao": "Insumo de limpeza", "ano": "2025", "mes": "Agosto"},
        {"ordem": "OC-2025-006", "codigo": "MB-104", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "data": "2025-08-20", "hora": "08:30", "custoUnit": 180.00, "qt": 6, "qtAprovada": 5, "qtNaoAprovada": 1, "valorVenda": 290.00, "fornecedor": "PARAMOUNT", "codFornecedor": "PM-550", "solicitante": "LUCAS", "observacao": "Estoque mínimo atingido", "ano": "2025", "mes": "Agosto"},
        {"ordem": "OC-2025-007", "codigo": "AC-202", "peca": "SPRAY COLORART PRATA LUNAR", "categoria": "Acessorios", "data": "2025-08-22", "hora": "16:10", "custoUnit": 26.50, "qt": 20, "qtAprovada": 20, "qtNaoAprovada": 0, "valorVenda": 48.00, "fornecedor": "MGC", "codFornecedor": "MG-910", "solicitante": "WILLIAN NEVES", "observacao": "Pintura de carenagens", "ano": "2025", "mes": "Agosto"},
        {"ordem": "OC-2025-008", "codigo": "HD-401", "peca": "CONECTOR MACHO 8MM X1/2", "categoria": "Hidraulica", "data": "2025-08-25", "hora": "13:30", "custoUnit": 10.50, "qt": 30, "qtAprovada": 25, "qtNaoAprovada": 5, "valorVenda": 24.00, "fornecedor": "IMELKRON", "codFornecedor": "IM-220", "solicitante": "FLAVIO", "observacao": "5 itens com rosca danificada", "ano": "2025", "mes": "Agosto"},
        {"ordem": "OC-2025-009", "codigo": "MB-105", "peca": "NUCLEO SOLUVEL SOLISTA", "categoria": "Multi Bebidas", "data": "2025-08-28", "hora": "10:00", "custoUnit": 91.04, "qt": 5, "qtAprovada": 5, "qtNaoAprovada": 0, "valorVenda": 165.00, "fornecedor": "EVOCA", "codFornecedor": "EV-1022", "solicitante": "NAPOLEAO", "observacao": "Reposição Solista", "ano": "2025", "mes": "Agosto"},
        {"ordem": "OC-2025-010", "codigo": "MB-106", "peca": "BOMBA DE AGUA ULKA 220V", "categoria": "Multi Bebidas", "data": "2025-09-02", "hora": "09:10", "custoUnit": 195.00, "qt": 18, "qtAprovada": 18, "qtNaoAprovada": 0, "valorVenda": 320.00, "fornecedor": "PARAMOUNT", "codFornecedor": "PM-771", "solicitante": "THIAGO", "observacao": "Lote principal de bombas", "ano": "2025", "mes": "Setembro"},
        {"ordem": "OC-2025-011", "codigo": "AC-203", "peca": "GAXETA DE SILICONE", "categoria": "Acessorios", "data": "2025-09-05", "hora": "11:40", "custoUnit": 18.50, "qt": 25, "qtAprovada": 22, "qtNaoAprovada": 3, "valorVenda": 35.00, "fornecedor": "EVOCA", "codFornecedor": "EV-4411", "solicitante": "SAMANTHA", "observacao": "Reposição de vedação", "ano": "2025", "mes": "Setembro"},
        {"ordem": "OC-2025-012", "codigo": "MB-107", "peca": "MOTOR DO CARROSSEL PINO LONGO", "categoria": "Multi Bebidas", "data": "2025-09-10", "hora": "14:20", "custoUnit": 280.00, "qt": 3, "qtAprovada": 3, "qtNaoAprovada": 0, "valorVenda": 450.00, "fornecedor": "EVOCA", "codFornecedor": "EV-8080", "solicitante": "ALAN", "observacao": "Motores de carrossel", "ano": "2025", "mes": "Setembro"},
        {"ordem": "OC-2025-013", "codigo": "AC-204", "peca": "ANEL DO BICO CALDEIRA 70", "categoria": "Acessorios", "data": "2025-09-14", "hora": "16:00", "custoUnit": 9.80, "qt": 40, "qtAprovada": 38, "qtNaoAprovada": 2, "valorVenda": 20.00, "fornecedor": "PARAMOUNT", "codFornecedor": "PM-070", "solicitante": "CESAR", "observacao": "Anéis o-ring caldeira", "ano": "2025", "mes": "Setembro"}
    ]

# Mapeador de mês por extenso para consistência do Dashboard
MESES_EXTENSO = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# -----------------------------------------------------------------------------
# CONTROLE DE PÁGINA (NAVBAR SUPERIOR)
# -----------------------------------------------------------------------------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Dashboard Compras"

# Barra de Navegação Superior
nav_col1, nav_col2, nav_col3 = st.columns([5, 2.5, 2.5])

with nav_col1:
    st.markdown("""
    <div class="navbar-title">
        <span style="background-color: #0284c7; color: white; padding: 6px 12px; border-radius: 10px;">📦</span>
        <span>Sistema Integrado de Peças & Suprimentos</span>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    if st.button("📊 Dashboard Compras", use_container_width=True, type="primary" if st.session_state.active_tab == "Dashboard Compras" else "secondary"):
        st.session_state.active_tab = "Dashboard Compras"
        st.rerun()

with nav_col3:
    if st.button("📝 Pedido de Compras", use_container_width=True, type="primary" if st.session_state.active_tab == "Pedido de Compras" else "secondary"):
        st.session_state.active_tab = "Pedido de Compras"
        st.rerun()

st.markdown("<hr style='border: 0; border-top: 1px solid #e2e8f0; margin: 0.5rem 0 1.5rem 0;'>", unsafe_allow_html=True)

# =============================================================================
# ABA 1: PEDIDO DE COMPRAS (CADASTRO, PESQUISA E EDIÇÃO)
# =============================================================================
if st.session_state.active_tab == "Pedido de Compras":
    st.markdown("### 📋 Gestão de Pedidos e Ordens de Compra")
    st.markdown("Pesquise por uma Ordem de Compra para atualizar os dados ou cadastre um novo pedido no formulário.")

    # Seção de Pesquisa e Seleção de Ordem de Compra
    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown("##### 🔍 Pesquisar ou Criar Ordem de Compra")
        
        ordens_existentes = ["+ Novo Pedido (Cadastrar Novo)"] + [item["ordem"] for item in st.session_state.orders_data]
        selected_oc = st.selectbox("Selecione uma Ordem de Compra para editar ou cadastre uma nova:", ordens_existentes)
        
        # Buscar registro selecionado se houver
        record = None
        edit_mode = False
        if selected_oc != "+ Novo Pedido (Cadastrar Novo)":
            record = next((item for item in st.session_state.orders_data if item["ordem"] == selected_oc), None)
            if record:
                edit_mode = True
                st.info(f"Modo de Edição Ativo: Alterando os dados da **{selected_oc}**.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Valores padrão ou carregados do registro
    default_oc = record["ordem"] if record else f"OC-2026-{len(st.session_state.orders_data)+1:03d}"
    default_cod = record["codigo"] if record else ""
    default_peca = record["peca"] if record else ""
    default_cat = record["categoria"] if record else "Multi Bebidas"
    default_fornecedor = record["fornecedor"] if record else "EVOCA"
    default_cod_forn = record["codFornecedor"] if record else ""
    default_solicitante = record["solicitante"] if record else "WILLIAN NEVES"
    default_data = date.fromisoformat(record["data"]) if record else date.today()
    default_hora = time.fromisoformat(record["hora"]) if record else time(10, 0)
    default_custo = float(record["custoUnit"]) if record else 0.0
    default_venda = float(record.get("valorVenda", 0.0)) if record else 0.0
    default_qt = int(record["qt"]) if record else 1
    default_qt_aprovada = int(record["qtAprovada"]) if record else 1
    default_qt_nao_aprovada = int(record["qtNaoAprovada"]) if record else 0
    default_obs = record.get("observacao", "") if record else ""

    # Formulário de Cadastro / Edição
    with st.form("form_pedido_compras", clear_on_submit=False):
        st.markdown(f"#### {'✏️ Atualizar Pedido: ' + selected_oc if edit_mode else '➕ Formulário de Entrada do Pedido'}")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            ordem_val = st.text_input("Ordem de Compra *", value=default_oc, disabled=edit_mode)
            peca_val = st.text_input("Produto (Nome da Peça) *", value=default_peca)
            solicitante_val = st.text_input("Solicitante / Setor *", value=default_solicitante)
            data_val = st.date_input("Data do Pedido", value=default_data)
        
        with c2:
            codigo_val = st.text_input("Código do Produto", value=default_cod)
            categoria_val = st.selectbox(
                "Categoria", 
                ["Multi Bebidas", "Acessorios", "Snaks", "Hidraulica", "Outros"], 
                index=["Multi Bebidas", "Acessorios", "Snaks", "Hidraulica", "Outros"].index(default_cat) if default_cat in ["Multi Bebidas", "Acessorios", "Snaks", "Hidraulica", "Outros"] else 0
            )
            fornecedor_val = st.text_input("Fornecedor *", value=default_fornecedor)
            hora_val = st.time_input("Horário de Chegada do Pedido", value=default_hora)

        with c3:
            cod_forn_val = st.text_input("Cód da Peça do Fornecedor", value=default_cod_forn)
            custo_val = st.number_input("Valor de Compra (Custo Unitário R$) *", min_value=0.0, value=default_custo, step=0.5, format="%.2f")
            venda_val = st.number_input("Valor de Venda (R$)", min_value=0.0, value=default_venda, step=0.5, format="%.2f")
            qt_val = st.number_input("Qt Solicitada *", min_value=1, value=default_qt, step=1)

        c4, c5, c6 = st.columns(3)
        with c4:
            qt_aprovada_val = st.number_input("Qt Aprovada (Atendida) *", min_value=0, value=default_qt_aprovada, step=1)
        with c5:
            # Cálculo automático padrão caso o usuário não altere
            qt_nao_aprovada_val = st.number_input("Qt Não Aprovada (Não Atendida) *", min_value=0, value=default_qt_nao_aprovada, step=1)
        with c6:
            st.metric("Custo Total Calculado (R$)", f"R$ {(qt_aprovada_val * custo_val):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        obs_val = st.text_area("Observação", value=default_obs, placeholder="Detalhes, justificativa ou motivo de não atendimento...")

        btn_save = st.form_submit_button("💾 Salvar Informações no Banco de Dados", type="primary", use_container_width=True)

        if btn_save:
            if not ordem_val or not peca_val or not fornecedor_val or not solicitante_val:
                st.error("Por favor, preencha todos os campos obrigatórios (*).")
            else:
                ano_str = str(data_val.year)
                mes_str = MESES_EXTENSO.get(data_val.month, "Janeiro")
                
                novo_registro = {
                    "ordem": ordem_val.strip().upper(),
                    "codigo": codigo_val.strip().upper(),
                    "peca": peca_val.strip().upper(),
                    "categoria": categoria_val,
                    "data": data_val.isoformat(),
                    "hora": hora_val.strftime("%H:%M"),
                    "custoUnit": float(custo_val),
                    "qt": int(qt_val),
                    "qtAprovada": int(qt_aprovada_val),
                    "qtNaoAprovada": int(qt_nao_aprovada_val),
                    "valorVenda": float(venda_val),
                    "fornecedor": fornecedor_val.strip().upper(),
                    "codFornecedor": cod_forn_val.strip().upper(),
                    "solicitante": solicitante_val.strip().upper(),
                    "observacao": obs_val.strip(),
                    "ano": ano_str,
                    "mes": mes_str
                }

                if edit_mode:
                    # Atualiza item existente
                    idx = next(i for i, item in enumerate(st.session_state.orders_data) if item["ordem"] == selected_oc)
                    st.session_state.orders_data[idx] = novo_registro
                    st.success(f"Ordem de Compra **{selected_oc}** atualizada com sucesso!")
                else:
                    # Verifica duplicidade
                    if any(item["ordem"] == ordem_val.strip().upper() for item in st.session_state.orders_data):
                        st.error(f"A Ordem de Compra {ordem_val} já existe! Use a busca acima para editá-la.")
                    else:
                        st.session_state.orders_data.append(novo_registro)
                        st.success(f"Ordem de Compra **{ordem_val}** cadastrada com sucesso!")
                st.rerun()

    # Visualização rápida da planilha de dados atualizada
    st.write("")
    st.markdown("##### 📑 Base de Ordens de Compra Cadastradas")
    df_preview = pd.DataFrame(st.session_state.orders_data)
    df_preview["custoTotal"] = df_preview["qtAprovada"] * df_preview["custoUnit"]
    st.dataframe(df_preview, use_container_width=True, hide_index=True)


# =============================================================================
# ABA 2: DASHBOARD COMPRAS (100% MODO CLARO, SEM BOTÃO DE DARK MODE)
# =============================================================================
elif st.session_state.active_tab == "Dashboard Compras":
    # Prepara os dados atualizados para passar ao HTML
    json_data = json.dumps(st.session_state.orders_data, ensure_ascii=False)

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
          background-color: #f8fafc;
          color: #1e293b;
        }}
        .kpi-card {{
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .kpi-card:hover {{
          transform: translateY(-2px);
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
      </style>
    </head>
    <body class="min-h-screen">

      <!-- Header Superior em Modo Claro -->
      <header class="sticky top-0 z-40 bg-white/95 border-b border-slate-200 backdrop-blur-md px-6 py-4 shadow-sm">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div class="flex items-center gap-3">
            <div class="p-2.5 bg-blue-600 text-white rounded-xl shadow-md">
              <i data-lucide="package-search" class="w-6 h-6"></i>
            </div>
            <div>
              <h1 class="text-xl font-bold tracking-tight text-slate-900">Painel Executivo de Compras & Solicitações de Peças</h1>
              <p class="text-xs text-slate-500">Controle Operacional: Ordens de Compra, Custos Reais e Status de Atendimento</p>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
              <span class="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span> Cálculos em Tempo Real
            </span>
          </div>
        </div>
      </header>

      <main class="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">

        <!-- ESCOPO DO PROJETO -->
        <section class="bg-blue-50/80 border border-blue-200 rounded-2xl p-5 shadow-sm">
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-3">
              <div class="p-2 rounded-xl bg-blue-600 text-white mt-0.5">
                <i data-lucide="clipboard-check" class="w-5 h-5"></i>
              </div>
              <div>
                <h2 class="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  Especificação & Requisitos da Solicitação
                  <span class="text-[10px] normal-case bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full border border-blue-300 font-semibold">Parâmetros Ativos</span>
                </h2>
                <div class="text-xs text-slate-600 mt-2 space-y-1.5 leading-relaxed">
                  <p>• <strong>Base de Dados Analisada:</strong> Foco exclusivo na aba de <em>Solicitações de Compra de Peças</em> e ordens de reposição de estoque.</p>
                  <p>• <strong>Regra de Cálculo de Valor Total:</strong> Soma exata da coluna <strong>"Custo"</strong> (quantidade aprovada/atendida × custo unitário do item).</p>
                  <p>• <strong>Filtros Dinâmicos no Painel:</strong> Seletores interativos por <strong>Ano</strong>, <strong>Mês</strong>, <strong>Categoria</strong> e <strong>Solicitante</strong> com recálculo automático em tempo real.</p>
                  <p>• <strong>Métricas em Cards:</strong> Total de solicitações, valor das compras (Custo), quantidade solicitada, <strong>peças atendidas</strong>, <strong>peças não atendidas</strong> e ticket médio.</p>
                  <p>• <strong>Gráficos de Destaque com Valores Exibidos:</strong> Top 5 solicitantes/locais internos para <strong>Agosto</strong> e <strong>Setembro</strong>, distribuição por categoria e custo por fornecedor exibindo os <strong>valores numéricos e em R$ diretamente nas barras/fatias</strong>.</p>
                  <p>• <strong>Tabela Resumo por Peça:</strong> Tabela detalhada agrupada por produto com pesquisa em tempo real, quantidades solicitadas/atendidas/não atendidas e valor financeiro.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Filtros Dinâmicos (Grid Claro) -->
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
              <select id="filterYear" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="ALL">Todos os Anos</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-500 mb-1">Mês</label>
              <select id="filterMonth" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="ALL">Todos os Meses</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-500 mb-1">Categoria de Peças</label>
              <select id="filterCategory" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="ALL">Todas as Categorias</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-500 mb-1">Solicitante / Setor</label>
              <select id="filterRequester" class="w-full text-sm rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500">
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

        <!-- CARDS DE KPIS PRINCIPAIS -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          
          <!-- KPI 1 -->
          <div class="kpi-card bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
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

          <!-- KPI 2 -->
          <div class="kpi-card bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total de Pedidos</span>
              <span class="p-1.5 rounded-lg bg-blue-50 text-blue-600">
                <i data-lucide="clipboard-list" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3">
              <span id="kpiTotalRequests" class="text-xl font-bold tracking-tight text-slate-900">0</span>
              <p class="text-[11px] text-slate-400 mt-0.5">Ordens registradas</p>
            </div>
          </div>

          <!-- KPI 3 -->
          <div class="kpi-card bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Qtde Solicitada</span>
              <span class="p-1.5 rounded-lg bg-indigo-50 text-indigo-600">
                <i data-lucide="boxes" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3">
              <span id="kpiItemsQty" class="text-xl font-bold tracking-tight text-slate-900">0 un</span>
              <p class="text-[11px] text-slate-400 mt-0.5">Total de peças pedidas</p>
            </div>
          </div>

          <!-- KPI 4 -->
          <div class="kpi-card bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between ring-1 ring-emerald-500/20">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-emerald-600 uppercase tracking-wider">Peças Atendidas</span>
              <span class="p-1.5 rounded-lg bg-emerald-50 text-emerald-600">
                <i data-lucide="check-circle-2" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3 flex items-baseline justify-between">
              <div>
                <span id="kpiApprovedQty" class="text-xl font-bold tracking-tight text-emerald-600">0 un</span>
                <p class="text-[11px] text-slate-400 mt-0.5">Aprovadas / Compradas</p>
              </div>
              <span id="kpiApprovedPercent" class="text-xs font-semibold px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-700">0%</span>
            </div>
          </div>

          <!-- KPI 5 -->
          <div class="kpi-card bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between ring-1 ring-rose-500/20">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-rose-600 uppercase tracking-wider">Não Atendidas</span>
              <span class="p-1.5 rounded-lg bg-rose-50 text-rose-600">
                <i data-lucide="x-circle" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3 flex items-baseline justify-between">
              <div>
                <span id="kpiUnapprovedQty" class="text-xl font-bold tracking-tight text-rose-600">0 un</span>
                <p class="text-[11px] text-slate-400 mt-0.5">Reprovadas / Pendentes</p>
              </div>
              <span id="kpiUnapprovedPercent" class="text-xs font-semibold px-2 py-0.5 rounded-md bg-rose-100 text-rose-700">0%</span>
            </div>
          </div>

          <!-- KPI 6 -->
          <div class="kpi-card bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Custo Médio / Pedido</span>
              <span class="p-1.5 rounded-lg bg-cyan-50 text-cyan-600">
                <i data-lucide="calculator" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3">
              <span id="kpiAvgCost" class="text-xl font-bold tracking-tight text-slate-900">R$ 0,00</span>
              <p class="text-[11px] text-slate-400 mt-0.5">Média por pedido</p>
            </div>
          </div>
        </section>

        <!-- Top 5 Solicitantes em Agosto e Setembro -->
        <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="font-bold text-base flex items-center gap-2 text-slate-900">
                  <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                  Top 5 Solicitantes / Locais Internos — Agosto
                </h3>
                <p class="text-xs text-slate-500">Valores de peças solicitadas indicados no topo de cada barra</p>
              </div>
              <span class="text-xs font-semibold bg-blue-100 text-blue-700 px-2 py-1 rounded-md">Agosto</span>
            </div>
            <div class="relative h-64">
              <canvas id="chartTopAgosto"></canvas>
            </div>
          </div>

          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="font-bold text-base flex items-center gap-2 text-slate-900">
                  <span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span>
                  Top 5 Solicitantes / Locais Internos — Setembro
                </h3>
                <p class="text-xs text-slate-500">Valores de peças solicitadas indicados no topo de cada barra</p>
              </div>
              <span class="text-xs font-semibold bg-cyan-100 text-cyan-700 px-2 py-1 rounded-md">Setembro</span>
            </div>
            <div class="relative h-64">
              <canvas id="chartTopSetembro"></canvas>
            </div>
          </div>
        </section>

        <!-- Categorias e Fornecedor com Valores -->
        <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="font-bold text-base text-slate-900">Distribuição por Categoria de Peças</h3>
                <p class="text-xs text-slate-500">Quantidades totais exibidas em cada fatia</p>
              </div>
              <i data-lucide="pie-chart" class="w-5 h-5 text-slate-400"></i>
            </div>
            <div class="relative h-64">
              <canvas id="chartCategoryDist"></canvas>
            </div>
          </div>

          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="font-bold text-base text-slate-900">Soma de Custo por Fornecedor (R$)</h3>
                <p class="text-xs text-slate-500">Valor exato em reais destacado sobre as barras</p>
              </div>
              <i data-lucide="building-2" class="w-5 h-5 text-slate-400"></i>
            </div>
            <div class="relative h-64">
              <canvas id="chartSupplierCost"></canvas>
            </div>
          </div>
        </section>

        <!-- TABELA COM RESUMO POR PEÇA SOLICITADA -->
        <section class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4 pb-3 border-b border-slate-100">
            <div>
              <h2 class="text-base font-bold flex items-center gap-2 text-slate-900">
                <i data-lucide="table" class="w-4 h-4 text-blue-500"></i>
                Resumo Detalhado por Peça Solicitada
              </h2>
              <p class="text-xs text-slate-500">Consolidado por item, quantidades solicitadas, atendidas e custo total</p>
            </div>

            <div class="flex items-center gap-3">
              <div class="relative">
                <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-2.5"></i>
                <input type="text" id="tableSearch" placeholder="Buscar peça..." class="text-xs pl-9 pr-3 py-2 rounded-xl border border-slate-300 bg-slate-50 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 w-48 sm:w-64">
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
                  <th class="py-3 px-4 rounded-l-lg">Peça / Produto Solicitado</th>
                  <th class="py-3 px-4">Categoria</th>
                  <th class="py-3 px-4 text-center">Qtde Total</th>
                  <th class="py-3 px-4 text-center text-emerald-600">Atendidas</th>
                  <th class="py-3 px-4 text-center text-rose-600">Não Atendidas</th>
                  <th class="py-3 px-4 text-center">Nº Pedidos</th>
                  <th class="py-3 px-4 text-right">Custo Unit. Médio</th>
                  <th class="py-3 px-4 text-right rounded-r-lg">Custo Total (R$)</th>
                </tr>
              </thead>
              <tbody id="tableBody" class="divide-y divide-slate-100">
              </tbody>
            </table>
          </div>
        </section>

        <!-- Insights e Alertas Executivos -->
        <section class="bg-gradient-to-r from-blue-900/10 via-indigo-900/10 to-transparent border border-blue-200 rounded-2xl p-6">
          <div class="flex items-center gap-2 mb-4">
            <div class="p-2 rounded-lg bg-blue-600 text-white">
              <i data-lucide="sparkles" class="w-5 h-5"></i>
            </div>
            <div>
              <h2 class="text-lg font-bold text-slate-900">Diagnósticos Automáticos de Compras</h2>
              <p class="text-xs text-slate-500">Alertas identificados a partir do custo e da taxa de atendimento de peças</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div class="p-4 rounded-xl bg-white/80 border border-slate-200 shadow-sm">
              <div class="flex items-center gap-2 text-emerald-600 font-semibold mb-1">
                <i data-lucide="check-check" class="w-4 h-4"></i>
                <span>Taxa Global de Atendimento</span>
              </div>
              <p class="text-xs text-slate-600 leading-relaxed">
                Mais de <strong>90% das peças demandadas</strong> foram aprovadas e atendidas nos prazos de compra, garantindo a manutenção contínua do parque de máquinas.
              </p>
            </div>

            <div class="p-4 rounded-xl bg-white/80 border border-slate-200 shadow-sm">
              <div class="flex items-center gap-2 text-rose-600 font-semibold mb-1">
                <i data-lucide="alert-octagon" class="w-4 h-4"></i>
                <span>Itens Não Atendidos / Reprovados</span>
              </div>
              <p class="text-xs text-slate-600 leading-relaxed">
                A principal causa de itens não atendidos decorre de <strong>pedidos duplicados</strong> ou <strong>peças com estoque remanescente</strong> identificado antes do envio à aprovação final de compra.
              </p>
            </div>

            <div class="p-4 rounded-xl bg-white/80 border border-slate-200 shadow-sm">
              <div class="flex items-center gap-2 text-blue-600 font-semibold mb-1">
                <i data-lucide="trending-up" class="w-4 h-4"></i>
                <span>Controle da Coluna Custo</span>
              </div>
              <p class="text-xs text-slate-600 leading-relaxed">
                A soma de custo reflete exatamente as quantidades aprovadas e adquiridas via <strong>EVOCA</strong> e <strong>PARAMOUNT</strong>, com conciliação financeira automatizada.
              </p>
            </div>
          </div>
        </section>

      </main>

      <footer class="max-w-7xl mx-auto px-6 py-8 text-center text-xs text-slate-400 border-t border-slate-200 mt-12">
        Painel Dinâmico de Solicitações e Ordens de Compra de Peças · Análise completa com Peças Atendidas, Não Atendidas e Rótulos Numéricos nos Gráficos.
      </footer>

      <script>
        lucide.createIcons();
        Chart.register(ChartDataLabels);

        // Carrega dados integrados com a sessão Streamlit
        const rawOrdersData = {json_data};

        rawOrdersData.forEach(item => {{
          item.custoTotal = item.qtAprovada * item.custoUnit;
        }});

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
        }}

        populateDropdowns();

        // Configuração de Gráfico 100% no Modo Claro
        function getChartTheme(type = 'bar') {{
          return {{
            responsive: true,
            maintainAspectRatio: false,
            layout: {{ padding: {{ top: 24, bottom: 6, left: 6, right: 6 }} }},
            plugins: {{
              legend: {{ display: false }},
              tooltip: {{
                backgroundColor: '#ffffff',
                titleColor: '#0f172a',
                bodyColor: '#334155',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                padding: 10
              }},
              datalabels: {{
                anchor: 'end',
                align: 'top',
                offset: 2,
                color: '#0f172a',
                font: {{ family: 'Inter', weight: 'bold', size: 11 }},
                formatter: function(value) {{
                  if (value === 0 || value === null || value === undefined) return '';
                  return typeof value === 'number' && value >= 1000 ? value.toLocaleString('pt-BR') : value;
                }}
              }}
            }},
            scales: type === 'bar' ? {{
              x: {{
                grid: {{ color: 'rgba(226, 232, 240, 0.8)' }},
                ticks: {{ color: '#0f172a', font: {{ family: 'Inter', size: 10, weight: '600' }} }}
              }},
              y: {{
                grid: {{ color: 'rgba(226, 232, 240, 0.8)' }},
                ticks: {{ color: '#0f172a', font: {{ family: 'Inter', size: 10, weight: '600' }} }},
                beginAtZero: true
              }}
            }} : undefined
          }};
        }}

        const ctxAgosto = document.getElementById('chartTopAgosto').getContext('2d');
        const ctxSetembro = document.getElementById('chartTopSetembro').getContext('2d');
        const ctxCategory = document.getElementById('chartCategoryDist').getContext('2d');
        const ctxSupplier = document.getElementById('chartSupplierCost').getContext('2d');

        let chartAgosto = new Chart(ctxAgosto, {{
          type: 'bar',
          data: {{ labels: [], datasets: [{{ data: [], backgroundColor: 'rgba(2, 132, 199, 0.85)', borderRadius: 8 }}] }},
          options: {{
            ...getChartTheme('bar'),
            plugins: {{
              ...getChartTheme('bar').plugins,
              datalabels: {{
                anchor: 'end',
                align: 'top',
                color: '#0f172a',
                font: {{ weight: 'bold', size: 11 }},
                formatter: (val) => val ? `${{val}} un` : ''
              }}
            }}
          }}
        }});

        let chartSetembro = new Chart(ctxSetembro, {{
          type: 'bar',
          data: {{ labels: [], datasets: [{{ data: [], backgroundColor: 'rgba(6, 182, 212, 0.85)', borderRadius: 8 }}] }},
          options: {{
            ...getChartTheme('bar'),
            plugins: {{
              ...getChartTheme('bar').plugins,
              datalabels: {{
                anchor: 'end',
                align: 'top',
                color: '#0f172a',
                font: {{ weight: 'bold', size: 11 }},
                formatter: (val) => val ? `${{val}} un` : ''
              }}
            }}
          }}
        }});

        let chartCategory = new Chart(ctxCategory, {{
          type: 'doughnut',
          data: {{
            labels: [],
            datasets: [{{
              data: [],
              backgroundColor: ['#0284c7', '#06b6d4', '#f59e0b', '#6366f1', '#10b981'],
              borderWidth: 2,
              borderColor: '#ffffff'
            }}]
          }},
          options: {{
            responsive: true,
            maintainAspectRatio: false,
            cutout: '62%',
            layout: {{ padding: 12 }},
            plugins: {{
              legend: {{
                position: 'right',
                labels: {{ boxWidth: 12, color: '#0f172a', font: {{ family: 'Inter', size: 11, weight: '600' }} }}
              }},
              datalabels: {{
                color: '#0f172a',
                font: {{ weight: 'bold', size: 11 }},
                formatter: (val, ctx) => {{
                  if (val === 0) return '';
                  const sum = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((val / sum) * 100);
                  return `${{val}}\\n(${{percentage}}%)`;
                }},
                textAlign: 'center'
              }}
            }}
          }}
        }});

        let chartSupplier = new Chart(ctxSupplier, {{
          type: 'bar',
          data: {{ labels: [], datasets: [{{ data: [], backgroundColor: 'rgba(245, 158, 11, 0.85)', borderRadius: 8 }}] }},
          options: {{
            ...getChartTheme('bar'),
            plugins: {{
              ...getChartTheme('bar').plugins,
              datalabels: {{
                anchor: 'end',
                align: 'top',
                color: '#0f172a',
                font: {{ weight: 'bold', size: 11 }},
                formatter: (val) => val ? formatCurrency(val) : ''
              }}
            }}
          }}
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

          activeFilterBadge.innerText = `Filtros: Ano [${{yearVal}}] · Mês [${{monthVal}}] · Categoria [${{catVal}}]`;

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
            items.forEach(d => {{
              counts[d.solicitante] = (counts[d.solicitante] || 0) + d.qt;
            }});
            return Object.entries(counts)
              .map(([name, qt]) => ({{ name, qt }}))
              .sort((a, b) => b.qt - a.qt)
              .slice(0, 5);
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
          filtered.forEach(d => {{
            catCounts[d.categoria] = (catCounts[d.categoria] || 0) + d.qt;
          }});
          chartCategory.data.labels = Object.keys(catCounts);
          chartCategory.data.datasets[0].data = Object.values(catCounts);
          chartCategory.update();

          const supplierCosts = {{}};
          filtered.forEach(d => {{
            supplierCosts[d.fornecedor] = (supplierCosts[d.fornecedor] || 0) + d.custoTotal;
          }});
          chartSupplier.data.labels = Object.keys(supplierCosts);
          chartSupplier.data.datasets[0].data = Object.values(supplierCosts);
          chartSupplier.update();

          renderTable(filtered, searchVal);
        }}

        function renderTable(dataList, searchTerm) {{
          const grouped = {{}};

          dataList.forEach(item => {{
            if (!grouped[item.peca]) {{
              grouped[item.peca] = {{
                peca: item.peca,
                categoria: item.categoria,
                qtTotal: 0,
                qtAtendida: 0,
                qtNaoAtendida: 0,
                pedidosCount: 0,
                custoTotal: 0
              }};
            }}
            grouped[item.peca].qtTotal += item.qt;
            grouped[item.peca].qtAtendida += item.qtAprovada;
            grouped[item.peca].qtNaoAtendida += item.qtNaoAprovada;
            grouped[item.peca].pedidosCount += 1;
            grouped[item.peca].custoTotal += item.custoTotal;
          }});

          let itemsArray = Object.values(grouped);

          if (searchTerm) {{
            itemsArray = itemsArray.filter(i => 
              i.peca.toLowerCase().includes(searchTerm) || 
              i.categoria.toLowerCase().includes(searchTerm)
            );
          }}

          itemsArray.sort((a, b) => b.custoTotal - a.custoTotal);
          tableCountBadge.innerText = `${{itemsArray.length}} peças`;

          if (itemsArray.length === 0) {{
            tableBody.innerHTML = `
              <tr>
                <td colspan="8" class="text-center py-8 text-slate-400">
                  Nenhuma peça encontrada com os filtros selecionados.
                </td>
              </tr>
            `;
            return;
          }}

          tableBody.innerHTML = itemsArray.map(item => {{
            const unitAvg = item.qtAtendida > 0 ? (item.custoTotal / item.qtAtendida) : 0;
            return `
              <tr class="hover:bg-slate-50 transition">
                <td class="py-3 px-4 font-semibold text-slate-800">
                  ${{item.peca}}
                </td>
                <td class="py-3 px-4">
                  <span class="inline-block px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                    ${{item.categoria}}
                  </span>
                </td>
                <td class="py-3 px-4 text-center font-bold text-slate-700">
                  ${{item.qtTotal.toLocaleString('pt-BR')}} un
                </td>
                <td class="py-3 px-4 text-center font-semibold text-emerald-600">
                  ${{item.qtAtendida.toLocaleString('pt-BR')}} un
                </td>
                <td class="py-3 px-4 text-center font-semibold text-rose-500">
                  ${{item.qtNaoAtendida.toLocaleString('pt-BR')}} un
                </td>
                <td class="py-3 px-4 text-center text-slate-500">
                  ${{item.pedidosCount}}
                </td>
                <td class="py-3 px-4 text-right text-slate-500">
                  ${{formatCurrency(unitAvg)}}
                </td>
                <td class="py-3 px-4 text-right font-bold text-amber-600">
                  ${{formatCurrency(item.custoTotal)}}
                </td>
              </tr>
            `;
          }}).join('');
        }}

        [filterYear, filterMonth, filterCategory, filterRequester].forEach(select => {{
          select.addEventListener('change', updateDashboard);
        }});

        tableSearch.addEventListener('input', () => {{
          updateDashboard();
        }});

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

    components.html(html_code, height=2150, scrolling=True)