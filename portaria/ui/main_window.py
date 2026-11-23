"""Janela principal: menu lateral + área de conteúdo com as telas."""

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from tkinter import messagebox, ttk

from portaria import config
from portaria.bootstrap import Servicos
from portaria.config import FONTE, Cores
from portaria.models.usuario import Usuario
from portaria.ui.views.base import BaseView, Contexto
from portaria.ui.views.cadastro_view import CadastroView
from portaria.ui.views.controle_view import ControleView
from portaria.ui.views.inicio_view import InicioView
from portaria.ui.views.ocorrencias_view import OcorrenciasView
from portaria.ui.views.relatorios_view import RelatoriosView
from portaria.ui.views.veiculos_view import VeiculosView
from portaria.ui.widgets import BotaoMenu, criar_logo


@dataclass(frozen=True, slots=True)
class ItemMenu:
    chave: str
    texto: str
    icone: str
    tela: type[BaseView]


ITENS_MENU: tuple[ItemMenu, ...] = (
    ItemMenu("inicio", "Início", "⌂", InicioView),
    ItemMenu("cadastro", "Cadastro", "✚", CadastroView),
    ItemMenu("controle", "Controle de Acesso", "⇄", ControleView),
    ItemMenu("relatorios", "Relatórios", "▤", RelatoriosView),
    ItemMenu("veiculos", "Veículos", "◈", VeiculosView),
    ItemMenu("ocorrencias", "Ocorrências", "⚠", OcorrenciasView),
)


class MainFrame(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        servicos: Servicos,
        usuario: Usuario,
        ao_sair: Callable[[], None],
    ) -> None:
        super().__init__(master, bg=Cores.FUNDO)
        self._ao_sair = ao_sair
        self._ctx = Contexto(servicos=servicos, usuario=usuario, navegar=self.navegar)
        self._telas: dict[str, BaseView] = {}
        self._botoes: dict[str, BotaoMenu] = {}

        self._construir_menu(usuario)
        self._conteudo = ttk.Frame(self, padding=20)
        self._conteudo.pack(side="left", fill="both", expand=True)
        self._conteudo.rowconfigure(0, weight=1)
        self._conteudo.columnconfigure(0, weight=1)
        self.navegar("inicio")

    def _construir_menu(self, usuario: Usuario) -> None:
        menu = tk.Frame(self, bg=Cores.AZUL_MARINHO, width=220)
        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)

        criar_logo(menu, Cores.AZUL_MARINHO, tamanho=26).pack(anchor="w", padx=20, pady=(22, 26))
        for item in ITENS_MENU:
            botao = BotaoMenu(menu, item.texto, item.icone, lambda chave=item.chave: self.navegar(chave))
            botao.pack(fill="x")
            self._botoes[item.chave] = botao

        BotaoMenu(menu, "Sair", "⏻", self._sair).pack(side="bottom", fill="x", pady=(0, 16))
        tk.Label(
            menu,
            text=f"Conectado como\n{usuario.nome}",
            justify="left",
            bg=Cores.AZUL_MARINHO,
            fg=Cores.TEXTO_MENU_SUAVE,
            font=(FONTE, 9),
        ).pack(side="bottom", anchor="w", padx=20, pady=(0, 10))

    def navegar(self, chave: str) -> None:
        item = next(i for i in ITENS_MENU if i.chave == chave)
        tela = self._telas.get(chave)
        if tela is None:
            tela = item.tela(self._conteudo, self._ctx)
            tela.grid(row=0, column=0, sticky="nsew")
            self._telas[chave] = tela
        tela.tkraise()
        tela.ao_exibir()

        for outra_chave, botao in self._botoes.items():
            botao.definir_ativo(outra_chave == chave)
        self.winfo_toplevel().title(f"{config.NOME_SISTEMA} - {item.texto}")

    def _sair(self) -> None:
        if messagebox.askyesno("Sair", "Deseja encerrar a sessão?", parent=self):
            self._ao_sair()
