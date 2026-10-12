#
# schemas/delivery_area_schema.py
#

from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.delivery_area import DeliveryArea
from app.utils.utils import normalize_zip_code


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
    zip_code_start: str = Field(..., pattern=r'^\d{8}$')
    zip_code_end: str = Field(..., pattern=r'^\d{8}$')
    delivery_fee: Decimal = Field(..., ge=0)
    estimated_minutes: int = Field(..., ge=1)
    active: bool = True

    @field_validator('zip_code_start', 'zip_code_end', mode='before')
    @classmethod
    def validate_zip_code(cls, value: str) -> str:
        """
        Normaliza os limites da faixa antes da validação do contrato.

        Args:
            value: CEP recebido com ou sem máscara.

        Returns:
            CEP contendo somente oito dígitos.

        Raises:
            ValueError: Quando o CEP informado for inválido.
        """

        return normalize_zip_code(value)


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
    zip_code_start: str | None = Field(default=None, pattern=r'^\d{8}$')
    zip_code_end: str | None = Field(default=None, pattern=r'^\d{8}$')
    delivery_fee: Decimal | None = Field(default=None, ge=0) 
    estimated_minutes: int | None = Field(default=None, ge=1) 
    active: bool | None = None

    @field_validator('zip_code_start', 'zip_code_end', mode='before')
    @classmethod
    def validate_zip_code(cls, value: str | None) -> str | None:
        """
        Normaliza os limites opcionais antes da validação do contrato.

        Args:
            value: CEP recebido com ou sem máscara.

        Returns:
            CEP contendo somente oito dígitos ou `None` quando ausente.

        Raises:
            ValueError: Quando o CEP informado for inválido.
        """

        return normalize_zip_code(value) if value is not None else None


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
    zip_code_start: str = Field(pattern=r'^\d{8}$')
    zip_code_end: str = Field(pattern=r'^\d{8}$')
    delivery_fee: Decimal 
    estimated_minutes: int 
    active: bool 
    created_at: datetime 
    updated_at: datetime 

    @field_validator('zip_code_start', 'zip_code_end', mode='before')
    @classmethod
    def validate_zip_code(cls, value: str) -> str:
        """
        Normaliza os limites recuperados antes de montar a resposta.

        Args:
            value: CEP recuperado da persistência.

        Returns:
            CEP contendo somente oito dígitos.

        Raises:
            ValueError: Quando o CEP persistido for inválido.
        """

        return normalize_zip_code(value)
    
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
