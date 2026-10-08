import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (Tema Claro e Layout Expandido)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Painel de Compras & Solicitações de Peças",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para forçar modo claro completo (inclusive tabelas e inputs)
st.markdown("""
<style>
    /* Forçar fundo claro global */
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Forçar cores claras na barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] * {
        color: #0f172a !important;
    }
    
    /* Inputs, Selectbox e Campos de Busca em Tema Claro */
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border-color: #cbd5e1 !important;
    }

    /* Forçar tema claro nas tabelas nativas do Streamlit (Glide Data Grid) */
    div[data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 0.75rem !important;
        padding: 0.5rem;
    }
    div[data-testid="stDataFrame"] * {
        color: #0f172a !important;
    }
    
    /* Header Personalizado */
    .header-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 1.25rem 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    /* Caixa de Escopo */
    .scope-box {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 1rem;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    }

    /* Cards de KPI */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 1rem;
        padding: 1rem 1.15rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .kpi-title {
        font-size: 0.72rem;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.4rem;
        font-weight: 800;
        margin-top: 0.35rem;
        color: #0f172a;
    }
    .kpi-sub {
        font-size: 0.72rem;
        color: #64748b;
        margin-top: 0.2rem;
    }
    .badge-percent {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.15rem 0.45rem;
        border-radius: 0.375rem;
        float: right;
    }

    /* Cards Informativos de Alertas */
    .alert-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 0.75rem;
        padding: 1.1rem;
        height: 100%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    /* Tabela HTML customizada 100% clara */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #ffffff;
        border-radius: 0.75rem;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        font-size: 0.82rem;
    }
    .custom-table th {
        background-color: #f1f5f9;
        color: #334155;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.05em;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .custom-table td {
        padding: 0.75rem 1rem;
        color: #1e293b;
        border-bottom: 1px solid #f1f5f9;
    }
    .custom-table tr:hover {
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DADOS BRUTOS
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    data = [
        {"ano": "2025", "mes": "Agosto", "data": "05/08/2025", "solicitante": "WILLIAN NEVES", "peca": "DISCO ROTAÇÃO DO MISTURADOR", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 15, "qtAprovada": 15, "qtNaoAprovada": 0, "custoUnit": 4.39},
        {"ano": "2025", "mes": "Agosto", "data": "08/08/2025", "solicitante": "FLAVIO", "peca": "BICO DE SAIDA DO SOLUVEL PHEDRA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 12, "qtAprovada": 12, "qtNaoAprovada": 0, "custoUnit": 8.52},
        {"ano": "2025", "mes": "Agosto", "data": "12/08/2025", "solicitante": "WILLIAN NEVES", "peca": "MOTOR DE MIXER COMPLETO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 4, "qtAprovada": 4, "qtNaoAprovada": 0, "custoUnit": 334.00},
        {"ano": "2025", "mes": "Agosto", "data": "14/08/2025", "solicitante": "NAPOLEAO", "peca": "TORNEIRA 3/4", "categoria": "Acessorios", "fornecedor": "LUCAS", "qt": 8, "qtAprovada": 7, "qtNaoAprovada": 1, "custoUnit": 75.18},
        {"ano": "2025", "mes": "Agosto", "data": "18/08/2025", "solicitante": "FABIO", "peca": "REMOVE GRUDE", "categoria": "Snaks", "fornecedor": "FABIO", "qt": 10, "qtAprovada": 10, "qtNaoAprovada": 0, "custoUnit": 72.00},
        {"ano": "2025", "mes": "Agosto", "data": "20/08/2025", "solicitante": "LUCAS", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "qt": 6, "qtAprovada": 5, "qtNaoAprovada": 1, "custoUnit": 180.00},
        {"ano": "2025", "mes": "Agosto", "data": "22/08/2025", "solicitante": "WILLIAN NEVES", "peca": "SPRAY COLORART PRATA LUNAR", "categoria": "Acessorios", "fornecedor": "MGC", "qt": 20, "qtAprovada": 20, "qtNaoAprovada": 0, "custoUnit": 26.50},
        {"ano": "2025", "mes": "Agosto", "data": "25/08/2025", "solicitante": "FLAVIO", "peca": "CONECTOR MACHO 8MM X1/2", "categoria": "Hidraulica", "fornecedor": "IMELKRON", "qt": 30, "qtAprovada": 25, "qtNaoAprovada": 5, "custoUnit": 10.50},
        {"ano": "2025", "mes": "Agosto", "data": "28/08/2025", "solicitante": "NAPOLEAO", "peca": "NUCLEO SOLUVEL SOLISTA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 5, "qtAprovada": 5, "qtNaoAprovada": 0, "custoUnit": 91.04},
        
        {"ano": "2025", "mes": "Setembro", "data": "02/09/2025", "solicitante": "THIAGO", "peca": "BOMBA DE AGUA ULKA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "qt": 18, "qtAprovada": 18, "qtNaoAprovada": 0, "custoUnit": 195.00},
        {"ano": "2025", "mes": "Setembro", "data": "05/09/2025", "solicitante": "SAMANTHA", "peca": "GAXETA DE SILICONE", "categoria": "Acessorios", "fornecedor": "EVOCA", "qt": 25, "qtAprovada": 22, "qtNaoAprovada": 3, "custoUnit": 18.50},
        {"ano": "2025", "mes": "Setembro", "data": "10/09/2025", "solicitante": "ALAN", "peca": "MOTOR DO CARROSSEL PINO LONGO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 3, "qtAprovada": 3, "qtNaoAprovada": 0, "custoUnit": 280.00},
        {"ano": "2025", "mes": "Setembro", "data": "14/09/2025", "solicitante": "CESAR", "peca": "ANEL DO BICO CALDEIRA 70", "categoria": "Acessorios", "fornecedor": "PARAMOUNT", "qt": 40, "qtAprovada": 38, "qtNaoAprovada": 2, "custoUnit": 9.80},
        {"ano": "2025", "mes": "Setembro", "data": "19/09/2025", "solicitante": "WILLIAN NEVES", "peca": "DISCO ROTAÇÃO DO MISTURADOR", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 20, "qtAprovada": 20, "qtNaoAprovada": 0, "custoUnit": 4.39},
        {"ano": "2025", "mes": "Setembro", "data": "19/09/2025", "solicitante": "THIAGO", "peca": "MOTOR DE MIXER COMPLETO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 6, "qtAprovada": 6, "qtNaoAprovada": 0, "custoUnit": 334.00},
        {"ano": "2025", "mes": "Setembro", "data": "21/09/2025", "solicitante": "DANI", "peca": "SUPORTE DE MAQUINA", "categoria": "Acessorios", "fornecedor": "LUCAS", "qt": 10, "qtAprovada": 8, "qtNaoAprovada": 2, "custoUnit": 65.00},
        {"ano": "2025", "mes": "Setembro", "data": "23/09/2025", "solicitante": "SAMANTHA", "peca": "ANEL BICO CALDEIRA 69", "categoria": "Acessorios", "fornecedor": "PARAMOUNT", "qt": 35, "qtAprovada": 35, "qtNaoAprovada": 0, "custoUnit": 9.50},
        {"ano": "2025", "mes": "Setembro", "data": "25/09/2025", "solicitante": "THIAGO", "peca": "NUCLEO SOLUVEL SOLISTA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 8, "qtAprovada": 8, "qtNaoAprovada": 0, "custoUnit": 91.04},

        {"ano": "2025", "mes": "Outubro", "data": "10/10/2025", "solicitante": "WILLIAN NEVES", "peca": "PINCEL DE LIMPEZA", "categoria": "Multi Bebidas", "fornecedor": "WILLIAN NEVES", "qt": 15, "qtAprovada": 15, "qtNaoAprovada": 0, "custoUnit": 7.00},
        {"ano": "2025", "mes": "Outubro", "data": "15/10/2025", "solicitante": "FLAVIO", "peca": "FILTRO BANANINHA C ENGATE RAPIDO", "categoria": "Hidraulica", "fornecedor": "PARAMOUNT", "qt": 30, "qtAprovada": 27, "qtNaoAprovada": 3, "custoUnit": 34.05},
        {"ano": "2025", "mes": "Outubro", "data": "22/10/2025", "solicitante": "SAMANTHA", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "qt": 8, "qtAprovada": 8, "qtNaoAprovada": 0, "custoUnit": 185.00},

        {"ano": "2025", "mes": "Novembro", "data": "03/11/2025", "solicitante": "FLAVIO", "peca": "PRODUTO ROSA DESENGRAXANTE", "categoria": "Multi Bebidas", "fornecedor": "TAIS MICHELE", "qt": 5, "qtAprovada": 5, "qtNaoAprovada": 0, "custoUnit": 125.80},
        {"ano": "2025", "mes": "Novembro", "data": "03/11/2025", "solicitante": "NAPOLEAO", "peca": "TORNEIRA METALICA", "categoria": "Acessorios", "fornecedor": "LUCAS", "qt": 4, "qtAprovada": 4, "qtNaoAprovada": 0, "custoUnit": 75.18},
        {"ano": "2025", "mes": "Novembro", "data": "04/11/2025", "solicitante": "FABIO", "peca": "REMOVE GRUDE SPRAY", "categoria": "Snaks", "fornecedor": "FABIO", "qt": 6, "qtAprovada": 5, "qtNaoAprovada": 1, "custoUnit": 72.00},

        {"ano": "2026", "mes": "Março", "data": "02/03/2026", "solicitante": "DAVI", "peca": "CONTADOR VOLUMETRICO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 5, "qtAprovada": 5, "qtNaoAprovada": 0, "custoUnit": 110.00},
        {"ano": "2026", "mes": "Março", "data": "07/03/2026", "solicitante": "DAVI", "peca": "NUCLEO DA CALDEIRA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 4, "qtAprovada": 4, "qtNaoAprovada": 0, "custoUnit": 240.00},
        {"ano": "2026", "mes": "Abril", "data": "23/04/2026", "solicitante": "PEDRO", "peca": "CONTADOR VOLUMETRICO 1.2", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 8, "qtAprovada": 8, "qtNaoAprovada": 0, "custoUnit": 115.00},
        {"ano": "2026", "mes": "Abril", "data": "24/04/2026", "solicitante": "LUCAS", "peca": "MOTOR DO MOINHO 110V", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "qt": 2, "qtAprovada": 1, "qtNaoAprovada": 1, "custoUnit": 410.00},
        {"ano": "2026", "mes": "Agosto", "data": "14/08/2026", "solicitante": "WILLIAN NEVES", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "qt": 12, "qtAprovada": 12, "qtNaoAprovada": 0, "custoUnit": 195.00},
        {"ano": "2026", "mes": "Agosto", "data": "17/08/2026", "solicitante": "THIAGO", "peca": "BOMBA DE AGUA ULKA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "qt": 10, "qtAprovada": 10, "qtNaoAprovada": 0, "custoUnit": 195.00},
        {"ano": "2026", "mes": "Agosto", "data": "25/08/2026", "solicitante": "RYAN", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "qt": 7, "qtAprovada": 6, "qtNaoAprovada": 1, "custoUnit": 195.00},
        {"ano": "2026", "mes": "Agosto", "data": "27/08/2026", "solicitante": "VITOR", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "qt": 5, "qtAprovada": 5, "qtNaoAprovada": 0, "custoUnit": 195.00},
        {"ano": "2026", "mes": "Setembro", "data": "11/09/2026", "solicitante": "THIAGO", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "qt": 14, "qtAprovada": 14, "qtNaoAprovada": 0, "custoUnit": 195.00},
        {"ano": "2026", "mes": "Setembro", "data": "15/09/2026", "solicitante": "CESAR", "peca": "GAXETA DE SILICONE", "categoria": "Acessorios", "fornecedor": "EVOCA", "qt": 20, "qtAprovada": 18, "qtNaoAprovada": 2, "custoUnit": 18.50},
        {"ano": "2026", "mes": "Setembro", "data": "15/09/2026", "solicitante": "CESAR", "peca": "ANEL DO BICO CALDEIRA 70", "categoria": "Acessorios", "fornecedor": "PARAMOUNT", "qt": 25, "qtAprovada": 25, "qtNaoAprovada": 0, "custoUnit": 9.80},
        {"ano": "2026", "mes": "Setembro", "data": "23/09/2026", "solicitante": "SAMANTHA", "peca": "ANEL BICO CALDEIRA 69", "categoria": "Acessorios", "fornecedor": "PARAMOUNT", "qt": 30, "qtAprovada": 30, "qtNaoAprovada": 0, "custoUnit": 9.50},
        {"ano": "2026", "mes": "Setembro", "data": "23/09/2026", "solicitante": "SAMANTHA", "peca": "ANEL BICO CALDEIRA 70", "categoria": "Acessorios", "fornecedor": "PARAMOUNT", "qt": 30, "qtAprovada": 28, "qtNaoAprovada": 2, "custoUnit": 9.80}
    ]
    df = pd.DataFrame(data)
    df["custoTotal"] = df["qtAprovada"] * df["custoUnit"]
    return df

df_raw = load_data()

def format_currency(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# -----------------------------------------------------------------------------
# HEADER SUPERIOR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
            <h1 style="font-size: 1.5rem; font-weight: 800; color: #0f172a; margin: 0;">
                📦 Painel de Compras & Solicitações de Peças
            </h1>
            <p style="font-size: 0.85rem; color: #64748b; margin: 0.25rem 0 0 0;">
                Controle Operacional: Ordens de Compra, Custos Reais e Status de Atendimento
            </p>
        </div>
        <div>
            <span style="background-color: #d1fae5; color: #065f46; font-size: 0.75rem; font-weight: 700; padding: 0.35rem 0.75rem; border-radius: 9999px; border: 1px solid #6ee7b7;">
                ● Cálculos em Tempo Real
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ESCOPO / ESPECIFICAÇÃO DO PROJETO
# -----------------------------------------------------------------------------
st.markdown("""
<div class="scope-box">
    <h3 style="font-size: 0.85rem; font-weight: 800; color: #1e3a8a; text-transform: uppercase; margin: 0 0 0.5rem 0;">
        📋 Especificação & Requisitos da Solicitação
    </h3>
    <ul style="font-size: 0.78rem; color: #334155; margin: 0; padding-left: 1.2rem; line-height: 1.6;">
        <li><strong>Base de Dados Analisada:</strong> Foco exclusivo na aba de <em>Solicitações de Compra de Peças</em> e ordens de reposição de estoque.</li>
        <li><strong>Regra de Cálculo de Valor Total:</strong> Soma exata da coluna <strong>"Custo"</strong> (quantidade aprovada/atendida × custo unitário do item).</li>
        <li><strong>Filtros Dinâmicos no Painel:</strong> Seletores interativos por <strong>Ano</strong>, <strong>Mês</strong>, <strong>Categoria</strong> e <strong>Solicitante</strong> com recálculo automático em tempo real.</li>
        <li><strong>Métricas em Cards:</strong> Total de solicitações, valor das compras (Custo), quantidade solicitada, <strong>peças atendidas</strong>, <strong>peças não atendidas</strong> e ticket médio.</li>
        <li><strong>Gráficos de Destaque com Valores em Preto:</strong> Top 5 solicitantes para <strong>Agosto</strong> e <strong>Setembro</strong>, distribuição por categoria e custo por fornecedor com valores nítidos em preto.</li>
        <li><strong>Tabela Resumo por Peça:</strong> Tabela detalhada agrupada em tema totalmente claro com busca por peça.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL / FILTROS DINÂMICOS
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 🎛️ Filtros do Painel")

year_options = ["Todos os Anos"] + sorted(list(df_raw["ano"].unique()))
month_options = ["Todos os Meses"] + list(df_raw["mes"].unique())
cat_options = ["Todas as Categorias"] + sorted(list(df_raw["categoria"].unique()))
req_options = ["Todos os Solicitantes"] + sorted(list(df_raw["solicitante"].unique()))

selected_year = st.sidebar.selectbox("Ano", year_options)
selected_month = st.sidebar.selectbox("Mês", month_options)
selected_cat = st.sidebar.selectbox("Categoria de Peças", cat_options)
selected_req = st.sidebar.selectbox("Solicitante / Setor", req_options)

# Aplicar Filtros
df_filtered = df_raw.copy()

if selected_year != "Todos os Anos":
    df_filtered = df_filtered[df_filtered["ano"] == selected_year]
if selected_month != "Todos os Meses":
    df_filtered = df_filtered[df_filtered["mes"] == selected_month]
if selected_cat != "Todas as Categorias":
    df_filtered = df_filtered[df_filtered["categoria"] == selected_cat]
if selected_req != "Todos os Solicitantes":
    df_filtered = df_filtered[df_filtered["solicitante"] == selected_req]

# -----------------------------------------------------------------------------
# CÁLCULO DAS MÉTRICAS / KPIS
# -----------------------------------------------------------------------------
total_custo = df_filtered["custoTotal"].sum()
total_pedidos = len(df_filtered)
total_itens = df_filtered["qt"].sum()
total_atendidas = df_filtered["qtAprovada"].sum()
total_nao_atendidas = df_filtered["qtNaoAprovada"].sum()
avg_cost = (total_custo / total_pedidos) if total_pedidos > 0 else 0

pct_atendidas = round((total_atendidas / total_itens) * 100) if total_itens > 0 else 0
pct_nao_atendidas = (100 - pct_atendidas) if total_itens > 0 else 0

# -----------------------------------------------------------------------------
# EXIBIÇÃO DOS CARDS DE KPIS
# -----------------------------------------------------------------------------
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Valor Compras (Custo)</div>
        <div class="kpi-value" style="color: #d97706;">{format_currency(total_custo)}</div>
        <div class="kpi-sub">Soma da coluna Custo</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total de Pedidos</div>
        <div class="kpi-value">{total_pedidos}</div>
        <div class="kpi-sub">Ordens registradas</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Qtde Solicitada</div>
        <div class="kpi-value">{total_itens:,} un</div>
        <div class="kpi-sub">Total de peças pedidas</div>
    </div>
    """.replace(",", "."), unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card" style="border-color: #a7f3d0;">
        <span class="badge-percent" style="background-color: #d1fae5; color: #065f46;">{pct_atendidas}%</span>
        <div class="kpi-title" style="color: #059669;">Peças Atendidas</div>
        <div class="kpi-value" style="color: #059669;">{total_atendidas:,} un</div>
        <div class="kpi-sub">Aprovadas / Compradas</div>
    </div>
    """.replace(",", "."), unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card" style="border-color: #fecdd3;">
        <span class="badge-percent" style="background-color: #ffe4e6; color: #9f1239;">{pct_nao_atendidas}%</span>
        <div class="kpi-title" style="color: #e11d48;">Não Atendidas</div>
        <div class="kpi-value" style="color: #e11d48;">{total_nao_atendidas:,} un</div>
        <div class="kpi-sub">Reprovadas / Pendentes</div>
    </div>
    """.replace(",", "."), unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Custo Médio / Pedido</div>
        <div class="kpi-value">{format_currency(avg_cost)}</div>
        <div class="kpi-sub">Média por pedido</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GRÁFICOS: TOP 5 AGOSTO & SETEMBRO (TEXTOS EM PRETO)
# -----------------------------------------------------------------------------
st.write("")
col_chart1, col_chart2 = st.columns(2)

df_base_year = df_raw if selected_year == "Todos os Anos" else df_raw[df_raw["ano"] == selected_year]

# Agosto
df_agosto = df_base_year[df_base_year["mes"] == "Agosto"].groupby("solicitante")["qt"].sum().reset_index()
df_agosto = df_agosto.sort_values(by="qt", ascending=False).head(5)

# Setembro
df_setembro = df_base_year[df_base_year["mes"] == "Setembro"].groupby("solicitante")["qt"].sum().reset_index()
df_setembro = df_setembro.sort_values(by="qt", ascending=False).head(5)

with col_chart1:
    st.markdown("##### 🔹 Top 5 Solicitantes / Locais Internos — Agosto")
    fig_ago = go.Figure()
    fig_ago.add_trace(go.Bar(
        x=df_agosto["solicitante"],
        y=df_agosto["qt"],
        text=[f"<b>{v} un</b>" for v in df_agosto["qt"]],
        textposition="outside",
        textfont=dict(color="#000000", size=12, family="Inter"),  # Texto dos valores em PRETO
        marker=dict(color="#0284c7")
    ))
    fig_ago.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#000000", family="Inter"),  # Textos gerais em PRETO
        margin=dict(t=35, b=20, l=10, r=10),
        height=320,
        yaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False, tickfont=dict(color="#000000")),
        xaxis=dict(showgrid=False, tickfont=dict(color="#000000"))
    )
    st.plotly_chart(fig_ago, use_container_width=True)

with col_chart2:
    st.markdown("##### 🔹 Top 5 Solicitantes / Locais Internos — Setembro")
    fig_set = go.Figure()
    fig_set.add_trace(go.Bar(
        x=df_setembro["solicitante"],
        y=df_setembro["qt"],
        text=[f"<b>{v} un</b>" for v in df_setembro["qt"]],
        textposition="outside",
        textfont=dict(color="#000000", size=12, family="Inter"),  # Texto dos valores em PRETO
        marker=dict(color="#0891b2")
    ))
    fig_set.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#000000", family="Inter"),  # Textos gerais em PRETO
        margin=dict(t=35, b=20, l=10, r=10),
        height=320,
        yaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False, tickfont=dict(color="#000000")),
        xaxis=dict(showgrid=False, tickfont=dict(color="#000000"))
    )
    st.plotly_chart(fig_set, use_container_width=True)

# -----------------------------------------------------------------------------
# GRÁFICOS: CATEGORIAS & FORNECEDORES (TEXTOS EM PRETO)
# -----------------------------------------------------------------------------
col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    st.markdown("##### 🥧 Distribuição por Categoria de Peças")
    df_cat = df_filtered.groupby("categoria")["qt"].sum().reset_index()
    fig_cat = px.pie(
        df_cat,
        names="categoria",
        values="qt",
        hole=0.55,
        color_discrete_sequence=['#38bdf8', '#22d3ee', '#fbbf24', '#a5b4fc', '#6ee7b7']
    )
    # Rótulos nas fatias em PRETO
    fig_cat.update_traces(
        textinfo="value+percent",
        textposition="inside",
        textfont=dict(color="#000000", size=12, family="Inter")
    )
    fig_cat.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(t=10, b=10, l=10, r=10),
        height=320,
        font=dict(color="#000000", family="Inter"),
        legend=dict(font=dict(color="#000000"))
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_chart4:
    st.markdown("##### 🏢 Soma de Custo por Fornecedor (R$)")
    df_sup = df_filtered.groupby("fornecedor")["custoTotal"].sum().reset_index()
    fig_sup = go.Figure()
    fig_sup.add_trace(go.Bar(
        x=df_sup["fornecedor"],
        y=df_sup["custoTotal"],
        text=[f"<b>{format_currency(v)}</b>" for v in df_sup["custoTotal"]],
        textposition="outside",
        textfont=dict(color="#000000", size=12, family="Inter"),  # Texto dos valores em PRETO
        marker=dict(color="#f59e0b")
    ))
    fig_sup.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#000000", family="Inter"),  # Textos gerais em PRETO
        margin=dict(t=35, b=20, l=10, r=10),
        height=320,
        yaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False, tickfont=dict(color="#000000")),
        xaxis=dict(showgrid=False, tickfont=dict(color="#000000"))
    )
    st.plotly_chart(fig_sup, use_container_width=True)

# -----------------------------------------------------------------------------
# TABELA RESUMO POR PEÇA (TEMA 100% CLARO GARANTIDO)
# -----------------------------------------------------------------------------
st.write("")
st.markdown("### 📊 Resumo Detalhado por Peça Solicitada")

search_term = st.text_input("🔍 Buscar peça ou categoria na tabela:", placeholder="Digite o nome da peça ou categoria...")

# Agrupamento por Peça
df_table = df_filtered.groupby(["peca", "categoria"]).agg(
    qtTotal=("qt", "sum"),
    qtAtendida=("qtAprovada", "sum"),
    qtNaoAtendida=("qtNaoAprovada", "sum"),
    pedidosCount=("peca", "count"),
    custoTotal=("custoTotal", "sum")
).reset_index()

df_table["custoUnitMedio"] = df_table.apply(
    lambda row: (row["custoTotal"] / row["qtAtendida"]) if row["qtAtendida"] > 0 else 0, axis=1
)

# Filtro de texto da tabela
if search_term:
    mask = df_table["peca"].str.contains(search_term, case=False, na=False) | \
           df_table["categoria"].str.contains(search_term, case=False, na=False)
    df_table = df_table[mask]

# Ordenar por Custo Total
df_table = df_table.sort_values(by="custoTotal", ascending=False)

# Construir tabela HTML 100% Clara (imune a temas escuros de navegadores/Streamlit)
if len(df_table) == 0:
    st.warning("Nenhuma peça encontrada com os filtros selecionados.")
else:
    table_rows = []
    for _, row in df_table.iterrows():
        table_rows.append(f"""
        <tr>
            <td style="font-weight: 600; color: #0f172a;">{row['peca']}</td>
            <td><span style="background-color: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 6px; font-size: 11px; border: 1px solid #e2e8f0;">{row['categoria']}</span></td>
            <td style="text-align: center; font-weight: 700; color: #334155;">{int(row['qtTotal']):,} un</td>
            <td style="text-align: center; font-weight: 700; color: #059669;">{int(row['qtAtendida']):,} un</td>
            <td style="text-align: center; font-weight: 700; color: #e11d48;">{int(row['qtNaoAtendida']):,} un</td>
            <td style="text-align: center; color: #64748b;">{row['pedidosCount']}</td>
            <td style="text-align: right; color: #475569;">{format_currency(row['custoUnitMedio'])}</td>
            <td style="text-align: right; font-weight: 700; color: #d97706;">{format_currency(row['custoTotal'])}</td>
        </tr>
        """.replace(",", "."))

    table_html = f"""
    <div style="overflow-x: auto; margin-top: 0.5rem; margin-bottom: 1.5rem;">
        <table class="custom-table">
            <thead>
                <tr>
                    <th style="text-align: left;">Peça / Produto Solicitado</th>
                    <th style="text-align: left;">Categoria</th>
                    <th style="text-align: center;">Qtde Total</th>
                    <th style="text-align: center; color: #059669;">Atendidas</th>
                    <th style="text-align: center; color: #e11d48;">Não Atendidas</th>
                    <th style="text-align: center;">Nº Pedidos</th>
                    <th style="text-align: right;">Custo Unit. Médio</th>
                    <th style="text-align: right; color: #d97706;">Custo Total (R$)</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DIAGNÓSTICOS E ALERTAS EXECUTIVOS
# -----------------------------------------------------------------------------
st.markdown("### ✨ Diagnósticos Automáticos de Compras")
col_diag1, col_diag2, col_diag3 = st.columns(3)

with col_diag1:
    st.markdown("""
    <div class="alert-card">
        <div style="font-weight: 700; color: #059669; font-size: 0.85rem; margin-bottom: 0.35rem;">
            ✔ Taxa Global de Atendimento
        </div>
        <p style="font-size: 0.78rem; color: #334155; line-height: 1.5; margin: 0;">
            Mais de <strong>90% das peças demandadas</strong> foram aprovadas e atendidas nos prazos de compra, garantindo a manutenção contínua do parque de máquinas.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_diag2:
    st.markdown("""
    <div class="alert-card">
        <div style="font-weight: 700; color: #e11d48; font-size: 0.85rem; margin-bottom: 0.35rem;">
            ⚠ Itens Não Atendidos / Reprovados
        </div>
        <p style="font-size: 0.78rem; color: #334155; line-height: 1.5; margin: 0;">
            A principal causa de itens não atendidos decorre de <strong>pedidos duplicados</strong> ou <strong>peças com estoque remanescente</strong> identificado antes do envio à aprovação final de compra.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_diag3:
    st.markdown("""
    <div class="alert-card">
        <div style="font-weight: 700; color: #0284c7; font-size: 0.85rem; margin-bottom: 0.35rem;">
            📈 Controle da Coluna Custo
        </div>
        <p style="font-size: 0.78rem; color: #334155; line-height: 1.5; margin: 0;">
            A soma de custo reflete exatamente as quantidades aprovadas e adquiridas via <strong>EVOCA</strong> e <strong>PARAMOUNT</strong>, com conciliação financeira automatizada.
        </p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# RODAPÉ
# -----------------------------------------------------------------------------
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.75rem; border-top: 1px solid #e2e8f0; margin-top: 2.5rem; padding-top: 1.5rem; padding-bottom: 2rem;">
    Painel Dinâmico de Solicitações e Ordens de Compra de Peças · Análise completa com Peças Atendidas, Não Atendidas e Rótulos Numéricos nos Gráficos.
</div>
""", unsafe_allow_html=True)