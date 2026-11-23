"""Tela 1 — Login."""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from portaria import config
from portaria.config import FONTE, Cores
from portaria.exceptions import AutenticacaoError, ValidacaoError
from portaria.models.usuario import Usuario
from portaria.services.auth_service import AuthService
from portaria.ui.widgets import PlaceholderEntry, criar_logo

_LARGURA_PAINEL = 330
_OCULTAR = "•"


class LoginFrame(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        auth: AuthService,
        ao_autenticar: Callable[[Usuario], None],
    ) -> None:
        super().__init__(master, bg=Cores.BRANCO)
        self._auth = auth
        self._ao_autenticar = ao_autenticar
        self._mostrar_senha = tk.BooleanVar(value=False)
        self._construir_painel_marca()
        self._construir_formulario()

    # --- Painel esquerdo -----------------------------------------------------
    def _construir_painel_marca(self) -> None:
        painel = tk.Frame(self, bg=Cores.AZUL_MARINHO, width=_LARGURA_PAINEL)
        painel.pack(side="left", fill="y")
        painel.pack_propagate(False)

        criar_logo(painel, Cores.AZUL_MARINHO, tamanho=34).pack(pady=(36, 18))
        self._desenhar_cadeado(painel).pack()
        tk.Label(
            painel, text=config.NOME_SISTEMA, bg=Cores.AZUL_MARINHO, fg=Cores.BRANCO, font=(FONTE, 15, "bold")
        ).pack(pady=(14, 0))
        tk.Label(painel, text="Acesso restrito", bg=Cores.AZUL_MARINHO, fg=Cores.TEXTO_MENU_SUAVE, font=(FONTE, 10)).pack()

        if config.FACHADA_PATH.exists():
            imagem = tk.PhotoImage(file=str(config.FACHADA_PATH))
            rotulo = tk.Label(painel, image=imagem, bg=Cores.AZUL_MARINHO, bd=0)
            rotulo.image = imagem  # type: ignore[attr-defined]
            rotulo.pack(side="bottom", fill="x")
        else:
            self._desenhar_predio(painel).pack(side="bottom", fill="x")

    @staticmethod
    def _desenhar_cadeado(master: tk.Misc) -> tk.Canvas:
        tela = tk.Canvas(master, width=70, height=80, bg=Cores.AZUL_MARINHO, highlightthickness=0)
        tela.create_arc(18, 6, 52, 46, start=0, extent=180, style="arc", outline=Cores.BRANCO, width=6)
        tela.create_line(18, 26, 18, 38, fill=Cores.BRANCO, width=6)
        tela.create_line(52, 26, 52, 38, fill=Cores.BRANCO, width=6)
        tela.create_rectangle(8, 36, 62, 76, fill=Cores.BRANCO, outline=Cores.BRANCO)
        tela.create_oval(30, 47, 40, 57, fill=Cores.AZUL_MARINHO, outline="")
        tela.create_rectangle(33, 54, 37, 66, fill=Cores.AZUL_MARINHO, outline="")
        return tela

    @staticmethod
    def _desenhar_predio(master: tk.Misc) -> tk.Canvas:
        """Ilustração simples de fachada (substituível por assets/fachada.png)."""
        altura = 150
        tela = tk.Canvas(master, width=_LARGURA_PAINEL, height=altura, bg=Cores.FACHADA_CEU, highlightthickness=0)
        tela.create_rectangle(30, 30, _LARGURA_PAINEL - 30, altura, fill=Cores.FACHADA_PREDIO, outline="")
        tela.create_rectangle(30, 22, _LARGURA_PAINEL - 30, 32, fill=Cores.FACHADA_TELHADO, outline="")
        acesas = {(0, 2), (1, 5), (2, 1), (0, 6), (1, 3)}
        for linha in range(3):
            for coluna in range(8):
                x = 44 + coluna * 32
                y = 44 + linha * 28
                cor = Cores.FACHADA_JANELA_ACESA if (linha, coluna) in acesas else Cores.FACHADA_JANELA
                tela.create_rectangle(x, y, x + 20, y + 16, fill=cor, outline="")
        meio = _LARGURA_PAINEL // 2
        tela.create_rectangle(meio - 26, altura - 34, meio + 26, altura, fill=Cores.FACHADA_PORTA, outline="")
        tela.create_line(meio, altura - 34, meio, altura, fill=Cores.FACHADA_JANELA, width=2)
        return tela

    # --- Formulário -------------------------------------------------------------
    def _construir_formulario(self) -> None:
        area = tk.Frame(self, bg=Cores.BRANCO)
        area.pack(side="left", fill="both", expand=True)
        form = tk.Frame(area, bg=Cores.BRANCO)
        form.place(relx=0.5, rely=0.5, anchor="center", width=380)

        tk.Label(form, text="Bem-vindo(a)", bg=Cores.BRANCO, fg=Cores.AZUL_MARINHO, font=(FONTE, 20, "bold")).pack(
            anchor="w"
        )
        tk.Label(
            form, text="Informe seu usuário e senha para continuar.", bg=Cores.BRANCO, fg=Cores.TEXTO_SUAVE
        ).pack(anchor="w", pady=(0, 22))

        self.usuario = self._campo_com_icone(form, "👤", "Usuário")
        self.senha = self._campo_com_icone(form, "🔒", "Senha", show=_OCULTAR, olho=True)

        ttk.Checkbutton(
            form,
            text="Mostrar senha",
            variable=self._mostrar_senha,
            command=self._atualizar_visibilidade_senha,
            style="Card.TCheckbutton",
        ).pack(anchor="w", pady=(4, 20))

        botoes = tk.Frame(form, bg=Cores.BRANCO)
        botoes.pack(fill="x")
        botoes.columnconfigure((0, 1), weight=1, uniform="b")
        ttk.Button(botoes, text="➜  Entrar", style="Azul.TButton", command=self._entrar).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(botoes, text="Limpar", style="Cinza.TButton", command=self._limpar).grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )

        for entrada in (self.usuario, self.senha):
            entrada.bind("<Return>", lambda _e: self._entrar())
        self.after(100, self.usuario.focus_set)

    def _campo_com_icone(
        self, master: tk.Misc, icone: str, dica: str, show: str = "", olho: bool = False
    ) -> PlaceholderEntry:
        caixa = tk.Frame(master, bg=Cores.BRANCO, highlightthickness=1, highlightbackground=Cores.BORDA)
        caixa.pack(fill="x", pady=(0, 12))
        tk.Label(caixa, text=icone, bg=Cores.BRANCO, fg=Cores.AZUL_MARINHO, font=("Segoe UI Emoji", 12)).pack(
            side="left", padx=(10, 4)
        )
        entrada = PlaceholderEntry(caixa, placeholder=dica, show=show, font=(FONTE, 11))
        entrada.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 6), pady=4)
        entrada.bind("<FocusIn>", lambda _e: caixa.configure(highlightbackground=Cores.AZUL), add="+")
        entrada.bind("<FocusOut>", lambda _e: caixa.configure(highlightbackground=Cores.BORDA), add="+")
        if olho:
            botao = tk.Label(
                caixa, text="👁", bg=Cores.BRANCO, fg=Cores.AZUL_MARINHO, cursor="hand2", font=("Segoe UI Emoji", 12)
            )
            botao.pack(side="right", padx=(0, 10))
            botao.bind("<Button-1>", lambda _e: self._alternar_senha())
        return entrada

    # --- Ações ----------------------------------------------------------------
    def _alternar_senha(self) -> None:
        self._mostrar_senha.set(not self._mostrar_senha.get())
        self._atualizar_visibilidade_senha()

    def _atualizar_visibilidade_senha(self) -> None:
        self.senha.definir_show("" if self._mostrar_senha.get() else _OCULTAR)

    def _limpar(self) -> None:
        self.usuario.limpar()
        self.senha.limpar()
        self._mostrar_senha.set(False)
        self._atualizar_visibilidade_senha()
        self.usuario.focus_set()

    def _entrar(self) -> None:
        try:
            usuario = self._auth.autenticar(self.usuario.valor(), self.senha.valor())
        except ValidacaoError as erro:
            messagebox.showwarning("Campos obrigatórios", str(erro), parent=self)
            (self.usuario if not self.usuario.valor().strip() else self.senha).focus_set()
        except AutenticacaoError as erro:
            messagebox.showerror("Acesso negado", str(erro), parent=self)
            self.senha.limpar()
            self.senha.focus_set()
        except Exception as erro:  # noqa: BLE001
            messagebox.showerror("Erro inesperado", f"{type(erro).__name__}: {erro}", parent=self)
        else:
            self._ao_autenticar(usuario)
