#
# routes/user_password_routes.py
#

from uuid import UUID

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.schemas.user_password_schema import (
    UserPasswordUpdateRequest,
    UserPasswordResetRequest,
    UserPasswordResetConfirmRequest
)

from app.schemas.jsend_schema import JSendSuccessResponse

from app.exceptions.user_exceptions import (
    UserNotFoundError,
    UserUpdateError,
    UserNotConfirmedError
)

from app.exceptions.user_password_exceptions import (
    UserInvalidPasswordError,
    UserPasswordMismatchError,
    UserPasswordResetError,
    UserInvalidPasswordResetTokenError
)

from app.services.user_password_service import (
    UserPasswordService,
    get_user_password_service
)
from app.dependencies.authentication import get_current_user_id
from app.responses.jsend import fail_response, success_response

router = APIRouter()


#
# PUT: /users/me/password
#
@router.put(
    '/users/me/password',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def update_password(
    payload: UserPasswordUpdateRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    service: UserPasswordService = Depends(get_user_password_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Atualiza a senha do usuário autenticado.

    A alteração da senha exige a validação da senha atual.
    A nova senha deve ser informada juntamente com sua confirmação.

    Args:
        payload: Dados necessários para alteração da senha.
        current_user_id: Identificador UUID do usuário autenticado.
        service: Serviço responsável pelas operações de senha dos usuários.

    Returns:
        Resposta de sucesso no padrão JSend.

    Raises:
        UserNotFoundError: Caso o usuário autenticado não seja encontrado.
        UserInvalidPasswordError: Caso a senha atual informada seja inválida.
        UserPasswordMismatchError: Caso a nova senha e sua confirmação 
            sejam diferentes.
        UserUpdateError: Caso ocorra uma falha durante a atualização.
    """

    try:
        service.update_password(
            user_id=current_user_id,
            current_password=payload.current_password,
            new_password=payload.new_password,
            confirm_new_password=payload.confirm_new_password
        )
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )
    except UserNotConfirmedError:
        return fail_response(
            status.HTTP_403_FORBIDDEN,
            'USER_NOT_CONFIRMED',
            'User email must be confirmed before changing the password.'
        )
    except UserInvalidPasswordError:
        return fail_response(
            status.HTTP_400_BAD_REQUEST,
            'INVALID_PASSWORD',
            'Current password is invalid.'
        )
    except UserPasswordMismatchError:
        return fail_response(
            status.HTTP_400_BAD_REQUEST,
            'PASSWORD_MISMATCH',
            'New password confirmation does not match.'
        )
    except UserUpdateError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'USER_UPDATE_ERROR',
            'Error updating password.'
        )

    return success_response(
        {
            'message': 'Password updated successfully.'
        }
    )

#
# POST: /users/password-reset/request
#
@router.post(
    '/users/password-reset/request',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def request_password_reset(
    payload: UserPasswordResetRequest,
    service: UserPasswordService = Depends(get_user_password_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Solicita a redefinição da senha de um usuário.

    O usuário informa o endereço de e-mail associado à conta.
    Caso a conta exista e esteja confirmada, o serviço inicia o fluxo
    de recuperação de senha, gerando um token temporário e
    solicitando o envio da mensagem através do `notification-service`.

    Args:
        payload: Dados necessários para iniciar o processo de
            redefinição de senha.
        service: Serviço responsável pelos casos de uso relacionados
            à senha dos usuários.

    Returns:
        Resposta de sucesso no padrão JSend indicando que a solicitação 
        de recuperação de senha foi recebida.
    """

    try:
        service.request_password_reset(email=payload.email)
    except UserNotConfirmedError:
        return fail_response(
            status.HTTP_403_FORBIDDEN,
            'USER_NOT_CONFIRMED',
            'User email must be confirmed before changing the password.'
        )
    except UserPasswordResetError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'PASSWORD_RESET_REQUEST_ERROR',
            'Error requesting password reset.'
        )

    return success_response(
        {
            'message': 'Password reset request received.'
        }
    )

#
# POST: /users/password-reset/confirm
#
@router.post(
    '/users/password-reset/confirm',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def confirm_password_reset(
    payload: UserPasswordResetConfirmRequest,
    service: UserPasswordService = Depends(get_user_password_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Confirma a redefinição da senha de um usuário.

    O token recebido pelo usuário é validado e, caso seja válido, permite 
    a definição de uma nova senha sem exigir a senha atual.

    Args:
        payload: Dados necessários para confirmação da redefinição de senha, 
            incluindo token, nova senha e confirmação.
        service: Serviço responsável pelos casos de uso relacionados à senha 
            dos usuários.

    Returns:
        Resposta de sucesso no padrão JSend indicando que a senha foi 
        redefinida com sucesso.
    """
    try:
        # Valida o token recebido e redefine a senha do usuário.
        service.reset_password(
            token=payload.token,
            new_password=payload.new_password,
            confirm_new_password=payload.confirm_new_password
        )
    except UserPasswordMismatchError:
        return fail_response(
            status.HTTP_400_BAD_REQUEST,
            'PASSWORD_MISMATCH',
            'New password confirmation does not match.'
        )
    except UserInvalidPasswordResetTokenError:
        return fail_response(
            status.HTTP_400_BAD_REQUEST,
            'INVALID_PASSWORD_RESET_TOKEN',
            'Password reset token is invalid or expired.'
        )
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )
    except UserPasswordResetError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'PASSWORD_RESET_ERROR',
            'Error resetting password.'
        )
    
    return success_response(
        {
            'message': 'Password reset successfully.'
        }
    )