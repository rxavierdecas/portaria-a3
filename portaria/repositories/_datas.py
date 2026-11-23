"""Conversão entre ``datetime`` e o texto ISO gravado no SQLite."""

from datetime import datetime

from portaria import config


def para_texto(momento: datetime | None) -> str | None:
    return None if momento is None else momento.strftime(config.FORMATO_ISO)


def para_datetime(texto: str | None) -> datetime | None:
    return None if texto is None else datetime.strptime(texto, config.FORMATO_ISO)


def para_datetime_obrigatorio(texto: str) -> datetime:
    return datetime.strptime(texto, config.FORMATO_ISO)
