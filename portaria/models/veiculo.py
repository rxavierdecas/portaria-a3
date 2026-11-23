from dataclasses import dataclass

from portaria.utils.formatters import formatar_placa


@dataclass(slots=True)
class Veiculo:
    pessoa_id: int
    placa: str  # normalizada: só letras e números, maiúsculas
    modelo: str
    cor: str
    id: int | None = None
    pessoa_nome: str = ""

    @property
    def placa_formatada(self) -> str:
        return formatar_placa(self.placa)
