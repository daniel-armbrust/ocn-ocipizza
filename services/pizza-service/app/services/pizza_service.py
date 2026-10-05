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

        image_url = self.objectstorage_service.get_object_url(
            pizza.image_name
        )

        return pizza, image_url

    def create(self,
               payload: PizzaCreateRequest,
               image_data: bytes,
               content_type: str) -> tuple[Pizza, str]:
        """
        Cria uma nova pizza e armazena sua respectiva imagem.

        Args:
            payload: Dados utilizados para criação da pizza.
            image_data: Conteúdo binário da imagem da pizza.
            content_type: Tipo MIME da imagem.

        Returns:
            Pizza criada e a respectiva URL de imagem.

        Raises:
            PizzaCreationError: Caso ocorra uma falha durante a criação
                da pizza.
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
        except Exception as ex:
            self.unit_of_work.rollback()
            raise PizzaCreationError('Failed to create pizza.') from ex

        try:
            # Envia a imagem para o Object Storage somente após a
            # persistência da pizza ter sido confirmada.
            self.objectstorage_service.upload_object(
                object_name=pizza.image_name,
                data=image_data,
                content_type=content_type
            )
        except Exception as ex:
            # TODO: Implementar tratamento de inconsistência entre a criação
            # da pizza e o upload da imagem no Object Storage, incluindo
            # compensação, retry ou processamento assíncrono.
            raise PizzaCreationError(
                'Pizza created, but failed to upload image.'
            ) from ex

        # Obtém a URL correspondente ao objeto armazenado.
        image_url = self.objectstorage_service.get_object_url(
            pizza.image_name
        )

        return pizza, image_url

    def update(self,
               pizza_id: UUID,
               payload: PizzaUpdateRequest,
               image_data: bytes | None = None,
               content_type: str | None = None) -> tuple[Pizza, str]:
        """
        Atualiza os dados de uma pizza e, quando informado,
        substitui sua imagem.

        Args:
            pizza_id: Identificador da pizza.
            payload: Dados utilizados para atualização da pizza.
            image_data: Conteúdo binário da nova imagem.
            content_type: Tipo MIME da nova imagem.

        Returns:
            Pizza atualizada e a respectiva URL de imagem.

        Raises:
            PizzaNotFoundError: Caso a pizza não seja encontrada.
            PizzaUpdateError: Caso ocorra uma falha durante a atualização.
        """

        try:
            # Consulta a pizza atualmente persistida.
            pizza = self.pizza_repository.get_by_id(pizza_id)

            if pizza is None:
                raise PizzaNotFoundError()

            # Mantém o nome da imagem atual para permitir sua remoção
            # caso uma nova imagem seja enviada.
            previous_image_name = pizza.image_name

            # Obtém somente os campos efetivamente enviados.
            update_data = payload.model_dump(exclude_unset=True)

            # Atualiza apenas os atributos informados na requisição.
            for field, value in update_data.items():
                setattr(pizza, field, value)

            pizza.updated_at = now_utc()

            # Persiste as alterações.
            pizza = self.pizza_repository.update(pizza)

            self.unit_of_work.commit()
        except PizzaNotFoundError:
            self.unit_of_work.rollback()
            raise
        except Exception as ex:
            self.unit_of_work.rollback()
            raise PizzaUpdateError('Failed to update pizza.') from ex

        # Quando uma nova imagem é enviada, realiza o upload após
        # a atualização da pizza ter sido confirmada.
        if image_data is not None:
            try:
                if not content_type:
                    raise ValueError(
                        'Content type is required when image data is provided.'
                    )

                self.objectstorage_service.upload_object(
                    object_name=pizza.image_name,
                    data=image_data,
                    content_type=content_type
                )

                # Remove a imagem anterior somente quando o nome do objeto
                # tiver sido alterado.
                if previous_image_name != pizza.image_name:
                    self.objectstorage_service.delete_object(
                        previous_image_name
                    )
            except Exception as ex:
                # TODO: Implementar tratamento de inconsistência entre a
                # atualização da pizza e as operações no Object Storage,
                # incluindo compensação, retry ou processamento assíncrono.
                raise PizzaUpdateError(
                    'Pizza updated, but failed to update image.'
                ) from ex

        # A URL é calculada a partir do nome da imagem atualmente
        # associado à pizza.
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

        try:
            self.objectstorage_service.delete_object(pizza.image_name)
        except Exception as ex:
            # TODO: Implementar tratamento de inconsistência entre a
            # exclusão da pizza e a remoção da imagem no Object Storage,
            # incluindo retry ou processamento assíncrono.
            raise PizzaDeletionError(
                'Pizza deleted, but failed to delete image.'
            ) from ex


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
