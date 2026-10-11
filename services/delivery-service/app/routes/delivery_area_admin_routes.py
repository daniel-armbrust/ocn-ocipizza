#
# routes/delivery_area_admin_routes.py
#

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.authentication import get_current_admin_id

from app.services.delivery_area_service import (
    DeliveryAreaService,
    get_delivery_area_service
)

from app.schemas.jsend_schema import JSendSuccessResponse

from app.schemas.delivery_area_schema import (
    DeliveryAreaResponse, 
    DeliveryAreaCreateRequest,
    DeliveryAreaUpdateRequest
)

from app.responses.jsend import fail_response, success_response

router = APIRouter()

#
# GET: /admin/delivery/areas
#
@router.get(
        '/admin/delivery/areas',
        status_code=status.HTTP_200_OK,
        response_model=JSendSuccessResponse
)
def get_delivery_areas(
    active: bool | None = None,
    limit: int = 10,
    offset: int = 0,
    _: UUID = Depends(get_current_admin_id),
    service: DeliveryAreaService = Depends(
        get_delivery_area_service
    )
) -> JSendSuccessResponse:
    """
    Retorna as áreas de entrega cadastradas.

    Args:
        active: Filtra as áreas pelo status ativo ou inativo.
        limit: Quantidade máxima de registros retornados.
        offset: Quantidade de registros ignorados antes do retorno.
        _: Identificador do administrador autenticado.
        service: Serviço responsável pelas regras de negócio das áreas de entrega.

    Returns:
        Resposta contendo as áreas de entrega encontradas.
    """

    # Consulta as áreas de entrega utilizando os filtros e parâmetros
    # de paginação informados pela interface administrativa.
    delivery_areas = service.get_all(
        active=active,
        limit=limit,
        offset=offset
    )

    # Converte os models de domínio para o schema utilizado na resposta da API.
    return success_response({
        'delivery_areas': [
            DeliveryAreaResponse.from_model(
                delivery_area
            ).model_dump(mode='json')
            for delivery_area in delivery_areas
        ]
    })

#
# GET: /admin/delivery/areas/{delivery_area_id}
#
@router.get(
        '/admin/delivery/areas/{delivery_area_id}',
        status_code=status.HTTP_200_OK,
        response_model=JSendSuccessResponse
)
def get_delivery_area(
    delivery_area_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: DeliveryAreaService = Depends(
        get_delivery_area_service
    )
) -> JSendSuccessResponse | JSONResponse:
    """
    Retorna uma área de entrega pelo identificador.

    Args:
        delivery_area_id: Identificador da área de entrega.
        _: Identificador do administrador autenticado.
        service: Serviço responsável pelas regras de negócio das áreas de entrega.

    Returns:
        Resposta contendo a área de entrega encontrada.
    """
    # Consulta a área de entrega pelo identificador informado.
    delivery_area = service.get_by_id(
        delivery_area_id
    )

    if not delivery_area:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'DELIVERY_AREA_NOT_FOUND',
            'Delivery area not found.'
        )

    # Converte o model de domínio para o schema utilizado na resposta da API.
    return success_response({
        'delivery_area': DeliveryAreaResponse.from_model(
            delivery_area
        ).model_dump(mode='json')
    })

#
# POST: /admin/delivery/areas
#
@router.post(
        '/admin/delivery/areas',
    status_code=status.HTTP_201_CREATED,
    response_model=JSendSuccessResponse
)
def create_delivery_area(
        payload: DeliveryAreaCreateRequest,
        _: UUID = Depends(get_current_admin_id),
        service: DeliveryAreaService = Depends(
            get_delivery_area_service
        )
) -> JSendSuccessResponse:
    """
    Cria uma nova área de entrega.

    Args:
        payload: Dados utilizados para criar a área de entrega.
        _: Identificador do administrador autenticado.
        service: Serviço responsável pelas regras de negócio das áreas de entrega.

    Returns:
        Resposta contendo a área de entrega criada.
    """

    # Cria a nova área de entrega utilizando as regras de negócio
    # definidas na camada de serviço.
    delivery_area = service.create(
        payload
    )

    # Converte o model de domínio para o schema utilizado na resposta da API.
    return success_response({
        'delivery_area': DeliveryAreaResponse.from_model(
            delivery_area
        ).model_dump(mode='json')
    })

