import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestão de Pedidos de Compras",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CORPORATIVA MODERNA (TEMA CLARO) ---
st.markdown("""
<style>
    /* Estilo geral e tipografia */
    .main {
        background-color: #F8FAFC;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Cartões / Containers */
    .corp-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        border: 1px solid #E2E8F0;
        margin-bottom: 24px;
    }
    
    .corp-header {
        font-size: 24px;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 8px;
    }
    
    .corp-subtitle {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    
    /* Botões estilizados */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM O GOOGLE SHEETS ---
# URL da Planilha
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1iWjdaZLAp5hi9YIhmfSO4cPBn6fkfDjef8PAdZp1nsY/edit"
SHEET_PEDIDOS_GID = 643448898
SHEET_PECAS_GID = 270834817

@st.cache_resource
def get_gspread_client():
    """Autentica com as credenciais da Conta de Serviço."""
    # Pode usar st.secrets["gcp_service_account"] ou arquivo 'credentials.json' local
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Se configurado em .streamlit/secrets.toml
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    except Exception:
        # Fallback para arquivo local
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=600)
def load_pecas_reference():
    """Carrega tabela de referência de peças (Colunas A, B e F)."""
    try:
        client = get_gspread_client()
        sh = client.open_by_url(SPREADSHEET_URL)
        worksheet = next((ws for ws in sh.worksheets() if ws.id == SHEET_PECAS_GID), sh.sheet1)
        
        data = worksheet.get_all_values()
        if not data:
            return pd.DataFrame(columns=["Código", "Produto", "Fornecedor"])
        
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows)
        # Seleciona A (índice 0), B (índice 1) e F (índice 5 se houver)
        col_cod = df[0] if 0 in df.columns else ""
        col_nome = df[1] if 1 in df.columns else ""
        col_forn = df[5] if 5 in df.columns else ""
        
        ref_df = pd.DataFrame({
            "Código": col_cod,
            "Produto": col_nome,
            "Fornecedor": col_forn
        }).dropna(subset=["Código", "Produto"])
        
        # Filtra linhas vazias
        ref_df = ref_df[(ref_df["Código"] != "") | (ref_df["Produto"] != "")]
        ref_df["Display"] = ref_df["Código"].astype(str) + " - " + ref_df["Produto"].astype(str)
        return ref_df
    except Exception as e:
        st.error(f"Erro ao carregar peças: {e}")
        return pd.DataFrame(columns=["Código", "Produto", "Fornecedor", "Display"])

def get_pedidos_worksheet():
    """Abre a aba de Pedidos de Compras."""
    client = get_gspread_client()
    sh = client.open_by_url(SPREADSHEET_URL)
    worksheet = next((ws for ws in sh.worksheets() if ws.id == SHEET_PEDIDOS_GID), None)
    if not worksheet:
        worksheet = sh.get_worksheet(0)
    return worksheet

# --- INTERFACE PRINCIPAL ---
menu = st.sidebar.radio(
    "Navegação",
    ["➕ Novo Pedido de Compra", "🔍 Consultar e Editar Ordens"],
    index=0
)

ref_pecas = load_pecas_reference()

# ========================================================
# ABA 1: NOVO PEDIDO DE COMPRA (MÚLTIPLAS PEÇAS)
# ========================================================
if menu == "➕ Novo Pedido de Compra":
    st.markdown('<div class="corp-header">Novo Pedido de Compras</div>', unsafe_allow_html=True)
    st.markdown('<div class="corp-subtitle">Cadastre uma ou mais peças para uma mesma Ordem de Compra.</div>', unsafe_allow_html=True)
    
    # 1. Informações Gerais da Ordem de Compra
    with st.container():
        st.markdown('<div class="corp-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Dados Gerais da Ordem")
        col1, col2, col3 = st.columns(3)
        with col1:
            ordem_compra = st.text_input("Ordem de Compra *", placeholder="Ex: OC-2026-001")
        with col2:
            data_pedido = st.date_input("Data do Pedido", value=datetime.date.today())
        with col3:
            horario_chegada = st.time_input("Horário de Chegada do Pedido", value=datetime.datetime.now().time())
        st.markdown('</div>', unsafe_allow_html=True)

    # Inicializa carrinho de peças na sessão
    if "itens_pedido" not in st.session_state:
        st.session_state.itens_pedido = []

    # 2. Adicionar Itens na Ordem de Compra
    with st.container():
        st.markdown('<div class="corp-card">', unsafe_allow_html=True)
        st.markdown("### 📦 Adicionar Peça / Item")
        
        # Pesquisa de peças com autocompletar
        opcoes_pecas = [""] + list(ref_pecas["Display"].values) if not ref_pecas.empty else [""]
        peca_selecionada = st.selectbox(
            "Pesquisar Peça por Código ou Nome (Tabela de Referência):",
            opcoes_pecas,
            index=0
        )
        
        # Auto-preenche código, nome e fornecedor se selecionado
        default_cod = ""
        default_nome = ""
        default_forn = ""
        if peca_selecionada:
            item_match = ref_pecas[ref_pecas["Display"] == peca_selecionada].iloc[0]
            default_cod = item_match["Código"]
            default_nome = item_match["Produto"]
            default_forn = item_match["Fornecedor"]
            
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            cod_prod = st.text_input("Código do Produto *", value=default_cod)
            categoria = st.text_input("Categoria", placeholder="Ex: Pneumáticos, Elétrica, Fixação")
            fornecedor = st.text_input("Fornecedor", value=default_forn)
        with c_p2:
            produto_nome = st.text_input("Produto *", value=default_nome)
            qt_solicitada = st.number_input("Qt Solicitada", min_value=0.0, step=1.0, value=1.0)
            qt_aprovada = st.number_input("Qt Aprovada", min_value=0.0, step=1.0, value=0.0)
            qt_nao_aprovada = st.number_input("Qt Não Aprovada", min_value=0.0, step=1.0, value=0.0)
        with c_p3:
            cod_peca_forn = st.text_input("Cód. da Peça do Fornecedor")
            valor_compra = st.number_input("Valor de Compra (R$)", min_value=0.0, step=0.01, format="%.2f")
            valor_venda = st.number_input("Valor de Venda (R$)", min_value=0.0, step=0.01, format="%.2f")
            obs = st.text_input("Observação")
            
        col_btn_add, _ = st.columns([1, 4])
        with col_btn_add:
            if st.button("➕ Inserir Item no Pedido", use_container_width=True):
                if not cod_prod or not produto_nome:
                    st.warning("Código e Nome do Produto são obrigatórios.")
                else:
                    item = {
                        "Ordem de Compra": ordem_compra,
                        "Código do produto": cod_prod,
                        "Produto": produto_nome,
                        "Categoria": categoria,
                        "Data do Pedido": data_pedido.strftime("%d/%m/%Y"),
                        "Horário de Chegada do Pedido": horario_chegada.strftime("%H:%M:%S"),
                        "Valor de Compra": valor_compra,
                        "Qt Solicitada": qt_solicitada,
                        "Qt Aprovada": qt_aprovada,
                        "Qt Não Aprovada": qt_nao_aprovada,
                        "Valor de Venda": valor_venda,
                        "Fornecedor": fornecedor,
                        "Cod da Peça do Fornecedor": cod_peca_forn,
                        "Observação": obs
                    }
                    st.session_state.itens_pedido.append(item)
                    st.success(f"Peça '{produto_nome}' adicionada ao pedido!")
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Tabela de Peças Adicionadas e Submissão Final
    if st.session_state.itens_pedido:
        st.markdown('<div class="corp-card">', unsafe_allow_html=True)
        st.markdown("### 🛒 Peças Incluídas nesta Ordem")
        df_carrinho = pd.DataFrame(st.session_state.itens_pedido)
        st.dataframe(df_carrinho, use_container_width=True)
        
        c_sub1, c_sub2, _ = st.columns([2, 1, 3])
        with c_sub1:
            if st.button("💾 Finalizar e Enviar para Planilha", type="primary", use_container_width=True):
                if not ordem_compra.strip():
                    st.error("Informe o número da Ordem de Compra antes de salvar.")
                else:
                    try:
                        ws = get_pedidos_worksheet()
                        # Atualiza caso a Ordem de Compra tenha sido informada depois
                        for it in st.session_state.itens_pedido:
                            it["Ordem de Compra"] = ordem_compra
                        
                        linhas = [list(it.values()) for it in st.session_state.itens_pedido]
                        ws.append_rows(linhas)
                        st.success(f"{len(linhas)} itens cadastrados com sucesso na planilha!")
                        st.session_state.itens_pedido = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar na planilha: {e}")
        with c_sub2:
            if st.button("🗑️ Limpar Lista", use_container_width=True):
                st.session_state.itens_pedido = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ========================================================
# ABA 2: CONSULTAR E EDITAR ORDENS DE COMPRA
# ========================================================
elif menu == "🔍 Consultar e Editar Ordens":
    st.markdown('<div class="corp-header">Pesquisa e Edição de Pedidos</div>', unsafe_allow_html=True)
    st.markdown('<div class="corp-subtitle">Consulte itens por Ordem de Compra e altere seus dados diretamente.</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="corp-card">', unsafe_allow_html=True)
        oc_busca = st.text_input("Digite o número da Ordem de Compra para pesquisar:")
        buscar = st.button("Pesquisar", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)
        
    if buscar or ("oc_pesquisada" in st.session_state and st.session_state.oc_pesquisada == oc_busca):
        if oc_busca:
            st.session_state.oc_pesquisada = oc_busca
            try:
                ws = get_pedidos_worksheet()
                todos_dados = ws.get_all_values()
                if not todos_dados:
                    st.info("A planilha está vazia.")
                else:
                    cabecalhos = todos_dados[0]
                    linhas = todos_dados[1:]
                    df_todos = pd.DataFrame(linhas, columns=cabecalhos)
                    
                    # Procura coluna da Ordem de Compra
                    col_oc = next((c for c in cabecalhos if "ordem" in c.lower()), cabecalhos[0])
                    itens_filtrados = df_todos[df_todos[col_oc].str.strip() == oc_busca.strip()]
                    
                    if itens_filtrados.empty:
                        st.warning(f"Nenhum pedido encontrado para a Ordem: {oc_busca}")
                    else:
                        st.markdown('<div class="corp-card">', unsafe_allow_html=True)
                        st.markdown(f"### Itens da Ordem: **{oc_busca}** ({len(itens_filtrados)} encontrado(s))")
                        
                        # Adiciona índice da planilha para referência de edição
                        itens_filtrados["Linha Planilha"] = itens_filtrados.index + 2
                        st.dataframe(itens_filtrados, use_container_width=True)
                        
                        st.markdown("---")
                        st.markdown("#### ✏️ Editar Registro")
                        
                        opcoes_edicao = [
                            f"Linha {row['Linha Planilha']} - {row.get('Produto', '')}" 
                            for _, row in itens_filtrados.iterrows()
                        ]
                        item_selecionado = st.selectbox("Selecione o item para editar:", opcoes_edicao)
                        num_linha = int(item_selecionado.split(" ")[1])
                        
                        dados_linha = df_todos.loc[num_linha - 2].to_dict()
                        
                        # Formulário de edição
                        with st.form("form_edicao"):
                            e_c1, e_c2, e_c3 = st.columns(3)
                            campos_atualizados = {}
                            
                            for idx, col in enumerate(cabecalhos):
                                valor_atual = dados_linha.get(col, "")
                                if idx % 3 == 0:
                                    col_dest = e_c1
                                elif idx % 3 == 1:
                                    col_dest = e_c2
                                else:
                                    col_dest = e_c3
                                
                                with col_dest:
                                    campos_atualizados[col] = st.text_input(f"{col}", value=str(valor_atual))
                            
                            btn_salvar = st.form_submit_button("💾 Salvar Alterações na Planilha")
                            if btn_salvar:
                                novos_valores = [campos_atualizados[c] for c in cabecalhos]
                                ws.update(f"A{num_linha}:{chr(65+len(cabecalhos)-1)}{num_linha}", [novos_valores])
                                st.success(f"Linha {num_linha} atualizada com sucesso!")
                                st.rerun()
                                
                        st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao buscar/atualizar dados: {e}")