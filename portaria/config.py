"""Configurações globais: caminhos, constantes de negócio e identidade visual."""

from pathlib import Path
from typing import Final

# --- Caminhos ---------------------------------------------------------------
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
DATA_DIR: Final[Path] = BASE_DIR / "data"
DB_PATH: Final[Path] = DATA_DIR / "portaria.db"
ASSETS_DIR: Final[Path] = BASE_DIR / "assets"
LOGO_PATH: Final[Path] = ASSETS_DIR / "logo.png"
FACHADA_PATH: Final[Path] = ASSETS_DIR / "fachada.png"

# --- Identidade -------------------------------------------------------------
NOME_SISTEMA: Final[str] = "Sistema de Portaria"
MARCA: Final[str] = "una"

# --- Regras de negócio ------------------------------------------------------
TIPOS_ACESSO: Final[tuple[str, ...]] = ("Visitante", "Funcionário", "Prestador")
FILTRO_TODOS: Final[str] = "Todos"
FILTROS_SITUACAO: Final[tuple[str, ...]] = (FILTRO_TODOS, "Dentro", "Saiu")
TIPOS_OCORRENCIA: Final[tuple[str, ...]] = (
    "Acesso negado",
    "Comportamento suspeito",
    "Dano ao patrimônio",
    "Objeto esquecido",
    "Falha de equipamento",
    "Outros",
)

# Usuário criado automaticamente na primeira execução.
ADMIN_USERNAME: Final[str] = "admin"
ADMIN_SENHA: Final[str] = "admin123"
ADMIN_NOME: Final[str] = "Administrador"

# --- Formatos de data/hora --------------------------------------------------
FORMATO_DATA: Final[str] = "%d/%m/%Y"
FORMATO_HORA: Final[str] = "%H:%M"
FORMATO_DATA_HORA: Final[str] = "%d/%m/%Y %H:%M"
FORMATO_ISO: Final[str] = "%Y-%m-%d %H:%M:%S"


# --- Paleta (Slate + Indigo) -------------------------------------------------
class Cores:
    # Menu lateral / painel do login (grafite)
    AZUL_MARINHO: Final[str] = "#0f172a"
    AZUL_MARINHO_HOVER: Final[str] = "#1e293b"
    TEXTO_MENU_SUAVE: Final[str] = "#94a3b8"
    # Ações
    AZUL: Final[str] = "#4f46e5"  # índigo — cor de destaque principal
    AZUL_HOVER: Final[str] = "#4338ca"
    VERDE: Final[str] = "#059669"
    VERDE_HOVER: Final[str] = "#047857"
    VERMELHO: Final[str] = "#e11d48"
    VERMELHO_HOVER: Final[str] = "#be123c"
    CINZA: Final[str] = "#e2e8f0"
    CINZA_HOVER: Final[str] = "#cbd5e1"
    # Superfícies e texto
    FUNDO: Final[str] = "#f1f5f9"
    BRANCO: Final[str] = "#ffffff"
    TEXTO: Final[str] = "#0f172a"
    TEXTO_SUAVE: Final[str] = "#64748b"
    PLACEHOLDER: Final[str] = "#94a3b8"
    BORDA: Final[str] = "#e2e8f0"
    # Tabelas
    CABECALHO_TABELA: Final[str] = "#f8fafc"
    CABECALHO_TABELA_HOVER: Final[str] = "#f1f5f9"
    LINHA_PAR: Final[str] = "#fafbfd"
    SELECAO: Final[str] = "#e0e7ff"
    DENTRO_FUNDO: Final[str] = "#ecfdf5"
    SAIU_FUNDO: Final[str] = "#fff1f2"
    # Ilustração da fachada (tela de login)
    FACHADA_CEU: Final[str] = "#1e293b"
    FACHADA_PREDIO: Final[str] = "#334155"
    FACHADA_TELHADO: Final[str] = "#475569"
    FACHADA_JANELA: Final[str] = "#64748b"
    FACHADA_JANELA_ACESA: Final[str] = "#a5b4fc"
    FACHADA_PORTA: Final[str] = "#0f172a"


FONTE: Final[str] = "Segoe UI"
