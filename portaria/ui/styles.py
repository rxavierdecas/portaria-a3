"""Tema visual (ttk) baseado na paleta do mockup."""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from portaria.config import FONTE, Cores

# (nome do estilo, cor, cor ao passar o mouse, cor do texto)
_BOTOES: tuple[tuple[str, str, str, str], ...] = (
    ("Verde", Cores.VERDE, Cores.VERDE_HOVER, Cores.BRANCO),
    ("Vermelho", Cores.VERMELHO, Cores.VERMELHO_HOVER, Cores.BRANCO),
    ("Azul", Cores.AZUL, Cores.AZUL_HOVER, Cores.BRANCO),
    ("Cinza", Cores.CINZA, Cores.CINZA_HOVER, Cores.TEXTO),
)


def configurar_estilos(root: tk.Misc) -> ttk.Style:
    # Ajusta as fontes padrão nomeadas (não use option_add("*Font"): ele
    # sobrescreve a opção -font dos widgets ttk e anula as fontes dos estilos).
    for nome in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
        tkfont.nametofont(nome, root).configure(family=FONTE, size=10)
    root.option_add("*TCombobox*Listbox.font", (FONTE, 10))

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", font=(FONTE, 10), background=Cores.FUNDO, foreground=Cores.TEXTO)
    style.configure("TFrame", background=Cores.FUNDO)
    style.configure("Card.TFrame", background=Cores.BRANCO)
    style.configure("TLabel", background=Cores.FUNDO)
    style.configure("Card.TLabel", background=Cores.BRANCO)
    style.configure("Titulo.TLabel", background=Cores.BRANCO, foreground=Cores.AZUL_MARINHO, font=(FONTE, 16, "bold"))
    style.configure("Subtitulo.TLabel", background=Cores.BRANCO, foreground=Cores.TEXTO_SUAVE, font=(FONTE, 10))
    style.configure("Rotulo.TLabel", background=Cores.BRANCO, font=(FONTE, 9, "bold"))
    style.configure("Status.TLabel", background=Cores.BRANCO, foreground=Cores.TEXTO_SUAVE, font=(FONTE, 9))
    style.configure("StatusOk.TLabel", background=Cores.BRANCO, foreground=Cores.VERDE, font=(FONTE, 9, "bold"))
    style.configure("Numero.TLabel", background=Cores.BRANCO, foreground=Cores.AZUL_MARINHO, font=(FONTE, 26, "bold"))

    # Campos de texto
    style.configure(
        "TEntry",
        padding=6,
        fieldbackground=Cores.BRANCO,
        bordercolor=Cores.BORDA,
        lightcolor=Cores.BORDA,
        darkcolor=Cores.BORDA,
    )
    style.map("TEntry", bordercolor=[("focus", Cores.AZUL)], lightcolor=[("focus", Cores.AZUL)])
    style.configure("Placeholder.TEntry", foreground=Cores.PLACEHOLDER)
    style.configure(
        "TCombobox",
        padding=5,
        bordercolor=Cores.BORDA,
        lightcolor=Cores.BORDA,
        darkcolor=Cores.BORDA,
        arrowcolor=Cores.AZUL_MARINHO,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", Cores.BRANCO)],
        selectbackground=[("readonly", Cores.BRANCO)],
        selectforeground=[("readonly", Cores.TEXTO)],
        bordercolor=[("focus", Cores.AZUL)],
    )
    style.configure("Card.TCheckbutton", background=Cores.BRANCO)
    style.map("Card.TCheckbutton", background=[("active", Cores.BRANCO)])

    # Botões coloridos
    for nome, cor, hover, texto in _BOTOES:
        estilo = f"{nome}.TButton"
        style.configure(
            estilo,
            background=cor,
            foreground=texto,
            bordercolor=cor,
            lightcolor=cor,
            darkcolor=cor,
            focuscolor=cor,
            padding=(16, 8),
            font=(FONTE, 10, "bold"),
        )
        style.map(
            estilo,
            background=[("pressed", hover), ("active", hover)],
            bordercolor=[("pressed", hover), ("active", hover)],
            lightcolor=[("pressed", hover), ("active", hover)],
            darkcolor=[("pressed", hover), ("active", hover)],
        )

    # Tabelas
    style.configure(
        "Treeview",
        rowheight=30,
        background=Cores.BRANCO,
        fieldbackground=Cores.BRANCO,
        bordercolor=Cores.BORDA,
        font=(FONTE, 9),
    )
    style.configure(
        "Treeview.Heading",
        background=Cores.CABECALHO_TABELA,
        foreground=Cores.AZUL_MARINHO,
        font=(FONTE, 9, "bold"),
        relief="flat",
        padding=(6, 6),
    )
    style.map("Treeview.Heading", background=[("active", Cores.CABECALHO_TABELA_HOVER)])
    style.map("Treeview", background=[("selected", Cores.SELECAO)], foreground=[("selected", Cores.TEXTO)])
    return style
