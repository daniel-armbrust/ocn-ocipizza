#
# services/token_service.py
#

import hashlib
import secrets


class TokenService:
    """
    Serviço responsável por operações técnicas relacionadas a tokens
    aleatórios utilizados pela aplicação.

    Este serviço não possui conhecimento sobre usuários, persistência
    ou sobre os casos de uso nos quais os tokens serão utilizados.

    Sua responsabilidade é gerar tokens criptograficamente seguros e
    produzir hashes que possam ser armazenados de forma segura no banco
    de dados.

    Os serviços responsáveis pelos casos de uso, como UserEmailService
    e UserPasswordService, utilizam esta classe para geração e hash dos
    tokens necessários aos seus respectivos fluxos.
    """

    def generate_token(self) -> str:
        """
        Gera um token aleatório criptograficamente seguro.

        O token gerado pode ser enviado ao usuário em fluxos como
        confirmação de e-mail e redefinição de senha.

        Returns:
            Token aleatório codificado em formato seguro para utilização
            em URLs e mensagens.
        """

        return secrets.token_urlsafe(32)

    def hash_token(self, token: str) -> str:
        """
        Gera o hash SHA-256 de um token.

        Apenas o hash deve ser armazenado no banco de dados. O token
        original deve permanecer disponível somente durante o fluxo
        necessário para envio ao usuário.

        Args:
            token: Token original que será convertido em hash.

        Returns:
            Representação hexadecimal do hash SHA-256 do token.
        """

        return hashlib.sha256(token.encode('utf-8')).hexdigest()