#
# PUT: /admin/delivery/areas/{delivery_area_id}
#
@router.put(
        '/admin/delivery/areas/{delivery_area_id}',
        status_code=status.HTTP_200_OK,
        response_model=JSendSuccessResponse
)
def update_delivery_area(
    delivery_area_id: UUID,
    payload: DeliveryAreaUpdateRequest,
    _: UUID = Depends(get_current_admin_id),
    service: DeliveryAreaService = Depends(
        get_delivery_area_service
    )
) -> JSendSuccessResponse | JSONResponse:
    """
    Atualiza uma área de entrega existente.

    Args:
        delivery_area_id: Identificador da área de entrega.
        payload: Dados utilizados para atualizar a área de entrega.
        _: Identificador do administrador autenticado.
        service: Serviço responsável pelas regras de negócio das áreas de entrega.

    Returns:
        Resposta contendo a área de entrega atualizada.
    """

    try:
        # Atualiza a área de entrega utilizando as regras de negócio
        # definidas na camada de serviço.
        delivery_area = service.update(
            delivery_area_id,
            payload
        )
    except ValueError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'DELIVERY_AREA_NOT_FOUND',
            'Delivery area not found.'
        )
    
    # Converte o model de domínio para o schema utilizado na resposta da API.
    return success_response({
        'delivery_area': DeliveryAreaResponse.from_model(
            delivery_area
        ).model_dump(mode='json')
    })

#
# DELETE: /admin/delivery/areas/{delivery_area_id}
#
@router.delete(
        '/admin/delivery/areas/{delivery_area_id}',
        status_code=status.HTTP_200_OK,
        response_model=JSendSuccessResponse
)
def delete_delivery_area(
    delivery_area_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: DeliveryAreaService = Depends(
        get_delivery_area_service
    )
) -> JSendSuccessResponse | JSONResponse:
    """
    Remove uma área de entrega pelo identificador.

    Args:
        delivery_area_id: Identificador da área de entrega.
        _: Identificador do administrador autenticado.
        service: Serviço responsável pelas regras de negócio das áreas de entrega.

    Returns:
        Resposta indicando que a área de entrega foi removida com sucesso.
    """

    try:
        # Remove a área de entrega utilizando as regras de negócio
        # definidas na camada de serviço.
        service.delete(
            delivery_area_id
        )
    except ValueError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'DELIVERY_AREA_NOT_FOUND',
            'Delivery area not found.'
        )

    return success_response({
        'message': 'Delivery area deleted successfully.'
    })

#
# PATCH: /admin/delivery/areas/{delivery_area_id}/active
#
@router.patch(
        '/admin/delivery/areas/{delivery_area_id}/active',
        status_code=status.HTTP_200_OK,
        response_model=JSendSuccessResponse
)
def update_delivery_area_active(
    delivery_area_id: UUID,
    active: bool,
    _: UUID = Depends(get_current_admin_id),
    service: DeliveryAreaService = Depends(
        get_delivery_area_service
    )
) -> JSendSuccessResponse | JSONResponse:
    """
    Altera o status de uma área de entrega.

    Args:
        delivery_area_id: Identificador da área de entrega.
        active: Indica se a área de entrega deve permanecer ativa.
        _: Identificador do administrador autenticado.
        service: Serviço responsável pelas regras de negócio das áreas de entrega.

    Returns:
        Resposta contendo a área de entrega com o status atualizado.
    """

    try:
        # Altera somente o status da área de entrega, preservando
        # os demais dados cadastrados.
        delivery_area = service.set_active(
            delivery_area_id,
            active
        )
    except ValueError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'DELIVERY_AREA_NOT_FOUND',
            'Delivery area not found.'
        )

    # Converte o model de domínio para o schema utilizado na resposta da API.
    return success_response({
        'delivery_area': DeliveryAreaResponse.from_model(
            delivery_area
        ).model_dump(mode='json')
    })