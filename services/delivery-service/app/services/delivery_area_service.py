#
# services/delivery_area_service.py
#

from uuid import UUID, uuid4
from decimal import Decimal

from fastapi import Depends

from app.repositories.unit_of_work import UnitOfWork
from app.dependencies.database import get_unit_of_work

from app.repositories.delivery_area_repository import DeliveryAreaRepository
from app.dependencies.database import get_delivery_area_repository

from app.schemas.delivery_area_schema import (
    DeliveryAreaCreateRequest, 
    DeliveryAreaUpdateRequest
)

from app.models.delivery_area import DeliveryArea

from app.utils.utils import now_utc, normalize_zip_code


class DeliveryAreaService: 
    """ 
    Implementa as regras de negócio relacionadas às áreas de entrega. 
    """ 
    
    def __init__(self, 
                 delivery_area_repository: DeliveryAreaRepository, 
                 unit_of_work: UnitOfWork): 
        """ Inicializa o serviço de áreas de entrega. 
        
        Args: 
            delivery_area_repository: Repositório utilizado para 
                acessar e persistir as áreas de entrega. 
            unit_of_work: Unidade de trabalho responsável pelo 
                controle das transações. 
        """ 
        
        self.delivery_area_repository = delivery_area_repository
        self.unit_of_work = unit_of_work 
        
    def get_by_zip_code(self, zip_code: str) -> DeliveryArea | None: 
        """
        Busca uma área de entrega ativa correspondente ao CEP 
        informado. 
        
        Args: 
            zip_code: CEP utilizado para localizar uma área de entrega. 
        
        Returns: 
            Área de entrega correspondente ao CEP ou None caso nenhuma 
            área esteja disponível. 
        
        Raises: 
            ValueError: Quando o CEP informado possui formato inválido. 
        """ 
        
        normalized_zip_code = normalize_zip_code(zip_code) 
        
        # Consulta uma área ativa cuja faixa contemple o CEP informado. 
        return self.delivery_area_repository.get_by_zip_code(normalized_zip_code) 
    
    def get_by_id(self, delivery_area_id: UUID) -> DeliveryArea | None: 
        """ 
        Busca uma área de entrega pelo identificador. 
        
        Args: 
            delivery_area_id: Identificador da área de entrega. 
            
        Returns: 
            Área de entrega encontrada ou None caso não exista. 
        """ 
        
        return self.delivery_area_repository.get_by_id(delivery_area_id) 
    
    def get_all(self, 
                active: bool | None = None, 
                limit: int = 10, 
                offset: int = 0) -> list[DeliveryArea]: 
        """
        Retorna as áreas de entrega cadastradas. 
        
        Args: 
            active: Filtra as áreas pelo status ativo ou inativo. 
            limit: Quantidade máxima de registros retornados. 
            offset: Quantidade de registros ignorados antes do retorno. 
        
        Returns:
            Lista contendo as áreas de entrega encontradas.
        """
        
        return self.delivery_area_repository.get_all(
            active=active, 
            limit=limit, 
            offset=offset
        ) 
        
    def create(self, payload: DeliveryAreaCreateRequest) -> DeliveryArea: 
        """
        Cria uma nova área de entrega. 
        
        Args: 
            payload: Dados utilizados para criar a área de entrega. 
        
        Returns: 
            Área de entrega criada. 
            
        Raises: 
            ValueError: Quando a faixa de CEP informada é inválida. 
            Exception: Quando ocorre erro durante a persistência.
        """ 
        
        # Normaliza os CEPs antes de validar a faixa e persistir os dados. 
        zip_code_start = self._normalize_zip_code(payload.zip_code_start) 
        zip_code_end = self._normalize_zip_code(payload.zip_code_end) 
        
        # O CEP inicial não pode ser maior que o CEP final da área. 
        if zip_code_start > zip_code_end: 
            raise ValueError('Invalid zip code range.') 
        
        now = now_utc() 
        
        # O identificador e os timestamps são definidos pelo próprio serviço. 
        delivery_area = DeliveryArea(
            id=uuid4(), 
            name=payload.name, 
            zip_code_start=zip_code_start, 
            zip_code_end=zip_code_end, 
            delivery_fee=Decimal(str(payload.delivery_fee)), 
            estimated_minutes=payload.estimated_minutes, 
            active=payload.active, 
            created_at=now, 
            updated_at=now
        ) 
        
        try: 
            delivery_area = self.delivery_area_repository.create(delivery_area) 
            self.unit_of_work.commit() 
            
            return delivery_area 
        except Exception: 
            self.unit_of_work.rollback() 
            raise 
    
    def update(self,
               delivery_area_id: UUID,
               payload: DeliveryAreaUpdateRequest) -> DeliveryArea:
        """ 
        Atualiza uma área de entrega existente. 
         
        Args: 
            delivery_area_id: Identificador da área de entrega. 
            payload: Dados utilizados para atualizar a área de entrega. 
        
        Returns: 
            Área de entrega atualizada. 
        
        Raises: 
            ValueError: Quando a área não existe ou a faixa de CEP 
                é inválida. 
            Exception: Quando ocorre erro durante a persistência. 
        """ 

        # Recupera a área atual antes de aplicar as alterações recebidas.
        delivery_area = self.delivery_area_repository.get_by_id(delivery_area_id)
          
        if not delivery_area:
            raise ValueError('Delivery area not found.') 
    
        # Considera somente os campos enviados explicitamente na requisição. 
        data = payload.model_dump(exclude_unset=True) 
        
        zip_code_start = delivery_area.zip_code_start 
        zip_code_end = delivery_area.zip_code_end 
    
        if 'zip_code_start' in data: 
            zip_code_start = self._normalize_zip_code(data['zip_code_start']) 
        
        if 'zip_code_end' in data: 
            zip_code_end = self._normalize_zip_code(data['zip_code_end']) 
            
        # Valida novamente a faixa após combinar os valores atuais e novos. 
        if zip_code_start > zip_code_end: 
            raise ValueError('Invalid zip code range.') 
        
        updated_delivery_area = DeliveryArea(
            id=delivery_area.id, 
            name=data.get('name', delivery_area.name), 
            zip_code_start=zip_code_start, 
            zip_code_end=zip_code_end, 
            delivery_fee=Decimal(str(data.get('delivery_fee', delivery_area.delivery_fee))), 
            estimated_minutes=data.get('estimated_minutes', delivery_area.stimated_minutes),
            active=data.get('active', delivery_area.active), 
            created_at=delivery_area.created_at, 
            updated_at=now_utc()
        ) 
    
        try: 
            # Substitui o registro existente pelos dados atualizados. 
            updated_delivery_area = self.delivery_area_repository.update(
                updated_delivery_area 
            ) 
            
            self.unit_of_work.commit() 
            
            return updated_delivery_area 
        except Exception: 
            self.unit_of_work.rollback() 
            raise
    
    def delete(self, delivery_area_id: UUID) -> None: 
        """
        Remove uma área de entrega. 
        
        Args: 
            delivery_area_id: Identificador da área de entrega. 
        
        Raises: 
            ValueError: Quando a área de entrega não existe. 
            Exception: Quando ocorre erro durante a persistência.
        """ 
        
        # Verifica se a área existe antes de solicitar sua remoção. 
        delivery_area = self.delivery_area_repository.get_by_id(delivery_area_id) 
        
        if not delivery_area: 
            raise ValueError('Delivery area not found.') 
        
        try: 
            # Remove a área de entrega utilizando sua chave primária. 
            self.delivery_area_repository.delete(delivery_area_id) 
            self.unit_of_work.commit() 
        except Exception:
            self.unit_of_work.rollback() 
            raise 
        
    def set_active(self, delivery_area_id: UUID, active: bool) -> DeliveryArea: 
        """
        Altera o status de uma área de entrega. 
        
        Args: 
            delivery_area_id: Identificador da área de entrega. 
            active: Indica se a área deve permanecer ativa. 
        
        Returns: 
            Área de entrega com o status atualizado. 
        
        Raises: 
            ValueError: Quando a área de entrega não existe. 
            Exception: Quando ocorre erro durante a persistência. 
        """
        
        # Recupera a área antes de alterar seu status. 
        delivery_area = self.delivery_area_repository.get_by_id(delivery_area_id) 
        
        if not delivery_area: 
            raise ValueError('Delivery area not found.') 
        
        # Preserva os demais dados e altera somente o status e a data de atualização
        updated_delivery_area = delivery_area.model_copy(
            update={
                'active': active, 
                'updated_at': now_utc() 
            }
        ) 
        
        try:
            updated_delivery_area = self.delivery_area_repository.update(updated_delivery_area)
            self.unit_of_work.commit() 
            
            return updated_delivery_area 
        except Exception:
            self.unit_of_work.rollback() 
            raise


def get_delivery_area_service(
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
        delivery_area_repository: DeliveryAreaRepository = Depends(
            get_delivery_area_repository
        )
) -> DeliveryAreaService:
    """
    Obtém o serviço responsável pelas regras de negócio das áreas de entrega. 
    
    Args: 
        delivery_area_repository: Repositório utilizado para acessar e 
            persistir as áreas de entrega. 
        unit_of_work: Unidade de trabalho responsável pelo controle 
            das transações. 
    
    Returns: 
        Serviço responsável pelas operações relacionadas às áreas 
            de entrega. 
    """
    
    return DeliveryAreaService(
        delivery_area_repository=delivery_area_repository, 
        unit_of_work=unit_of_work
    )