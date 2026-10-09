#
# dependencies/authentication.py
#

# app/dependencies/authentication.py

from fastapi import Depends, Request

from app.config.settings import settings
from app.exceptions.user_auth_exceptions import AuthenticationRequiredError

from app.services.session_service import SessionService
from app.services.session_service import get_session_service


async def load_authentication_context(
    request: Request,
    session_service: SessionService = Depends(get_session_service)
) -> dict | None:
    """
    Carrega opcionalmente a sessão utilizada para montar a navegação.

    Args:
        request: Requisição HTTP utilizada para obter o cookie de sessão.
        session_service: Serviço responsável pelo gerenciamento das sessões.

    Returns:
        Sessão autenticada ou `None` quando o cookie não existir, estiver
        expirado ou não corresponder a uma sessão persistida.
    """

    session_id = request.cookies.get(settings.session_cookie_name)
    
    session = (
        await session_service.get(session_id=session_id)
        if session_id
        else None
    )

    # Armazena o resultado na própria requisição para que os templates e as
    # dependências de rotas protegidas reutilizem a mesma consulta.
    request.state.authentication_checked = True
    request.state.authenticated_session = session
    request.state.is_authenticated = session is not None

    return session


async def get_authenticated_session(
    request: Request,
    session_service: SessionService = Depends(get_session_service)
):
    """
    Obtém a sessão autenticada do usuário.

    Args:
        request: Requisição HTTP utilizada para obter o cookie de sessão.
        session_service: Serviço responsável pelo gerenciamento das sessões.

    Returns:
        Sessão autenticada do usuário.

    Raises:
        AuthenticationRequiredError: Quando não existir uma sessão válida.
    """

    if getattr(request.state, 'authentication_checked', False):
        session = request.state.authenticated_session
    else:
        session = await load_authentication_context(
            request=request,
            session_service=session_service
        )

    if not session:
        raise AuthenticationRequiredError()

    return session
