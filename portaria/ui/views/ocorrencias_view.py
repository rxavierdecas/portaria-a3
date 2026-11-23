"""Desafio extra — Registro de ocorrências na portaria."""

from tkinter import ttk

from portaria import config
from portaria.ui.views.base import BaseView, campo
from portaria.ui.widgets import Coluna, TextoMultilinha, criar_tabela
from portaria.utils.formatters import formatar_data_hora

_SELECIONE = "Selecione..."
_NENHUMA = "Nenhuma"


class OcorrenciasView(BaseView):
    titulo = "Ocorrências"
    subtitulo = "Registro de ocorrências na portaria. Dê um duplo clique para ver a descrição completa."

    def construir(self) -> None:
        self._pessoas_por_rotulo: dict[str, int] = {}

        grade = ttk.Frame(self.corpo, style="Card.TFrame")
        grade.pack(fill="x")
        grade.columnconfigure(0, weight=1, uniform="o")
        grade.columnconfigure(1, weight=1, uniform="o")
        grade.columnconfigure(2, weight=2, uniform="o")

        self.tipo = campo(
            grade, "Tipo *", 0, 0, lambda m: ttk.Combobox(m, values=config.TIPOS_OCORRENCIA, state="readonly")
        )
        self.pessoa = campo(grade, "Pessoa envolvida", 0, 1, lambda m: ttk.Combobox(m, state="readonly"))
        self.descricao = campo(grade, "Descrição *", 0, 2, lambda m: TextoMultilinha(m, altura=3))

        botoes = ttk.Frame(self.corpo, style="Card.TFrame")
        botoes.pack(fill="x", pady=(0, 12))
        ttk.Button(botoes, text="✚  Registrar", style="Verde.TButton", command=self._registrar).pack(side="left")
        ttk.Button(botoes, text="Limpar", style="Cinza.TButton", command=self._limpar).pack(side="left", padx=10)

        moldura, self.tabela = criar_tabela(
            self.corpo,
            (
                Coluna("data", "Data/hora", 130, "center"),
                Coluna("tipo", "Tipo", 160),
                Coluna("descricao", "Descrição", 300, expandir=True),
                Coluna("pessoa", "Pessoa", 160),
                Coluna("usuario", "Registrado por", 130),
            ),
        )
        moldura.pack(fill="both", expand=True)
        self.tabela.bind("<Double-1>", lambda _e: self._ver_detalhes())
        self._descricoes: dict[str, str] = {}
        self._limpar()

    def ao_exibir(self) -> None:
        pessoas = self.executar(self.ctx.servicos.pessoas.listar) or []
        self._pessoas_por_rotulo = {p.rotulo: p.id for p in pessoas if p.id is not None}
        self.pessoa.configure(values=[_NENHUMA, *self._pessoas_por_rotulo])
        if self.pessoa.get() not in self._pessoas_por_rotulo:
            self.pessoa.set(_NENHUMA)
        self._atualizar_tabela()

    def _limpar(self) -> None:
        self.tipo.set(_SELECIONE)
        self.pessoa.set(_NENHUMA)
        self.descricao.limpar()

    def _atualizar_tabela(self) -> None:
        ocorrencias = self.executar(self.ctx.servicos.ocorrencias.listar) or []
        self.tabela.delete(*self.tabela.get_children())
        self._descricoes.clear()
        for indice, ocorrencia in enumerate(ocorrencias):
            iid = str(ocorrencia.id)
            resumo = " ".join(ocorrencia.descricao.split())
            self._descricoes[iid] = ocorrencia.descricao
            self.tabela.insert(
                "",
                "end",
                iid=iid,
                values=(
                    formatar_data_hora(ocorrencia.data_hora),
                    ocorrencia.tipo,
                    resumo,
                    ocorrencia.pessoa_nome or "-",
                    ocorrencia.registrado_por_nome,
                ),
                tags=("par",) if indice % 2 else (),
            )

    def _registrar(self) -> None:
        pessoa_id = self._pessoas_por_rotulo.get(self.pessoa.get())
        ocorrencia = self.executar(
            lambda: self.ctx.servicos.ocorrencias.registrar(
                tipo=self.tipo.get(),
                descricao=self.descricao.valor(),
                usuario_id=self.ctx.usuario.id,
                pessoa_id=pessoa_id,
            )
        )
        if ocorrencia is None:
            return
        self.informar("Ocorrência registrada", f"Ocorrência registrada em {formatar_data_hora(ocorrencia.data_hora)}.")
        self._limpar()
        self._atualizar_tabela()

    def _ver_detalhes(self) -> None:
        selecao = self.tabela.selection()
        if not selecao:
            return
        valores = self.tabela.item(selecao[0], "values")
        self.informar(
            f"Ocorrência — {valores[1]}",
            f"Data/hora: {valores[0]}\nPessoa: {valores[3]}\nRegistrado por: {valores[4]}\n\n"
            f"{self._descricoes.get(selecao[0], '')}",
        )
