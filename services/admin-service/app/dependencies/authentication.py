#
# dependencies/authentication.py
#

from fastapi import Depends, Request

from app.config.settings import settings
from app.exceptions.admin_auth_exceptions import AdminAccessDeniedError
from app.exceptions.auth_exceptions import AuthenticationRequiredError

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


async def get_admin_authenticated_session(
    request: Request,
    session_service: SessionService = Depends(get_session_service)
) -> dict:
    """
    Obtém uma sessão autenticada com acesso administrativo.

    Args:
        request: Requisição HTTP utilizada para obter o cookie de sessão.
        session_service: Serviço responsável pelo gerenciamento das sessões.

    Returns:
        Sessão do usuário com permissão administrativa.

    Raises:
        AuthenticationRequiredError: Quando não existir uma sessão válida.
        AdminAccessDeniedError: Quando o usuário autenticado não possui
            permissão administrativa.
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

    if session.get('is_admin') is not True:
        raise AdminAccessDeniedError(
            'Administrative access is required.'
        )

    return session


async def get_kitchen_authenticated_session(
    request: Request,
    session_service: SessionService = Depends(get_session_service)
) -> dict:
    """
    Obtém uma sessão autenticada com acesso às funcionalidades da cozinha.

    Args:
        request: Requisição HTTP utilizada para obter o cookie de sessão.
        session_service: Serviço responsável pelo gerenciamento das sessões.

    Returns:
        Sessão do usuário com permissão de acesso à cozinha.

    Raises:
        AuthenticationRequiredError: Quando não existir uma sessão válida.
        AdminAccessDeniedError: Quando o usuário autenticado não possui
            permissão de acesso à cozinha.
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

    if session.get('is_kitchen') is not True:
        raise AdminAccessDeniedError(
            'Kitchen access is required.'
        )

    return session
