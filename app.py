import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Configuração do Tema Corporativo Claro ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Constantes da Planilha
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1iWjdaZLAp5hi9YIhmfSO4cPBn6fkfDjef8PAdZp1nsY/edit"
GID_PEDIDOS = 643448898
GID_CATALOGO = 270834817
CREDENTIALS_FILE = "credentials.json"

COLUNAS_PEDIDO = [
    "Ordem de Compra", "Código do produto", "Produto", "Categoria",
    "Data do Pedido", "Horário de Chegada do Pedido", "Valor de Compra",
    "Qt Solicitada", "Qt Aprovada", "Qt Não Aprovada", "Valor de Venda",
    "Fornecedor", "Cod da Peça do Fornecedor", "Observação"
]


class SistemaComprasApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Portal Corporativo - Pedidos de Compra")
        self.geometry("1180x820")
        self.minsize(1050, 720)

        # Dados em memória
        self.catalogo_pecas = []  # Lista com dicts {codigo, nome, fornecedor}
        self.itens_carrinho = []   # Itens temporários da Ordem de Compra atual
        self.ws_pedidos = None
        self.ws_catalogo = None

        self.iniciar_conexao_sheets()
        self.construir_interface()
        self.carregar_catalogo()

    def iniciar_conexao_sheets(self):
        """Conecta com as abas do Google Sheets pelos seus GIDs."""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
            client = gspread.authorize(creds)
            planilha = client.open_by_url(SPREADSHEET_URL)
            
            # Localizar abas pelos GIDs fornecidos
            for sheet in planilha.worksheets():
                if sheet.id == GID_PEDIDOS:
                    self.ws_pedidos = sheet
                elif sheet.id == GID_CATALOGO:
                    self.ws_catalogo = sheet

            if not self.ws_pedidos:
                self.ws_pedidos = planilha.sheet1
        except Exception as e:
            messagebox.showwarning(
                "Aviso de Conexão",
                f"Modo offline ou erro ao conectar com o Google Sheets: {e}\n"
                "Verifique o arquivo credentials.json e os acessos da conta de serviço."
            )

    def carregar_catalogo(self):
        """Carrega as peças da aba de catálogo (Col A: Código, Col B: Nome, Col F: Fornecedor)."""
        if not self.ws_catalogo:
            return
        try:
            valores = self.ws_catalogo.get_all_values()
            self.catalogo_pecas = []
            # Pula linha de cabeçalho
            for row in valores[1:]:
                if len(row) >= 2 and (row[0].strip() or row[1].strip()):
                    cod = row[0].strip()
                    nome = row[1].strip()
                    fornecedor = row[5].strip() if len(row) > 5 else ""
                    self.catalogo_pecas.append({
                        "codigo": cod,
                        "nome": nome,
                        "fornecedor": fornecedor
                    })
        except Exception as e:
            print(f"Erro ao carregar catálogo: {e}")

    def construir_interface(self):
        # Top Banner / Header
        header = ctk.CTkFrame(self, fg_color="#1E3A8A", height=70, corner_radius=0)
        header.pack(fill="x")
        
        titulo_label = ctk.CTkLabel(
            header, text="SISTEMA DE GESTÃO DE COMPRAS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF"
        )
        titulo_label.pack(side="left", padx=25, pady=18)

        # Tabview (Abas principais: Novo Pedido e Consulta/Edição)
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=15)
        
        self.tab_novo = self.tabview.add("  Novo Pedido de Compra  ")
        self.tab_consulta = self.tabview.add("  Consultar e Editar Ordem  ")

        self.montar_aba_novo_pedido()
        self.montar_aba_consulta()

    # ==========================================
    # ABA 1: NOVO PEDIDO (MÚLTIPLAS PEÇAS)
    # ==========================================
    def montar_aba_novo_pedido(self):
        container = ctk.CTkScrollableFrame(self.tab_novo, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Bloco 1: Dados Gerais da Ordem ---
        box_ordem = ctk.CTkFrame(container, fg_color="#F8FAFC", border_color="#CBD5E1", border_width=1)
        box_ordem.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(
            box_ordem, text="Identificação da Ordem de Compra",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#1E293B"
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(10, 8))

        ctk.CTkLabel(box_ordem, text="Ordem de Compra *:", text_color="#334155").grid(row=1, column=0, sticky="w", padx=15)
        self.txt_ordem = ctk.CTkEntry(box_ordem, width=220, placeholder_text="Ex: OC-2026-001")
        self.txt_ordem.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(box_ordem, text="Data do Pedido:", text_color="#334155").grid(row=1, column=2, sticky="w", padx=15)
        self.txt_data_pedido = ctk.CTkEntry(box_ordem, width=180)
        self.txt_data_pedido.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.txt_data_pedido.configure(state="readonly")
        self.txt_data_pedido.grid(row=1, column=3, sticky="w", padx=10, pady=5)

        # --- Bloco 2: Seleção e Dados do Item ---
        box_item = ctk.CTkFrame(container, fg_color="#FFFFFF", border_color="#CBD5E1", border_width=1)
        box_item.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(
            box_item, text="Adicionar Peça / Produto",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#1E293B"
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(10, 5))

        # Busca rápida no catálogo
        ctk.CTkLabel(box_item, text="Buscar no Catálogo:", text_color="#334155").grid(row=1, column=0, sticky="w", padx=15, pady=3)
        self.txt_busca_catalogo = ctk.CTkEntry(box_item, width=320, placeholder_text="Digite código ou nome da peça...")
        self.txt_busca_catalogo.grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=3)
        btn_buscar = ctk.CTkButton(box_item, text="Localizar Peça", command=self.abrir_dialogo_catalogo, width=120)
        btn_buscar.grid(row=1, column=3, sticky="w", padx=10, pady=3)

        # Campos do Item
        ctk.CTkLabel(box_item, text="Código do Produto:").grid(row=2, column=0, sticky="w", padx=15, pady=4)
        self.txt_cod_prod = ctk.CTkEntry(box_item, width=220)
        self.txt_cod_prod.grid(row=2, column=1, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(box_item, text="Nome do Produto:").grid(row=2, column=2, sticky="w", padx=15, pady=4)
        self.txt_produto = ctk.CTkEntry(box_item, width=280)
        self.txt_produto.grid(row=2, column=3, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(box_item, text="Categoria:").grid(row=3, column=0, sticky="w", padx=15, pady=4)
        self.txt_categoria = ctk.CTkEntry(box_item, width=220)
        self.txt_categoria.grid(row=3, column=1, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(box_item, text="Fornecedor:").grid(row=3, column=2, sticky="w", padx=15, pady=4)
        self.txt_fornecedor = ctk.CTkEntry(box_item, width=280)
        self.txt_fornecedor.grid(row=3, column=3, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(box_item, text="Cód Peça Fornecedor:").grid(row=4, column=0, sticky="w", padx=15, pady=4)
        self.txt_cod_forn = ctk.CTkEntry(box_item, width=220)
        self.txt_cod_forn.grid(row=4, column=1, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(box_item, text="Horário de Chegada:").grid(row=4, column=2, sticky="w", padx=15, pady=4)
        self.txt_hora_chegada = ctk.CTkEntry(box_item, width=150, placeholder_text="Ex: 14:30")
        self.txt_hora_chegada.grid(row=4, column=3, sticky="w", padx=10, pady=4)

        # Quantidades e Valores
        ctk.CTkLabel(box_item, text="Qt Solicitada:").grid(row=5, column=0, sticky="w", padx=15, pady=4)
        self.txt_qt_solicitada = ctk.CTkEntry(box_item, width=140)
        self.txt_qt_solicitada.grid(row=5, column=1, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(box_item, text="Qt Aprovada:").grid(row=5, column=2, sticky="w", padx=15, pady=4)
        self.txt_qt_aprovada = ctk.CTkEntry(box_item, width=140)
        self.txt_qt_aprovada.grid(row=5, column=3, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(box_item, text="Qt Não Aprovada:").grid(row=6, column=0, sticky="w", padx=15, pady=4)
        self.txt_qt_nao_aprovada = ctk.CTkEntry(box_item, width=140)
        self.txt_qt_nao_aprovada.grid(row=6, column=1, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(box_item, text="Valor de Compra (R$):").grid(row=6, column=2, sticky="w", padx=15, pady=4)
        self.txt_vlr_compra = ctk.CTkEntry(box_item, width=140)
        self.txt_vlr_compra.grid(row=6, column=3, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(box_item, text="Valor de Venda (R$):").grid(row=7, column=0, sticky="w", padx=15, pady=4)
        self.txt_vlr_venda = ctk.CTkEntry(box_item, width=140)
        self.txt_vlr_venda.grid(row=7, column=1, sticky="w", padx=10, pady=4)

        ctk.CTkLabel(box_item, text="Observação:").grid(row=7, column=2, sticky="w", padx=15, pady=4)
        self.txt_obs = ctk.CTkEntry(box_item, width=280)
        self.txt_obs.grid(row=7, column=3, sticky="w", padx=10, pady=4)

        # Botão para adicionar peça à grade
        btn_adicionar_item = ctk.CTkButton(
            box_item, text="+ Incluir Peça na Ordem",
            fg_color="#0F766E", hover_color="#115E59",
            command=self.adicionar_item_lista
        )
        btn_adicionar_item.grid(row=8, column=2, columnspan=2, sticky="e", padx=15, pady=12)

        # --- Bloco 3: Tabela de Peças Inseridas na OC Atual ---
        box_grid = ctk.CTkFrame(container, fg_color="#F8FAFC", border_color="#CBD5E1", border_width=1)
        box_grid.pack(fill="both", expand=True, pady=8, padx=5)

        ctk.CTkLabel(
            box_grid, text="Peças Adicionadas a esta Ordem de Compra",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#1E293B"
        ).pack(anchor="w", padx=15, pady=(10, 5))

        colunas_tabela = ("cod", "produto", "categoria", "fornecedor", "qt_solic", "vlr_compra")
        self.tree_itens = ttk.Treeview(box_grid, columns=colunas_tabela, show="headings", height=5)
        self.tree_itens.heading("cod", text="Cód. Produto")
        self.tree_itens.heading("produto", text="Produto")
        self.tree_itens.heading("categoria", text="Categoria")
        self.tree_itens.heading("fornecedor", text="Fornecedor")
        self.tree_itens.heading("qt_solic", text="Qt. Solic.")
        self.tree_itens.heading("vlr_compra", text="Vlr. Compra")

        self.tree_itens.column("cod", width=90)
        self.tree_itens.column("produto", width=260)
        self.tree_itens.column("categoria", width=120)
        self.tree_itens.column("fornecedor", width=160)
        self.tree_itens.column("qt_solic", width=70)
        self.tree_itens.column("vlr_compra", width=90)
        self.tree_itens.pack(fill="x", padx=15, pady=5)

        # Botões de Ação Final
        acoes_frame = ctk.CTkFrame(container, fg_color="transparent")
        acoes_frame.pack(fill="x", pady=10)

        btn_remover = ctk.CTkButton(
            acoes_frame, text="Remover Item Selecionado",
            fg_color="#DC2626", hover_color="#B91C1C",
            command=self.remover_item_lista
        )
        btn_remover.pack(side="left", padx=10)

        btn_salvar_ordem = ctk.CTkButton(
            acoes_frame, text="✔ Gravar Ordem Completa na Planilha",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", height=40,
            command=self.salvar_ordem_na_planilha
        )
        btn_salvar_ordem.pack(side="right", padx=10)

    # ==========================================
    # MODAL DE SELEÇÃO DE PEÇAS DO CATÁLOGO
    # ==========================================
    def abrir_dialogo_catalogo(self):
        """Abre uma janela modal para pesquisar e selecionar do catálogo."""
        termo = self.txt_busca_catalogo.get().strip().lower()

        dialog = ctk.CTkToplevel(self)
        dialog.title("Catálogo de Peças Pré-criadas")
        dialog.geometry("680x440")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Selecione a Peça Desejada:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=10)

        cols = ("cod", "nome", "fornecedor")
        tree = ttk.Treeview(dialog, columns=cols, show="headings", height=12)
        tree.heading("cod", text="Cód. Peça (Col A)")
        tree.heading("nome", text="Nome da Peça (Col B)")
        tree.heading("fornecedor", text="Fornecedor (Col F)")
        tree.column("cod", width=120)
        tree.column("nome", width=340)
        tree.column("fornecedor", width=180)
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Filtrar registros
        for p in self.catalogo_pecas:
            if not termo or termo in p["codigo"].lower() or termo in p["nome"].lower():
                tree.insert("", "end", values=(p["codigo"], p["nome"], p["fornecedor"]))

        def selecionar():
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showwarning("Atenção", "Selecione uma peça na lista.")
                return
            dados = tree.item(selecionado[0], "values")
            self.txt_cod_prod.delete(0, "end")
            self.txt_cod_prod.insert(0, dados[0])
            self.txt_produto.delete(0, "end")
            self.txt_produto.insert(0, dados[1])
            self.txt_fornecedor.delete(0, "end")
            self.txt_fornecedor.insert(0, dados[2])
            dialog.destroy()

        btn_confirmar = ctk.CTkButton(dialog, text="Carregar no Formulário", command=selecionar)
        btn_confirmar.pack(pady=10)

    def adicionar_item_lista(self):
        """Valida e adiciona um item à fila da Ordem de Compra atual."""
        ordem = self.txt_ordem.get().strip()
        cod_prod = self.txt_cod_prod.get().strip()
        prod = self.txt_produto.get().strip()

        if not ordem:
            messagebox.showwarning("Validação", "Preencha a 'Ordem de Compra' antes de inserir itens.")
            return
        if not prod:
            messagebox.showwarning("Validação", "Selecione ou preencha o nome do 'Produto'.")
            return

        item = {
            "Ordem de Compra": ordem,
            "Código do produto": cod_prod,
            "Produto": prod,
            "Categoria": self.txt_categoria.get().strip(),
            "Data do Pedido": self.txt_data_pedido.get().strip(),
            "Horário de Chegada do Pedido": self.txt_hora_chegada.get().strip(),
            "Valor de Compra": self.txt_vlr_compra.get().strip(),
            "Qt Solicitada": self.txt_qt_solicitada.get().strip(),
            "Qt Aprovada": self.txt_qt_aprovada.get().strip(),
            "Qt Não Aprovada": self.txt_qt_nao_aprovada.get().strip(),
            "Valor de Venda": self.txt_vlr_venda.get().strip(),
            "Fornecedor": self.txt_fornecedor.get().strip(),
            "Cod da Peça do Fornecedor": self.txt_cod_forn.get().strip(),
            "Observação": self.txt_obs.get().strip(),
        }

        self.itens_carrinho.append(item)
        self.tree_itens.insert("", "end", values=(
            item["Código do produto"], item["Produto"], item["Categoria"],
            item["Fornecedor"], item["Qt Solicitada"], item["Valor de Compra"]
        ))

        # Limpar campos de peça
        for campo in [self.txt_cod_prod, self.txt_produto, self.txt_categoria,
                      self.txt_fornecedor, self.txt_cod_forn, self.txt_hora_chegada,
                      self.txt_qt_solicitada, self.txt_qt_aprovada, self.txt_qt_nao_aprovada,
                      self.txt_vlr_compra, self.txt_vlr_venda, self.txt_obs]:
            campo.delete(0, "end")

    def remover_item_lista(self):
        sel = self.tree_itens.selection()
        if not sel:
            return
        idx = self.tree_itens.index(sel[0])
        del self.itens_carrinho[idx]
        self.tree_itens.delete(sel[0])

    def salvar_ordem_na_planilha(self):
        """Persiste todas as peças da ordem na aba de pedidos."""
        if not self.itens_carrinho:
            messagebox.showwarning("Atenção", "Adicione ao menos 1 peça antes de gravar a ordem.")
            return

        if not self.ws_pedidos:
            messagebox.showerror("Erro", "Sem conexão com o Google Sheets.")
            return

        try:
            linhas_para_inserir = []
            for item in self.itens_carrinho:
                linha = [item.get(col, "") for col in COLUNAS_PEDIDO]
                linhas_para_inserir.append(linha)

            self.ws_pedidos.append_rows(linhas_para_inserir)
            messagebox.showinfo("Sucesso", f"Ordem {self.txt_ordem.get()} salva com {len(linhas_para_inserir)} peça(s)!")

            # Resetar tela
            self.itens_carrinho.clear()
            for i in self.tree_itens.get_children():
                self.tree_itens.delete(i)
            self.txt_ordem.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Falha ao enviar para o Google Sheets:\n{e}")

    # ==========================================
    # ABA 2: CONSULTAR E EDITAR ORDEM DE COMPRA
    # ==========================================
    def montar_aba_consulta(self):
        frame = ctk.CTkFrame(self.tab_consulta, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Barra de Pesquisa de OC
        busca_box = ctk.CTkFrame(frame, fg_color="#F8FAFC", border_color="#CBD5E1", border_width=1)
        busca_box.pack(fill="x", pady=5)

        ctk.CTkLabel(busca_box, text="Ordem de Compra:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15, pady=10)
        self.txt_consulta_oc = ctk.CTkEntry(busca_box, width=220, placeholder_text="Digite a OC para buscar...")
        self.txt_consulta_oc.pack(side="left", padx=10, pady=10)

        btn_consultar = ctk.CTkButton(busca_box, text="Pesquisar Ordem", command=self.pesquisar_ordem)
        btn_consultar.pack(side="left", padx=10, pady=10)

        # Lista de Itens Encontrados
        self.tree_consulta = ttk.Treeview(
            frame,
            columns=("linha", "oc", "cod", "produto", "fornecedor", "qt_aprov", "vlr_compra"),
            show="headings",
            height=10
        )
        self.tree_consulta.heading("linha", text="Linha Planilha")
        self.tree_consulta.heading("oc", text="Ordem Compra")
        self.tree_consulta.heading("cod", text="Cód. Produto")
        self.tree_consulta.heading("produto", text="Produto")
        self.tree_consulta.heading("fornecedor", text="Fornecedor")
        self.tree_consulta.heading("qt_aprov", text="Qt Aprovada")
        self.tree_consulta.heading("vlr_compra", text="Vlr Compra")

        self.tree_consulta.column("linha", width=80)
        self.tree_consulta.column("oc", width=110)
        self.tree_consulta.column("cod", width=100)
        self.tree_consulta.column("produto", width=250)
        self.tree_consulta.column("fornecedor", width=160)
        self.tree_consulta.column("qt_aprov", width=90)
        self.tree_consulta.column("vlr_compra", width=90)
        self.tree_consulta.pack(fill="both", expand=True, pady=10)

        # Botão de Ação para Edição do Item Selecionado
        btn_editar = ctk.CTkButton(
            frame, text="Editar Item Selecionado",
            fg_color="#0F766E", hover_color="#115E59",
            command=self.abrir_janela_edicao
        )
        btn_editar.pack(anchor="e", pady=5)

    def pesquisar_ordem(self):
        """Busca todas as linhas correspondentes à Ordem de Compra pesquisada."""
        oc_alvo = self.txt_consulta_oc.get().strip()
        if not oc_alvo:
            messagebox.showwarning("Aviso", "Informe a Ordem de Compra para pesquisa.")
            return

        for item in self.tree_consulta.get_children():
            self.tree_consulta.delete(item)

        if not self.ws_pedidos:
            messagebox.showerror("Erro", "Sem conexão com o Google Sheets.")
            return

        try:
            todos_dados = self.ws_pedidos.get_all_values()
            encontrados = 0
            for idx, row in enumerate(todos_dados[1:], start=2):
                if len(row) > 0 and row[0].strip().lower() == oc_alvo.lower():
                    encontrados += 1
                    cod = row[1] if len(row) > 1 else ""
                    prod = row[2] if len(row) > 2 else ""
                    forn = row[11] if len(row) > 11 else ""
                    qt_apr = row[8] if len(row) > 8 else ""
                    vlr_c = row[6] if len(row) > 6 else ""
                    self.tree_consulta.insert("", "end", values=(idx, row[0], cod, prod, forn, qt_apr, vlr_c))

            if encontrados == 0:
                messagebox.showinfo("Pesquisa", f"Nenhum registro encontrado para a ordem '{oc_alvo}'.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao pesquisar: {e}")

    def abrir_janela_edicao(self):
        """Abre modal com todos os campos daquela linha para edição."""
        sel = self.tree_consulta.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma peça na tabela acima para editar.")
            return

        num_linha = int(self.tree_consulta.item(sel[0], "values")[0])
        linha_atual = self.ws_pedidos.row_values(num_linha)

        modal = ctk.CTkToplevel(self)
        modal.title(f"Editar Item - Linha {num_linha}")
        modal.geometry("650x600")
        modal.transient(self)
        modal.grab_set()

        scroll_edit = ctk.CTkScrollableFrame(modal)
        scroll_edit.pack(fill="both", expand=True, padx=15, pady=15)

        entradas = {}
        for idx, col_nome in enumerate(COLUNAS_PEDIDO):
            ctk.CTkLabel(scroll_edit, text=col_nome + ":").grid(row=idx, column=0, sticky="w", padx=10, pady=4)
            ent = ctk.CTkEntry(scroll_edit, width=320)
            valor = linha_atual[idx] if idx < len(linha_atual) else ""
            ent.insert(0, valor)
            ent.grid(row=idx, column=1, sticky="w", padx=10, pady=4)
            entradas[idx + 1] = ent

        def salvar_alteracoes():
            try:
                novos_valores = [entradas[i + 1].get().strip() for i in range(len(COLUNAS_PEDIDO))]
                # Atualizar a linha correspondente na planilha
                cell_range = f"A{num_linha}:N{num_linha}"
                self.ws_pedidos.update(range_name=cell_range, values=[novos_valores])
                messagebox.showinfo("Sucesso", "Dados atualizados com sucesso!")
                modal.destroy()
                self.pesquisar_ordem()
            except Exception as ex:
                messagebox.showerror("Erro ao Atualizar", f"Falha: {ex}")

        btn_salvar = ctk.CTkButton(
            scroll_edit, text="Gravar Atualização na Planilha",
            fg_color="#2563EB", hover_color="#1D4ED8",
            command=salvar_alteracoes
        )
        btn_salvar.grid(row=len(COLUNAS_PEDIDO), column=0, columnspan=2, pady=15)


if __name__ == "__main__":
    app = SistemaComprasApp()
    app.mainloop()