#
# services/pizza_service.py
#

from uuid import UUID
from uuid import uuid4

from fastapi import Depends

from app.exceptions.pizza_exception import (
    PizzaCreationError,
    PizzaDeletionError,
    PizzaNotFoundError,
    PizzaQueryError,
    PizzaUpdateError
)

from app.models.pizza import Pizza

from app.repositories.pizza_repository import PizzaRepository
from app.dependencies.database import get_pizza_repository

from app.dependencies.database import UnitOfWork, get_unit_of_work

from app.schemas.pizza_schema import (
    PizzaCategory,
    PizzaCreateRequest,
    PizzaUpdateRequest
)

from app.services.objectstorage_service import (
    ObjectStorageService, 
    get_objectstorage_service
)

from app.utils.utils import now_utc


class PizzaService:
    """
    Serviço responsável pelos casos de uso relacionados às pizzas.

    Esta camada concentra as regras de negócio utilizadas para criação,
    consulta, atualização e remoção das pizzas.

    O serviço não possui conhecimento sobre a tecnologia utilizada
    para persistência dos dados. O acesso aos dados é realizado através
    da abstração `PizzaRepository`.
    """

    def __init__(self, 
                 pizza_repository: PizzaRepository,
                 unit_of_work: UnitOfWork,
                 objectstorage_service: ObjectStorageService) -> None:
        """
        Inicializa o serviço responsável pelos casos de uso
        relacionados às pizzas.

        Args:
            pizza_repository: Repositório utilizado para persistir
                e consultar os dados das pizzas.

        Returns:
            None.
        """

        self.pizza_repository = pizza_repository
        self.unit_of_work = unit_of_work
        self.objectstorage_service = objectstorage_service

    def get_all(self,
                    category: PizzaCategory | None = None,
                    available: bool | None = None,
                    limit: int = 10,
                    offset: int = 0) -> list[tuple[Pizza, str]]:
        """
        Retorna as pizzas cadastradas de acordo com os filtros informados.

        Args:
            category: Categoria utilizada para filtrar as pizzas.
            available: Filtra pizzas de acordo com sua disponibilidade.
            limit: Quantidade máxima de pizzas retornadas.
            offset: Quantidade de registros ignorados antes do retorno.

        Returns:
            Lista contendo as pizzas encontradas.

        Raises:
            PizzaQueryError: Caso ocorra uma falha durante a consulta
                das pizzas.
        """

        try:
            pizzas = self.pizza_repository.get_all(
                category=category,
                available=available,
                limit=limit,
                offset=offset
            )

            return [
                (
                    pizza,
                    self.objectstorage_service.get_object_url(
                        pizza.image_name
                    )
                )
                for pizza in pizzas
            ]
        except Exception as ex:
            raise PizzaQueryError('Error retrieving pizzas.') from ex

    def get_by_id(self, pizza_id: UUID) -> tuple[Pizza, str]:
        """
        Retorna uma pizza através de seu identificador.

        Args:
            pizza_id: Identificador UUID da pizza.

        Returns:
            Pizza encontrada.

        Raises:
            PizzaNotFoundError: Caso a pizza não seja encontrada.
            PizzaQueryError: Caso ocorra uma falha durante a consulta.
        """

        try:
            pizza = self.pizza_repository.get_by_id(pizza_id)
        except Exception as ex:
            raise PizzaQueryError(
                'Error retrieving pizza.'
            ) from ex

        if pizza is None:
            raise PizzaNotFoundError('Pizza not found.')

        image_url = self.object_storage_service.get_object_url(
            pizza.image_name
        )

        return pizza, image_url

    def create(self, payload: PizzaCreateRequest) -> tuple[Pizza, str]:
        """
        Cria uma nova pizza.

        Args:
            payload: Dados necessários para criação da pizza.

        Returns:
            Pizza criada.

        Raises:
            PizzaCreationError: Caso ocorra uma falha durante
                a criação da pizza.
        """

        now = now_utc()

        # Cria o modelo da aplicação a partir dos dados recebidos
        # pela camada HTTP.
        pizza = Pizza(
            id=uuid4(),
            name=payload.name,
            description=payload.description,
            category=payload.category,
            price=payload.price,
            image_name=payload.image_name,
            available=payload.available,
            created_at=now,
            updated_at=now
        )

        try:
            pizza = self.pizza_repository.create(pizza)
            self.unit_of_work.commit()
        except Exception as exc:
            self.unit_of_work.rollback()
            raise PizzaCreationError('Failed to create pizza.') from exc

        # A URL da imagem é derivada somente após a persistência.
        # Ela não é armazenada junto com a pizza.
        image_url = self.object_storage_service.get_object_url(
            pizza.image_name
        )

        return pizza, image_url

    def update(self, 
               pizza_id: UUID, 
               payload: PizzaUpdateRequest) -> tuple[Pizza, str]:
        """
        Atualiza os dados de uma pizza.

        Somente os campos informados na requisição são alterados.
        Os demais valores permanecem inalterados.

        Args:
            pizza_id: Identificador UUID da pizza que será atualizada.
            payload: Dados permitidos para atualização da pizza.

        Returns:
            Pizza atualizada.

        Raises:
            PizzaNotFoundError: Caso a pizza não seja encontrada.
            PizzaUpdateError: Caso ocorra uma falha durante
                a atualização da pizza.
        """

        try:
            pizza = self.pizza_repository.get_by_id(pizza_id)
        except Exception as exc:
            # Converte falhas técnicas da consulta em uma exceção
            # específica do caso de uso de atualização.
            raise PizzaUpdateError(
                'Failed to query pizza for update.'
            ) from exc

        # Interrompe a operação caso a pizza não exista.
        if pizza is None:
            raise PizzaNotFoundError()

        # Obtém somente os campos efetivamente enviados na requisição.
        update_data = payload.model_dump(exclude_unset=True)

        # Atualiza dinamicamente apenas os atributos enviados.
        for field, value in update_data.items():
            setattr(pizza, field, value)

        # Registra a data da última modificação.
        pizza.updated_at = now_utc()

        try:
            pizza = self.pizza_repository.update(pizza)
            self.unit_of_work.commit()
        except Exception as ex:
            self.unit_of_work.rollback()
            # Converte falhas técnicas da persistência em uma exceção
            # específica do caso de uso de atualização.
            raise PizzaUpdateError('Failed to update pizza.') from ex

        # Constrói a URL completa da imagem somente após a persistência
        # ter sido concluída com sucesso.
        image_url = self.objectstorage_service.get_object_url(
            pizza.image_name
        )

        return pizza, image_url

    def delete(self, pizza_id: UUID) -> None:
        """
        Remove uma pizza.

        Args:
            pizza_id: Identificador UUID da pizza que será removida.

        Returns:
            None.

        Raises:
            PizzaNotFoundError: Caso a pizza não seja encontrada.
            PizzaDeletionError: Caso ocorra uma falha durante
                a remoção da pizza.
        """

        try:
            pizza = self.pizza_repository.get_by_id(pizza_id)
        except Exception as ex:
            raise PizzaDeletionError(
                'Error retrieving pizza for deletion.'
            ) from ex

        # Interrompe a operação caso a pizza não exista.
        if pizza is None:
            raise PizzaNotFoundError('Pizza not found.')

        try:
            self.pizza_repository.delete(pizza_id)
            self.unit_of_work.commit()
        except Exception as ex:
            self.unit_of_work.rollback()
            raise PizzaDeletionError('Error deleting pizza.') from ex


def get_pizza_service(
        pizza_repository: PizzaRepository = Depends(
            get_pizza_repository
        ),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
        objectstorage_service: ObjectStorageService = Depends(
            get_objectstorage_service
        )
) -> PizzaService:
    """
    Fornece o serviço responsável pelos casos de uso relacionados
    às pizzas.

    Args:
        pizza_repository: Repositório utilizado para persistir
            e consultar os dados das pizzas.

    Returns:
        Instância de `PizzaService`.
    """

    return PizzaService(
        pizza_repository=pizza_repository,
        unit_of_work=unit_of_work,
        objectstorage_service=objectstorage_service
    )