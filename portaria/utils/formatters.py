"""Funções de formatação para exibição."""

from datetime import date, datetime

from portaria import config
from portaria.utils.validators import normalizar_placa, somente_digitos


def aplicar_mascara(digitos: str, mascara: str) -> str:
    """Aplica uma máscara progressiva, onde ``#`` representa um dígito.

    >>> aplicar_mascara("1234", "###.###.###-##")
    '123.4'
    """
    resultado: list[str] = []
    indice = 0
    for simbolo in mascara:
        if indice >= len(digitos):
            break
        if simbolo == "#":
            resultado.append(digitos[indice])
            indice += 1
        else:
            resultado.append(simbolo)
    return "".join(resultado)


def formatar_cpf(cpf: str) -> str:
    return aplicar_mascara(somente_digitos(cpf)[:11], "###.###.###-##")


def formatar_telefone(telefone: str) -> str:
    digitos = somente_digitos(telefone)[:11]
    if len(digitos) <= 10:
        return aplicar_mascara(digitos, "(##) ####-####")
    return aplicar_mascara(digitos, "(##) #####-####")


def formatar_horario(horario: str) -> str:
    return aplicar_mascara(somente_digitos(horario)[:4], "##:##")


def formatar_codigo(identificador: int | None) -> str:
    return "-" if identificador is None else f"{identificador:03d}"


def formatar_placa(placa: str) -> str:
    normalizada = normalizar_placa(placa)
    if len(normalizada) == 7 and normalizada[4].isdigit():  # padrão antigo
        return f"{normalizada[:3]}-{normalizada[3:]}"
    return normalizada


def formatar_hora_movimento(momento: datetime | None, hoje: date | None = None) -> str:
    """Hora (HH:MM) se for hoje; caso contrário, inclui o dia (dd/mm HH:MM)."""
    if momento is None:
        return "-"
    hoje = hoje or date.today()
    if momento.date() == hoje:
        return momento.strftime(config.FORMATO_HORA)
    return momento.strftime("%d/%m %H:%M")


def formatar_data_hora(momento: datetime | None) -> str:
    return "-" if momento is None else momento.strftime(config.FORMATO_DATA_HORA)
