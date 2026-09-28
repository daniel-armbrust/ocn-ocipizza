#
# services/user_password_service.py
#

import hashlib
import hmac
import secrets


class UserPasswordService:
    """
    Serviço responsável pelas operações relacionadas à senha dos usuários.

    Esta camada concentra as regras de negócio de segurança de senha,
    como geração de hash, validação de credenciais e operações relacionadas
    ao ciclo de vida da senha.

    O serviço não possui conhecimento sobre detalhes de infraestrutura,
    como banco de dados, ORM ou mecanismo de persistência. As operações
    de armazenamento e recuperação de dados são responsabilidade dos
    repositories apropriados.

    A responsabilidade deste serviço é garantir que as operações envolvendo
    senhas utilizem mecanismos seguros de processamento, mantendo a senha
    original protegida e evitando seu armazenamento em texto puro.
    """
    
    def __init__(self):
        pass

    def hash_password(self, password: str) -> str:
        """
        Gera hash seguro de senha usando PBKDF2-SHA256 e salt aleatório.

        Args:
            password: Senha em texto puro recebida no cadastro.

        Returns:
            String serializada contendo algoritmo, iterações, salt e digest.
        """
        salt = secrets.token_hex(16)

        iterations = 600000

        digest = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        ).hex()

        return f'pbkdf2_sha256${iterations}${salt}${digest}'

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Valida uma senha em texto puro contra hash PBKDF2-SHA256 armazenado.

        Args:
            password: Senha em texto puro enviada no login.
            password_hash: Hash armazenado no repositório de usuários.

        Returns:
            `True` quando a senha corresponde ao hash armazenado.
        """

        try:
            algorithm, iterations, salt, digest = password_hash.split('$', 3)
        except ValueError:
            return False

        if algorithm != 'pbkdf2_sha256':
            return False

        computed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            int(iterations)
        ).hex()

        return hmac.compare_digest(computed, digest)
        

def get_user_password_service() -> UserPasswordService:
    """
    Monta o serviço de senhas para uso nas dependências da aplicação.

    Returns:
        Instância de `UserPasswordService`.
    """

    return UserPasswordService()