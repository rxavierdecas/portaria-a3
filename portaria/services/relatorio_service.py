"""Relatórios de movimentação: agregações com pandas e exportação CSV."""

import csv
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from portaria.exceptions import ValidacaoError
from portaria.repositories.movimentacao_repository import MovimentacaoRepository
from portaria.utils.formatters import formatar_data_hora

COLUNAS = ["Código", "Nome", "CPF", "Tipo de acesso", "Entrada", "Saída", "Permanência (min)"]


class RelatorioService:
    def __init__(self, movimentacoes: MovimentacaoRepository) -> None:
        self._movimentacoes = movimentacoes

    def movimentacoes_periodo(self, inicio: date, fim: date) -> pd.DataFrame:
        """DataFrame com uma linha por movimentação no período."""
        if inicio > fim:
            raise ValidacaoError("A data inicial deve ser anterior ou igual à data final.")

        linhas: list[dict[str, object]] = []
        for item in self._movimentacoes.listar_periodo(inicio, fim):
            mov = item.movimentacao
            permanencia: float | None = None
            if mov.saida is not None:
                permanencia = round((mov.saida - mov.entrada).total_seconds() / 60)
            linhas.append(
                {
                    "Código": item.pessoa.codigo,
                    "Nome": item.pessoa.nome,
                    "CPF": item.pessoa.cpf_formatado,
                    "Tipo de acesso": item.pessoa.tipo_acesso,
                    "Entrada": mov.entrada,
                    "Saída": mov.saida,
                    "Permanência (min)": permanencia,
                }
            )
        return pd.DataFrame(linhas, columns=COLUNAS)

    @staticmethod
    def entradas_por_dia(df: pd.DataFrame, inicio: date, fim: date) -> pd.Series:
        """Quantidade de entradas por dia, incluindo dias sem movimento (zero)."""
        dias = [inicio + timedelta(days=n) for n in range((fim - inicio).days + 1)]
        if df.empty:
            contagem = pd.Series(dtype="int64")
        else:
            contagem = pd.to_datetime(df["Entrada"]).dt.date.value_counts()
        return contagem.reindex(dias, fill_value=0).astype("int64")

    @staticmethod
    def entradas_por_tipo(df: pd.DataFrame) -> pd.Series:
        if df.empty:
            return pd.Series(dtype="int64")
        return df["Tipo de acesso"].value_counts().sort_index()

    @staticmethod
    def permanencia_media(df: pd.DataFrame) -> float | None:
        if df.empty or df["Permanência (min)"].isna().all():
            return None
        return float(df["Permanência (min)"].mean())

    @staticmethod
    def exportar_csv(df: pd.DataFrame, caminho: Path) -> None:
        """Grava o relatório em CSV (separador ';' e BOM, para abrir no Excel pt-BR)."""
        with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(COLUNAS)
            for registro in df.itertuples(index=False):
                codigo, nome, cpf, tipo, entrada, saida, permanencia = registro
                escritor.writerow(
                    [
                        codigo,
                        nome,
                        cpf,
                        tipo,
                        formatar_data_hora(_como_datetime(entrada)),
                        formatar_data_hora(_como_datetime(saida)),
                        "" if pd.isna(permanencia) else int(permanencia),
                    ]
                )


def _como_datetime(valor: object) -> datetime | None:
    """Converte Timestamp/NaT do pandas em ``datetime | None``."""
    if valor is None or pd.isna(valor):
        return None
    return pd.Timestamp(valor).to_pydatetime()
