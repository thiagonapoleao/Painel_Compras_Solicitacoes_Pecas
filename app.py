import streamlit as st
import pandas as pd
import datetime
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Portal de Compras | Gestão Corporativa",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PERSONALIZADO: DESIGN MODERNO CORPORATIVO LIGHT ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #F8FAFC !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #0F172A !important;
    }

    /* Ocultar elementos desnecessários do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}

    /* Barra Superior / Navbar */
    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        padding: 14px 28px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        margin-bottom: 24px;
    }

    .brand-title {
        font-size: 20px;
        font-weight: 700;
        color: #1E293B;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-badge {
        font-size: 11px;
        font-weight: 600;
        color: #2563EB;
        background: #EFF6FF;
        padding: 3px 8px;
        border-radius: 20px;
        border: 1px solid #DBEAFE;
    }

    /* Cartões Corporativos */
    .saas-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
    }

    .card-heading {
        font-size: 16px;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 10px;
    }

    /* Inputs e Controles */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input, .stSelectbox [data-baseweb="select"] {
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-size: 14px !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 1px #2563EB !important;
    }

    /* Botões */
    .stButton button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 8px 16px !important;
        transition: all 0.15s ease-in-out !important;
    }

    .stButton button[kind="primary"] {
        background-color: #2563EB !important;
        border: 1px solid #1D4ED8 !important;
        color: #FFFFFF !important;
        box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2) !important;
    }

    .stButton button[kind="primary"]:hover {
        background-color: #1D4ED8 !important;
    }

    /* Radio do Menu Superior (Estilizado como segmented tabs) */
    div[data-testid="stRadio"] > div {
        display: flex;
        flex-direction: row;
        background: #F1F5F9;
        padding: 4px;
        border-radius: 10px;
        gap: 6px;
    }

    div[data-testid="stRadio"] label {
        background: transparent;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        cursor: pointer;
        transition: all 0.2s;
    }

    /* Contador Badge */
    .counter-badge {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        font-weight: 600;
        font-size: 12px;
        padding: 2px 10px;
        border-radius: 12px;
        border: 1px solid #BFDBFE;
    }
