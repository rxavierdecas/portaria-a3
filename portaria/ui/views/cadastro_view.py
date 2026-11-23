"""Tela 2 — Cadastro de Pessoas."""

from datetime import date, datetime
from tkinter import ttk

from tkcalendar import DateEntry

from portaria import config
from portaria.services.pessoa_service import DadosCadastro
from portaria.ui.views.base import BaseView, campo
from portaria.ui.widgets import MaskedEntry, PlaceholderEntry, TextoMultilinha
from portaria.utils.formatters import formatar_cpf, formatar_horario, formatar_telefone

_SELECIONE = "Selecione..."


class CadastroView(BaseView):
    titulo = "Cadastro de Pessoas"
    subtitulo = "Cadastro de pessoas que terão acesso à portaria. Campos com * são obrigatórios."

    def construir(self) -> None:
        grade = ttk.Frame(self.corpo, style="Card.TFrame")
        grade.pack(fill="x")
        grade.columnconfigure(0, weight=3, uniform="col")
        grade.columnconfigure(1, weight=2, uniform="col")

        self.nome = campo(grade, "Nome completo *", 0, 0, lambda m: PlaceholderEntry(m, "Digite o nome completo"))
        self.cpf = campo(grade, "CPF *", 0, 1, lambda m: MaskedEntry(m, formatar_cpf, "000.000.000-00"))
        self.telefone = campo(
            grade, "Telefone *", 1, 0, lambda m: MaskedEntry(m, formatar_telefone, "(00) 00000-0000")
        )
        self.empresa = campo(grade, "Empresa *", 1, 1, lambda m: PlaceholderEntry(m, "Digite a empresa"))
        self.tipo = campo(
            grade,
            "Tipo de acesso *",
            2,
            0,
            lambda m: ttk.Combobox(m, values=config.TIPOS_ACESSO, state="readonly"),
        )
        self.data = campo(
            grade,
            "Data de entrada *",
            2,
            1,
            lambda m: DateEntry(
                m,
                date_pattern="dd/mm/yyyy",
                locale="pt_BR",
                maxdate=date.today(),
                background=config.Cores.AZUL_MARINHO,
                selectbackground=config.Cores.AZUL,
            ),
        )
        self.horario = campo(grade, "Horário de entrada *", 3, 0, lambda m: MaskedEntry(m, formatar_horario, "__:__"))
        self.motivo = campo(grade, "Motivo da visita *", 3, 1, lambda m: TextoMultilinha(m, altura=3))

        botoes = ttk.Frame(self.corpo, style="Card.TFrame")
        botoes.pack(fill="x", pady=(12, 0))
        ttk.Button(botoes, text="✚  Cadastrar", style="Verde.TButton", command=self._cadastrar).pack(side="left")
        ttk.Button(botoes, text="Limpar", style="Cinza.TButton", command=self.limpar).pack(side="left", padx=10)
        ttk.Button(botoes, text="✕  Cancelar", style="Vermelho.TButton", command=self._cancelar).pack(side="left")

        self.limpar()

    def ao_exibir(self) -> None:
        self.data.configure(maxdate=date.today())
        if not self.horario.valor():
            self.horario.definir(datetime.now().strftime(config.FORMATO_HORA))
        self.nome.focus_set()

    def limpar(self) -> None:
        for entrada in (self.nome, self.cpf, self.telefone, self.empresa):
            entrada.limpar()
        self.tipo.set(_SELECIONE)
        self.data.set_date(date.today())
        self.horario.definir(datetime.now().strftime(config.FORMATO_HORA))
        self.motivo.limpar()

    def _dados(self) -> DadosCadastro:
        tipo = self.tipo.get()
        return DadosCadastro(
            nome=self.nome.valor(),
            cpf=self.cpf.valor(),
            telefone=self.telefone.valor(),
            empresa=self.empresa.valor(),
            tipo_acesso="" if tipo == _SELECIONE else tipo,
            data_entrada=self.data.get(),
            horario_entrada=self.horario.valor(),
            motivo=self.motivo.valor(),
        )

    def _cadastrar(self) -> None:
        pessoa = self.executar(lambda: self.ctx.servicos.pessoas.cadastrar(self._dados()))
        if pessoa is None:
            return
        self.informar(
            "Cadastro realizado",
            f"{pessoa.nome} cadastrado(a) com sucesso!\n\n"
            f"Código de identificação: {pessoa.codigo}\n"
            "Entrada registrada — situação: Dentro.",
        )
        self.limpar()
        self.nome.focus_set()

    def _cancelar(self) -> None:
        self.limpar()
        self.ctx.navegar("inicio")
