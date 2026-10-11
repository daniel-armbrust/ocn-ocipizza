#
# routes/delivery_area_routes.py
#

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.authentication import get_current_user_id

from app.services.delivery_area_service import (
    DeliveryAreaService,
    get_delivery_area_service
)

from app.schemas.jsend_schema import JSendSuccessResponse
from app.responses.jsend import success_response

router = APIRouter()

#
# GET: /delivery/quote/{zip_code}
#
@router.get(
    '/delivery/quote/{zip_code}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_delivery_quote(
    zip_code: str,
    _: UUID = Depends(get_current_user_id),
    service: DeliveryAreaService = Depends(
        get_delivery_area_service
    )
) -> JSendSuccessResponse | JSONResponse:
    """
    Consulta a disponibilidade e a cotação de entrega para um CEP.

    Args:
        zip_code: CEP utilizado para consultar a disponibilidade da entrega.
        _: Identificador do usuário autenticado.
        service: Serviço responsável pelas regras de negócio das áreas
            de entrega.

    Returns:
        Resposta contendo a disponibilidade, taxa e prazo estimado
        da entrega.
    """

    # Consulta a área de entrega correspondente ao CEP informado.
    delivery_area = service.get_by_zip_code(zip_code)

    if not delivery_area:
        return success_response({
            'available': False,
            'delivery_fee': None,
            'estimated_minutes': None
        })

    # Retorna apenas as informações necessárias para a cotação,
    # sem expor as faixas de CEP utilizadas internamente pelo serviço.
    return success_response({
        'available': True,
        'delivery_fee': str(delivery_area.delivery_fee),
        'estimated_minutes': delivery_area.estimated_minutes
    })