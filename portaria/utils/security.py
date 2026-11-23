"""Hash e verificação de senhas (PBKDF2-HMAC-SHA256, biblioteca padrão)."""

import hashlib
import hmac
import secrets

_ITERACOES = 200_000


def hash_senha(senha: str, salt: str | None = None) -> tuple[str, str]:
    """Retorna ``(hash_hex, salt_hex)`` para a senha informada."""
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), bytes.fromhex(salt), _ITERACOES)
    return digest.hex(), salt


def verificar_senha(senha: str, senha_hash: str, salt: str) -> bool:
    """Compara a senha com o hash armazenado em tempo constante."""
    calculado, _ = hash_senha(senha, salt)
    return hmac.compare_digest(calculado, senha_hash)
