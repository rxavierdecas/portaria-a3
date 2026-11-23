"""Classe base das telas exibidas na área de conteúdo da janela principal."""

import sqlite3
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import TypeVar

from portaria.bootstrap import Servicos
from portaria.exceptions import PortariaError
from portaria.models.usuario import Usuario

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Contexto:
    """Dependências compartilhadas por todas as telas."""

    servicos: Servicos
    usuario: Usuario
    navegar: Callable[[str], None]


class BaseView(ttk.Frame):
    titulo: str = ""
    subtitulo: str = ""

    def __init__(self, master: tk.Misc, ctx: Contexto) -> None:
        super().__init__(master, style="Card.TFrame", padding=24)
        self.ctx = ctx
        cabecalho = ttk.Frame(self, style="Card.TFrame")
        cabecalho.pack(fill="x", pady=(0, 16))
        ttk.Label(cabecalho, text=self.titulo, style="Titulo.TLabel").pack(anchor="w")
        if self.subtitulo:
            ttk.Label(cabecalho, text=self.subtitulo, style="Subtitulo.TLabel").pack(anchor="w")
        self.corpo = ttk.Frame(self, style="Card.TFrame")
        self.corpo.pack(fill="both", expand=True)
        self.construir()

    def construir(self) -> None:
        """Cria os widgets da tela (implementado pelas subclasses)."""
        raise NotImplementedError

    def ao_exibir(self) -> None:
        """Chamado sempre que a tela fica visível; recarrega os dados."""

    # --- Mensagens ----------------------------------------------------------
    def informar(self, titulo: str, mensagem: str) -> None:
        messagebox.showinfo(titulo, mensagem, parent=self)

    def avisar(self, titulo: str, mensagem: str) -> None:
        messagebox.showwarning(titulo, mensagem, parent=self)

    def confirmar(self, titulo: str, mensagem: str) -> bool:
        return messagebox.askyesno(titulo, mensagem, parent=self)

    def executar(self, acao: Callable[[], T]) -> T | None:
        """Executa uma ação de negócio; em caso de erro, mostra a mensagem e retorna None."""
        _, resultado = self._rodar(acao)
        return resultado

    def tentar(self, acao: Callable[[], object]) -> bool:
        """Como :meth:`executar`, mas indica apenas se a ação foi concluída."""
        sucesso, _ = self._rodar(acao)
        return sucesso

    def _rodar(self, acao: Callable[[], T]) -> tuple[bool, T | None]:
        try:
            return True, acao()
        except PortariaError as erro:
            messagebox.showwarning("Atenção", str(erro), parent=self)
        except sqlite3.Error as erro:
            messagebox.showerror("Erro no banco de dados", f"Não foi possível concluir a operação.\n\n{erro}", parent=self)
        except Exception as erro:  # noqa: BLE001 - última barreira antes do usuário
            messagebox.showerror("Erro inesperado", f"{type(erro).__name__}: {erro}", parent=self)
        return False, None


def campo(master: tk.Misc, rotulo: str, linha: int, coluna: int, widget_factory: Callable[[tk.Misc], T]) -> T:
    """Cria um rótulo + widget empilhados numa célula da grade e devolve o widget."""
    celula = ttk.Frame(master, style="Card.TFrame")
    celula.grid(row=linha, column=coluna, sticky="new", padx=(0, 20), pady=(0, 12))
    ttk.Label(celula, text=rotulo, style="Rotulo.TLabel").pack(anchor="w", pady=(0, 4))
    widget = widget_factory(celula)
    widget.pack(fill="x")  # type: ignore[attr-defined]
    return widget
