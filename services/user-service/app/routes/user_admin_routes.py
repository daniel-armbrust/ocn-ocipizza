#
# routes/user_admin_routes.py
#

from uuid import UUID

from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import JSONResponse

from app.schemas.user_schema import UserResponse

from app.schemas.user_admin_schema import (
    UserAdminCreateRequest,
    UserAdminUpdateRequest,
    UserAdminPasswordUpdateRequest
)

from app.schemas.user_address_schema import (
    UserAddressResponse,
    UserAddressCreateRequest,
    UserAddressUpdateRequest
)

from app.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    UserCreationError,
    UserNotFoundError,
    UserUpdateError,
    UserQueryError,
    UserDeletionError
)

from app.exceptions.user_address_exceptions import (
    UserAddressLimitExceededError,
    UserAddressNotFoundError
)

from app.exceptions.user_authentication_exceptions import UserAuthenticationError
from app.exceptions.user_password_exceptions import UserPasswordMismatchError

from app.services.user_admin_service import (
    UserServiceAdmin,
    get_user_service_admin
)

from app.services.user_authentication_service import (
    UserAuthenticationService,
    get_user_authentication_service
)

from app.services.user_password_service import (
    UserPasswordService,
    get_user_password_service
)

from app.services.user_address_service import (
    UserAddressService,
    get_user_address_service
)

from app.dependencies.authentication import get_current_admin_id

from app.schemas.jsend_schema import JSendSuccessResponse
from app.responses.jsend import fail_response, success_response

router = APIRouter()

#
# POST: /admin/users
#
@router.post(
    '/admin/users',
    status_code=status.HTTP_201_CREATED,
    response_model=JSendSuccessResponse
)
def create_user(
    payload: UserAdminCreateRequest,
    _: UUID = Depends(get_current_admin_id),
    service: UserServiceAdmin = Depends(get_user_service_admin)
) -> JSendSuccessResponse | JSONResponse:
    """
    Cria um novo usuário através de uma operação administrativa.

    Esta operação é restrita a usuários com privilégios administrativos
    e permite definir se o novo usuário também possuirá privilégios
    administrativos.

    Args:
        payload: Dados necessários para criação do usuário.
        service: Serviço responsável pelos casos de uso relacionados
            aos usuários.

    Returns:
        Resposta no padrão JSend contendo os dados do usuário criado.
    """

    try:
        user = service.create(payload=payload)
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
            'Error creating user.'
        )

    return success_response(
        {
            'user': UserResponse.from_model(user).model_dump(mode='json')
        }
    )

#
# GET: /admin/users
#
@router.get(
    '/admin/users',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse,
)
def list_users(
    email: str | None = None,
    confirmed: bool | None = None,
    is_admin: bool | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: UUID = Depends(get_current_admin_id),
    service: UserServiceAdmin = Depends(get_user_service_admin)
) -> JSendSuccessResponse | JSONResponse:
    """
    Retorna os usuários cadastrados de acordo com os filtros informados.

    Esta operação é restrita a usuários com privilégios
    administrativos.

    Args:
        email: Parte do endereço de e-mail utilizada como filtro.
        confirmed: Filtra usuários de acordo com o estado de confirmação.
        is_admin: Filtra usuários de acordo com o privilégio administrativo.
        limit: Quantidade máxima de usuários retornados.
        offset: Quantidade de registros ignorados antes do retorno.
        service: Serviço responsável pelos casos de uso relacionados
            aos usuários.

    Returns:
        Resposta no padrão JSend contendo os usuários encontrados.
    """

    try:
        users = service.get_all(
            email=email,
            confirmed=confirmed,
            is_admin=is_admin,
            limit=limit,
            offset=offset
        )
    except UserQueryError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'USER_QUERY_ERROR',
            'Error retrieving users.'
        )
    return success_response(
        {
            'users': [
                UserResponse.from_model(user).model_dump(mode='json')
                for user in users
            ]
        }
    )

#
# GET: /admin/users/{user_id}
#
@router.get(
    '/admin/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_user(
    user_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: UserServiceAdmin = Depends(get_user_service_admin)
) -> JSendSuccessResponse | JSONResponse:
    """
    Retorna os dados de um usuário específico.

    Esta operação é restrita a usuários com privilégios
    administrativos.

    Args:
        user_id: Identificador UUID do usuário que será consultado.
        service: Serviço responsável pelos casos de uso relacionados
            aos usuários.

    Returns:
        Resposta no padrão JSend contendo os dados do usuário.
    """

    try:
        user = service.get_by_id(user_id=user_id)
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )
    except UserQueryError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'USER_QUERY_ERROR',
            'Error retrieving user.'
        )

    return success_response(
        {
            'user': UserResponse.from_model(user).model_dump(mode='json')
        }
    )

