from dataclasses import dataclass
from datetime import datetime

from portaria.utils.formatters import formatar_codigo, formatar_cpf, formatar_telefone


@dataclass(slots=True)
class Pessoa:
    """Pessoa autorizada a acessar a portaria.

    ``cpf`` e ``telefone`` são armazenados apenas com dígitos.
    """

    nome: str
    cpf: str
    telefone: str
    empresa: str
    tipo_acesso: str
    motivo: str
    id: int | None = None
    criado_em: datetime | None = None

    @property
    def codigo(self) -> str:
        return formatar_codigo(self.id)

    @property
    def cpf_formatado(self) -> str:
        return formatar_cpf(self.cpf)

    @property
    def telefone_formatado(self) -> str:
        return formatar_telefone(self.telefone)

    @property
    def rotulo(self) -> str:
        """Texto curto para listas de seleção: ``001 - Maria Silva``."""
        return f"{self.codigo} - {self.nome}"
