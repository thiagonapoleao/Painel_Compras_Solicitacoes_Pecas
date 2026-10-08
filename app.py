import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import pandas as pd
import requests

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE GRAVAÇÃO NA PLANILHA GOOGLE VIA WEBHOOK
# -----------------------------------------------------------------------------
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbz8aGA0QU1Zfca6Lbq2olJeP5ituhE3_7Ix7ajFcQgPdby5SjrQj9D81BCfd9FRlzv9nw/exec"

def gravar_na_planilha_google(dados_registro):
    """Envia o novo registro diretamente para a planilha Google Sheets via Apps Script tratando redirecionamentos"""
    try:
        session = requests.Session()
        response = session.post(
            WEBHOOK_URL,
            data=json.dumps(dados_registro),
            headers={"Content-Type": "application/json"},
            allow_redirects=True,
            timeout=15
        )
        if response.status_code in [200, 302]:
            return True, "Gravado com sucesso na planilha Google!"
        else:
            return False, f"Falha na comunicação com Google Planilhas (HTTP {response.status_code})"
    except Exception as e:
        return False, f"Erro ao conectar com Google Planilhas: {str(e)}"

# Configuração da página Streamlit em modo Wide
st.set_page_config(
    page_title="Dashboard Executivo - Solicitações & Ordens de Compra de Peças",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# CONTROLE GLOBAL DE TEMA (LIGHT / DARK) COMPARTILHADO ENTRE TODAS AS ABAS
# -----------------------------------------------------------------------------
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = "light"

is_dark = st.session_state.current_theme == "dark"

# Estilização CSS que responde ao tema ativo em todas as abas
if is_dark:
    theme_css = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            background-color: #020617 !important;
            color: #f8fafc !important;
        }
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }
        .edit-mode-banner {
            background-color: #78350f;
            border-left: 5px solid #f59e0b;
            padding: 12px 18px;
            border-radius: 8px;
            margin-bottom: 15px;
            color: #fef3c7;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
    </style>
    """
else:
    theme_css = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }
        .edit-mode-banner {
            background-color: #fef3c7;
            border-left: 5px solid #d97706;
            padding: 12px 18px;
            border-radius: 8px;
            margin-bottom: 15px;
            color: #92400e;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FUNÇÃO PARA CARREGAR PRODUTOS DA PLANILHA GOOGLE (Aba gid=270834817)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300)
def carregar_catalogo_produtos():
    url_csv = "https://docs.google.com/spreadsheets/d/1iWjdaZLAp5hi9YIhmfSO4cPBn6fkfDjef8PAdZp1nsY/export?format=csv&gid=270834817"
    try:
        df = pd.read_csv(url_csv)
        col_cod = df.columns[0]
        col_prod = df.columns[1]
        
        df_clean = df[[col_cod, col_prod]].dropna(subset=[col_prod]).drop_duplicates(subset=[col_prod])
        catalogo = {}
        for _, row in df_clean.iterrows():
            nome = str(row[col_prod]).strip().upper()
            cod = str(row[col_cod]).strip() if pd.notna(row[col_cod]) else ""
            if nome:
                catalogo[nome] = cod
        return catalogo
    except Exception:
        return {
            "DISCO ROTAÇÃO DO MISTURADOR": "2290",
            "BICO DE SAIDA DO SOLUVEL PHEDRA": "1442",
            "MOTOR DE MIXER COMPLETO": "2672",
            "TORNEIRA 3/4": "301",
            "REMOVE GRUDE": "902",
            "BOMBA DE AGUA 220V": "534",
            "SPRAY COLORART PRATA LUNAR": "110",
            "CONECTOR MACHO 8MM X1/2": "405",
            "NUCLEO SOLUVEL SOLISTA": "2617",
            "BOMBA DE AGUA ULKA 220V": "535",
            "GAXETA DE SILICONE": "700",
            "MOTOR DO CARROSSEL PINO LONGO": "2673",
            "ANEL DO BICO CALDEIRA 70": "650",
            "SUPORTE DE MAQUINA": "305",
            "ANEL BICO CALDEIRA 69": "649",
            "PINCEL DE LIMPEZA": "105",
            "FILTRO BANANINHA C ENGATE RAPIDO": "410",
            "PRODUTO ROSA DESENGRAXANTE": "905",
            "TORNEIRA METALICA": "302",
            "REMOVE GRUDE SPRAY": "903",
            "CONTADOR VOLUMETRICO": "880",
            "NUCLEO DA CALDEIRA": "881",
            "CONTADOR VOLUMETRICO 1.2": "882",
            "MOTOR DO MOINHO 110V": "2680"
        }

catalogo_produtos = carregar_catalogo_produtos()

# -----------------------------------------------------------------------------
# BASE DE DADOS COMPLETA PRESERVADA (st.session_state)
# -----------------------------------------------------------------------------
if 'orders_data' not in st.session_state:
    st.session_state.orders_data = [
        { "ordemCompra": "OC-2025-001", "codProduto": "2290", "ano": "2025", "mes": "Agosto", "data": "05/08/2025", "horarioChegada": "14:30", "solicitante": "WILLIAN NEVES", "peca": "DISCO ROTAÇÃO DO MISTURADOR", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-2290", "qt": 15, "qtAprovada": 15, "qtNaoAprovada": 0, "custoUnit": 4.39, "valorVenda": 12.00, "observacao": "" },
        { "ordemCompra": "OC-2025-002", "codProduto": "1442", "ano": "2025", "mes": "Agosto", "data": "08/08/2025", "horarioChegada": "10:15", "solicitante": "FLAVIO", "peca": "BICO DE SAIDA DO SOLUVEL PHEDRA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-1442", "qt": 12, "qtAprovada": 12, "qtNaoAprovada": 0, "custoUnit": 8.52, "valorVenda": 18.00, "observacao": "" },
        { "ordemCompra": "OC-2025-003", "codProduto": "2672", "ano": "2025", "mes": "Agosto", "data": "12/08/2025", "horarioChegada": "16:00", "solicitante": "WILLIAN NEVES", "peca": "MOTOR DE MIXER COMPLETO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-2672", "qt": 4, "qtAprovada": 4, "qtNaoAprovada": 0, "custoUnit": 334.00, "valorVenda": 590.00, "observacao": "" },
        { "ordemCompra": "OC-2025-004", "codProduto": "301", "ano": "2025", "mes": "Agosto", "data": "14/08/2025", "horarioChegada": "09:00", "solicitante": "NAPOLEAO", "peca": "TORNEIRA 3/4", "categoria": "Acessorios", "fornecedor": "LUCAS", "codPecaFornecedor": "LC-301", "qt": 8, "qtAprovada": 7, "qtNaoAprovada": 1, "custoUnit": 75.18, "valorVenda": 130.00, "observacao": "1 unidade reprovada" },
        { "ordemCompra": "OC-2025-005", "codProduto": "902", "ano": "2025", "mes": "Agosto", "data": "18/08/2025", "horarioChegada": "11:20", "solicitante": "FABIO", "peca": "REMOVE GRUDE", "categoria": "Snaks", "fornecedor": "FABIO", "codPecaFornecedor": "FB-902", "qt": 10, "qtAprovada": 10, "qtNaoAprovada": 0, "custoUnit": 72.00, "valorVenda": 115.00, "observacao": "" },
        { "ordemCompra": "OC-2025-006", "codProduto": "534", "ano": "2025", "mes": "Agosto", "data": "20/08/2025", "horarioChegada": "13:40", "solicitante": "LUCAS", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-534", "qt": 6, "qtAprovada": 5, "qtNaoAprovada": 1, "custoUnit": 180.00, "valorVenda": 290.00, "observacao": "" },
        { "ordemCompra": "OC-2025-007", "codProduto": "110", "ano": "2025", "mes": "Agosto", "data": "22/08/2025", "horarioChegada": "15:00", "solicitante": "WILLIAN NEVES", "peca": "SPRAY COLORART PRATA LUNAR", "categoria": "Acessorios", "fornecedor": "MGC", "codPecaFornecedor": "MG-110", "qt": 20, "qtAprovada": 20, "qtNaoAprovada": 0, "custoUnit": 26.50, "valorVenda": 48.00, "observacao": "" },
        { "ordemCompra": "OC-2025-008", "codProduto": "405", "ano": "2025", "mes": "Agosto", "data": "25/08/2025", "horarioChegada": "10:30", "solicitante": "FLAVIO", "peca": "CONECTOR MACHO 8MM X1/2", "categoria": "Hidraulica", "fornecedor": "IMELKRON", "codPecaFornecedor": "IM-405", "qt": 30, "qtAprovada": 25, "qtNaoAprovada": 5, "custoUnit": 10.50, "valorVenda": 22.00, "observacao": "Estoque parcial" },
        { "ordemCompra": "OC-2025-009", "codProduto": "2617", "ano": "2025", "mes": "Agosto", "data": "28/08/2025", "horarioChegada": "17:10", "solicitante": "NAPOLEAO", "peca": "NUCLEO SOLUVEL SOLISTA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-2617", "qt": 5, "qtAprovada": 5, "qtNaoAprovada": 0, "custoUnit": 91.04, "valorVenda": 165.00, "observacao": "" },
        
        { "ordemCompra": "OC-2025-010", "codProduto": "535", "ano": "2025", "mes": "Setembro", "data": "02/09/2025", "horarioChegada": "08:45", "solicitante": "THIAGO", "peca": "BOMBA DE AGUA ULKA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-ULKA", "qt": 18, "qtAprovada": 18, "qtNaoAprovada": 0, "custoUnit": 195.00, "valorVenda": 320.00, "observacao": "" },
        { "ordemCompra": "OC-2025-011", "codProduto": "700", "ano": "2025", "mes": "Setembro", "data": "05/09/2025", "horarioChegada": "14:15", "solicitante": "SAMANTHA", "peca": "GAXETA DE SILICONE", "categoria": "Acessorios", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-700", "qt": 25, "qtAprovada": 22, "qtNaoAprovada": 3, "custoUnit": 18.50, "valorVenda": 35.00, "observacao": "" },
        { "ordemCompra": "OC-2025-012", "codProduto": "2673", "ano": "2025", "mes": "Setembro", "data": "10/09/2025", "horarioChegada": "11:50", "solicitante": "ALAN", "peca": "MOTOR DO CARROSSEL PINO LONGO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-CARROSSEL", "qt": 3, "qtAprovada": 3, "qtNaoAprovada": 0, "custoUnit": 280.00, "valorVenda": 480.00, "observacao": "" },
        { "ordemCompra": "OC-2025-013", "codProduto": "650", "ano": "2025", "mes": "Setembro", "data": "14/09/2025", "horarioChegada": "16:20", "solicitante": "CESAR", "peca": "ANEL DO BICO CALDEIRA 70", "categoria": "Acessorios", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-650", "qt": 40, "qtAprovada": 38, "qtNaoAprovada": 2, "custoUnit": 9.80, "valorVenda": 20.00, "observacao": "" },
        { "ordemCompra": "OC-2025-014", "codProduto": "2290", "ano": "2025", "mes": "Setembro", "data": "19/09/2025", "horarioChegada": "15:10", "solicitante": "WILLIAN NEVES", "peca": "DISCO ROTAÇÃO DO MISTURADOR", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-2290", "qt": 20, "qtAprovada": 20, "qtNaoAprovada": 0, "custoUnit": 4.39, "valorVenda": 12.00, "observacao": "" },
        { "ordemCompra": "OC-2025-015", "codProduto": "2672", "ano": "2025", "mes": "Setembro", "data": "19/09/2025", "horarioChegada": "09:30", "solicitante": "THIAGO", "peca": "MOTOR DE MIXER COMPLETO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-2672", "qt": 6, "qtAprovada": 6, "qtNaoAprovada": 0, "custoUnit": 334.00, "valorVenda": 590.00, "observacao": "" },
        { "ordemCompra": "OC-2025-016", "codProduto": "305", "ano": "2025", "mes": "Setembro", "data": "21/09/2025", "horarioChegada": "14:00", "solicitante": "DANI", "peca": "SUPORTE DE MAQUINA", "categoria": "Acessorios", "fornecedor": "LUCAS", "codPecaFornecedor": "LC-SUP", "qt": 10, "qtAprovada": 8, "qtNaoAprovada": 2, "custoUnit": 65.00, "valorVenda": 120.00, "observacao": "" },
        { "ordemCompra": "OC-2025-017", "codProduto": "649", "ano": "2025", "mes": "Setembro", "data": "23/09/2025", "horarioChegada": "10:00", "solicitante": "SAMANTHA", "peca": "ANEL BICO CALDEIRA 69", "categoria": "Acessorios", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-649", "qt": 35, "qtAprovada": 35, "qtNaoAprovada": 0, "custoUnit": 9.50, "valorVenda": 20.00, "observacao": "" },
        { "ordemCompra": "OC-2025-018", "codProduto": "2617", "ano": "2025", "mes": "Setembro", "data": "25/09/2025", "horarioChegada": "11:30", "solicitante": "THIAGO", "peca": "NUCLEO SOLUVEL SOLISTA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-2617", "qt": 8, "qtAprovada": 8, "qtNaoAprovada": 0, "custoUnit": 91.04, "valorVenda": 165.00, "observacao": "" },

        { "ordemCompra": "OC-2025-019", "codProduto": "105", "ano": "2025", "mes": "Outubro", "data": "10/10/2025", "horarioChegada": "13:00", "solicitante": "WILLIAN NEVES", "peca": "PINCEL DE LIMPEZA", "categoria": "Multi Bebidas", "fornecedor": "WILLIAN NEVES", "codPecaFornecedor": "WN-PINCEL", "qt": 15, "qtAprovada": 15, "qtNaoAprovada": 0, "custoUnit": 7.00, "valorVenda": 15.00, "observacao": "" },
        { "ordemCompra": "OC-2025-020", "codProduto": "410", "ano": "2025", "mes": "Outubro", "data": "15/10/2025", "horarioChegada": "15:45", "solicitante": "FLAVIO", "peca": "FILTRO BANANINHA C ENGATE RAPIDO", "categoria": "Hidraulica", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-BANANA", "qt": 30, "qtAprovada": 27, "qtNaoAprovada": 3, "custoUnit": 34.05, "valorVenda": 65.00, "observacao": "" },
        { "ordemCompra": "OC-2025-021", "codProduto": "534", "ano": "2025", "mes": "Outubro", "data": "22/10/2025", "horarioChegada": "10:20", "solicitante": "SAMANTHA", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-534", "qt": 8, "qtAprovada": 8, "qtNaoAprovada": 0, "custoUnit": 185.00, "valorVenda": 310.00, "observacao": "" },

        { "ordemCompra": "OC-2025-022", "codProduto": "905", "ano": "2025", "mes": "Novembro", "data": "03/11/2025", "horarioChegada": "09:10", "solicitante": "FLAVIO", "peca": "PRODUTO ROSA DESENGRAXANTE", "categoria": "Multi Bebidas", "fornecedor": "TAIS MICHELE", "codPecaFornecedor": "TM-ROSA", "qt": 5, "qtAprovada": 5, "qtNaoAprovada": 0, "custoUnit": 125.80, "valorVenda": 210.00, "observacao": "" },
        { "ordemCompra": "OC-2025-023", "codProduto": "302", "ano": "2025", "mes": "Novembro", "data": "03/11/2025", "horarioChegada": "14:40", "solicitante": "NAPOLEAO", "peca": "TORNEIRA METALICA", "categoria": "Acessorios", "fornecedor": "LUCAS", "codPecaFornecedor": "LC-MET", "qt": 4, "qtAprovada": 4, "qtNaoAprovada": 0, "custoUnit": 75.18, "valorVenda": 135.00, "observacao": "" },
        { "ordemCompra": "OC-2025-024", "codProduto": "903", "ano": "2025", "mes": "Novembro", "data": "04/11/2025", "horarioChegada": "16:15", "solicitante": "FABIO", "peca": "REMOVE GRUDE SPRAY", "categoria": "Snaks", "fornecedor": "FABIO", "codPecaFornecedor": "FB-SPRAY", "qt": 6, "qtAprovada": 5, "qtNaoAprovada": 1, "custoUnit": 72.00, "valorVenda": 115.00, "observacao": "" },

        { "ordemCompra": "OC-2026-001", "codProduto": "880", "ano": "2026", "mes": "Março", "data": "02/03/2026", "horarioChegada": "10:30", "solicitante": "DAVI", "peca": "CONTADOR VOLUMETRICO", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-880", "qt": 5, "qtAprovada": 5, "qtNaoAprovada": 0, "custoUnit": 110.00, "valorVenda": 190.00, "observacao": "" },
        { "ordemCompra": "OC-2026-002", "codProduto": "881", "ano": "2026", "mes": "Março", "data": "07/03/2026", "horarioChegada": "11:20", "solicitante": "DAVI", "peca": "NUCLEO DA CALDEIRA", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-881", "qt": 4, "qtAprovada": 4, "qtNaoAprovada": 0, "custoUnit": 240.00, "valorVenda": 390.00, "observacao": "" },
        { "ordemCompra": "OC-2026-003", "codProduto": "882", "ano": "2026", "mes": "Abril", "data": "23/04/2026", "horarioChegada": "14:00", "solicitante": "PEDRO", "peca": "CONTADOR VOLUMETRICO 1.2", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-882", "qt": 8, "qtAprovada": 8, "qtNaoAprovada": 0, "custoUnit": 115.00, "valorVenda": 195.00, "observacao": "" },
        { "ordemCompra": "OC-2026-004", "codProduto": "2680", "ano": "2026", "mes": "Abril", "data": "24/04/2026", "horarioChegada": "15:30", "solicitante": "LUCAS", "peca": "MOTOR DO MOINHO 110V", "categoria": "Multi Bebidas", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-MOINHO", "qt": 2, "qtAprovada": 1, "qtNaoAprovada": 1, "custoUnit": 410.00, "valorVenda": 690.00, "observacao": "" },
        { "ordemCompra": "OC-2026-005", "codProduto": "534", "ano": "2026", "mes": "Agosto", "data": "14/08/2026", "horarioChegada": "09:40", "solicitante": "WILLIAN NEVES", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-534", "qt": 12, "qtAprovada": 12, "qtNaoAprovada": 0, "custoUnit": 195.00, "valorVenda": 320.00, "observacao": "" },
        { "ordemCompra": "OC-2026-006", "codProduto": "535", "ano": "2026", "mes": "Agosto", "data": "17/08/2026", "horarioChegada": "10:50", "solicitante": "THIAGO", "peca": "BOMBA DE AGUA ULKA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-ULKA", "qt": 10, "qtAprovada": 10, "qtNaoAprovada": 0, "custoUnit": 195.00, "valorVenda": 320.00, "observacao": "" },
        { "ordemCompra": "OC-2026-007", "codProduto": "534", "ano": "2026", "mes": "Agosto", "data": "25/08/2026", "horarioChegada": "13:10", "solicitante": "RYAN", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-534", "qt": 7, "qtAprovada": 6, "qtNaoAprovada": 1, "custoUnit": 195.00, "valorVenda": 320.00, "observacao": "" },
        { "ordemCompra": "OC-2026-008", "codProduto": "534", "ano": "2026", "mes": "Agosto", "data": "27/08/2026", "horarioChegada": "16:20", "solicitante": "VITOR", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-534", "qt": 5, "qtAprovada": 5, "qtNaoAprovada": 0, "custoUnit": 195.00, "valorVenda": 320.00, "observacao": "" },
        { "ordemCompra": "OC-2026-009", "codProduto": "534", "ano": "2026", "mes": "Setembro", "data": "11/09/2026", "horarioChegada": "09:00", "solicitante": "THIAGO", "peca": "BOMBA DE AGUA 220V", "categoria": "Multi Bebidas", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-534", "qt": 14, "qtAprovada": 14, "qtNaoAprovada": 0, "custoUnit": 195.00, "valorVenda": 320.00, "observacao": "" },
        { "ordemCompra": "OC-2026-010", "codProduto": "700", "ano": "2026", "mes": "Setembro", "data": "15/09/2026", "horarioChegada": "11:15", "solicitante": "CESAR", "peca": "GAXETA DE SILICONE", "categoria": "Acessorios", "fornecedor": "EVOCA", "codPecaFornecedor": "EV-700", "qt": 20, "qtAprovada": 18, "qtNaoAprovada": 2, "custoUnit": 18.50, "valorVenda": 35.00, "observacao": "" },
        { "ordemCompra": "OC-2026-011", "codProduto": "650", "ano": "2026", "mes": "Setembro", "data": "15/09/2026", "horarioChegada": "14:40", "solicitante": "CESAR", "peca": "ANEL DO BICO CALDEIRA 70", "categoria": "Acessorios", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-650", "qt": 25, "qtAprovada": 25, "qtNaoAprovada": 0, "custoUnit": 9.80, "valorVenda": 20.00, "observacao": "" },
        { "ordemCompra": "OC-2026-012", "codProduto": "649", "ano": "2026", "mes": "Setembro", "data": "23/09/2026", "horarioChegada": "15:30", "solicitante": "SAMANTHA", "peca": "ANEL BICO CALDEIRA 69", "categoria": "Acessorios", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-649", "qt": 30, "qtAprovada": 30, "qtNaoAprovada": 0, "custoUnit": 9.50, "valorVenda": 20.00, "observacao": "" },
        { "ordemCompra": "OC-2026-013", "codProduto": "650", "ano": "2026", "mes": "Setembro", "data": "23/09/2026", "horarioChegada": "16:00", "solicitante": "SAMANTHA", "peca": "ANEL BICO CALDEIRA 70", "categoria": "Acessorios", "fornecedor": "PARAMOUNT", "codPecaFornecedor": "PM-650", "qt": 30, "qtAprovada": 28, "qtNaoAprovada": 2, "custoUnit": 9.80, "valorVenda": 20.00, "observacao": "" }
    ]

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard Compras"

if 'edit_order_id' not in st.session_state:
    st.session_state.edit_order_id = None

# -----------------------------------------------------------------------------
# BARRA DE NAVEGAÇÃO SUPERIOR (NAVBAR COM BOTÃO GLOBAL DE TEMA)
# -----------------------------------------------------------------------------
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([3.5, 2.5, 2.5, 1.5])

with nav_col1:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-top: 5px;">
            <span style="font-size: 1.4rem;">📦</span>
            <span style="font-size: 1.15rem; font-weight: 800; letter-spacing: -0.02em;">Sistema Integrado de Suprimentos</span>
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

with nav_col4:
    theme_btn_label = "☀️ Claro" if is_dark else "🌙 Escuro"
    if st.button(theme_btn_label, use_container_width=True):
        st.session_state.current_theme = "light" if is_dark else "dark"
        st.rerun()

st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1.25rem; border: none; border-top: 1px solid #94a3b833;'>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ABA 1: FORMULÁRIO DE CADASTRO E EDIÇÃO ("Pedido de Compras")
# -----------------------------------------------------------------------------
if st.session_state.active_tab == "Pedido de Compras":
    st.subheader("📝 Gestão e Lançamento de Pedidos de Compra")
    st.caption("Cadastre novas ordens e sincronize automaticamente com a aba 'Ordem de Compra(Peças)'.")

    # ------------------ SEÇÃO DE PESQUISA & EDIÇÃO ------------------
    with st.expander("🔍 Pesquisar por Ordem de Compra para Editar", expanded=(st.session_state.edit_order_id is not None)):
        col_search1, col_search2, col_search3 = st.columns([3, 1, 1])
        all_ocs = [d.get("ordemCompra", "") for d in st.session_state.orders_data if d.get("ordemCompra")]
        
        with col_search1:
            selected_oc = st.selectbox("Selecione ou digite a Ordem de Compra:", options=["-- Selecione uma OC --"] + all_ocs)
        with col_search2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Carregar para Edição", use_container_width=True, type="primary"):
                if selected_oc != "-- Selecione uma OC --":
                    st.session_state.edit_order_id = selected_oc
                    st.rerun()
                else:
                    st.warning("Selecione uma Ordem de Compra válida.")
        with col_search3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.session_state.edit_order_id:
                if st.button("Cancelar Edição", use_container_width=True):
                    st.session_state.edit_order_id = None
                    st.rerun()

    record_to_edit = None
    if st.session_state.edit_order_id:
        for item in st.session_state.orders_data:
            if item.get("ordemCompra") == st.session_state.edit_order_id:
                record_to_edit = item
                break
        if record_to_edit:
            st.markdown(f"""
                <div class="edit-mode-banner">
                    <span>✏️ Editando Ordem de Compra: <strong>{record_to_edit.get('ordemCompra')}</strong></span>
                    <span>Modifique os campos e clique em Salvar Alterações</span>
                </div>
            """, unsafe_allow_html=True)

    # ------------------ PREPARAÇÃO DOS DADOS DO FORMULÁRIO ------------------
    produtos_lista = sorted(list(catalogo_produtos.keys()))

    def_oc = record_to_edit.get("ordemCompra", f"OC-{datetime.today().year}-{len(st.session_state.orders_data)+1:03d}") if record_to_edit else f"OC-{datetime.today().year}-{len(st.session_state.orders_data)+1:03d}"
    def_prod = record_to_edit.get("peca", produtos_lista[0] if produtos_lista else "") if record_to_edit else (produtos_lista[0] if produtos_lista else "")
    def_cod = record_to_edit.get("codProduto", catalogo_produtos.get(def_prod, "")) if record_to_edit else catalogo_produtos.get(def_prod, "")
    def_cat = record_to_edit.get("categoria", "Multi Bebidas") if record_to_edit else "Multi Bebidas"
    def_forn = record_to_edit.get("fornecedor", "EVOCA") if record_to_edit else "EVOCA"
    def_cod_forn = record_to_edit.get("codPecaFornecedor", "") if record_to_edit else ""
    def_solicitante = record_to_edit.get("solicitante", "WILLIAN NEVES") if record_to_edit else "WILLIAN NEVES"
    
    try:
        def_data = datetime.strptime(record_to_edit.get("data"), "%d/%m/%Y").date() if record_to_edit and "data" in record_to_edit else datetime.today().date()
    except Exception:
        def_data = datetime.today().date()
        
    def_hora = record_to_edit.get("horarioChegada", "10:00") if record_to_edit else "10:00"
    def_valor_compra = float(record_to_edit.get("custoUnit", 10.0)) if record_to_edit else 10.0
    def_valor_venda = float(record_to_edit.get("valorVenda", 20.0)) if record_to_edit else 20.0
    def_qt_sol = int(record_to_edit.get("qt", 10)) if record_to_edit else 10
    def_qt_apr = int(record_to_edit.get("qtAprovada", 10)) if record_to_edit else 10
    def_obs = record_to_edit.get("observacao", "") if record_to_edit else ""

    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        produto_selecionado = st.selectbox(
            "Produto (Coluna B da planilha)*",
            options=produtos_lista + ["Outro (Digitar Manualmente)"],
            index=produtos_lista.index(def_prod) if def_prod in produtos_lista else 0,
            key="widget_produto_select"
        )
    with col_p2:
        codigo_auto = catalogo_produtos.get(produto_selecionado, "") if produto_selecionado != "Outro (Digitar Manualmente)" else ""
        st.info(f"Cód. Planilha: **{codigo_auto or 'N/A'}**")

    # ------------------ FORMULÁRIO PRINCIPAL ------------------
    with st.form("form_pedido_completo", clear_on_submit=False):
        st.markdown("##### 📦 Dados da Ordem e Peça")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            ordem_compra = st.text_input("Ordem de Compra*", value=def_oc)
            if produto_selecionado == "Outro (Digitar Manualmente)":
                produto_final = st.text_input("Nome do Produto (Manual)*", value=def_prod).upper().strip()
                codigo_produto = st.text_input("Codigo do produto*", value=def_cod).strip()
            else:
                produto_final = produto_selecionado
                codigo_produto = st.text_input("Codigo do produto*", value=codigo_auto if codigo_auto else def_cod).strip()

        with col_f2:
            categoria = st.selectbox("Categoria*", options=["Multi Bebidas", "Acessorios", "Hidraulica", "Snaks", "Eletrica", "Outra"], index=0 if def_cat not in ["Acessorios", "Hidraulica", "Snaks", "Eletrica"] else ["Multi Bebidas", "Acessorios", "Hidraulica", "Snaks", "Eletrica"].index(def_cat))
            solicitante = st.text_input("Solicitante / Setor*", value=def_solicitante).upper().strip()

        with col_f3:
            fornecedor = st.text_input("Fornecedor*", value=def_forn).upper().strip()
            cod_peca_fornecedor = st.text_input("Cod da Peça do Fornecedor", value=def_cod_forn).strip()

        st.markdown("##### 📅 Prazos e Horários")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            data_pedido = st.date_input("Data do Pedido*", value=def_data)
        with col_t2:
            horario_chegada = st.text_input("Horario de Chegada do Pedido*", value=def_hora, placeholder="Ex: 14:30")

        st.markdown("##### 🔢 Quantidades & Custos")
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        with col_q1:
            qt_solicitada = st.number_input("Qt Solicitada*", min_value=1, value=def_qt_sol, step=1)
        with col_q2:
            qt_aprovada = st.number_input("Qt Aprovada*", min_value=0, value=def_qt_apr, step=1)
        with col_q3:
            valor_compra = st.number_input("Valor de Compra (Custo Unit. R$)*", min_value=0.01, value=def_valor_compra, step=0.50, format="%.2f")
        with col_q4:
            valor_venda = st.number_input("Valor de Venda (R$)", min_value=0.00, value=def_valor_venda, step=0.50, format="%.2f")

        qt_nao_aprovada = max(0, qt_solicitada - qt_aprovada)
        st.caption(f"ℹ️ **Qt Não Aprovada calculada:** {qt_nao_aprovada} un | **Custo Total Previsto:** R$ {(qt_aprovada * valor_compra):,.2f}")

        observacao = st.text_area("Observação", value=def_obs, placeholder="Detalhes adicionais, motivo de recusa, etc.", height=70)

        st.markdown("<br>", unsafe_allow_html=True)
        btn_label = "💾 Salvar Alterações na Ordem" if record_to_edit else "💾 Gravar Pedido no Banco de Dados e na Planilha"
        btn_salvar = st.form_submit_button(btn_label, use_container_width=True, type="primary")

        if btn_salvar:
            if not ordem_compra or not produto_final or not fornecedor or not solicitante:
                st.error("Preencha todos os campos obrigatórios (*).")
            elif qt_aprovada > qt_solicitada:
                st.error("A Quantidade Aprovada não pode ser maior que a Quantidade Solicitada.")
            else:
                meses_pt = {
                    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
                }

                registro_dados = {
                    "ordemCompra": ordem_compra,
                    "codProduto": codigo_produto,
                    "peca": produto_final,
                    "categoria": categoria,
                    "ano": str(data_pedido.year),
                    "mes": meses_pt.get(data_pedido.month, "Indefinido"),
                    "data": data_pedido.strftime("%d/%m/%Y"),
                    "horarioChegada": horario_chegada,
                    "custoUnit": float(valor_compra),
                    "valorVenda": float(valor_venda),
                    "qt": int(qt_solicitada),
                    "qtAprovada": int(qt_aprovada),
                    "qtNaoAprovada": int(qt_nao_aprovada),
                    "fornecedor": fornecedor,
                    "codPecaFornecedor": cod_peca_fornecedor,
                    "solicitante": solicitante,
                    "observacao": observacao
                }

                # 1. Grava diretamente na planilha Google Sheets via Webhook
                sucesso_planilha, msg_planilha = gravar_na_planilha_google(registro_dados)
                if not sucesso_planilha:
                    st.warning(f"⚠️ {msg_planilha}")
                else:
                    st.success("✅ Pedido gravado com sucesso na planilha 'Gastos peças e suprimentos'!")

                # 2. Atualiza a memória de sessão para o dashboard refletir imediatamente
                if record_to_edit:
                    idx = st.session_state.orders_data.index(record_to_edit)
                    st.session_state.orders_data[idx] = registro_dados
                    st.session_state.edit_order_id = None
                    st.success(f"✅ Ordem de Compra **{ordem_compra}** atualizada!")
                    st.rerun()
                else:
                    st.session_state.orders_data.insert(0, registro_dados)
                    st.success(f"✅ Nova Ordem de Compra **{ordem_compra}** ({produto_final}) salva!")
                    st.rerun()

    # ------------------ TABELA COMPLETA DE REGISTROS ------------------
    st.markdown("---")
    st.markdown("#### 📋 Ordens de Compra Registradas")
    df_preview = pd.DataFrame(st.session_state.orders_data)
    df_preview["Custo Total (R$)"] = df_preview["qtAprovada"] * df_preview["custoUnit"]
    
    colunas_visiveis = [
        'ordemCompra', 'codProduto', 'peca', 'categoria', 'data', 'horarioChegada',
        'custoUnit', 'qt', 'qtAprovada', 'qtNaoAprovada', 'valorVenda',
        'fornecedor', 'codPecaFornecedor', 'solicitante', 'Custo Total (R$)', 'observacao'
    ]
    cols_existentes = [c for c in colunas_visiveis if c in df_preview.columns]
    st.dataframe(df_preview[cols_existentes], use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# ABA 2: PAINEL EXECUTIVO ("Dashboard Compras")
# -----------------------------------------------------------------------------
elif st.session_state.active_tab == "Dashboard Compras":
    json_orders_data = json.dumps(st.session_state.orders_data, ensure_ascii=False)
    html_theme_class = "dark" if is_dark else "light"

    html_code = f"""
    <!DOCTYPE html>
    <html lang="pt-BR" class="{html_theme_class}">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Dashboard Executivo - Solicitações & Ordens de Compra de Peças</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
      <script src="https://unpkg.com/lucide@latest"></script>
      <script>
        tailwind.config = {{
          darkMode: 'class',
          theme: {{
            extend: {{
              colors: {{
                brand: {{
                  50: '#f0f9ff',
                  100: '#e0f2fe',
                  500: '#0284c7',
                  600: '#0369a1',
                  700: '#075985',
                  900: '#0c4a6e',
                }}
              }}
            }}
          }}
        }}
      </script>
      <style>
        body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
        .kpi-card {{
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .kpi-card:hover {{
          transform: translateY(-2px);
        }}
      </style>
    </head>
    <body class="bg-slate-100 text-slate-800 dark:bg-slate-950 dark:text-slate-100 min-h-screen transition-colors duration-300">

      <header class="sticky top-0 z-40 bg-white/95 dark:bg-slate-900/95 border-b border-slate-200 dark:border-slate-800 backdrop-blur-md px-6 py-4 shadow-sm">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div class="flex items-center gap-3">
            <div class="p-2.5 bg-blue-600 text-white rounded-xl shadow-lg shadow-blue-500/25">
              <i data-lucide="package-search" class="w-6 h-6"></i>
            </div>
            <div>
              <h1 class="text-xl font-bold tracking-tight">Painel de Compras & Solicitações de Peças</h1>
              <p class="text-xs text-slate-500 dark:text-slate-400">Controle Operacional: Ordens de Compra, Custos Reais e Status de Atendimento</p>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
              <span class="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span> Cálculos em Tempo Real
            </span>
          </div>
        </div>
      </header>

      <main class="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">

        <section class="bg-blue-50/70 dark:bg-slate-900/90 border border-blue-200 dark:border-blue-900/50 rounded-2xl p-5 shadow-sm">
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-3">
              <div class="p-2 rounded-xl bg-blue-600 text-white mt-0.5">
                <i data-lucide="clipboard-check" class="w-5 h-5"></i>
              </div>
              <div>
                <h2 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
                  Especificação & Requisitos da Solicitação
                  <span class="text-[10px] normal-case bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded-full border border-blue-300 dark:border-blue-800 font-semibold">Parâmetros Ativos</span>
                </h2>
                <div class="text-xs text-slate-600 dark:text-slate-300 mt-2 space-y-1.5 leading-relaxed">
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

        <!-- Filtros Dinâmicos -->
        <section class="bg-white dark:bg-slate-900 p-5 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-slate-300">
              <i data-lucide="sliders" class="w-4 h-4 text-blue-500"></i>
              <span>Filtros do Painel de Solicitações</span>
            </div>
            <span id="activeFilterBadge" class="text-xs font-medium text-slate-500 dark:text-slate-400">Filtrando: Todos os registros</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Ano</label>
              <select id="filterYear" class="w-full text-sm rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="ALL">Todos os Anos</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Mês</label>
              <select id="filterMonth" class="w-full text-sm rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="ALL">Todos os Meses</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Categoria de Peças</label>
              <select id="filterCategory" class="w-full text-sm rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="ALL">Todas as Categorias</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Solicitante / Setor</label>
              <select id="filterRequester" class="w-full text-sm rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="ALL">Todos os Solicitantes</option>
              </select>
            </div>

            <div class="flex items-end">
              <button id="resetFilters" class="w-full py-2 px-4 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition flex items-center justify-center gap-1.5">
                <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i>
                Limpar Filtros
              </button>
            </div>
          </div>
        </section>

        <!-- CARDS DE KPIS -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <div class="kpi-card bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Valor Compras (Custo)</span>
              <span class="p-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400">
                <i data-lucide="badge-dollar-sign" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3">
              <span id="kpiTotalCost" class="text-xl font-bold tracking-tight text-amber-600 dark:text-amber-400">R$ 0,00</span>
              <p class="text-[11px] text-slate-400 mt-0.5">Soma da coluna Custo</p>
            </div>
          </div>

          <div class="kpi-card bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Total de Pedidos</span>
              <span class="p-1.5 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
                <i data-lucide="clipboard-list" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3">
              <span id="kpiTotalRequests" class="text-xl font-bold tracking-tight">0</span>
              <p class="text-[11px] text-slate-400 mt-0.5">Ordens registradas</p>
            </div>
          </div>

          <div class="kpi-card bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Qtde Solicitada</span>
              <span class="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
                <i data-lucide="boxes" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3">
              <span id="kpiItemsQty" class="text-xl font-bold tracking-tight">0 un</span>
              <p class="text-[11px] text-slate-400 mt-0.5">Total de peças pedidas</p>
            </div>
          </div>

          <div class="kpi-card bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between ring-1 ring-emerald-500/20">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Peças Atendidas</span>
              <span class="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
                <i data-lucide="check-circle-2" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3 flex items-baseline justify-between">
              <div>
                <span id="kpiApprovedQty" class="text-xl font-bold tracking-tight text-emerald-600 dark:text-emerald-400">0 un</span>
                <p class="text-[11px] text-slate-400 mt-0.5">Aprovadas / Compradas</p>
              </div>
              <span id="kpiApprovedPercent" class="text-xs font-semibold px-2 py-0.5 rounded-md bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">0%</span>
            </div>
          </div>

          <div class="kpi-card bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between ring-1 ring-rose-500/20">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-rose-600 dark:text-rose-400 uppercase tracking-wider">Não Atendidas</span>
              <span class="p-1.5 rounded-lg bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400">
                <i data-lucide="x-circle" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3 flex items-baseline justify-between">
              <div>
                <span id="kpiUnapprovedQty" class="text-xl font-bold tracking-tight text-rose-600 dark:text-rose-400">0 un</span>
                <p class="text-[11px] text-slate-400 mt-0.5">Reprovadas / Pendentes</p>
              </div>
              <span id="kpiUnapprovedPercent" class="text-xs font-semibold px-2 py-0.5 rounded-md bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300">0%</span>
            </div>
          </div>

          <div class="kpi-card bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Custo Médio / Pedido</span>
              <span class="p-1.5 rounded-lg bg-cyan-50 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400">
                <i data-lucide="calculator" class="w-4 h-4"></i>
              </span>
            </div>
            <div class="mt-3">
              <span id="kpiAvgCost" class="text-xl font-bold tracking-tight">R$ 0,00</span>
              <p class="text-[11px] text-slate-400 mt-0.5">Média por pedido</p>
            </div>
          </div>
        </section>

        <!-- Top 5 Solicitantes em Agosto e Setembro -->
        <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="font-bold text-base flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                  Top 5 Solicitantes / Locais Internos — Agosto
                </h3>
                <p class="text-xs text-slate-500 dark:text-slate-400">Valores de peças solicitadas indicados no topo de cada barra</p>
              </div>
              <span class="text-xs font-semibold bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300 px-2 py-1 rounded-md">Agosto</span>
            </div>
            <div class="relative h-64">
              <canvas id="chartTopAgosto"></canvas>
            </div>
          </div>

          <div class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="font-bold text-base flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span>
                  Top 5 Solicitantes / Locais Internos — Setembro
                </h3>
                <p class="text-xs text-slate-500 dark:text-slate-400">Valores de peças solicitadas indicados no topo de cada barra</p>
              </div>
              <span class="text-xs font-semibold bg-cyan-100 text-cyan-700 dark:bg-cyan-900/50 dark:text-cyan-300 px-2 py-1 rounded-md">Setembro</span>
            </div>
            <div class="relative h-64">
              <canvas id="chartTopSetembro"></canvas>
            </div>
          </div>
        </section>

        <!-- Gráficos de Categorias e Fornecedor -->
        <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="font-bold text-base">Distribuição por Categoria de Peças</h3>
                <p class="text-xs text-slate-500 dark:text-slate-400">Quantidades totais exibidas em cada fatia</p>
              </div>
              <i data-lucide="pie-chart" class="w-5 h-5 text-slate-400"></i>
            </div>
            <div class="relative h-64">
              <canvas id="chartCategoryDist"></canvas>
            </div>
          </div>

          <div class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div class="flex justify-between items-center mb-4">
              <div>
                <h3 class="font-bold text-base">Soma de Custo por Fornecedor (R$)</h3>
                <p class="text-xs text-slate-500 dark:text-slate-400">Valor exato em reais destacado sobre as barras</p>
              </div>
              <i data-lucide="building-2" class="w-5 h-5 text-slate-400"></i>
            </div>
            <div class="relative h-64">
              <canvas id="chartSupplierCost"></canvas>
            </div>
          </div>
        </section>

        <!-- TABELA COM RESUMO POR PEÇA -->
        <section class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h2 class="text-base font-bold flex items-center gap-2">
                <i data-lucide="table" class="w-4 h-4 text-blue-500"></i>
                Resumo Detalhado por Peça Solicitada
              </h2>
              <p class="text-xs text-slate-500 dark:text-slate-400">Consolidado por item, quantidades solicitadas, atendidas e custo total</p>
            </div>

            <div class="flex items-center gap-3">
              <div class="relative">
                <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-2.5"></i>
                <input type="text" id="tableSearch" placeholder="Buscar peça..." class="text-xs pl-9 pr-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 w-48 sm:w-64">
              </div>
              <span id="tableCountBadge" class="text-xs px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-semibold">
                0 itens
              </span>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-600 dark:text-slate-300">
              <thead class="bg-slate-50 dark:bg-slate-800/60 uppercase font-semibold text-slate-500 dark:text-slate-400">
                <tr>
                  <th class="py-3 px-4 rounded-l-lg">Peça / Produto Solicitado</th>
                  <th class="py-3 px-4">Categoria</th>
                  <th class="py-3 px-4 text-center">Qtde Total</th>
                  <th class="py-3 px-4 text-center text-emerald-600 dark:text-emerald-400">Atendidas</th>
                  <th class="py-3 px-4 text-center text-rose-600 dark:text-rose-400">Não Atendidas</th>
                  <th class="py-3 px-4 text-center">Nº Pedidos</th>
                  <th class="py-3 px-4 text-right">Custo Unit. Médio</th>
                  <th class="py-3 px-4 text-right rounded-r-lg">Custo Total (R$)</th>
                </tr>
              </thead>
              <tbody id="tableBody" class="divide-y divide-slate-100 dark:divide-slate-800">
              </tbody>
            </table>
          </div>
        </section>

      </main>

      <footer class="max-w-7xl mx-auto px-6 py-8 text-center text-xs text-slate-400 border-t border-slate-200 dark:border-slate-800 mt-12">
        Painel Dinâmico de Solicitações e Ordens de Compra de Peças · Análise com Peças Atendidas e Integração Direta com Google Planilhas.
      </footer>

      <script>
        lucide.createIcons();
        Chart.register(ChartDataLabels);

        const isSystemDark = document.documentElement.classList.contains('dark');
        const rawOrdersData = {json_orders_data};

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

        function getChartTheme(isDark, type = 'bar') {{
          const textColor = isDark ? '#94a3b8' : '#64748b';
          const labelColor = isDark ? '#f1f5f9' : '#0f172a';
          const gridColor = isDark ? 'rgba(51, 65, 85, 0.4)' : 'rgba(226, 232, 240, 0.8)';

          return {{
            responsive: true,
            maintainAspectRatio: false,
            layout: {{ padding: {{ top: 22, bottom: 6, left: 6, right: 6 }} }},
            plugins: {{
              legend: {{ display: false }},
              tooltip: {{
                backgroundColor: isDark ? '#0f172a' : '#ffffff',
                titleColor: isDark ? '#f8fafc' : '#0f172a',
                bodyColor: isDark ? '#cbd5e1' : '#334155',
                borderColor: isDark ? '#334155' : '#e2e8f0',
                borderWidth: 1,
                padding: 10
              }},
              datalabels: {{
                anchor: 'end',
                align: 'top',
                offset: 2,
                color: labelColor,
                font: {{ family: 'Inter', weight: 'bold', size: 11 }},
                formatter: function(value) {{
                  if (value === 0 || value === null || value === undefined) return '';
                  return typeof value === 'number' && value >= 1000 ? value.toLocaleString('pt-BR') : value;
                }}
              }}
            }},
            scales: type === 'bar' ? {{
              x: {{ grid: {{ color: gridColor }}, ticks: {{ color: textColor, font: {{ family: 'Inter', size: 10 }} }} }},
              y: {{ grid: {{ color: gridColor }}, ticks: {{ color: textColor, font: {{ family: 'Inter', size: 10 }} }}, beginAtZero: true }}
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
            ...getChartTheme(isSystemDark, 'bar'),
            plugins: {{
              ...getChartTheme(isSystemDark, 'bar').plugins,
              datalabels: {{
                anchor: 'end',
                align: 'top',
                color: isSystemDark ? '#38bdf8' : '#0284c7',
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
            ...getChartTheme(isSystemDark, 'bar'),
            plugins: {{
              ...getChartTheme(isSystemDark, 'bar').plugins,
              datalabels: {{
                anchor: 'end',
                align: 'top',
                color: isSystemDark ? '#22d3ee' : '#0891b2',
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
              backgroundColor: [
                'rgba(2, 132, 199, 0.85)',
                'rgba(6, 182, 212, 0.85)',
                'rgba(245, 158, 11, 0.85)',
                'rgba(99, 102, 241, 0.85)',
                'rgba(16, 185, 129, 0.85)'
              ],
              borderWidth: 2,
              borderColor: isSystemDark ? '#0f172a' : '#ffffff'
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
                labels: {{ boxWidth: 12, color: isSystemDark ? '#94a3b8' : '#64748b', font: {{ family: 'Inter', size: 11 }} }}
              }},
              datalabels: {{
                color: '#ffffff',
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
            ...getChartTheme(isSystemDark, 'bar'),
            plugins: {{
              ...getChartTheme(isSystemDark, 'bar').plugins,
              datalabels: {{
                anchor: 'end',
                align: 'top',
                color: isSystemDark ? '#fbbf24' : '#d97706',
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
              <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                <td class="py-3 px-4 font-semibold text-slate-800 dark:text-slate-200">
                  ${{item.peca}}
                </td>
                <td class="py-3 px-4">
                  <span class="inline-block px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                    ${{item.categoria}}
                  </span>
                </td>
                <td class="py-3 px-4 text-center font-bold text-slate-700 dark:text-slate-300">
                  ${{item.qtTotal.toLocaleString('pt-BR')}} un
                </td>
                <td class="py-3 px-4 text-center font-semibold text-emerald-600 dark:text-emerald-400">
                  ${{item.qtAtendida.toLocaleString('pt-BR')}} un
                </td>
                <td class="py-3 px-4 text-center font-semibold text-rose-500 dark:text-rose-400">
                  ${{item.qtNaoAtendida.toLocaleString('pt-BR')}} un
                </td>
                <td class="py-3 px-4 text-center text-slate-500">
                  ${{item.pedidosCount}}
                </td>
                <td class="py-3 px-4 text-right text-slate-500">
                  ${{formatCurrency(unitAvg)}}
                </td>
                <td class="py-3 px-4 text-right font-bold text-amber-600 dark:text-amber-400">
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