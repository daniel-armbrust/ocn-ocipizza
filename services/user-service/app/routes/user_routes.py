#
# routes/user_routes.py
#

from uuid import UUID

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserConfirmationRequest
)

from app.schemas.jsend_schema import JSendSuccessResponse

from app.exceptions.user_exceptions import (
    UserAlreadyExistsError, 
    UserCreationError,
    UserNotFoundError,
    UserUpdateError,
    UserInvalidEmailConfirmationTokenError
)

from app.services.user_service import UserService, get_user_service
from app.dependencies.authentication import get_current_user_id
from app.responses.jsend import fail_response, success_response

router = APIRouter()

#
# POST: /users
#
@router.post(
        '/users', 
        status_code=status.HTTP_201_CREATED,
        response_model=JSendSuccessResponse
)
def create_user(
    payload: UserCreateRequest,
    service: UserService = Depends(get_user_service)
) -> JSendSuccessResponse | JSONResponse:
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
        Resposta de sucesso no padrão JSend contendo os dados
            do usuário criado.
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

    return success_response(
        {
            'user': UserResponse.from_model(user).model_dump(mode='json')
        }
    )

#
# GET: /users/me
#
@router.get(
    '/users/me',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_me(
    current_user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Retorna os dados do usuário atual.

    Args:
        current_user_id: Identificador UUID do usuário atual.
        service: Serviço responsável pelos casos de uso relacionados
            aos usuários.

    Returns:
        Resposta de sucesso contendo os dados do usuário ou uma resposta
            de falha caso o usuário não seja encontrado.
    """

    try:
        user = service.get_by_id(current_user_id)
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        ) 

    return success_response(
        {
            'user': UserResponse.from_model(user).model_dump(mode='json')
        }
    )

#
# PUT: /users/me
#
@router.put(
    '/users/me',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def update_me(
    payload: UserUpdateRequest,
    current_user_id = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Atualiza os dados permitidos do usuário autenticado.

    Atualmente este endpoint permite somente a atualização do número
    de WhatsApp. Alterações de e-mail ou outros dados sensíveis devem
    possuir fluxos específicos de confirmação.

    Args:
        payload: Dados permitidos para atualização.
        current_user_id: Identificador do usuário autenticado.
        service: Serviço responsável pelos casos de uso do usuário.

    Returns:
        Resposta de sucesso contendo os dados atualizados do usuário.
    """

    try:
        user = service.update(
            user_id=current_user_id,
            payload=payload
        )
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )
    except UserUpdateError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'USER_UPDATE_ERROR',
            'Error updating user.'
        )

    return success_response(
        {
            'user': UserResponse.from_model(user).model_dump(mode='json')
        }
    )


#
# GET: /users/confirm
#
@router.post(
    '/users/confirm',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def confirm_user(
    payload: UserConfirmationRequest,
    service: UserService = Depends(get_user_service)
) -> JSendSuccessResponse | JSendSuccessResponse:
    """
    Confirma o endereço de e-mail de um usuário para que seja 
    possível o usuário utilizar o sistema.

    O token recebido é validado e, caso seja válido, o usuário
    associado é marcado como confirmado.

    Args:
        payload: Dados necessários para confirmação do usuário,
            contendo o endereço de e-mail e o token de confirmação.
        service: Serviço responsável pelos casos de uso relacionados
            à confirmação de e-mail.

    Returns:
        Resposta no padrão JSend indicando o resultado da operação.
    """

    try:
        service.confirm_email(
            email=payload.email,
            token=payload.token
        )
    except (
        UserNotFoundError,
        UserInvalidEmailConfirmationTokenError
    ):
        return fail_response(
            status.HTTP_400_BAD_REQUEST,
            'USER_CONFIRMATION_ERROR',
            'Unable to confirm user.'
        )

    return success_response(
        {
            'message': 'User confirmed successfully.',
        }
    )