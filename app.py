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
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FORÇAR TEMA CLARO CORPORATIVO VIA CSS ---
st.markdown("""
<style>
    /* Forçar fundo claro geral */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }

    /* Cartões Corporativos */
    .corp-card {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    .corp-title {
        font-size: 22px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }

    .corp-subtitle {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 18px;
    }

    /* Inputs e Caixas de Texto com visual limpo e claro */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input, .stSelectbox div {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border-color: #CBD5E1 !important;
        border-radius: 6px !important;
    }

    /* Botão Principal */
    .stButton > button[kind="primary"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600;
        border-radius: 6px;
    }

    .stButton > button[kind="secondary"] {
        background-color: #F1F5F9 !important;
        color: #334155 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# URL da Planilha e nomes das abas conforme a planilha real
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1iWjdaZLAp5hi9YIhmfSO4cPBn6fkfDjef8PAdZp1nsY/edit"
ABA_PEDIDOS_NOME = "Ordem de Compra(Peças)"
ABA_PECAS_NOME = "Base de Dados"

# --- AUTENTICAÇÃO COM TRATAMENTO DE ERRO CLARO ---
@st.cache_resource
def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # 1. Tentar ler de st.secrets (caso esteja configurado no Streamlit Cloud ou secrets.toml)
    if "gcp_service_account" in st.secrets:
        try:
            creds_info = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
            return gspread.authorize(creds)
        except Exception as e:
            st.error(f"Erro ao ler credenciais de st.secrets: {e}")

    # 2. Tentar ler de arquivo local credentials.json
    caminho_cred = "credentials.json"
    if not os.path.exists(caminho_cred):
        st.warning("""
        ⚠️ **Arquivo de Credenciais não encontrado!**
        
        Para conectar à planilha do Google:
        1. Baixe o arquivo JSON da sua Conta de Serviço no Google Cloud Console.
        2. Salve-o como **`credentials.json`** na mesma pasta deste arquivo `app.py`.
        3. Certifique-se de que o e-mail da Conta de Serviço tenha permissão de **Editor** na planilha.
        """)
        return None

    try:
        with open(caminho_cred, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            if not conteudo:
                st.error("O arquivo `credentials.json` está totalmente vazio (0 bytes). Baixe a chave JSON novamente.")
                return None
            creds_dict = json.loads(conteudo)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            return gspread.authorize(creds)
    except json.JSONDecodeError as jde:
        st.error(f"O arquivo `credentials.json` não é um JSON válido: {jde}")
        return None
    except Exception as e:
        st.error(f"Falha na autenticação com Google Drive/Sheets: {e}")
        return None

# --- CARREGAR BASE DE PEÇAS ---
@st.cache_data(ttl=300)
def load_pecas_reference():
    client = get_gspread_client()
    if not client:
        return pd.DataFrame(columns=["Código", "Produto", "Fornecedor", "Display"])
    
    try:
        sh = client.open_by_url(SPREADSHEET_URL)
        # Tenta pegar pela aba "Base de Dados" ou gid 270834817
        ws = None
        for w in sh.worksheets():
            if str(w.id) == "270834817" or w.title == ABA_PECAS_NOME:
                ws = w
                break
        if not ws:
            ws = sh.sheet1

        todos_valores = ws.get_all_values()
        if len(todos_valores) <= 1:
            return pd.DataFrame(columns=["Código", "Produto", "Fornecedor", "Display"])
        
        df = pd.DataFrame(todos_valores[1:])
        
        # Coluna A (0) = Código/Produto, Coluna B (1) = Descrição/Nome, Coluna F (5) = Fornecedor
        cod = df[0].astype(str).str.strip() if 0 in df.columns else ""
        nome = df[1].astype(str).str.strip() if 1 in df.columns else ""
        forn = df[5].astype(str).str.strip() if 5 in df.columns else ""
        
        ref_df = pd.DataFrame({
            "Código": cod,
            "Produto": nome,
            "Fornecedor": forn
        })
        
        # Filtra registros vazios
        ref_df = ref_df[(ref_df["Código"] != "") | (ref_df["Produto"] != "")]
        ref_df["Display"] = ref_df["Código"] + " - " + ref_df["Produto"]
        return ref_df
    except Exception as e:
        st.error(f"Erro ao ler aba de peças: {e}")
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

# --- MENU DE NAVEGAÇÃO ---
menu = st.sidebar.radio(
    "Menu do Sistema",
    ["➕ Novo Pedido de Compra", "🔍 Pesquisar / Editar Ordem"],
    index=0
)

ref_pecas = load_pecas_reference()

# ========================================================
# 1. NOVO PEDIDO DE COMPRA
# ========================================================
if menu == "➕ Novo Pedido de Compra":
    st.markdown('<div class="corp-title">Formulário de Pedido de Compras</div>', unsafe_allow_html=True)
    st.markdown('<div class="corp-subtitle">Preencha os dados da Ordem de Compra e inclua múltiplas peças antes de enviar.</div>', unsafe_allow_html=True)

    # Dados da Ordem
    st.markdown('<div class="corp-card">', unsafe_allow_html=True)
    st.markdown("##### 📌 Identificação da Ordem")
    c1, c2, c3 = st.columns(3)
    with c1:
        ordem_compra = st.text_input("Ordem de Compra *", placeholder="Ex: OC-2026-001")
    with c2:
        # Data do pedido mantida na data atual
        data_pedido = st.date_input("Data do Pedido", value=datetime.date.today())
    with c3:
        horario_chegada = st.time_input("Horário de Chegada do Pedido", value=datetime.datetime.now().time())
    st.markdown('</div>', unsafe_allow_html=True)

    if "carrinho_pecas" not in st.session_state:
        st.session_state.carrinho_pecas = []

    # Inclusão de Peças
    st.markdown('<div class="corp-card">', unsafe_allow_html=True)
    st.markdown("##### 🔍 Localizar e Adicionar Peça")
    
    opcoes = [""] + list(ref_pecas["Display"].values) if not ref_pecas.empty else [""]
    peca_sel = st.selectbox("Pesquisar por Código ou Descrição da Peça:", opcoes, index=0)
    
    def_cod = ""
    def_nome = ""
    def_forn = ""
    if peca_sel:
        match = ref_pecas[ref_pecas["Display"] == peca_sel].iloc[0]
        def_cod = match["Código"]
        def_nome = match["Produto"]
        def_forn = match["Fornecedor"]
        
    p1, p2, p3 = st.columns(3)
    with p1:
        cod_prod = st.text_input("Código do Produto *", value=def_cod)
        categoria = st.text_input("Categoria", placeholder="Ex: Multi Bebidas, Peças, Elétrica")
        fornecedor = st.text_input("Fornecedor", value=def_forn)
    with p2:
        prod_nome = st.text_input("Produto *", value=def_nome)
        qt_solic = st.number_input("Qt Solicitada", min_value=0.0, step=1.0, value=1.0)
        qt_aprov = st.number_input("Qt Aprovada", min_value=0.0, step=1.0, value=0.0)
        qt_nao_aprov = st.number_input("Qt Não Aprovada", min_value=0.0, step=1.0, value=0.0)
    with p3:
        cod_peca_forn = st.text_input("Cód da Peça do Fornecedor")
        vlr_compra = st.number_input("Valor de Compra (R$)", min_value=0.0, step=0.01, format="%.2f")
        vlr_venda = st.number_input("Valor de Venda (R$)", min_value=0.0, step=0.01, format="%.2f")
        obs = st.text_input("Observação")

    btn_add = st.button("➕ Inserir Peça no Pedido", type="secondary")
    if btn_add:
        if not cod_prod or not prod_nome:
            st.warning("Código e Nome do Produto são obrigatórios.")
        else:
            st.session_state.carrinho_pecas.append({
                "Ordem de Compra": ordem_compra,
                "Codigo do Produto": cod_prod,
                "Produto": prod_nome,
                "Categoria": categoria,
                "Data do pedido": data_pedido.strftime("%d/%m/%Y"),
                "Horário de chegada": horario_chegada.strftime("%H:%M:%S"),
                "Valor de Compra": f"R$ {vlr_compra:.2f}",
                "Qt Solicitada": qt_solic,
                "QT Aprovada": qt_aprov,
                "Qt Não Aprovada": qt_nao_aprov,
                "Valor de Venda": f"R$ {vlr_venda:.2f}",
                "Fornecedor": fornecedor,
                "Cod da Peça do Fornecedor": cod_peca_forn,
                "Observações": obs
            })
            st.success(f"Item '{prod_nome}' adicionado à lista!")
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabela com as peças adicionadas
    if st.session_state.carrinho_pecas:
        st.markdown('<div class="corp-card">', unsafe_allow_html=True)
        st.markdown("##### 📋 Itens adicionados à esta Ordem:")
        df_carrinho = pd.DataFrame(st.session_state.carrinho_pecas)
        st.dataframe(df_carrinho, use_container_width=True)

        col_save, col_clear, _ = st.columns([2, 1, 3])
        with col_save:
            if st.button("💾 Salvar Todos os Itens na Planilha", type="primary", use_container_width=True):
                if not ordem_compra.strip():
                    st.error("Preencha o campo 'Ordem de Compra' antes de enviar.")
                else:
                    ws = get_pedidos_worksheet()
                    if ws:
                        try:
                            for it in st.session_state.carrinho_pecas:
                                it["Ordem de Compra"] = ordem_compra
                            linhas = [list(it.values()) for it in st.session_state.carrinho_pecas]
                            ws.append_rows(linhas)
                            st.success(f"{len(linhas)} peça(s) gravada(s) com sucesso na planilha!")
                            st.session_state.carrinho_pecas = []
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar na planilha: {e}")
        with col_clear:
            if st.button("🗑️ Limpar Itens", use_container_width=True):
                st.session_state.carrinho_pecas = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ========================================================
# 2. CONSULTAR E EDITAR ORDENS
# ========================================================
elif menu == "🔍 Pesquisar / Editar Ordem":
    st.markdown('<div class="corp-title">Consulta e Edição de Ordens de Compra</div>', unsafe_allow_html=True)
    st.markdown('<div class="corp-subtitle">Pesquise uma Ordem de Compra existente para consultar ou atualizar itens.</div>', unsafe_allow_html=True)

    st.markdown('<div class="corp-card">', unsafe_allow_html=True)
    oc_busca = st.text_input("Número da Ordem de Compra:")
    btn_pesquisa = st.button("Pesquisar Ordem", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    if btn_pesquisa or ("oc_ativa" in st.session_state and st.session_state.oc_ativa == oc_busca):
        if oc_busca:
            st.session_state.oc_ativa = oc_busca
            ws = get_pedidos_worksheet()
            if ws:
                valores = ws.get_all_values()
                if not valores:
                    st.info("A planilha de pedidos está sem dados.")
                else:
                    cabecalhos = valores[0]
                    dados = valores[1:]
                    df = pd.DataFrame(dados, columns=cabecalhos)
                    
                    col_oc_nome = cabecalhos[0]  # Geralmente Coluna A: "Ordem de Compra"
                    filtrados = df[df[col_oc_nome].astype(str).str.strip() == oc_busca.strip()]

                    if filtrados.empty:
                        st.warning(f"Nenhum registro encontrado com a Ordem de Compra '{oc_busca}'.")
                    else:
                        st.markdown('<div class="corp-card">', unsafe_allow_html=True)
                        st.markdown(f"##### Registros encontrados ({len(filtrados)} itens):")
                        filtrados["Linha_Planilha"] = filtrados.index + 2
                        st.dataframe(filtrados, use_container_width=True)

                        st.markdown("---")
                        st.markdown("##### ✏️ Editar um item:")
                        opcoes_select = [
                            f"Linha {row['Linha_Planilha']} | Item: {row.get('Produto', '')}" 
                            for _, row in filtrados.iterrows()
                        ]
                        selecao = st.selectbox("Escolha qual item editar:", opcoes_select)
                        linha_planilha = int(selecao.split(" ")[1])
                        
                        registro_atual = df.loc[linha_planilha - 2].to_dict()

                        with st.form("form_edicao"):
                            novos_dados = {}
                            cols = st.columns(3)
                            for idx, c in enumerate(cabecalhos):
                                with cols[idx % 3]:
                                    novos_dados[c] = st.text_input(f"{c}", value=str(registro_atual.get(c, "")))
                            
                            salvar_edicao = st.form_submit_button("💾 Salvar Alterações na Planilha")
                            if salvar_edicao:
                                try:
                                    linha_atualizada = [novos_dados[c] for c in cabecalhos]
                                    fim_coluna = chr(65 + len(cabecalhos) - 1)
                                    ws.update(f"A{linha_planilha}:{fim_coluna}{linha_planilha}", [linha_atualizada])
                                    st.success(f"Linha {linha_planilha} alterada com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar edição: {e}")
                        st.markdown('</div>', unsafe_allow_html=True)