#
# PUT: /admin/users/{user_id}
#
@router.put(
    '/admin/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def update_user(
    user_id: UUID,
    payload: UserAdminUpdateRequest,
    _: UUID = Depends(get_current_admin_id),
    service: UserServiceAdmin = Depends(get_user_service_admin)
) -> JSendSuccessResponse | JSONResponse:
    """
    Atualiza os dados de um usuário através de uma operação administrativa.

    Esta operação é restrita a usuários com privilégios administrativos.

    Args:
        user_id: Identificador UUID do usuário que será atualizado.
        payload: Dados que serão utilizados na atualização do usuário.
        service: Serviço responsável pelos casos de uso relacionados
            aos usuários.

    Returns:
        Resposta no padrão JSend contendo os dados atualizados do usuário.
    """

    try:
        user = service.update(user_id=user_id, payload=payload)
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )
    except UserAlreadyExistsError:
        return fail_response(
            status.HTTP_409_CONFLICT,
            'USER_ALREADY_REGISTERED',
            'E-mail or WhatsApp already registered.'
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
# PUT: /admin/users/{user_id}/password
#
@router.put(
    '/admin/users/{user_id}/password',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def set_admin_password(
    user_id: UUID,
    payload: UserAdminPasswordUpdateRequest,
    _: UUID = Depends(get_current_admin_id),
    service: UserPasswordService = Depends(get_user_password_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Define administrativamente uma nova senha para um usuário.

    Args:
        user_id: Identificador UUID do usuário.
        payload: Nova senha e sua confirmação.
        service: Serviço responsável pelas operações de senha.

    Returns:
        Resposta no padrão JSend indicando o resultado da operação.
    """

    try:
        service.set_password_by_admin(
            user_id=user_id,
            new_password=payload.new_password,
            confirm_new_password=payload.confirm_new_password
        )
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )
    except UserPasswordMismatchError:
        return fail_response(
            status.HTTP_400_BAD_REQUEST,
            'USER_PASSWORD_MISMATCH',
            'New password confirmation does not match.'
        )
    except UserUpdateError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'USER_PASSWORD_UPDATE_ERROR',
            'Error setting user password.'
        )

    return success_response(
        {
            'message': 'User password updated successfully.',
        }
    )

#
# POST: /admin/users/{user_id}/confirm
#
@router.post(
    '/admin/users/{user_id}/confirm',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def confirm_user(
    user_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: UserServiceAdmin = Depends(get_user_service_admin)
) -> JSendSuccessResponse | JSONResponse:
    """
    Confirma administrativamente o cadastro de um usuário.

    Esta operação é restrita a usuários com privilégios administrativos
    e não exige o token normalmente utilizado no fluxo de confirmação
    por e-mail.

    Args:
        user_id: Identificador UUID do usuário que será confirmado.
        service: Serviço responsável pelos casos de uso relacionados
            aos usuários.

    Returns:
        Resposta no padrão JSend contendo os dados do usuário confirmado.
    """

    try:
        user = service.confirm(user_id=user_id)
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
            'Error confirming user.'
        )

    return success_response(
        {
            'user': UserResponse.from_model(user).model_dump(mode='json')
        }
    )

#
# POST: /admin/users/{user_id}/revoke-sessions
#
@router.post(
    '/admin/users/{user_id}/revoke-sessions',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def revoke_user_sessions(
    user_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: UserAuthenticationService = Depends(get_user_authentication_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Revoga todas as sessões de um usuário.

    Esta operação é restrita a usuários com privilégios administrativos.
    Todos os refresh tokens ativos associados ao usuário são revogados,
    impedindo a renovação dos access tokens dessas sessões.

    Args:
        user_id: Identificador UUID do usuário cujas sessões serão
            revogadas.
        service: Serviço responsável pelos casos de uso relacionados
            à autenticação dos usuários.

    Returns:
        Resposta no padrão JSend indicando o resultado da operação.
    """

    try:
        service.revoke_user_sessions(user_id=user_id)
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )
    except UserAuthenticationError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'USER_SESSION_REVOCATION_ERROR',
            'Error revoking user sessions.'
        )

    return success_response(
        {
            'message': 'User sessions revoked successfully.',
        }
    )

#
# DELETE: /admin/users/{user_id}
#
@router.delete(
    '/admin/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def delete_user(
    user_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: UserServiceAdmin = Depends(get_user_service_admin)
) -> JSendSuccessResponse | JSONResponse:
    """
    Remove um usuário através de uma operação administrativa.

    Esta operação é restrita a usuários com privilégios administrativos.

    Args:
        user_id: Identificador UUID do usuário que será removido.
        service: Serviço responsável pelos casos de uso relacionados
            aos usuários.

    Returns:
        Resposta no padrão JSend indicando o resultado da operação.
    """

    try:
        service.delete(user_id=user_id)
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )
    except UserDeletionError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'USER_DELETION_ERROR',
            'Error deleting user.'
        )

    return success_response(
        {
            'message': 'User deleted successfully.',
        }
    )

