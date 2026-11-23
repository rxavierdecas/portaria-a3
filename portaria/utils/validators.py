"""Funções de validação de dados de entrada."""

import re
from collections.abc import Mapping
from datetime import datetime

from portaria import config

_PLACA_ANTIGA = re.compile(r"^[A-Z]{3}\d{4}$")
_PLACA_MERCOSUL = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")
_DATA = re.compile(r"^\d{2}/\d{2}/\d{4}$")
_HORARIO = re.compile(r"^\d{2}:\d{2}$")


def somente_digitos(texto: str) -> str:
    return "".join(c for c in texto if c.isdigit())


def campos_vazios(campos: Mapping[str, str]) -> list[str]:
    """Retorna os rótulos dos campos que estão vazios (ou só com espaços)."""
    vazios: list[str] = []
    for rotulo, valor in campos.items():
        if not valor.strip():
            vazios.append(rotulo)
    return vazios


def _digito_verificador_cpf(digitos: str) -> int:
    peso = len(digitos) + 1
    soma = 0
    for digito in digitos:
        soma += int(digito) * peso
        peso -= 1
    resto = (soma * 10) % 11
    return 0 if resto == 10 else resto


def calcular_digitos_cpf(base: str) -> str:
    """Calcula os 2 dígitos verificadores a partir dos 9 primeiros dígitos."""
    primeiro = _digito_verificador_cpf(base)
    segundo = _digito_verificador_cpf(base + str(primeiro))
    return f"{primeiro}{segundo}"


def validar_cpf(cpf: str) -> bool:
    """Valida o CPF pelos dígitos verificadores (aceita com ou sem máscara)."""
    digitos = somente_digitos(cpf)
    if len(digitos) != 11:
        return False
    if digitos == digitos[0] * 11:  # 000.000.000-00, 111.111.111-11, ...
        return False
    return digitos[9:] == calcular_digitos_cpf(digitos[:9])


def validar_telefone(telefone: str) -> bool:
    """Fixo (10 dígitos) ou celular (11 dígitos), com DDD válido."""
    digitos = somente_digitos(telefone)
    if len(digitos) not in (10, 11):
        return False
    if digitos[0] == "0":
        return False
    if len(digitos) == 11 and digitos[2] != "9":
        return False
    return True


def validar_data(data: str) -> bool:
    """Data no formato estrito dd/mm/aaaa e existente no calendário."""
    if not _DATA.match(data.strip()):
        return False
    try:
        datetime.strptime(data.strip(), config.FORMATO_DATA)
    except ValueError:
        return False
    return True


def validar_horario(horario: str) -> bool:
    """Horário no formato estrito HH:MM (00:00 a 23:59)."""
    if not _HORARIO.match(horario.strip()):
        return False
    try:
        datetime.strptime(horario.strip(), config.FORMATO_HORA)
    except ValueError:
        return False
    return True


def normalizar_placa(placa: str) -> str:
    return "".join(c for c in placa.upper() if c.isalnum())


def validar_placa(placa: str) -> bool:
    """Aceita o padrão antigo (ABC-1234) e o Mercosul (ABC1D23)."""
    normalizada = normalizar_placa(placa)
    return bool(_PLACA_ANTIGA.match(normalizada) or _PLACA_MERCOSUL.match(normalizada))
