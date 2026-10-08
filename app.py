import streamlit as st
import pandas as pd
import datetime
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestão de Pedidos de Compras",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS MODERNO CORPORATIVO LIGHT ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #F8FAFC !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
        color: #0F172A !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}

    /* Topbar */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        padding: 16px 24px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .top-header h1 {
        font-size: 20px;
        font-weight: 700;
        margin: 0;
        color: #0F172A;
    }
    .top-header span {
        font-size: 13px;
        color: #64748B;
    }

    /* Cards e Containers */
    .saas-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }

    .card-title {
        font-size: 15px;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 16px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 8px;
    }

    /* Abas superiores estilizadas */
    button[data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #64748B !important;
        padding: 10px 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2563EB !important;
        border-bottom-color: #2563EB !important;
    }

    /* Inputs e Controles */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input {
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        font-size: 14px !important;
        color: #0F172A !important;
    }

    /* Botões */
    .stButton button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 8px 18px !important;
    }
    .stButton button[kind="primary"] {
        background-color: #2563EB !important;
        border: 1px solid #1D4ED8 !important;
        color: #FFFFFF !important;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #1D4ED8 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CONSTANTES E PLANILHA ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1iWjdaZLAp5hi9YIhmfSO4cPBn6fkfDjef8PAdZp1nsY/edit"
ABA_PEDIDOS_NOME = "Ordem de Compra(Peças)"
ABA_PECAS_NOME = "Base de Dados"
CREDENTIALS_FILE = "credentials.json"

# --- CONEXÃO COM GOOGLE SHEETS ---
@st.cache_resource
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Tentativa 1: secrets.toml
    if "gcp_service_account" in st.secrets:
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                dict(st.secrets["gcp_service_account"]), scope
            )
            return gspread.authorize(creds)
        except Exception:
            pass

    # Tentativa 2: credentials.json local
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(data, scope)
                    return gspread.authorize(creds)
        except Exception:
            return None

    return None

def get_worksheet(title_or_id):
    client = get_gspread_client()
    if not client:
        return None
    try:
        sh = client.open_by_url(SPREADSHEET_URL)
        for ws in sh.worksheets():
            if str(ws.id) == str(title_or_id) or ws.title == str(title_or_id):
                return ws
        return sh.sheet1
    except Exception as e:
        st.error(f"Erro de conexão com o Google Sheets: {e}")
        return None

@st.cache_data(ttl=300)
def carregar_base_pecas():
    ws = get_worksheet(ABA_PECAS_NOME)
    if not ws:
        return pd.DataFrame(columns=["Código", "Produto", "Fornecedor", "Rotulo"])
    try:
        linhas = ws.get_all_values()
        if len(linhas) <= 1:
            return pd.DataFrame(columns=["Código", "Produto", "Fornecedor", "Rotulo"])
        
        df = pd.DataFrame(linhas[1:])
        cod = df[0].astype(str).str.strip() if 0 in df.columns else ""
        nome = df[1].astype(str).str.strip() if 1 in df.columns else ""
        forn = df[5].astype(str).str.strip() if 5 in df.columns else ""

        res = pd.DataFrame({"Código": cod, "Produto": nome, "Fornecedor": forn})
        res = res[(res["Código"] != "") | (res["Produto"] != "")]
        res["Rotulo"] = res["Código"] + " — " + res["Produto"]
        return res
    except Exception:
        return pd.DataFrame(columns=["Código", "Produto", "Fornecedor", "Rotulo"])