#
# GET: /admin/users/{user_id}/addresses
#
@router.get(
    '/admin/users/{user_id}/addresses',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_admin_user_addresses(
    user_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Retorna os endereços cadastrados para um usuário.

    Args:
        user_id: Identificador único do usuário.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend contendo os endereços cadastrados para o usuário.
    """

    try:
        addresses = service.get_by_user_id(user_id)
    except UserNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'USER_NOT_FOUND',
            'User not found.'
        )

    return success_response(
        {
            'addresses': [
                UserAddressResponse.from_model(
                    address
                ).model_dump(mode='json')
                for address in addresses
            ]
        }
    )

#
# POST: /admin/users/{user_id}/addresses
#
@router.post(
    '/admin/users/{user_id}/addresses',
    status_code=status.HTTP_201_CREATED,
    response_model=JSendSuccessResponse
)
def create_admin_user_address(
    user_id: UUID,
    payload: UserAddressCreateRequest,
    _: UUID = Depends(get_current_admin_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Cadastra um novo endereço para um usuário.

    Args:
        user_id: Identificador único do usuário.
        payload: Dados necessários para cadastrar o endereço.
        _: Identificador do administrador autenticado, utilizado apenas
            para validar a autorização de acesso à rota.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend contendo o endereço cadastrado.
    """

    try:
        address = service.create(
            user_id,
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
# PUT: /admin/users/{user_id}/addresses/{address_id}
#
@router.put(
    '/admin/users/{user_id}/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def update_admin_user_address(
    user_id: UUID,
    address_id: UUID,
    payload: UserAddressUpdateRequest,
    _: UUID = Depends(get_current_admin_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Atualiza um endereço pertencente a um usuário.

    Args:
        user_id: Identificador único do usuário proprietário do endereço.
        address_id: Identificador único do endereço.
        payload: Dados do endereço que serão atualizados.
        _: Identificador do administrador autenticado, utilizado apenas
            para validar a autorização de acesso à rota.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend contendo o endereço atualizado.
    """

    try:
        address = service.update(
            address_id,
            user_id,
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
# DELETE: /admin/users/{user_id}/addresses/{address_id}
#
@router.delete(
    '/admin/users/{user_id}/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def delete_admin_user_address(
    user_id: UUID,
    address_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Remove um endereço pertencente a um usuário.

    Args:
        user_id: Identificador único do usuário proprietário do endereço.
        address_id: Identificador único do endereço.
        _: Identificador do administrador autenticado, utilizado apenas
            para validar a autorização de acesso à rota.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend indicando que o endereço foi removido.
    """

    try:
        service.delete(
            address_id,
            user_id
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
# PATCH: /admin/users/{user_id}/addresses/{address_id}/default
#
@router.patch(
    '/admin/users/{user_id}/addresses/{address_id}/default',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def set_admin_default_user_address(
    user_id: UUID,
    address_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: UserAddressService = Depends(get_user_address_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Define um endereço como padrão para um usuário.

    Args:
        user_id: Identificador único do usuário proprietário do endereço.
        address_id: Identificador único do endereço.
        _: Identificador do administrador autenticado, utilizado apenas
            para validar a autorização de acesso à rota.
        service: Serviço responsável pelas operações relacionadas aos
            endereços dos usuários.

    Returns:
        Resposta JSend contendo o endereço definido como padrão.
    """
    
    try:
        address = service.set_default(
            address_id,
            user_id
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