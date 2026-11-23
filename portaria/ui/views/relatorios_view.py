"""Relatórios: movimentações por período, gráficos (Matplotlib) e exportação CSV."""

from datetime import date, timedelta
from pathlib import Path
from tkinter import filedialog, ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkcalendar import DateEntry

from portaria.config import Cores
from portaria.ui.views.base import BaseView
from portaria.ui.widgets import Coluna, criar_tabela

_DIAS_PADRAO = 7
_CORES_TIPO = (Cores.AZUL, Cores.VERDE, Cores.VERMELHO, Cores.AZUL_MARINHO)


def _data_hora_curta(valor: object) -> str:
    """``dd/mm/aa HH:MM`` para caber na tabela (aceita Timestamp/NaT do pandas)."""
    if valor is None or pd.isna(valor):
        return "-"
    return pd.Timestamp(valor).strftime("%d/%m/%y %H:%M")


class RelatoriosView(BaseView):
    titulo = "Relatórios"
    subtitulo = "Movimentações por período, com gráficos e exportação para CSV."

    def construir(self) -> None:
        self._df: pd.DataFrame | None = None

        barra = ttk.Frame(self.corpo, style="Card.TFrame")
        barra.pack(fill="x", pady=(0, 12))
        ttk.Label(barra, text="De", style="Rotulo.TLabel").pack(side="left")
        self.inicio = DateEntry(barra, date_pattern="dd/mm/yyyy", locale="pt_BR", width=12)
        self.inicio.pack(side="left", padx=(6, 14))
        ttk.Label(barra, text="Até", style="Rotulo.TLabel").pack(side="left")
        self.fim = DateEntry(barra, date_pattern="dd/mm/yyyy", locale="pt_BR", width=12)
        self.fim.pack(side="left", padx=(6, 14))
        ttk.Button(barra, text="Gerar", style="Azul.TButton", command=self.gerar).pack(side="left")
        ttk.Button(barra, text="Exportar CSV", style="Verde.TButton", command=self._exportar).pack(
            side="left", padx=10
        )
        self.resumo = ttk.Label(self.corpo, text="", style="Status.TLabel")
        self.resumo.pack(anchor="w", pady=(0, 8))

        conteudo = ttk.Frame(self.corpo, style="Card.TFrame")
        conteudo.pack(fill="both", expand=True)
        conteudo.columnconfigure(0, weight=3)
        conteudo.columnconfigure(1, weight=2)
        conteudo.rowconfigure(0, weight=1)

        moldura, self.tabela = criar_tabela(
            conteudo,
            (
                Coluna("codigo", "Código", 55, "center"),
                Coluna("nome", "Nome", 130, expandir=True),
                Coluna("tipo", "Tipo", 85, "center"),
                Coluna("entrada", "Entrada", 105, "center"),
                Coluna("saida", "Saída", 105, "center"),
                Coluna("perm", "Perm. (min)", 80, "center"),
            ),
        )
        moldura.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.figura = Figure(figsize=(3.9, 4.6), dpi=90, facecolor=Cores.BRANCO)
        self.grafico_dia = self.figura.add_subplot(211)
        self.grafico_tipo = self.figura.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(self.figura, master=conteudo)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")

        self._definir_periodo_padrao()

    def _definir_periodo_padrao(self) -> None:
        hoje = date.today()
        self.inicio.set_date(hoje - timedelta(days=_DIAS_PADRAO - 1))
        self.fim.set_date(hoje)

    def ao_exibir(self) -> None:
        self.gerar()

    def gerar(self) -> None:
        inicio: date = self.inicio.get_date()
        fim: date = self.fim.get_date()
        df = self.executar(lambda: self.ctx.servicos.relatorios.movimentacoes_periodo(inicio, fim))
        if df is None:
            return
        self._df = df
        self._preencher_tabela(df)
        self._desenhar_graficos(df, inicio, fim)

        media = self.ctx.servicos.relatorios.permanencia_media(df)
        texto_media = "-" if media is None else f"{media:.0f} min"
        self.resumo.configure(
            text=f"{len(df)} movimentação(ões) · {df['Nome'].nunique()} pessoa(s) · permanência média {texto_media}"
        )

    def _preencher_tabela(self, df: pd.DataFrame) -> None:
        self.tabela.delete(*self.tabela.get_children())
        for indice, linha in enumerate(df.itertuples(index=False)):
            codigo, nome, _cpf, tipo, entrada, saida, permanencia = linha
            self.tabela.insert(
                "",
                "end",
                values=(
                    codigo,
                    nome,
                    tipo,
                    _data_hora_curta(entrada),
                    _data_hora_curta(saida),
                    "-" if pd.isna(permanencia) else int(permanencia),
                ),
                tags=("par",) if indice % 2 else (),
            )

    def _desenhar_graficos(self, df: pd.DataFrame, inicio: date, fim: date) -> None:
        servico = self.ctx.servicos.relatorios
        por_dia = servico.entradas_por_dia(df, inicio, fim)
        por_tipo = servico.entradas_por_tipo(df)

        ax = self.grafico_dia
        ax.clear()
        rotulos = [dia.strftime("%d/%m") for dia in por_dia.index]
        ax.bar(range(len(por_dia)), por_dia.to_numpy(), color=Cores.AZUL, width=0.6)
        passo = max(1, len(rotulos) // 8)
        ax.set_xticks(range(0, len(rotulos), passo), rotulos[::passo], fontsize=8)
        ax.set_title("Entradas por dia", fontsize=10, color=Cores.AZUL_MARINHO, loc="left")
        ax.yaxis.get_major_locator().set_params(integer=True)

        ax = self.grafico_tipo
        ax.clear()
        if por_tipo.empty:
            ax.text(0.5, 0.5, "Sem movimentações no período", ha="center", va="center", color=Cores.TEXTO_SUAVE)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            cores = [_CORES_TIPO[i % len(_CORES_TIPO)] for i in range(len(por_tipo))]
            ax.barh(list(por_tipo.index), por_tipo.to_numpy(), color=cores, height=0.5)
            ax.xaxis.get_major_locator().set_params(integer=True)
            ax.tick_params(labelsize=8)
        ax.set_title("Entradas por tipo de acesso", fontsize=10, color=Cores.AZUL_MARINHO, loc="left")

        for eixo in (self.grafico_dia, self.grafico_tipo):
            eixo.spines[["top", "right"]].set_visible(False)
            eixo.set_facecolor(Cores.BRANCO)
        self.figura.tight_layout(pad=1.2)
        self.canvas.draw_idle()

    def _exportar(self) -> None:
        if self._df is None or self._df.empty:
            self.avisar("Relatório vazio", "Não há movimentações no período para exportar.")
            return
        inicio: date = self.inicio.get_date()
        fim: date = self.fim.get_date()
        destino = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar relatório",
            defaultextension=".csv",
            initialfile=f"relatorio_portaria_{inicio:%Y%m%d}_{fim:%Y%m%d}.csv",
            filetypes=[("Arquivo CSV", "*.csv")],
        )
        if not destino:
            return
        df = self._df
        if self.tentar(lambda: self.ctx.servicos.relatorios.exportar_csv(df, Path(destino))):
            self.informar("Exportação concluída", f"Relatório salvo em:\n{destino}")
