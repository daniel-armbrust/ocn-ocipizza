#
# routes/user_address_routes.py
#

from uuid import UUID

from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import JSONResponse

from app.schemas.user_address_schema import (
    UserAddressResponse
)

from app.exceptions.user_exceptions import (
    UserNotFoundError
)

from app.services.user_address_service import UserAddressService, get_user_address_service
from app.dependencies.authentication import get_current_user_id

from app.schemas.jsend_schema import JSendSuccessResponse
from app.responses.jsend import fail_response, success_response

router = APIRouter()

# POST   /users/me/addresses (cadastra um novo endereço)
# GET    /users/me/addresses/{address_id} (retorna um endereço específico.)
# PUT    /users/me/addresses/{address_id} (altera o endereço.)
# DELETE /users/me/addresses/{address_id} (remove o endereço.)
# PATCH  /users/me/addresses/{address_id}/default (define aquele endereço como padrão.)

#
# GET: /users/me/addresses
#
@router.get(
    '/users/me/addresses',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_user_addresses(
    current_user_id: UUID = Depends(get_current_user_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Retorna os endereços de entrega do usuário autenticado.

    Args:
        current_user: Usuário autenticado obtido a partir do token JWT.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend contendo os endereços cadastrados pelo usuário
        autenticado.
    """
    try:
        addresses = service.get_by_user_id(current_user_id)
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )

    return success_response(
        {
            'addresses': [
                UserAddressResponse.from_model(address).model_dump(mode='json')
                for address in addresses
            ]
        }
    )