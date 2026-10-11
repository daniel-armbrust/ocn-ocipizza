#
# schemas/delivery_area_schema.py
#

from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.delivery_area import DeliveryArea


class DeliveryAreaCreateRequest(BaseModel):
    """
    Representa os dados necessários para criação de uma área de entrega.

    Attributes:
        name: Nome utilizado para identificar a área de entrega.
        zip_code_start: CEP inicial da faixa atendida.
        zip_code_end: CEP final da faixa atendida.
        delivery_fee: Valor da taxa de entrega.
        estimated_minutes: Tempo estimado de entrega em minutos.
        active: Indica se a área de entrega está ativa.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=100)
    zip_code_start: str = Field(..., min_length=8, max_length=9)
    zip_code_end: str = Field(..., min_length=8, max_length=9)
    delivery_fee: Decimal = Field(..., ge=0)
    estimated_minutes: int = Field(..., ge=1)
    active: bool = True


class DeliveryAreaUpdateRequest(BaseModel): 
    """
    Representa os dados permitidos para atualização de uma área de entrega. 
    
    Attributes: 
        name: Nome utilizado para identificar a área de entrega. 
        zip_code_start: CEP inicial da faixa atendida. 
        zip_code_end: CEP final da faixa atendida. 
        delivery_fee: Valor da taxa de entrega. 
        estimated_minutes: Tempo estimado de entrega em minutos. 
        active: Indica se a área de entrega está ativa.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True) 
    
    name: str | None = Field(default=None, min_length=1, max_length=100) 
    zip_code_start: str | None = Field(default=None, min_length=8, max_length=9) 
    zip_code_end: str | None = Field(default=None, min_length=8, max_length=9) 
    delivery_fee: Decimal | None = Field(default=None, ge=0) 
    estimated_minutes: int | None = Field(default=None, ge=1) 
    active: bool | None = None


class DeliveryAreaResponse(BaseModel): 
    """
    Representa os dados de uma área de entrega retornados pela API. 
    
    Attributes: 
        id: Identificador único da área de entrega. 
        name: Nome utilizado para identificar a área de entrega. 
        zip_code_start: CEP inicial da faixa atendida. 
        zip_code_end: CEP final da faixa atendida. 
        delivery_fee: Valor da taxa de entrega. 
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
    
    @classmethod 
    def from_model(cls, delivery_area: DeliveryArea) -> 'DeliveryAreaResponse': 
        """
        Converte um model de domínio em um schema de resposta. 

        Args: 
            delivery_area: Área de entrega que será convertida. 
                
        Returns: 
            Schema contendo os dados da área de entrega. 
        """ 
        
        return cls(
            id=delivery_area.id, 
            name=delivery_area.name, 
            zip_code_start=delivery_area.zip_code_start, 
            zip_code_end=delivery_area.zip_code_end, 
            delivery_fee=delivery_area.delivery_fee, 
            estimated_minutes=delivery_area.estimated_minutes, 
            active=delivery_area.active, 
            created_at=delivery_area.created_at, 
            updated_at=delivery_area.updated_at
        )