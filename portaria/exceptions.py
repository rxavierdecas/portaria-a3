"""Exceções de domínio.

As camadas de serviço e repositório lançam estas exceções; a interface
gráfica as captura com try/except e exibe a mensagem ao usuário.
"""


class PortariaError(Exception):
    """Base para todos os erros de negócio do sistema."""


class ValidacaoError(PortariaError):
    """Dados informados são inválidos ou incompletos."""


class AutenticacaoError(PortariaError):
    """Usuário ou senha incorretos."""


class DuplicadoError(PortariaError):
    """Registro já existente (ex.: CPF ou placa repetidos)."""


class AcessoError(PortariaError):
    """Operação de entrada/saída não permitida no estado atual."""


class NaoEncontradoError(PortariaError):
    """Registro solicitado não existe."""
