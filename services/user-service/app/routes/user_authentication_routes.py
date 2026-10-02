#
# routes/user_authentication_router.py
#

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.schemas.user_authentication_schema import (
    UserLoginRequest,
    UserLogoutRequest,
    UserTokenResponse
)

from app.schemas.jsend_schema import JSendSuccessResponse
from app.responses.jsend import success_response, fail_response

from app.services.user_authentication_service import (
    UserAuthenticationService,
    get_user_authentication_service
)

from app.exceptions.user_exceptions import UserNotFoundError, UserNotConfirmedError
from app.exceptions.user_password_exceptions import UserInvalidPasswordError
from app.exceptions.user_authentication_exceptions import UserAuthenticationError

router = APIRouter()

#
# POST: /auth/login
#
@router.post(
    '/auth/login',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def login(
    payload: UserLoginRequest,
    service: UserAuthenticationService = Depends(get_user_authentication_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Autentica um usuário através de e-mail e senha.

    Após a validação das credenciais, são gerados um access token
    e um refresh token que poderão ser utilizados nas requisições
    autenticadas da aplicação.

    Args:
        payload: Dados utilizados para autenticação do usuário,
            contendo e-mail e senha.
        service: Serviço responsável pelos casos de uso relacionados
            à autenticação dos usuários.

    Returns:
        Resposta no padrão JSend contendo os tokens gerados após
        uma autenticação bem-sucedida.
    """

    try:
        tokens = service.login(
            email=payload.email,
            password=payload.password
        )
    except (
        UserNotFoundError,
        UserInvalidPasswordError
    ):
        return fail_response(
            status.HTTP_401_UNAUTHORIZED,
            'INVALID_CREDENTIALS',
            'Invalid email or password.'
        )
    except UserNotConfirmedError:
        return fail_response(
            status.HTTP_403_FORBIDDEN,
            'USER_NOT_CONFIRMED',
            'User email is not confirmed.'
        )
    except UserAuthenticationError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'AUTHENTICATION_ERROR',
            'Error authenticating user.'
        )
    return success_response(
        UserTokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type='Bearer',
            expires_in=tokens.expires_in
        ).model_dump()
    )

#
# POST: /auth/logout
#

#
# POST: /auth/refresh
#