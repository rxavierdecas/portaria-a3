from portaria.exceptions import AutenticacaoError, ValidacaoError
from portaria.models.usuario import Usuario
from portaria.repositories.usuario_repository import UsuarioRepository
from portaria.utils.security import verificar_senha


class AuthService:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self._usuarios = usuarios

    def autenticar(self, username: str, senha: str) -> Usuario:
        """Valida as credenciais e retorna o usuário autenticado.

        Raises:
            ValidacaoError: usuário ou senha em branco.
            AutenticacaoError: credenciais incorretas.
        """
        username = username.strip()
        if not username or not senha:
            raise ValidacaoError("Preencha o usuário e a senha.")

        usuario = self._usuarios.buscar_por_username(username)
        # Mesma mensagem para usuário inexistente e senha errada (não revela qual falhou).
        if usuario is None or not verificar_senha(senha, usuario.senha_hash, usuario.salt):
            raise AutenticacaoError("Usuário ou senha incorretos.")
        return usuario
