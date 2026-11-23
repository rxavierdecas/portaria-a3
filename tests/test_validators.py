import pytest

from portaria.utils.formatters import (
    aplicar_mascara,
    formatar_codigo,
    formatar_cpf,
    formatar_placa,
    formatar_telefone,
)
from portaria.utils.security import hash_senha, verificar_senha
from portaria.utils.validators import (
    campos_vazios,
    validar_cpf,
    validar_data,
    validar_horario,
    validar_placa,
    validar_telefone,
)


@pytest.mark.parametrize("cpf", ["529.982.247-25", "52998224725", "111.444.777-35", "123.456.789-09"])
def test_cpf_valido(cpf: str) -> None:
    assert validar_cpf(cpf)


@pytest.mark.parametrize(
    "cpf",
    ["529.982.247-26", "111.111.111-11", "000.000.000-00", "123", "", "123.456.789-00"],
)
def test_cpf_invalido(cpf: str) -> None:
    assert not validar_cpf(cpf)


@pytest.mark.parametrize(
    ("telefone", "esperado"),
    [
        ("(31) 98888-7777", True),
        ("(31) 3333-4444", True),
        ("(31) 88888-7777", False),  # celular sem 9
        ("(01) 3333-4444", False),
        ("3333-4444", False),
    ],
)
def test_telefone(telefone: str, esperado: bool) -> None:
    assert validar_telefone(telefone) is esperado


def test_data_e_horario() -> None:
    assert validar_data("29/02/2024")
    assert not validar_data("29/02/2025")
    assert validar_horario("23:59")
    assert not validar_horario("24:00")
    assert not validar_horario("12:6")


@pytest.mark.parametrize(
    ("placa", "esperado"),
    [("ABC-1234", True), ("abc1234", True), ("BRA2E19", True), ("AB-1234", False), ("ABCD123", False)],
)
def test_placa(placa: str, esperado: bool) -> None:
    assert validar_placa(placa) is esperado


def test_campos_vazios() -> None:
    assert campos_vazios({"Nome": "  ", "CPF": "1", "Empresa": ""}) == ["Nome", "Empresa"]


def test_formatadores() -> None:
    assert aplicar_mascara("1234", "###.###.###-##") == "123.4"
    assert formatar_cpf("52998224725") == "529.982.247-25"
    assert formatar_telefone("31988887777") == "(31) 98888-7777"
    assert formatar_telefone("3133334444") == "(31) 3333-4444"
    assert formatar_codigo(7) == "007"
    assert formatar_placa("abc1234") == "ABC-1234"
    assert formatar_placa("bra2e19") == "BRA2E19"


def test_hash_senha() -> None:
    senha_hash, salt = hash_senha("segredo")
    assert verificar_senha("segredo", senha_hash, salt)
    assert not verificar_senha("errada", senha_hash, salt)
    assert hash_senha("segredo")[0] != senha_hash  # salt aleatório
