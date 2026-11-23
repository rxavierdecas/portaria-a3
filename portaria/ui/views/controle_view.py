"""Tela 3 — Controle de Entrada e Saída."""

from tkinter import ttk

from portaria import config
from portaria.config import Cores
from portaria.models.movimentacao import Movimentacao, RegistroAcesso, Situacao
from portaria.ui.views.base import BaseView
from portaria.ui.widgets import Coluna, PlaceholderEntry, criar_tabela
from portaria.utils.formatters import formatar_hora_movimento

_COLUNAS = (
    Coluna("codigo", "Código", 70, "center"),
    Coluna("nome", "Nome", 220, expandir=True),
    Coluna("cpf", "CPF", 130, "center"),
    Coluna("tipo", "Tipo de acesso", 120, "center"),
    Coluna("entrada", "Entrada", 100, "center"),
    Coluna("saida", "Saída", 100, "center"),
    Coluna("situacao", "Situação", 90, "center"),
)


class ControleView(BaseView):
    titulo = "Controle de Acesso"
    subtitulo = "Acompanhamento da movimentação de pessoas na portaria."

    def construir(self) -> None:
        barra = ttk.Frame(self.corpo, style="Card.TFrame")
        barra.pack(fill="x", pady=(0, 12))
        self.busca = PlaceholderEntry(barra, "Pesquisar por nome ou CPF...", width=40)
        self.busca.pack(side="left", fill="x", expand=True)
        self.busca.bind("<Return>", lambda _e: self.atualizar())
        ttk.Button(barra, text="Pesquisar", style="Azul.TButton", command=self.atualizar).pack(
            side="left", padx=10
        )
        self.filtro = ttk.Combobox(barra, values=config.FILTROS_SITUACAO, state="readonly", width=12)
        self.filtro.set(config.FILTRO_TODOS)
        self.filtro.bind("<<ComboboxSelected>>", lambda _e: self.atualizar())
        self.filtro.pack(side="left")

        moldura, self.tabela = criar_tabela(self.corpo, _COLUNAS, altura=12)
        moldura.pack(fill="both", expand=True)
        self.tabela.tag_configure(Situacao.DENTRO.value, background=Cores.DENTRO_FUNDO)
        self.tabela.tag_configure(Situacao.SAIU.value, background=Cores.SAIU_FUNDO)

        rodape = ttk.Frame(self.corpo, style="Card.TFrame")
        rodape.pack(fill="x", pady=(12, 0))
        ttk.Button(rodape, text="➜  Registrar Entrada", style="Verde.TButton", command=self._registrar_entrada).pack(
            side="left"
        )
        ttk.Button(rodape, text="➜  Registrar Saída", style="Vermelho.TButton", command=self._registrar_saida).pack(
            side="left", padx=10
        )
        ttk.Button(rodape, text="Atualizar", style="Azul.TButton", command=self.atualizar).pack(side="left")
        ttk.Button(rodape, text="←  Voltar", style="Cinza.TButton", command=lambda: self.ctx.navegar("inicio")).pack(
            side="right"
        )
        self.status = ttk.Label(self.corpo, text="", style="Status.TLabel")
        self.status.pack(anchor="w", pady=(8, 0))

    def ao_exibir(self) -> None:
        self.atualizar()

    def atualizar(self, selecionar: int | None = None, mensagem: str = "") -> None:
        registros = self.executar(
            lambda: self.ctx.servicos.acesso.listar_controle(self.busca.valor(), self.filtro.get())
        )
        if registros is None:
            return
        self.tabela.delete(*self.tabela.get_children())
        for registro in registros:
            self.tabela.insert(
                "",
                "end",
                iid=str(registro.pessoa.id),
                values=self._valores(registro),
                tags=(registro.situacao.value,),
            )
        if selecionar is not None and self.tabela.exists(str(selecionar)):
            self.tabela.selection_set(str(selecionar))
            self.tabela.see(str(selecionar))

        dentro = sum(1 for r in registros if r.situacao is Situacao.DENTRO)
        resumo = f"{len(registros)} registro(s) exibido(s) · {dentro} pessoa(s) dentro"
        if mensagem:
            self.status.configure(text=f"✔ {mensagem}   ·   {resumo}", style="StatusOk.TLabel")
        else:
            self.status.configure(text=resumo, style="Status.TLabel")

    @staticmethod
    def _valores(registro: RegistroAcesso) -> tuple[str, ...]:
        mov = registro.movimentacao
        return (
            registro.pessoa.codigo,
            registro.pessoa.nome,
            registro.pessoa.cpf_formatado,
            registro.pessoa.tipo_acesso,
            formatar_hora_movimento(mov.entrada if mov else None),
            formatar_hora_movimento(mov.saida if mov else None),
            registro.situacao.value,
        )

    def _pessoa_selecionada(self) -> int | None:
        selecao = self.tabela.selection()
        if not selecao:
            self.avisar("Nenhuma pessoa selecionada", "Selecione uma pessoa na tabela.")
            return None
        return int(selecao[0])

    def _registrar_entrada(self) -> None:
        pessoa_id = self._pessoa_selecionada()
        if pessoa_id is None:
            return
        mov = self.executar(lambda: self.ctx.servicos.acesso.registrar_entrada(pessoa_id))
        self._apos_operacao(pessoa_id, mov, "Entrada")

    def _registrar_saida(self) -> None:
        pessoa_id = self._pessoa_selecionada()
        if pessoa_id is None:
            return
        mov = self.executar(lambda: self.ctx.servicos.acesso.registrar_saida(pessoa_id))
        self._apos_operacao(pessoa_id, mov, "Saída")

    def _apos_operacao(self, pessoa_id: int, mov: Movimentacao | None, tipo: str) -> None:
        if mov is None:
            return
        nome = self.tabela.set(str(pessoa_id), "nome")
        momento = mov.saida if tipo == "Saída" and mov.saida else mov.entrada
        mensagem = f"{tipo} de {nome} registrada às {momento:%H:%M}"
        # Limpa o filtro se a pessoa deixaria de aparecer com o filtro atual.
        if self.filtro.get() != config.FILTRO_TODOS:
            self.filtro.set(config.FILTRO_TODOS)
        self.atualizar(selecionar=pessoa_id, mensagem=mensagem)
