#
# models/delivery_area.py
#

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class DeliveryArea(BaseModel):
    """
    Representa uma área de entrega atendida pelo delivery-service.

    Attributes:
        id: Identificador único da área de entrega.
        name: Nome utilizado para identificar a área de entrega.
        zip_code_start: CEP inicial da faixa atendida.
        zip_code_end: CEP final da faixa atendida.
        delivery_fee: Valor da taxa de entrega para a área.
        estimated_minutes: Tempo estimado de entrega em minutos.
        active: Indica se a área de entrega está ativa.
        created_at: Data e hora de criação da área de entrega em UTC.
        updated_at: Data e hora da última atualização da área de entrega em UTC.
    """

    id: UUID
    name: str
    zip_code_start: str
    zip_code_end: str
    delivery_fee: Decimal
    estimated_minutes: int
    active: bool
    created_at: datetime
    updated_at: datetime