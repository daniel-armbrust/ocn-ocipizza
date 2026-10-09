#
# routes/user_address_routes.py
#

from uuid import UUID

from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import JSONResponse

from app.schemas.user_address_schema import (
    UserAddressResponse,
    UserAddressCreateRequest,
    UserAddressUpdateRequest
)

from app.exceptions.user_exceptions import UserNotFoundError
from app.exceptions.user_address_exceptions import (
    UserAddressLimitExceededError,
    UserAddressNotFoundError
)

from app.services.user_address_service import UserAddressService, get_user_address_service
from app.dependencies.authentication import get_current_user_id

from app.schemas.jsend_schema import JSendSuccessResponse
from app.responses.jsend import fail_response, success_response

router = APIRouter()

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

#
# GET: /users/me/addresses/{address_id}
#
@router.get(
    '/users/me/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_user_address(
    address_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Retorna um endereço específico do usuário autenticado.

    Args:
        address_id: Identificador único do endereço.
        current_user_id: Identificador único do usuário autenticado obtido
            a partir do token JWT.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend contendo o endereço solicitado.
    """

    try:
        address = service.get_by_id(
            address_id,
            current_user_id
        )
    except UserAddressNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_ADDRESS_NOT_FOUND',
            'User address not found.'
        )

    return success_response(
        {
            'address': UserAddressResponse.from_model(
                address
            ).model_dump(mode='json')
        }
    )

#
# POST: /users/me/addresses
#
@router.post(
    '/users/me/addresses',
    status_code=status.HTTP_201_CREATED,
    response_model=JSendSuccessResponse
)
def create_user_address(
    payload: UserAddressCreateRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Cadastra um novo endereço para o usuário autenticado.

    Args:
        payload: Dados necessários para cadastrar o endereço.
        current_user_id: Identificador único do usuário autenticado obtido
            a partir do token JWT.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend contendo o endereço cadastrado.
    """

    try:
        address = service.create(
            current_user_id,
            payload
        )
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )
    except UserAddressLimitExceededError:
        return fail_response(
            status.HTTP_409_CONFLICT,
            'USER_ADDRESS_LIMIT_EXCEEDED',
            'Maximum number of addresses reached.'
        )
    
    return success_response(
        {
            'address': UserAddressResponse.from_model(
                address
            ).model_dump(mode='json')
        }
    )

#
# PUT: /users/me/addresses/{address_id} 
#
@router.put(
    '/users/me/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def update_user_address(
    address_id: UUID,
    payload: UserAddressUpdateRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Atualiza um endereço do usuário autenticado.

    Args:
        address_id: Identificador único do endereço.
        payload: Dados do endereço que serão atualizados.
        current_user_id: Identificador único do usuário autenticado obtido
            a partir do token JWT.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend contendo o endereço atualizado.
    """

    try:
        address = service.update(
            address_id,
            current_user_id,
            payload
        )
    except UserAddressNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_ADDRESS_NOT_FOUND',
            'User address not found.'
        )

    return success_response(
        {
            'address': UserAddressResponse.from_model(
                address
            ).model_dump(mode='json')
        }
    )

#
# DELETE: /users/me/addresses/{address_id}
#
@router.delete(
    '/users/me/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def delete_user_address(
    address_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Remove um endereço do usuário autenticado.

    Args:
        address_id: Identificador único do endereço.
        current_user_id: Identificador único do usuário autenticado obtido
            a partir do token JWT.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend indicando que o endereço foi removido.
    """

    try:
        service.delete(
            address_id,
            current_user_id
        )
    except UserAddressNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_ADDRESS_NOT_FOUND',
            'User address not found.'
        )

    return success_response(
        {
            'message': 'User address deleted successfully.'
        }
    )

#
# PATCH: /users/me/addresses/{address_id}/default
#
@router.patch(
    '/users/me/addresses/{address_id}/default',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def set_default_user_address(
    address_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Define um endereço como padrão para o usuário autenticado.

    Args:
        address_id: Identificador único do endereço.
        current_user_id: Identificador único do usuário autenticado obtido
            a partir do token JWT.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend contendo o endereço definido como padrão.
    """
    
    try:
        address = service.set_default(
            address_id,
            current_user_id
        )
    except UserAddressNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_ADDRESS_NOT_FOUND',
            'User address not found.'
        )

    return success_response(
        {
            'address': UserAddressResponse.from_model(
                address
            ).model_dump(mode='json')
        }
    )