# --- BANNER SUPERIOR ---
st.markdown("""
<div class="top-header">
    <div>
        <h1>📦 Central de Compras</h1>
        <span>Gestão de Suprimentos & Ordens de Compra</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Verificação de credenciais
client_ok = get_gspread_client()
if not client_ok:
    st.warning("⚠️ **Autenticação pendente:** Adicione o arquivo `credentials.json` na raiz da pasta do projeto para sincronizar com o Google Sheets.")

base_pecas = carregar_base_pecas()

# --- NAVEGAÇÃO PRINCIPAL NO TOPO ---
tab_novo, tab_consulta = st.tabs(["➕ Novo Pedido de Compra", "🔍 Pesquisar / Editar Ordem"])

# ========================================================
# ABA 1: NOVO PEDIDO DE COMPRA
# ========================================================
with tab_novo:
    # 1. Cabeçalho da Ordem
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">1. Dados Gerais da Ordem</div>', unsafe_allow_html=True)
    c_oc1, c_oc2, c_oc3 = st.columns([1.5, 1, 1])
    with c_oc1:
        ordem_num = st.text_input("Ordem de Compra *", placeholder="Ex: OC-2026-001")
    with c_oc2:
        data_ped = st.date_input("Data do Pedido", value=datetime.date.today())
    with c_oc3:
        hora_ped = st.time_input("Horário de Chegada", value=datetime.datetime.now().time())
    st.markdown('</div>', unsafe_allow_html=True)

    # Inicialização do carrinho
    if "carrinho_itens" not in st.session_state:
        st.session_state.carrinho_itens = []

    # 2. Formulário de Peça
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">2. Inclusão de Peça / Item</div>', unsafe_allow_html=True)

    lista_opcoes = [""] + list(base_pecas["Rotulo"].values) if not base_pecas.empty else [""]
    peca_busca = st.selectbox("Pesquisar na Base de Peças:", lista_opcoes, index=0)

    # Defaults baseados na busca
    p_cod, p_nome, p_forn = "", "", ""
    if peca_busca:
        match = base_pecas[base_pecas["Rotulo"] == peca_busca].iloc[0]
        p_cod, p_nome, p_forn = match["Código"], match["Produto"], match["Fornecedor"]

    f1, f2, f3 = st.columns(3)
    with f1:
        in_cod = st.text_input("Código do Produto *", value=p_cod)
        in_cat = st.text_input("Categoria", placeholder="Ex: Multi Bebidas, Elétrica")
        in_forn = st.text_input("Fornecedor", value=p_forn)

    with f2:
        in_nome = st.text_input("Produto *", value=p_nome)
        in_q_solic = st.number_input("Qt Solicitada", min_value=0.0, step=1.0, value=1.0)
        in_q_aprov = st.number_input("Qt Aprovada", min_value=0.0, step=1.0, value=0.0)
        in_q_nao_aprov = st.number_input("Qt Não Aprovada", min_value=0.0, step=1.0, value=0.0)

    with f3:
        in_cod_forn = st.text_input("Cod da Peça do Fornecedor")
        in_vlr_compra = st.number_input("Valor de Compra (R$)", min_value=0.0, step=0.01, format="%.2f")
        in_vlr_venda = st.number_input("Valor de Venda (R$)", min_value=0.0, step=0.01, format="%.2f")
        in_obs = st.text_input("Observação")

    if st.button("➕ Adicionar Peça", type="secondary"):
        if not in_cod.strip() or not in_nome.strip():
            st.error("Preencha o Código e o Nome do Produto antes de adicionar.")
        else:
            st.session_state.carrinho_itens.append({
                "Ordem de Compra": ordem_num,
                "Codigo do Produto": in_cod,
                "Produto": in_nome,
                "Categoria": in_cat,
                "Data do pedido": data_ped.strftime("%d/%m/%Y"),
                "Horário de chegada": hora_ped.strftime("%H:%M:%S"),
                "Valor de Compra": f"R$ {in_vlr_compra:.2f}",
                "Qt Solicitada": in_q_solic,
                "QT Aprovada": in_q_aprov,
                "Qt Não Aprovada": in_q_nao_aprov,
                "Valor de Venda": f"R$ {in_vlr_venda:.2f}",
                "Fornecedor": in_forn,
                "Cod da Peça do Fornecedor": in_cod_forn,
                "Observações": in_obs
            })
            st.success(f"Item '{in_nome}' inserido com sucesso!")
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Lista de Peças e Gravação
    if st.session_state.carrinho_itens:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">3. Peças Adicionadas ({len(st.session_state.carrinho_itens)})</div>', unsafe_allow_html=True)
        
        df_itens = pd.DataFrame(st.session_state.carrinho_itens)
        st.dataframe(df_itens, use_container_width=True, hide_index=True)

        btn_c1, btn_c2, _ = st.columns([1.5, 1, 3])
        with btn_c1:
            if st.button("💾 Enviar Pedido para a Planilha", type="primary", use_container_width=True):
                if not ordem_num.strip():
                    st.error("Informe a Ordem de Compra antes de enviar.")
                else:
                    ws_pedidos = get_worksheet(ABA_PEDIDOS_NOME)
                    if ws_pedidos:
                        try:
                            for it in st.session_state.carrinho_itens:
                                it["Ordem de Compra"] = ordem_num
                            dados_envio = [list(it.values()) for it in st.session_state.carrinho_itens]
                            ws_pedidos.append_rows(dados_envio)
                            st.success("Pedido gravado com sucesso na planilha!")
                            st.session_state.carrinho_itens = []
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar na planilha: {e}")
        with btn_c2:
            if st.button("🗑️ Limpar Todos", use_container_width=True):
                st.session_state.carrinho_itens = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ========================================================
# ABA 2: PESQUISAR E EDITAR ORDEM
# ========================================================
with tab_consulta:
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Localizar Ordem de Compra</div>', unsafe_allow_html=True)
    
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        busca_oc = st.text_input("Número da Ordem de Compra:", placeholder="Digite o número exato, ex: OC-2026-001")
    with sc2:
        st.write("")
        st.write("")
        btn_busca = st.button("🔍 Buscar", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if btn_busca or ("filtro_oc" in st.session_state and st.session_state.filtro_oc == busca_oc):
        if busca_oc.strip():
            st.session_state.filtro_oc = busca_oc
            ws = get_worksheet(ABA_PEDIDOS_NOME)
            if ws:
                todas_linhas = ws.get_all_values()
                if len(todas_linhas) <= 1:
                    st.info("Nenhum registro encontrado na planilha.")
                else:
                    headers = todas_linhas[0]
                    rows = todas_linhas[1:]
                    df_base = pd.DataFrame(rows, columns=headers)

                    col_ordem = headers[0]
                    filtrados = df_base[df_base[col_ordem].astype(str).str.strip() == busca_oc.strip()]

                    if filtrados.empty:
                        st.warning(f"Nenhum pedido encontrado para '{busca_oc}'.")
                    else:
                        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-title">Itens Encontrados ({len(filtrados)})</div>', unsafe_allow_html=True)
                        
                        filtrados["Linha Planilha"] = filtrados.index + 2
                        st.dataframe(filtrados, use_container_width=True, hide_index=True)

                        st.markdown('<div class="card-title" style="margin-top: 20px;">Editar Registro</div>', unsafe_allow_html=True)
                        opcoes_edicao = [
                            f"Linha {r['Linha Planilha']} — {r.get('Produto', '')}"
                            for _, r in filtrados.iterrows()
                        ]
                        selecionado = st.selectbox("Escolha o item para alteração:", opcoes_edicao)
                        num_linha = int(selecionado.split(" ")[1])
                        dados_atuais = df_base.loc[num_linha - 2].to_dict()

                        with st.form("form_edicao"):
                            cols = st.columns(3)
                            campos_novos = {}
                            for i, h in enumerate(headers):
                                with cols[i % 3]:
                                    campos_novos[h] = st.text_input(f"{h}", value=str(dados_atuais.get(h, "")))

                            if st.form_submit_button("💾 Salvar Alterações", type="primary"):
                                try:
                                    linha_editada = [campos_novos[h] for h in headers]
                                    fim_col = chr(65 + len(headers) - 1)
                                    ws.update(f"A{num_linha}:{fim_col}{num_linha}", [linha_editada])
                                    st.success(f"Linha {num_linha} atualizada com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar edição: {e}")
                        st.markdown('</div>', unsafe_allow_html=True)