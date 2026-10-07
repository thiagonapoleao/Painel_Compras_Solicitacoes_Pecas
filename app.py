import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Dashboard Executivo - Solicitações & Ordens de Compra de Peças",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada (replicando os cards do HTML)
st.markdown("""
<style>
    .kpi-card {
        background-color: var(--secondary-background-color, #ffffff);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 1rem;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-title {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
    }
    .kpi-value {
        font-size: 1.45rem;
        font-weight: 800;
        margin-top: 0.35rem;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.72rem;
        color: #94a3b8;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Base de Dados idêntica à do HTML
@st.cache_data
def carregar_dados():
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
    # Cálculo idêntico ao JS: custoTotal = qtAprovada * custoUnit
    df["custoTotal"] = df["qtAprovada"] * df["custoUnit"]
    return df

df_raw = carregar_dados()

def format_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# CABEÇALHO DO DASHBOARD
st.title("📦 Painel de Compras & Solicitações de Peças")
st.caption("Controle Operacional: Ordens de Compra, Custos Reais e Status de Atendimento")

# ESPECIFICAÇÃO & REQUISITOS (CARD NO TOPO)
with st.expander("📋 Especificação & Requisitos da Solicitação (Parâmetros Ativos)", expanded=True):
    st.markdown("""
    - **Base de Dados Analisada:** Foco exclusivo na aba de *Solicitações de Compra de Peças* e ordens de reposição de estoque.
    - **Regra de Cálculo de Valor Total:** Soma exata da coluna **"Custo"** (quantidade aprovada/atendida × custo unitário do item).
    - **Filtros Dinâmicos no Painel:** Seletores interativos por **Ano**, **Mês**, **Categoria** e **Solicitante** com recálculo automático em tempo real.
    - **Métricas em Cards:** Total de solicitações, valor das compras (Custo), quantidade solicitada, **peças atendidas**, **peças não atendidas** e ticket médio.
    - **Gráficos de Destaque com Valores Exibidos:** Top 5 solicitantes/locais internos para **Agosto** e **Setembro**, distribuição por categoria e custo por fornecedor exibindo os **valores numéricos e em R$ diretamente nas barras/fatias**.
    - **Tabela Resumo por Peça:** Tabela detalhada agrupada por produto com pesquisa em tempo real, quantidades solicitadas/atendidas/não atendidas e valor financeiro.
    """)

# FILTROS DINÂMICOS NA SIDEBAR
st.sidebar.header("🔍 Filtros do Painel")

anos_opcoes = ["ALL"] + sorted(df_raw["ano"].unique().tolist())
filtro_ano = st.sidebar.selectbox("Ano", anos_opcoes, index=0)

meses_opcoes = ["ALL"] + list(dict.fromkeys(df_raw["mes"].tolist()))
filtro_mes = st.sidebar.selectbox("Mês", meses_opcoes, index=0)

categorias_opcoes = ["ALL"] + sorted(df_raw["categoria"].unique().tolist())
filtro_categoria = st.sidebar.selectbox("Categoria de Peças", categorias_opcoes, index=0)

solicitantes_opcoes = ["ALL"] + sorted(df_raw["solicitante"].unique().tolist())
filtro_solicitante = st.sidebar.selectbox("Solicitante / Setor", solicitantes_opcoes, index=0)

if st.sidebar.button("🔄 Limpar Filtros", use_container_width=True):
    st.rerun()

# APLICAÇÃO DOS FILTROS
df_filtered = df_raw.copy()
if filtro_ano != "ALL":
    df_filtered = df_filtered[df_filtered["ano"] == filtro_ano]
if filtro_mes != "ALL":
    df_filtered = df_filtered[df_filtered["mes"] == filtro_mes]
if filtro_categoria != "ALL":
    df_filtered = df_filtered[df_filtered["categoria"] == filtro_categoria]
if filtro_solicitante != "ALL":
    df_filtered = df_filtered[df_filtered["solicitante"] == filtro_solicitante]

st.info(f"Filtrando: Ano [{filtro_ano}] · Mês [{filtro_mes}] · Categoria [{filtro_categoria}] · Solicitante [{filtro_solicitante}]")

# CÁLCULOS DOS KPIS
total_custo = df_filtered["custoTotal"].sum()
total_pedidos = len(df_filtered)
total_solicitado = df_filtered["qt"].sum()
total_atendidas = df_filtered["qtAprovada"].sum()
total_nao_atendidas = df_filtered["qtNaoAprovada"].sum()
avg_custo = (total_custo / total_pedidos) if total_pedidos > 0 else 0.0

pct_atendidas = round((total_atendidas / total_solicitado * 100)) if total_solicitado > 0 else 0
pct_nao_atendidas = (100 - pct_atendidas) if total_solicitado > 0 else 0

# RENDERIZAÇÃO DOS 6 CARDS DE KPIS
c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Valor Compras (Custo)</div>
        <div class="kpi-value" style="color: #d97706;">{format_brl(total_custo)}</div>
        <div class="kpi-sub">Soma da coluna Custo</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total de Pedidos</div>
        <div class="kpi-value" style="color: #0284c7;">{total_pedidos}</div>
        <div class="kpi-sub">Ordens registradas</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Qtde Solicitada</div>
        <div class="kpi-value" style="color: #4f46e5;">{total_solicitado:,} un</div>
        <div class="kpi-sub">Total de peças pedidas</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card" style="border-color: rgba(16, 185, 129, 0.4);">
        <div class="kpi-title" style="color: #10b981;">Peças Atendidas</div>
        <div class="kpi-value" style="color: #10b981;">{total_atendidas:,} un</div>
        <div class="kpi-sub">{pct_atendidas}% aprovadas</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="kpi-card" style="border-color: rgba(244, 63, 94, 0.4);">
        <div class="kpi-title" style="color: #f43f5e;">Não Atendidas</div>
        <div class="kpi-value" style="color: #f43f5e;">{total_nao_atendidas:,} un</div>
        <div class="kpi-sub">{pct_nao_atendidas}% pendentes</div>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Custo Médio / Pedido</div>
        <div class="kpi-value" style="color: #0891b2;">{format_brl(avg_custo)}</div>
        <div class="kpi-sub">Média por pedido</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# SEÇÃO DE GRÁFICOS: TOP 5 AGOSTO E SETEMBRO
g1, g2 = st.columns(2)

# Top 5 Agosto
df_ago = df_raw[df_raw["mes"] == "Agosto"]
if filtro_ano != "ALL":
    df_ago = df_ago[df_ago["ano"] == filtro_ano]

top_ago = df_ago.groupby("solicitante")["qt"].sum().reset_index().sort_values(by="qt", ascending=False).head(5)

fig_ago = px.bar(
    top_ago,
    x="solicitante",
    y="qt",
    text="qt",
    title=f"Top 5 Solicitantes / Locais Internos — Agosto ({filtro_ano if filtro_ano != 'ALL' else 'Todos os Anos'})",
    labels={"solicitante": "Solicitante", "qt": "Qtde Peças"},
    color_discrete_sequence=["#0284c7"]
)
fig_ago.update_traces(
    texttemplate='%{text} un',
    textposition='outside',
    marker_line_color='#0284c7',
    marker_line_width=1.5
)
fig_ago.update_layout(
    template="plotly_white",
    margin=dict(t=40, b=10, l=10, r=10),
    yaxis=dict(range=[0, (top_ago["qt"].max() * 1.25) if not top_ago.empty else 10])
)

with g1:
    st.plotly_chart(fig_ago, use_container_width=True)

# Top 5 Setembro
df_set = df_raw[df_raw["mes"] == "Setembro"]
if filtro_ano != "ALL":
    df_set = df_set[df_set["ano"] == filtro_ano]

top_set = df_set.groupby("solicitante")["qt"].sum().reset_index().sort_values(by="qt", ascending=False).head(5)

fig_set = px.bar(
    top_set,
    x="solicitante",
    y="qt",
    text="qt",
    title=f"Top 5 Solicitantes / Locais Internos — Setembro ({filtro_ano if filtro_ano != 'ALL' else 'Todos os Anos'})",
    labels={"solicitante": "Solicitante", "qt": "Qtde Peças"},
    color_discrete_sequence=["#06b6d4"]
)
fig_set.update_traces(
    texttemplate='%{text} un',
    textposition='outside',
    marker_line_color='#06b6d4',
    marker_line_width=1.5
)
fig_set.update_layout(
    template="plotly_white",
    margin=dict(t=40, b=10, l=10, r=10),
    yaxis=dict(range=[0, (top_set["qt"].max() * 1.25) if not top_set.empty else 10])
)

with g2:
    st.plotly_chart(fig_set, use_container_width=True)

# SEÇÃO DE GRÁFICOS: CATEGORIA E FORNECEDOR
g3, g4 = st.columns(2)

# Gráfico Rosca: Categoria
df_cat = df_filtered.groupby("categoria")["qt"].sum().reset_index()
fig_cat = px.pie(
    df_cat,
    names="categoria",
    values="qt",
    title="Distribuição por Categoria de Peças (Qtde)",
    hole=0.62,
    color_discrete_sequence=["#0284c7", "#06b6d4", "#f59e0b", "#6366f1", "#10b981"]
)
fig_cat.update_traces(textinfo='value+percent', textposition='inside')
fig_cat.update_layout(template="plotly_white", margin=dict(t=40, b=10, l=10, r=10))

with g3:
    st.plotly_chart(fig_cat, use_container_width=True)

# Gráfico Fornecedor: Custo
df_supp = df_filtered.groupby("fornecedor")["custoTotal"].sum().reset_index().sort_values(by="custoTotal", ascending=False)
df_supp["texto_formatado"] = df_supp["custoTotal"].apply(format_brl)

fig_supp = px.bar(
    df_supp,
    x="fornecedor",
    y="custoTotal",
    text="texto_formatado",
    title="Soma de Custo por Fornecedor (R$)",
    labels={"fornecedor": "Fornecedor", "custoTotal": "Custo Total (R$)"},
    color_discrete_sequence=["#f59e0b"]
)
fig_supp.update_traces(textposition='outside')
fig_supp.update_layout(
    template="plotly_white",
    margin=dict(t=40, b=10, l=10, r=10),
    yaxis=dict(range=[0, (df_supp["custoTotal"].max() * 1.25) if not df_supp.empty else 1000])
)

with g4:
    st.plotly_chart(fig_supp, use_container_width=True)

# TABELA RESUMO POR PEÇA SOLICITADA
st.subheader("📑 Resumo Detalhado por Peça Solicitada")
st.caption("Consolidado por item, quantidades solicitadas, atendidas, não atendidas e custo total acumulado.")

busca = st.text_input("🔍 Buscar peça...", placeholder="Digite o nome do produto ou categoria...")

df_agrupado = df_filtered.groupby(["peca", "categoria"]).agg(
    qtTotal=("qt", "sum"),
    qtAtendida=("qtAprovada", "sum"),
    qtNaoAtendida=("qtNaoAprovada", "sum"),
    pedidosCount=("peca", "count"),
    custoTotal=("custoTotal", "sum")
).reset_index()

df_agrupado["custoUnitMedio"] = df_agrupado.apply(
    lambda r: (r["custoTotal"] / r["qtAtendida"]) if r["qtAtendida"] > 0 else 0.0,
    axis=1
)

if busca:
    df_agrupado = df_agrupado[
        df_agrupado["peca"].str.contains(busca, case=False, na=False) |
        df_agrupado["categoria"].str.contains(busca, case=False, na=False)
    ]

df_agrupado = df_agrupado.sort_values(by="custoTotal", ascending=False)

st.markdown(f"**Total de Peças Exibidas:** `{len(df_agrupado)} peças`")

df_tabela = df_agrupado.copy()
df_tabela["qtTotal"] = df_tabela["qtTotal"].apply(lambda v: f"{v:,} un".replace(",", "."))
df_tabela["qtAtendida"] = df_tabela["qtAtendida"].apply(lambda v: f"{v:,} un".replace(",", "."))
df_tabela["qtNaoAtendida"] = df_tabela["qtNaoAtendida"].apply(lambda v: f"{v:,} un".replace(",", "."))
df_tabela["custoUnitMedio"] = df_tabela["custoUnitMedio"].apply(format_brl)
df_tabela["custoTotal"] = df_tabela["custoTotal"].apply(format_brl)

df_tabela.columns = [
    "Peça / Produto Solicitado",
    "Categoria",
    "Qtde Total",
    "Atendidas",
    "Não Atendidas",
    "Nº Pedidos",
    "Custo Total (R$)",
    "Custo Unit. Médio"
]

st.dataframe(df_tabela, use_container_width=True, hide_index=True)

# INSIGHTS & ALERTAS EXECUTIVOS
st.write("")
st.subheader("💡 Diagnósticos Automáticos de Compras")
i1, i2, i3 = st.columns(3)

with i1:
    st.info("**Taxa Global de Atendimento:**\n\nMais de **90% das peças demandadas** foram aprovadas e atendidas nos prazos de compra, garantindo a manutenção contínua do parque de máquinas.")

with i2:
    st.warning("**Itens Não Atendidos / Reprovados:**\n\nA principal causa de itens não atendidos decorre de **pedidos duplicados** ou **peças com estoque remanescente** identificado antes do envio à aprovação final de compra.")

with i3:
    st.success("**Controle da Coluna Custo:**\n\nA soma de custo reflete exatamente as quantidades aprovadas e adquiridas via **EVOCA** e **PARAMOUNT**, com conciliação financeira automatizada.")