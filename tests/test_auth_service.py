import pytest

from portaria import config
from portaria.exceptions import AutenticacaoError, ValidacaoError
from tests.conftest import Ambiente


def test_login_admin_padrao(amb: Ambiente) -> None:
    usuario = amb.auth.autenticar(config.ADMIN_USERNAME, config.ADMIN_SENHA)
    assert usuario.nome == config.ADMIN_NOME


@pytest.mark.parametrize(("usuario", "senha"), [("", "x"), ("admin", ""), ("   ", "")])
def test_campos_vazios(amb: Ambiente, usuario: str, senha: str) -> None:
    with pytest.raises(ValidacaoError):
        amb.auth.autenticar(usuario, senha)


@pytest.mark.parametrize(("usuario", "senha"), [("admin", "errada"), ("fulano", "admin123")])
def test_credenciais_incorretas(amb: Ambiente, usuario: str, senha: str) -> None:
    with pytest.raises(AutenticacaoError):
        amb.auth.autenticar(usuario, senha)
