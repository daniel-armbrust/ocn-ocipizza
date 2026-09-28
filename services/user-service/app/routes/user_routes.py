#
# routes/user_routes.py
#

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.schemas.user_schema import (
    UserCreateRequest,
    UserResponse,
    UserSuccessData,
    UserSuccessResponse
)

from app.exceptions.user_exceptions import (
    UserAlreadyExistsError, 
    UserCreationError
)

from app.services.user_service import UserService, get_user_service

from app.responses.jsend import fail_response


router = APIRouter()

#
# POST: /users
#
@router.post(
        '/users', 
        status_code=status.HTTP_201_CREATED,
        response_model=UserSuccessResponse
)
def create_user(
    payload: UserCreateRequest,
    service: UserService = Depends(get_user_service)
) -> UserSuccessResponse | JSONResponse:
    """
    Cria um novo usuário.

    O usuário é criado inicialmente com o e-mail não confirmado.
    Após a criação, uma solicitação de envio do e-mail de confirmação
    é publicada no mecanismo de mensageria configurado.

    Args:
        payload: Dados necessários para criação do usuário.

        service: Serviço responsável pelos casos de uso relacionados
            aos usuários.

    Returns:
        Resposta de sucesso contendo os dados do usuário criado.
    """

    try: 
        user = service.create(payload) 
    except UserAlreadyExistsError:
        return fail_response(
            status.HTTP_409_CONFLICT,
            'USER_ALREADY_REGISTERED',
            'E-mail or WhatsApp already registered.'
        )
    except UserCreationError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'USER_CREATION_ERROR',
            'Unable to create user.'
        )

    return UserSuccessResponse(
        data=UserSuccessData(
            user=UserResponse.from_model(user),
        )
    )
