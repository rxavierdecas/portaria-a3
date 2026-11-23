"""Ponto de entrada do Sistema de Portaria.

Uso:
    python main.py            # inicia o sistema
    python main.py --demo     # inicia com dados de exemplo (se o banco estiver vazio)
"""

import argparse
from pathlib import Path

from portaria import config
from portaria.bootstrap import criar_servicos
from portaria.database import Database
from portaria.database.demo import popular_dados_demo
from portaria.ui.app import App


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=config.NOME_SISTEMA)
    parser.add_argument("--demo", action="store_true", help="popula o banco com dados de exemplo")
    parser.add_argument("--db", type=Path, default=config.DB_PATH, help="caminho do arquivo SQLite")
    args = parser.parse_args(argv)

    servicos = criar_servicos(args.db)
    if args.demo and popular_dados_demo(Database(args.db)):
        print("Dados de demonstração inseridos.")

    App(servicos).mainloop()


if __name__ == "__main__":
    main()