</style>
""", unsafe_allow_html=True)

# URL da Planilha e Abas
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1iWjdaZLAp5hi9YIhmfSO4cPBn6fkfDjef8PAdZp1nsY/edit"
ABA_PEDIDOS_NOME = "Ordem de Compra(Peças)"
ABA_PECAS_NOME = "Base de Dados"

# --- AUTENTICAÇÃO COM GOOGLE SHEETS ---
@st.cache_resource
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # 1. Tentar st.secrets
    if "gcp_service_account" in st.secrets:
        try:
            creds_info = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
            return gspread.authorize(creds)
        except Exception:
            pass

    # 2. Tentar credentials.json local
    caminho_cred = "credentials.json"
    if os.path.exists(caminho_cred):
        try:
            with open(caminho_cred, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if conteudo:
                    creds_dict = json.loads(conteudo)
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                    return gspread.authorize(creds)
        except Exception as e:
            st.error(f"Erro no arquivo credentials.json: {e}")
            return None

    return None

# --- CARREGAR BASE DE REFERÊNCIA ---
@st.cache_data(ttl=300)
def load_pecas_reference():
    client = get_gspread_client()
    if not client:
        return pd.DataFrame(columns=["Código", "Produto", "Fornecedor", "Display"])
    try:
        sh = client.open_by_url(SPREADSHEET_URL)
        ws = next((w for w in sh.worksheets() if str(w.id) == "270834817" or w.title == ABA_PECAS_NOME), sh.sheet1)
        valores = ws.get_all_values()
        if len(valores) <= 1:
            return pd.DataFrame(columns=["Código", "Produto", "Fornecedor", "Display"])
        
        df = pd.DataFrame(valores[1:])
        cod = df[0].astype(str).str.strip() if 0 in df.columns else ""
        nome = df[1].astype(str).str.strip() if 1 in df.columns else ""
        forn = df[5].astype(str).str.strip() if 5 in df.columns else ""
        
        ref_df = pd.DataFrame({"Código": cod, "Produto": nome, "Fornecedor": forn})
        ref_df = ref_df[(ref_df["Código"] != "") | (ref_df["Produto"] != "")]
        ref_df["Display"] = ref_df["Código"] + " - " + ref_df["Produto"]
        return ref_df
    except Exception as e:
        st.error(f"Erro ao carregar peças: {e}")
        return pd.DataFrame(columns=["Código", "Produto", "Fornecedor", "Display"])

def get_pedidos_worksheet():
    client = get_gspread_client()
    if not client:
        return None
    sh = client.open_by_url(SPREADSHEET_URL)
    for w in sh.worksheets():
        if str(w.id) == "643448898" or w.title == ABA_PEDIDOS_NOME:
            return w
    return sh.sheet1

# --- HEADER SUPERIOR COM LOGO E MENU INTEGRADO ---
header_col1, header_col2 = st.columns([1, 1.4])

with header_col1:
    st.markdown("""
        <div style="padding-top: 8px;">
            <span style="font-size: 22px; font-weight: 700; color: #0F172A;">📦 Sistema de Compras</span>
            <span class="brand-badge">Enterprise</span>
        </div>
    """, unsafe_allow_html=True)

with header_col2:
    aba_selecionada = st.radio(
        label="Navegação",
        options=["➕ Novo Pedido de Compra", "🔍 Pesquisar / Editar Ordem"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

st.markdown("<hr style='margin-top: 6px; margin-bottom: 24px; border: 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

# Verificação inicial de credenciais
client_google = get_gspread_client()
if not client_google:
    st.info("💡 **Atenção:** Coloque o arquivo de autenticação `credentials.json` na mesma pasta da aplicação para salvar diretamente na planilha do Google.")

ref_pecas = load_pecas_reference()

# ========================================================
# VIEW 1: NOVO PEDIDO DE COMPRA
# ========================================================
if aba_selecionada == "➕ Novo Pedido de Compra":
    
    # Seção 1: Identificação da Ordem
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-heading">🏷️ Dados Principais da Ordem</div>', unsafe_allow_html=True)
    
    col_oc1, col_oc2, col_oc3 = st.columns([1.5, 1, 1])
    with col_oc1:
        ordem_compra = st.text_input("Ordem de Compra *", placeholder="Ex: OC-2026-001")
    with col_oc2:
        data_pedido = st.date_input("Data do Pedido", value=datetime.date.today())
    with col_oc3:
        horario_chegada = st.time_input("Horário de Chegada", value=datetime.datetime.now().time())
    st.markdown('</div>', unsafe_allow_html=True)

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    # Seção 2: Adição de Itens / Peças
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-heading">🔧 Seleção de Peças e Quantidades</div>', unsafe_allow_html=True)

    # Busca inteligente com autocompletar
    opcoes = [""] + list(ref_pecas["Display"].values) if not ref_pecas.empty else [""]
    peca_sel = st.selectbox("🔎 Pesquisar Peça na Tabela de Referência:", opcoes, index=0)

    val_cod = ""
    val_nome = ""
    val_forn = ""
    if peca_sel:
        filtro = ref_pecas[ref_pecas["Display"] == peca_sel].iloc[0]
        val_cod = filtro["Código"]
        val_nome = filtro["Produto"]
        val_forn = filtro["Fornecedor"]

    c_item1, c_item2, c_item3 = st.columns(3)
    with c_item1:
        cod_produto = st.text_input("Código do Produto *", value=val_cod)
        categoria = st.text_input("Categoria", placeholder="Ex: Multi Bebidas, Peças, Elétrica")
        fornecedor = st.text_input("Fornecedor", value=val_forn)

    with c_item2:
        produto_nome = st.text_input("Produto *", value=val_nome)
        q_solic = st.number_input("Qt Solicitada", min_value=0.0, step=1.0, value=1.0)
        q_aprov = st.number_input("Qt Aprovada", min_value=0.0, step=1.0, value=0.0)
        q_nao_aprov = st.number_input("Qt Não Aprovada", min_value=0.0, step=1.0, value=0.0)

    with c_item3:
        cod_peca_forn = st.text_input("Cód da Peça do Fornecedor")
        vlr_compra = st.number_input("Valor de Compra (R$)", min_value=0.0, step=0.01, format="%.2f")
        vlr_venda = st.number_input("Valor de Venda (R$)", min_value=0.0, step=0.01, format="%.2f")
        obs = st.text_input("Observação")

    btn_add = st.button("➕ Inserir Peça no Pedido", type="secondary")
    if btn_add:
        if not cod_produto or not produto_nome:
            st.error("Informe o Código e o Nome do Produto antes de adicionar.")
        else:
            st.session_state.carrinho.append({
                "Ordem de Compra": ordem_compra,
                "Codigo do Produto": cod_produto,
                "Produto": produto_nome,
                "Categoria": categoria,
                "Data do pedido": data_pedido.strftime("%d/%m/%Y"),
                "Horário de chegada": horario_chegada.strftime("%H:%M:%S"),
                "Valor de Compra": f"R$ {vlr_compra:.2f}",
                "Qt Solicitada": q_solic,
                "QT Aprovada": q_aprov,
                "Qt Não Aprovada": q_nao_aprov,
                "Valor de Venda": f"R$ {vlr_venda:.2f}",
                "Fornecedor": fornecedor,
                "Cod da Peça do Fornecedor": cod_peca_forn,
                "Observações": obs
            })
            st.success(f"Item '{produto_nome}' adicionado com sucesso!")
    st.markdown('</div>', unsafe_allow_html=True)

    # Seção 3: Itens no Carrinho / Envio
    if st.session_state.carrinho:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-heading">📋 Itens Inclusos nesta Ordem <span class="counter-badge">{len(st.session_state.carrinho)} item(s)</span></div>', unsafe_allow_html=True)
        
        df_carrinho = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_carrinho, use_container_width=True)

        col_save, col_clear, _ = st.columns([1.5, 1, 3])
        with col_save:
            if st.button("💾 Gravar Todos na Planilha", type="primary", use_container_width=True):
                if not ordem_compra.strip():
                    st.error("Preencha o campo 'Ordem de Compra' antes de salvar.")
                else:
                    ws = get_pedidos_worksheet()
                    if ws:
                        try:
                            for it in st.session_state.carrinho:
                                it["Ordem de Compra"] = ordem_compra
                            linhas = [list(it.values()) for it in st.session_state.carrinho]
                            ws.append_rows(linhas)
                            st.success(f"{len(linhas)} registro(s) enviados para a planilha!")
                            st.session_state.carrinho = []
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar na planilha: {e}")
        with col_clear:
            if st.button("🗑️ Limpar Lista", use_container_width=True):
                st.session_state.carrinho = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ========================================================
# VIEW 2: PESQUISAR E EDITAR
# ========================================================
elif aba_selecionada == "🔍 Pesquisar / Editar Ordem":
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-heading">🔍 Buscar Pedidos Cadastrados</div>', unsafe_allow_html=True)
    
    col_b1, col_b2 = st.columns([3, 1])
    with col_b1:
        oc_pesquisa = st.text_input("Digite o número da Ordem de Compra:", placeholder="Ex: OC-2026-001")
    with col_b2:
        st.write("")
        st.write("")
        btn_buscar = st.button("Buscar Ordem", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if btn_buscar or ("oc_atual" in st.session_state and st.session_state.oc_atual == oc_pesquisa):
        if oc_pesquisa:
            st.session_state.oc_atual = oc_pesquisa
            ws = get_pedidos_worksheet()
            if ws:
                valores = ws.get_all_values()
                if not valores:
                    st.info("A planilha de pedidos está sem registros.")
                else:
                    cabecalhos = valores[0]
                    dados = valores[1:]
                    df = pd.DataFrame(dados, columns=cabecalhos)
                    
                    col_oc = cabecalhos[0]
                    filtrados = df[df[col_oc].astype(str).str.strip() == oc_pesquisa.strip()]

                    if filtrados.empty:
                        st.warning(f"Nenhum pedido encontrado para a Ordem '{oc_pesquisa}'.")
                    else:
                        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-heading">Resultados Encontrados ({len(filtrados)})</div>', unsafe_allow_html=True)
                        filtrados["Linha_Planilha"] = filtrados.index + 2
                        st.dataframe(filtrados, use_container_width=True)

                        st.markdown("---")
                        st.markdown('<div class="card-heading">✏️ Editar Item Selecionado</div>', unsafe_allow_html=True)
                        
                        opcoes_itens = [
                            f"Linha {row['Linha_Planilha']} | {row.get('Produto', '')}"
                            for _, row in filtrados.iterrows()
                        ]
                        item_escolhido = st.selectbox("Selecione qual item deseja alterar:", opcoes_itens)
                        linha_num = int(item_escolhido.split(" ")[1])
                        registro = df.loc[linha_num - 2].to_dict()

                        with st.form("form_edicao"):
                            cols_edit = st.columns(3)
                            campos_novos = {}
                            for idx, c in enumerate(cabecalhos):
                                with cols_edit[idx % 3]:
                                    campos_novos[c] = st.text_input(f"{c}", value=str(registro.get(c, "")))
                            
                            salvar_edicao = st.form_submit_button("💾 Salvar Alterações na Planilha")
                            if salvar_edicao:
                                try:
                                    dados_atualizados = [campos_novos[c] for c in cabecalhos]
                                    col_fim = chr(65 + len(cabecalhos) - 1)
                                    ws.update(f"A{linha_num}:{col_fim}{linha_num}", [dados_atualizados])
                                    st.success(f"Linha {linha_num} atualizada com sucesso na planilha!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar edição: {e}")
                        st.markdown('</div>', unsafe_allow_html=True)