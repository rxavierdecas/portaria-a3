"""Desafio extra — Cadastro de veículos e placas."""

from tkinter import ttk

from portaria.ui.views.base import BaseView, campo
from portaria.ui.widgets import Coluna, PlaceholderEntry, criar_tabela

_SELECIONE = "Selecione..."


class VeiculosView(BaseView):
    titulo = "Veículos"
    subtitulo = "Cadastro de veículos e placas vinculados às pessoas cadastradas."

    def construir(self) -> None:
        self._pessoas_por_rotulo: dict[str, int] = {}

        grade = ttk.Frame(self.corpo, style="Card.TFrame")
        grade.pack(fill="x")
        for coluna, peso in enumerate((3, 2, 2, 2)):
            grade.columnconfigure(coluna, weight=peso, uniform="v")

        self.pessoa = campo(grade, "Proprietário *", 0, 0, lambda m: ttk.Combobox(m, state="readonly"))
        self.placa = campo(grade, "Placa *", 0, 1, lambda m: PlaceholderEntry(m, "ABC-1234 / ABC1D23"))
        self.modelo = campo(grade, "Modelo *", 0, 2, lambda m: PlaceholderEntry(m, "Ex.: Onix"))
        self.cor = campo(grade, "Cor *", 0, 3, lambda m: PlaceholderEntry(m, "Ex.: Prata"))
        self.placa.bind("<KeyRelease>", lambda _e: self._placa_maiuscula(), add="+")

        botoes = ttk.Frame(self.corpo, style="Card.TFrame")
        botoes.pack(fill="x", pady=(0, 12))
        ttk.Button(botoes, text="✚  Cadastrar", style="Verde.TButton", command=self._cadastrar).pack(side="left")
        ttk.Button(botoes, text="Limpar", style="Cinza.TButton", command=self._limpar).pack(side="left", padx=10)
        ttk.Button(botoes, text="✕  Excluir selecionado", style="Vermelho.TButton", command=self._excluir).pack(
            side="right"
        )

        moldura, self.tabela = criar_tabela(
            self.corpo,
            (
                Coluna("codigo", "Código", 70, "center"),
                Coluna("placa", "Placa", 110, "center"),
                Coluna("modelo", "Modelo", 160),
                Coluna("cor", "Cor", 110),
                Coluna("dono", "Proprietário", 240, expandir=True),
            ),
        )
        moldura.pack(fill="both", expand=True)

    def ao_exibir(self) -> None:
        pessoas = self.executar(self.ctx.servicos.pessoas.listar) or []
        self._pessoas_por_rotulo = {p.rotulo: p.id for p in pessoas if p.id is not None}
        self.pessoa.configure(values=list(self._pessoas_por_rotulo))
        if self.pessoa.get() not in self._pessoas_por_rotulo:
            self.pessoa.set(_SELECIONE)
        self._atualizar_tabela()

    def _placa_maiuscula(self) -> None:
        texto = self.placa.valor()
        if texto != texto.upper():
            posicao = self.placa.index("insert")
            self.placa.definir(texto.upper())
            self.placa.icursor(posicao)

    def _atualizar_tabela(self) -> None:
        veiculos = self.executar(self.ctx.servicos.veiculos.listar) or []
        self.tabela.delete(*self.tabela.get_children())
        for indice, veiculo in enumerate(veiculos):
            self.tabela.insert(
                "",
                "end",
                iid=str(veiculo.id),
                values=(f"{veiculo.id:03d}", veiculo.placa_formatada, veiculo.modelo, veiculo.cor, veiculo.pessoa_nome),
                tags=("par",) if indice % 2 else (),
            )

    def _limpar(self) -> None:
        self.pessoa.set(_SELECIONE)
        for entrada in (self.placa, self.modelo, self.cor):
            entrada.limpar()

    def _cadastrar(self) -> None:
        pessoa_id = self._pessoas_por_rotulo.get(self.pessoa.get())
        veiculo = self.executar(
            lambda: self.ctx.servicos.veiculos.cadastrar(
                pessoa_id, self.placa.valor(), self.modelo.valor(), self.cor.valor()
            )
        )
        if veiculo is None:
            return
        self.informar("Veículo cadastrado", f"Placa {veiculo.placa_formatada} cadastrada com sucesso.")
        self._limpar()
        self._atualizar_tabela()

    def _excluir(self) -> None:
        selecao = self.tabela.selection()
        if not selecao:
            self.avisar("Nenhum veículo selecionado", "Selecione um veículo na tabela.")
            return
        placa = self.tabela.set(selecao[0], "placa")
        if not self.confirmar("Excluir veículo", f"Deseja excluir o veículo de placa {placa}?"):
            return
        veiculo_id = int(selecao[0])
        if self.tentar(lambda: self.ctx.servicos.veiculos.excluir(veiculo_id)):
            self._atualizar_tabela()
