#
# repositories/delivery_area_repository.py
#

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.delivery_area import DeliveryArea


class DeliveryAreaRepository(ABC):
    """
    Define o contrato de persistência para as áreas de entrega.
    """

    @abstractmethod
    def create(self, delivery_area: DeliveryArea) -> DeliveryArea:
        """
        Cria uma nova área de entrega.

        Args:
            delivery_area: Área de entrega que será persistida.

        Returns:
            A área de entrega criada.
        """
        pass

    @abstractmethod
    def get_by_id(self, delivery_area_id: UUID) -> DeliveryArea | None:
        """
        Busca uma área de entrega pelo identificador.

        Args:
            delivery_area_id: Identificador UUID da área de entrega.

        Returns:
            A área de entrega encontrada ou None caso não exista.
        """
        pass

    @abstractmethod
    def get_by_zip_code(self, zip_code: str) -> DeliveryArea | None:
        """
        Busca uma área de entrega que contemple o CEP informado.

        Args:
            zip_code: CEP utilizado para localizar a área de entrega.

        Returns:
            A área de entrega correspondente ao CEP ou None caso
            nenhuma área esteja disponível.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def update(self, delivery_area: DeliveryArea) -> DeliveryArea:
        """
        Atualiza uma área de entrega existente.

        Args:
            delivery_area: Área de entrega com os dados atualizados.

        Returns:
            A área de entrega atualizada.
        """
        pass

    @abstractmethod
    def delete(self, delivery_area_id: UUID) -> None:
        """
        Remove uma área de entrega.

        Args:
            delivery_area_id: Identificador UUID da área de entrega.
        """
        pass