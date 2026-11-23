"""Componentes visuais reutilizáveis."""

import tkinter as tk
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from tkinter import ttk

from portaria import config
from portaria.config import FONTE, Cores


class PlaceholderEntry(ttk.Entry):
    """Entry que exibe um texto de dica enquanto está vazio e sem foco.

    Use :meth:`valor` (e não ``get``) para ler o conteúdo digitado.
    """

    def __init__(self, master: tk.Misc, placeholder: str = "", show: str = "", **kwargs: object) -> None:
        super().__init__(master, **kwargs)  # type: ignore[arg-type]
        self._placeholder = placeholder
        self._show = show
        self._exibindo_dica = False
        self.bind("<FocusIn>", lambda _e: self._esconder_dica(), add="+")
        self.bind("<FocusOut>", lambda _e: self._mostrar_dica(), add="+")
        self._mostrar_dica()

    def _mostrar_dica(self) -> None:
        if not self._placeholder or self.get():
            return
        self._exibindo_dica = True
        self.configure(style="Placeholder.TEntry", show="")
        self.insert(0, self._placeholder)

    def _esconder_dica(self) -> None:
        if self._exibindo_dica:
            self.delete(0, "end")
            self.configure(style="TEntry", show=self._show)
            self._exibindo_dica = False

    def _tem_foco(self) -> bool:
        try:
            return self.focus_get() is self
        except (KeyError, tk.TclError):  # foco em janela popup (ex.: calendário)
            return False

    def valor(self) -> str:
        return "" if self._exibindo_dica else self.get()

    def definir(self, texto: str) -> None:
        self._esconder_dica()
        self.delete(0, "end")
        if texto:
            self.insert(0, texto)
        elif not self._tem_foco():
            self._mostrar_dica()

    def limpar(self) -> None:
        self.definir("")

    def definir_show(self, show: str) -> None:
        """Altera o caractere de ocultação (ex.: ``"•"`` para senhas)."""
        self._show = show
        if not self._exibindo_dica:
            self.configure(show=show)


class MaskedEntry(PlaceholderEntry):
    """Entry que reformata o texto a cada tecla (CPF, telefone, horário...)."""

    def __init__(
        self,
        master: tk.Misc,
        formatador: Callable[[str], str],
        placeholder: str = "",
        **kwargs: object,
    ) -> None:
        super().__init__(master, placeholder=placeholder, **kwargs)
        self._formatador = formatador
        self.bind("<KeyRelease>", self._reformatar, add="+")

    def _reformatar(self, _evento: tk.Event | None = None) -> None:
        if self._exibindo_dica:
            return
        atual = self.get()
        novo = self._formatador(atual)
        if novo != atual:
            self.delete(0, "end")
            self.insert(0, novo)
            self.icursor("end")


class TextoMultilinha(tk.Text):
    """``tk.Text`` com borda no padrão visual dos demais campos."""

    def __init__(self, master: tk.Misc, altura: int = 4, **kwargs: object) -> None:
        super().__init__(
            master,
            height=altura,
            wrap="word",
            relief="flat",
            padx=8,
            pady=6,
            font=(FONTE, 10),
            highlightthickness=1,
            highlightbackground=Cores.BORDA,
            highlightcolor=Cores.AZUL,
            **kwargs,  # type: ignore[arg-type]
        )

    def valor(self) -> str:
        return self.get("1.0", "end-1c")

    def limpar(self) -> None:
        self.delete("1.0", "end")


@dataclass(frozen=True, slots=True)
class Coluna:
    id: str
    titulo: str
    largura: int
    alinhamento: str = "w"
    expandir: bool = False


def criar_tabela(master: tk.Misc, colunas: Sequence[Coluna], altura: int = 10) -> tuple[ttk.Frame, ttk.Treeview]:
    """Treeview com barra de rolagem vertical. Retorna ``(moldura, tabela)``."""
    moldura = ttk.Frame(master, style="Card.TFrame")
    tabela = ttk.Treeview(
        moldura,
        columns=[c.id for c in colunas],
        show="headings",
        height=altura,
        selectmode="browse",
    )
    for coluna in colunas:
        tabela.heading(coluna.id, text=coluna.titulo, anchor=coluna.alinhamento)  # type: ignore[arg-type]
        tabela.column(
            coluna.id,
            width=coluna.largura,
            minwidth=40,
            anchor=coluna.alinhamento,  # type: ignore[arg-type]
            stretch=coluna.expandir,
        )
    rolagem = ttk.Scrollbar(moldura, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=rolagem.set)
    tabela.pack(side="left", fill="both", expand=True)
    rolagem.pack(side="right", fill="y")
    tabela.tag_configure("par", background=Cores.LINHA_PAR)
    return moldura, tabela


class BotaoMenu(tk.Label):
    """Item clicável do menu lateral."""

    def __init__(self, master: tk.Misc, texto: str, icone: str, comando: Callable[[], None]) -> None:
        super().__init__(
            master,
            text=f"{icone}   {texto}",
            anchor="w",
            bg=Cores.AZUL_MARINHO,
            fg=Cores.BRANCO,
            font=(FONTE, 10),
            padx=20,
            pady=11,
            cursor="hand2",
        )
        self._comando = comando
        self._ativo = False
        self.bind("<Button-1>", lambda _e: self._comando())
        self.bind("<Enter>", lambda _e: self._pintar(hover=True))
        self.bind("<Leave>", lambda _e: self._pintar(hover=False))

    def _pintar(self, hover: bool = False) -> None:
        if self._ativo:
            cor = Cores.AZUL
        elif hover:
            cor = Cores.AZUL_MARINHO_HOVER
        else:
            cor = Cores.AZUL_MARINHO
        self.configure(bg=cor)

    def definir_ativo(self, ativo: bool) -> None:
        self._ativo = ativo
        self._pintar()


def criar_logo(master: tk.Misc, fundo: str, tamanho: int = 26) -> tk.Frame:
    """Logotipo: imagem em ``assets/logo.png`` ou, na falta dela, a marca em texto."""
    moldura = tk.Frame(master, bg=fundo)
    if config.LOGO_PATH.exists():
        imagem = tk.PhotoImage(file=str(config.LOGO_PATH))
        rotulo = tk.Label(moldura, image=imagem, bg=fundo)
        rotulo.image = imagem  # type: ignore[attr-defined]  # evita coleta pelo GC
        rotulo.pack()
        return moldura
    tk.Label(moldura, text="❯", bg=fundo, fg=Cores.VERMELHO, font=(FONTE, tamanho, "bold")).pack(side="left")
    tk.Label(moldura, text=config.MARCA, bg=fundo, fg=Cores.BRANCO, font=(FONTE, tamanho, "bold")).pack(side="left")
    return moldura
