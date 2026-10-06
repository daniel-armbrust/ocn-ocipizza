#
# services/session_service.py
#

from secrets import token_urlsafe
from typing import Any

from fastapi import Depends

from app.repositories.session_repository import SessionRepository
from app.dependencies.database import get_session_repository


class SessionService:
    """
    Gerencia as sessões utilizadas pelo frontend-service.

    O serviço mantém a lógica de criação e manipulação das sessões
    independente da tecnologia utilizada para persistência.
    """

    def __init__(self, session_repository: SessionRepository) -> None:
        """
        Inicializa o serviço de sessões.

        Args:
            session_repository: Repositório utilizado para persistir
                e recuperar os dados das sessões.
        """

        self.session_repository = session_repository

    async def create(self,
                     access_token: str,
                     refresh_token: str,
                     expires_in: int) -> str:
        """
        Cria uma nova sessão para um usuário autenticado.

        Args:
            access_token: Token utilizado para autenticação junto
                aos microserviços.
            refresh_token: Token utilizado para renovação do
                access token.
            expires_in: Tempo de validade da sessão, em segundos.

        Returns:
            Identificador opaco da sessão criada.
        """

        # Gera um identificador aleatório que será armazenado
        # exclusivamente no cookie enviado ao navegador.
        session_id = token_urlsafe(32)

        session_data: dict[str, Any] = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

        await self.session_repository.create(
            session_id=session_id,
            data=session_data,
            ttl=expires_in
        )

        return session_id

    async def get(self, session_id: str) -> dict[str, Any] | None:
        """
        Retorna os dados associados a uma sessão.

        Args:
            session_id: Identificador da sessão.

        Returns:
            Dados da sessão ou `None` caso ela não exista
            ou tenha expirado.
        """

        return await self.session_repository.get(
            session_id
        )

    async def update(self,
                     session_id: str,
                     data: dict[str, Any],
                     ttl: int | None = None) -> None:
        """
        Atualiza os dados armazenados em uma sessão.

        Args:
            session_id: Identificador da sessão.
            data: Dados que substituirão os valores atuais.
            ttl: Novo tempo de validade da sessão, em segundos.
                Quando não informado, mantém a expiração atual.
        """

        await self.session_repository.update(
            session_id=session_id,
            data=data,
            ttl=ttl
        )

    async def delete(self, session_id: str) -> None:
        """
        Remove uma sessão.

        Args:
            session_id: Identificador da sessão.
        """

        await self.session_repository.delete(session_id)

    async def exists(self, session_id: str) -> bool:
        """
        Verifica se uma sessão existe e continua válida.

        Args:
            session_id: Identificador da sessão.

        Returns:
            `True` quando a sessão existir; caso contrário,
            `False`.
        """

        return await self.session_repository.exists(
            session_id
        )


def get_session_service(
        session_repository: SessionRepository = Depends(
            get_session_repository
        )
) -> SessionService:
    """
    Retorna o serviço responsável pelo gerenciamento
    das sessões do frontend-service.

    Args:
        session_repository: Repositório utilizado para persistir
            e recuperar os dados das sessões.

    Returns:
        Instância configurada de `SessionService`.
    """

    return SessionService(
        session_repository=session_repository
    )