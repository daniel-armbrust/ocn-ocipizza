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
                offset: int = 0) -> list[Pizza]:
        """
        Retorna as pizzas cadastradas de acordo com os filtros informados.

        Args:
            category: Categoria utilizada para filtrar as pizzas.
            available: Indica se o resultado deve ser filtrado
                pela disponibilidade.
            limit: Quantidade máxima de pizzas retornadas.
            offset: Quantidade de registros ignorados antes do retorno.

        Returns:
            Lista de pizzas encontradas.
        """

        return self.pizza_repository.get_all(
            category=category,
            available=available,
            limit=limit,
            offset=offset
        )

    def get_by_id(self, pizza_id: UUID) -> Pizza:
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
            raise PizzaQueryError('Error retrieving pizza.') from ex

        if pizza is None:
            raise PizzaNotFoundError('Pizza not found.')

        return pizza

    def get_image(self, pizza_id: UUID) -> tuple[bytes, str]:
        """
        Retorna a imagem associada à pizza informada.

        Args:
            pizza_id: Identificador UUID da pizza.

        Returns:
            Conteúdo binário da imagem e seu tipo MIME.

        Raises:
            PizzaNotFoundError: Caso a pizza não seja encontrada.
            PizzaQueryError: Caso ocorra uma falha durante a consulta.
        """

        pizza = self.get_by_id(pizza_id)

        return self.objectstorage_service.get_object(
            pizza.image_name
        )

    def create(self,
               payload: PizzaCreateRequest,
               image_data: bytes,
               content_type: str) -> Pizza:
        """
        Cria uma nova pizza e armazena sua respectiva imagem.

        Args:
            payload: Dados utilizados para criação da pizza.
            image_data: Conteúdo binário da imagem da pizza.
            content_type: Tipo MIME da imagem.

        Returns:
            Pizza criada.

        Raises:
            PizzaCreationError: Caso ocorra uma falha durante a criação
                da pizza ou no armazenamento de sua imagem.
        """

        if not content_type or not content_type.startswith('image/'):
            raise PizzaCreationError(
                'An image content type is required for creation.'
            )

        # TODO: Integrar o OCI Vision para verificar se o conteúdo representa
        # uma pizza antes de persistir o registro e enviar a imagem ao
        # Object Storage. A validação deverá considerar um modelo customizado
        # e um limiar mínimo de confiança configurável.

        # Quando o consumidor não informa um nome, o próprio serviço define
        # a chave do objeto para manter essa regra independente do cliente.
        image_name = payload.image_name or self._generate_image_name(
            content_type
        )

        now = now_utc()

        # Cria o modelo da aplicação a partir dos dados recebidos
        # pela camada HTTP.
        pizza = Pizza(
            id=uuid4(),

            # Padroniza a apresentação antes de persistir os textos do
            # catálogo, independentemente do cliente que enviou a requisição.
            name=payload.name.title(),
            description=payload.description.capitalize(),
            category=payload.category,
            price=payload.price,
            image_name=image_name,
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

        return pizza

    def update(self,
               pizza_id: UUID,
               payload: PizzaUpdateRequest,
               image_data: bytes | None = None,
               content_type: str | None = None) -> Pizza:
        """
        Atualiza os dados de uma pizza e, quando informado,
        substitui sua imagem.

        Args:
            pizza_id: Identificador da pizza.
            payload: Dados utilizados para atualização da pizza.
            image_data: Conteúdo binário da nova imagem.
            content_type: Tipo MIME da nova imagem.

        Returns:
            Pizza atualizada.

        Raises:
            PizzaNotFoundError: Caso a pizza não seja encontrada.
            PizzaUpdateError: Caso ocorra uma falha durante a atualização.
        """

        if image_data is not None and (
            not content_type or not content_type.startswith('image/')
        ):
            raise PizzaUpdateError(
                'An image content type is required when image data is provided.'
            )

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

            # Aplica a mesma padronização da criação somente aos campos
            # enviados na atualização parcial.
            if 'name' in update_data:
                update_data['name'] = update_data['name'].title()

            if 'description' in update_data:
                update_data['description'] =  update_data['description'].capitalize()

            # Quando uma nova imagem é enviada e nenhum nome foi informado,
            # gera uma nova chave para o objeto.
            if image_data is not None and 'image_name' not in update_data:
                update_data['image_name'] = self._generate_image_name(content_type)

            # Atualiza apenas os atributos informados na requisição.
            for field, value in update_data.items():
                setattr(
                    pizza,
                    field,
                    value
                )

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

        return pizza

    def delete(self, pizza_id: UUID) -> None:
        """
        Remove uma pizza e sua respectiva imagem.

        Args:
            pizza_id: Identificador da pizza.

        Raises:
            PizzaNotFoundError: Caso a pizza não seja encontrada.
            PizzaDeleteError: Caso ocorra uma falha durante a remoção.
        """

        try:
            # Consulta a pizza atualmente persistida para obter
            # o nome da imagem associada antes da remoção.
            pizza = self.pizza_repository.get_by_id(pizza_id)

            if pizza is None:
                raise PizzaNotFoundError()

            image_name = pizza.image_name

            # Remove a pizza do repositório.
            self.pizza_repository.delete(pizza_id)

            self.unit_of_work.commit()
        except PizzaNotFoundError:
            self.unit_of_work.rollback()
            raise
        except Exception as ex:
            self.unit_of_work.rollback()
            raise PizzaDeletionError('Failed to delete pizza.') from ex

        try:
            # Remove a imagem somente após a exclusão da pizza
            # ter sido confirmada no repositório.
            self.objectstorage_service.delete_object(image_name)
        except Exception as ex:
            # TODO: Implementar tratamento de inconsistência entre a remoção
            # da pizza e a exclusão da imagem no Object Storage, incluindo
            # retry, compensação ou processamento assíncrono.
            raise PizzaDeletionError(
                'Pizza deleted, but failed to delete image.'
            ) from ex

    @staticmethod
    def _generate_image_name(content_type: str) -> str:
        """
        Gera um nome único para uma imagem armazenada no Object Storage.

        Args:
            content_type: Tipo MIME informado para a imagem recebida.

        Returns:
            Nome seguro e único para o objeto armazenado.
        """

        # A extensão é derivada do tipo MIME, e não do nome enviado pelo
        # cliente, para evitar confiar em dados controlados externamente.
        extensions = {
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/webp': 'webp',
            'image/svg+xml': 'svg'
        }

        extension = extensions.get(content_type, 'img')

        # UUID4 reduz o risco de colisão mesmo quando múltiplas instâncias
        # do serviço recebem uploads simultaneamente.
        return f'pizza-{uuid4().hex}.{extension}'
    

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
