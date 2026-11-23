"""Janela raiz da aplicação: alterna entre a tela de login e a principal."""

import tkinter as tk

from portaria import config
from portaria.bootstrap import Servicos
from portaria.config import Cores
from portaria.models.usuario import Usuario
from portaria.ui.login_window import LoginFrame
from portaria.ui.main_window import MainFrame
from portaria.ui.styles import configurar_estilos


class App(tk.Tk):
    def __init__(self, servicos: Servicos) -> None:
        super().__init__()
        self._servicos = servicos
        self._tela: tk.Widget | None = None
        self.configure(bg=Cores.FUNDO)
        configurar_estilos(self)
        self.mostrar_login()

    def _trocar_tela(self, tela: tk.Widget) -> None:
        if self._tela is not None:
            self._tela.destroy()
        self._tela = tela
        tela.pack(fill="both", expand=True)

    def _centralizar(self, largura: int, altura: int) -> None:
        x = max(0, (self.winfo_screenwidth() - largura) // 2)
        y = max(0, (self.winfo_screenheight() - altura) // 3)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def mostrar_login(self) -> None:
        self.title(f"{config.NOME_SISTEMA} - Login")
        self.minsize(1, 1)
        self.resizable(False, False)
        self._centralizar(880, 520)
        self._trocar_tela(LoginFrame(self, self._servicos.auth, self.mostrar_principal))

    def mostrar_principal(self, usuario: Usuario) -> None:
        self.resizable(True, True)
        self.minsize(1080, 640)
        self._centralizar(1240, 740)
        self._trocar_tela(MainFrame(self, self._servicos, usuario, ao_sair=self.mostrar_login))
