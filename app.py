import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- Configurações da Página (Design Corporativo) ---
st.set_page_config(
    page_title="Portal de Compras - Suprimentos",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para visual corporativo limpo
st.markdown("""
    <style>
    .main {
        background-color: #F8FAFC;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

# Parâmetros da Planilha
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1iWjdaZLAp5hi9YIhmfSO4cPBn6fkfDjef8PAdZp1nsY/edit"
GID_PEDIDOS = 643448898
GID_CATALOGO = 270834817

COLUNAS_PEDIDO = [
    "Ordem de Compra", "Código do produto", "Produto", "Categoria",
    "Data do Pedido", "Horário de Chegada do Pedido", "Valor de Compra",
    "Qt Solicitada", "Qt Aprovada", "Qt Não Aprovada", "Valor de Venda",
    "Fornecedor", "Cod da Peça do Fornecedor", "Observação"
]


# --- Autenticação com o Google Sheets (Passo 3 Atualizado) ---
@st.cache_resource
def conectar_sheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # 1. Tenta carregar do Streamlit Secrets (Nuvem)
    if "gcp_service_account" in st.secrets:
        secret_data = st.secrets["gcp_service_account"]
        # Se for string (formato com aspas triplas), converte para dict
        if isinstance(secret_data, str):
            creds_dict = json.loads(secret_data)
        else:
            creds_dict = dict(secret_data)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    # 2. Se rodar localmente no computador com o arquivo credentials.json
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

    client = gspread.authorize(creds)
    planilha = client.open_by_url(SPREADSHEET_URL)

    ws_pedidos = None
    ws_catalogo = None

    for sheet in planilha.worksheets():
        if sheet.id == GID_PEDIDOS:
            ws_pedidos = sheet
        elif sheet.id == GID_CATALOGO:
            ws_catalogo = sheet

    if not ws_pedidos:
        ws_pedidos = planilha.sheet1

    return ws_pedidos, ws_catalogo


try:
    ws_pedidos, ws_catalogo = conectar_sheets()
except Exception as e:
    st.error(f"Erro ao conectar ao Google Sheets: {e}")
    st.info("Dica: Adicione suas credenciais no painel do Streamlit Cloud em 'App settings > Secrets' ou certifique-se de que o arquivo 'credentials.json' está presente.")
    st.stop()


# --- Carregamento de Peças do Catálogo (Colunas A, B e F) ---
@st.cache_data(ttl=600)
def carregar_catalogo():
    if not ws_catalogo:
        return pd.DataFrame(columns=["codigo", "nome", "fornecedor"])
    valores = ws_catalogo.get_all_values()
    if len(valores) <= 1:
        return pd.DataFrame(columns=["codigo", "nome", "fornecedor"])

    registros = []
    for row in valores[1:]:
        if len(row) >= 2 and (row[0].strip() or row[1].strip()):
            cod = row[0].strip()
            nome = row[1].strip()
            forn = row[5].strip() if len(row) > 5 else ""
            registros.append({"codigo": cod, "nome": nome, "fornecedor": forn})

    df = pd.DataFrame(registros)
    df["display"] = df["codigo"] + " - " + df["nome"]
    return df


df_catalogo = carregar_catalogo()

# Inicialização do estado para a lista temporária de peças
if "itens_da_ordem" not in st.session_state:
    st.session_state.itens_da_ordem = []

# --- Interface Principal ---
st.title("📦 Sistema de Pedidos de Compras")
aba1, aba2 = st.tabs(["📝 Novo Pedido de Compra", "🔍 Consultar e Editar Ordem"])

# ==========================================
# ABA 1: NOVO PEDIDO
# ==========================================
with aba1:
    st.subheader("1. Identificação da Ordem")
    col_oc1, col_oc2 = st.columns(2)
    with col_oc1:
        ordem_compra = st.text_input("Ordem de Compra *", placeholder="Ex: OC-2026-001")
    with col_oc2:
        data_pedido = st.text_input("Data do Pedido", value=datetime.now().strftime("%d/%m/%Y"), disabled=True)

    st.markdown("---")
    st.subheader("2. Adicionar Peça / Produto")

    # Busca no catálogo pré-criado
    opcoes_catalogo = ["-- Digite ou selecione uma peça --"] + df_catalogo["display"].tolist()
    peca_selecionada = st.selectbox("Pesquisar Peça no Catálogo (Aba Catálogo):", opcoes_catalogo)

    # Preenchimento automático ao selecionar
    cod_inicial = ""
    nome_inicial = ""
    forn_inicial = ""
    if peca_selecionada != "-- Digite ou selecione uma peça --":
        item_sel = df_catalogo[df_catalogo["display"] == peca_selecionada].iloc[0]
        cod_inicial = item_sel["codigo"]
        nome_inicial = item_sel["nome"]
        forn_inicial = item_sel["fornecedor"]

    col1, col2, col3 = st.columns(3)
    with col1:
        cod_prod = st.text_input("Código do Produto", value=cod_inicial)
        categoria = st.text_input("Categoria")
        qt_solicitada = st.number_input("Qt Solicitada", min_value=0, step=1, value=1)
        vlr_venda = st.text_input("Valor de Venda (R$)")

    with col2:
        produto = st.text_input("Produto *", value=nome_inicial)
        fornecedor = st.text_input("Fornecedor", value=forn_inicial)
        qt_aprovada = st.number_input("Qt Aprovada", min_value=0, step=1, value=0)
        vlr_compra = st.text_input("Valor de Compra (R$)")

    with col3:
        cod_fornecedor = st.text_input("Cod da Peça do Fornecedor")
        hora_chegada = st.text_input("Horário de Chegada do Pedido", placeholder="Ex: 14:00")
        qt_nao_aprovada = st.number_input("Qt Não Aprovada", min_value=0, step=1, value=0)
        observacao = st.text_input("Observação")

    if st.button("➕ Adicionar Peça à Ordem Atual"):
        if not ordem_compra.strip():
            st.warning("Preencha o campo 'Ordem de Compra' antes de inserir itens.")
        elif not produto.strip():
            st.warning("O nome do 'Produto' é obrigatório.")
        else:
            novo_item = {
                "Ordem de Compra": ordem_compra,
                "Código do produto": cod_prod,
                "Produto": produto,
                "Categoria": categoria,
                "Data do Pedido": data_pedido,
                "Horário de Chegada do Pedido": hora_chegada,
                "Valor de Compra": vlr_compra,
                "Qt Solicitada": qt_solicitada,
                "Qt Aprovada": qt_aprovada,
                "Qt Não Aprovada": qt_nao_aprovada,
                "Valor de Venda": vlr_venda,
                "Fornecedor": fornecedor,
                "Cod da Peça do Fornecedor": cod_fornecedor,
                "Observação": observacao
            }
            st.session_state.itens_da_ordem.append(novo_item)
            st.success(f"Peça '{produto}' adicionada à fila!")

    # Exibição das peças incluídas na Ordem
    if st.session_state.itens_da_ordem:
        st.markdown("---")
        st.subheader(f"Peças Incluídas na Ordem: {ordem_compra}")
        df_itens = pd.DataFrame(st.session_state.itens_da_ordem)
        st.dataframe(df_itens, use_container_width=True)

        col_b1, col_b2 = st.columns([1, 4])
        with col_b1:
            if st.button("🗑 Limpar Peças"):
                st.session_state.itens_da_ordem = []
                st.rerun()

        with col_b2:
            if st.button("💾 Gravar Ordem Completa na Planilha", type="primary"):
                try:
                    linhas = [[item.get(col, "") for col in COLUNAS_PEDIDO] for item in st.session_state.itens_da_ordem]
                    ws_pedidos.append_rows(linhas)
                    st.success(f"Ordem {ordem_compra} gravada com sucesso com {len(linhas)} peça(s)!")
                    st.session_state.itens_da_ordem = []
                except Exception as ex:
                    st.error(f"Erro ao salvar na planilha: {ex}")

# ==========================================
# ABA 2: CONSULTAR E EDITAR
# ==========================================
with aba2:
    st.subheader("Pesquisar por Ordem de Compra")
    col_pesq1, col_pesq2 = st.columns([3, 1])
    with col_pesq1:
        oc_pesquisa = st.text_input("Informe a Ordem de Compra:", placeholder="Ex: OC-2026-001")
    with col_pesq2:
        st.write("")
        st.write("")
        btn_pesquisar = st.button("🔍 Buscar Registros")

    if oc_pesquisa:
        try:
            dados_planilha = ws_pedidos.get_all_values()
            if len(dados_planilha) > 1:
                linhas_encontradas = []
                for idx, row in enumerate(dados_planilha[1:], start=2):
                    if len(row) > 0 and row[0].strip().lower() == oc_pesquisa.strip().lower():
                        # Normaliza tamanho da linha para coincidir com COLUNAS_PEDIDO
                        row_ajustada = row + [""] * (len(COLUNAS_PEDIDO) - len(row))
                        linhas_encontradas.append({"Linha_Planilha": idx, **dict(zip(COLUNAS_PEDIDO, row_ajustada))})

                if linhas_encontradas:
                    df_resultado = pd.DataFrame(linhas_encontradas)
                    st.write(f"Foram encontradas **{len(linhas_encontradas)}** peça(s) para esta Ordem:")
                    st.dataframe(df_resultado.drop(columns=["Linha_Planilha"]), use_container_width=True)

                    st.markdown("---")
                    st.subheader("Editar Peça da Ordem")
                    
                    opcoes_linhas = {f"Linha {d['Linha_Planilha']} - {d['Produto']}": d['Linha_Planilha'] for d in linhas_encontradas}
                    linha_escolhida = st.selectbox("Selecione qual peça deseja editar:", list(opcoes_linhas.keys()))
                    linha_id = opcoes_linhas[linha_escolhida]
                    
                    dados_atuais = next(d for d in linhas_encontradas if d["Linha_Planilha"] == linha_id)

                    with st.form("form_edicao"):
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            e_oc = st.text_input("Ordem de Compra", value=dados_atuais["Ordem de Compra"])
                            e_cod = st.text_input("Código do Produto", value=dados_atuais["Código do produto"])
                            e_prod = st.text_input("Produto", value=dados_atuais["Produto"])
                            e_cat = st.text_input("Categoria", value=dados_atuais["Categoria"])
                            e_dt = st.text_input("Data do Pedido", value=dados_atuais["Data do Pedido"])
                        with c2:
                            e_hr = st.text_input("Horário de Chegada", value=dados_atuais["Horário de Chegada do Pedido"])
                            e_vc = st.text_input("Valor de Compra", value=dados_atuais["Valor de Compra"])
                            e_qs = st.text_input("Qt Solicitada", value=str(dados_atuais["Qt Solicitada"]))
                            e_qa = st.text_input("Qt Aprovada", value=str(dados_atuais["Qt Aprovada"]))
                            e_qn = st.text_input("Qt Não Aprovada", value=str(dados_atuais["Qt Não Aprovada"]))
                        with c3:
                            e_vv = st.text_input("Valor de Venda", value=dados_atuais["Valor de Venda"])
                            e_forn = st.text_input("Fornecedor", value=dados_atuais["Fornecedor"])
                            e_cod_f = st.text_input("Cod Peça Fornecedor", value=dados_atuais["Cod da Peça do Fornecedor"])
                            e_obs = st.text_input("Observação", value=dados_atuais["Observação"])

                        if st.form_submit_button("💾 Salvar Alterações na Planilha"):
                            novos_dados = [
                                e_oc, e_cod, e_prod, e_cat, e_dt, e_hr,
                                e_vc, e_qs, e_qa, e_qn, e_vv, e_forn, e_cod_f, e_obs
                            ]
                            ws_pedidos.update(range_name=f"A{linha_id}:N{linha_id}", values=[novos_dados])
                            st.success("Item atualizado com sucesso na planilha!")
                            st.rerun()
                else:
                    st.info(f"Nenhum registro encontrado para a ordem: '{oc_pesquisa}'.")
        except Exception as e:
            st.error(f"Erro na consulta: {e}")