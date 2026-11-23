"""Tela inicial: resumo da portaria e atalhos."""

import tkinter as tk
from tkinter import ttk

from portaria.config import FONTE, Cores
from portaria.models.movimentacao import Situacao
from portaria.ui.views.base import BaseView
from portaria.ui.widgets import Coluna, criar_tabela
from portaria.utils.formatters import formatar_hora_movimento


class InicioView(BaseView):
    titulo = "Início"
    subtitulo = "Resumo da movimentação da portaria."

    def construir(self) -> None:
        ttk.Label(
            self.corpo,
            text=f"Olá, {self.ctx.usuario.nome}!",
            style="Card.TLabel",
            font=(FONTE, 12, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        cartoes = ttk.Frame(self.corpo, style="Card.TFrame")
        cartoes.pack(fill="x")
        self._numeros: dict[str, ttk.Label] = {}
        definicoes = (
            ("dentro", "Pessoas dentro agora", Cores.VERDE),
            ("hoje", "Entradas hoje", Cores.AZUL),
            ("total", "Pessoas cadastradas", Cores.TEXTO_MENU_SUAVE),
        )
        for indice, (chave, rotulo, cor) in enumerate(definicoes):
            cartoes.columnconfigure(indice, weight=1, uniform="cartao")
            cartao = tk.Frame(cartoes, bg=Cores.BRANCO, highlightthickness=1, highlightbackground=Cores.BORDA)
            cartao.grid(row=0, column=indice, sticky="ew", padx=(0 if indice == 0 else 12, 0))
            tk.Frame(cartao, bg=cor, height=4).pack(fill="x")
            numero = ttk.Label(cartao, text="0", style="Numero.TLabel")
            numero.pack(anchor="w", padx=16, pady=(10, 0))
            ttk.Label(cartao, text=rotulo, style="Subtitulo.TLabel").pack(anchor="w", padx=16, pady=(0, 12))
            self._numeros[chave] = numero

        atalhos = ttk.Frame(self.corpo, style="Card.TFrame")
        atalhos.pack(fill="x", pady=16)
        ttk.Button(
            atalhos, text="✚  Novo cadastro", style="Verde.TButton", command=lambda: self.ctx.navegar("cadastro")
        ).pack(side="left")
        ttk.Button(
            atalhos, text="Controle de acesso", style="Azul.TButton", command=lambda: self.ctx.navegar("controle")
        ).pack(side="left", padx=10)
        ttk.Button(
            atalhos, text="Relatórios", style="Cinza.TButton", command=lambda: self.ctx.navegar("relatorios")
        ).pack(side="left")

        ttk.Label(self.corpo, text="Pessoas dentro agora", style="Rotulo.TLabel").pack(anchor="w", pady=(4, 6))
        moldura, self.tabela = criar_tabela(
            self.corpo,
            (
                Coluna("codigo", "Código", 70, "center"),
                Coluna("nome", "Nome", 260, expandir=True),
                Coluna("tipo", "Tipo de acesso", 140, "center"),
                Coluna("entrada", "Entrada", 120, "center"),
            ),
            altura=8,
        )
        moldura.pack(fill="both", expand=True)

    def ao_exibir(self) -> None:
        resumo = self.executar(self.ctx.servicos.acesso.resumo)
        if resumo is not None:
            self._numeros["dentro"].configure(text=str(resumo.pessoas_dentro))
            self._numeros["hoje"].configure(text=str(resumo.entradas_hoje))
            self._numeros["total"].configure(text=str(resumo.total_cadastrado))

        registros = self.executar(
            lambda: self.ctx.servicos.acesso.listar_controle(filtro=Situacao.DENTRO.value)
        )
        self.tabela.delete(*self.tabela.get_children())
        for indice, registro in enumerate(registros or []):
            mov = registro.movimentacao
            self.tabela.insert(
                "",
                "end",
                values=(
                    registro.pessoa.codigo,
                    registro.pessoa.nome,
                    registro.pessoa.tipo_acesso,
                    formatar_hora_movimento(mov.entrada if mov else None),
                ),
                tags=("par",) if indice % 2 else (),
            )
