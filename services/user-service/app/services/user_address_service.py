#
# services/user_address_service.py
#

from uuid import uuid4, UUID

from fastapi import Depends

from app.utils.utils import now_utc

from app.repositories.user_address_repository import UserAddressRepository
from app.dependencies.database import get_user_address_repository

from app.models.user_address import UserAddress

from app.schemas.user_address_schema import (
    UserAddressCreateRequest,
    UserAddressUpdateRequest
)

from app.exceptions.user_address_exceptions import (
    UserAddressLimitExceededError,
    UserAddressNotFoundError
)

# Quantidade máxima de endereços que um usuário 
# pode cadastrar.
MAX_ADDRESSES_PER_USER = 3


class UserAddressService:
    """
    Serviço responsável pelas regras de negócio dos endereços dos usuários.
    """

    def __init__(self, user_address_repository: UserAddressRepository):
        """
        Inicializa o serviço de endereços de usuário.

        Args:
            user_address_repository: Repositório responsável pela persistência
                dos endereços dos usuários.
        """

        self.user_address_repository = user_address_repository

    def get_by_user_id(self, user_id: UUID) -> list[UserAddress]:
        """
        Retorna todos os endereços cadastrados pelo usuário.

        Args:
            user_id: Identificador único do usuário.

        Returns:
            Lista contendo os endereços cadastrados pelo usuário.
        """

        return self.user_address_repository.get_by_user_id(user_id)

    def get_by_id(self,
                  address_id: UUID,
                  user_id: UUID) -> UserAddress | None:
        """
        Retorna um endereço pertencente ao usuário.

        Args:
            address_id: Identificador único do endereço.
            user_id: Identificador único do usuário proprietário do endereço.

        Returns:
            O endereço encontrado ou None caso não exista ou não pertença
            ao usuário.
        """

        return self.user_address_repository.get_by_id_and_user_id(
            address_id,
            user_id
        )

    def create(self,
               user_id: UUID,
               payload: UserAddressCreateRequest) -> UserAddress:
        """
        Cria um novo endereço para o usuário.

        Args:
            user_id: Identificador único do usuário.
            payload: Dados do endereço que será cadastrado.

        Returns:
            O endereço criado.

        Raises:
            UserAddressLimitExceededError: Quando o usuário atingir o limite
                máximo de endereços permitidos.
        """

        addresses = self.user_address_repository.get_by_user_id(user_id)

        if len(addresses) >= MAX_ADDRESSES_PER_USER:
            raise UserAddressLimitExceededError()

        now = now_utc()

        # Define o primeiro endereço cadastrado como padrão automaticamente.
        # Nos demais casos, respeita a escolha informada pelo usuário.
        is_default = payload.is_default or len(addresses) == 0

        # Remove a marcação de padrão de qualquer outro endereço do usuário
        # antes de definir o novo endereço como padrão.
        if is_default:
            self.user_address_repository.unset_default_by_user_id(
                user_id,
                now
            )

        address = UserAddress(
            id=uuid4(),
            user_id=user_id,
            label=payload.label,
            zip_code=payload.zip_code,
            street=payload.street,
            number=payload.number,
            complement=payload.complement,
            neighborhood=payload.neighborhood,
            city=payload.city,
            state=payload.state.upper(),
            is_default=is_default,
            created_at=now,
            updated_at=now
        )

        return self.user_address_repository.create(address)

    def update(self,
               address_id: UUID,
               user_id: UUID,
               payload: UserAddressUpdateRequest) -> UserAddress:
        """
        Atualiza um endereço pertencente ao usuário.

        Args:
            address_id: Identificador único do endereço.
            user_id: Identificador único do usuário proprietário do endereço.
            payload: Dados que serão atualizados.

        Returns:
            O endereço atualizado.

        Raises:
            UserAddressNotFoundError: Quando o endereço não existir ou não
                pertencer ao usuário.
        """

        address = self.user_address_repository.get_by_id_and_user_id(
            address_id,
            user_id
        )

        if address is None:
            raise UserAddressNotFoundError()

        changes = payload.model_dump(exclude_unset=True)

        for field, value in changes.items():
            setattr(address, field, value)

        if address.state:
            address.state = address.state.upper()

        address.updated_at = now_utc()

        if changes.get('is_default') is True:
            self.user_address_repository.unset_default_by_user_id(
                user_id,
                address.updated_at
            )

            address.is_default = True

        return self.user_address_repository.update(
            address_id,
            address
        )

    def set_default(self,
                    address_id: UUID,
                    user_id: UUID) -> UserAddress:
        """
        Define um endereço como padrão para o usuário.

        Args:
            address_id: Identificador único do endereço.
            user_id: Identificador único do usuário proprietário do endereço.

        Returns:
            O endereço definido como padrão.

        Raises:
            UserAddressNotFoundError: Quando o endereço não existir ou não
                pertencer ao usuário.
        """

        address = self.user_address_repository.get_by_id_and_user_id(
            address_id,
            user_id
        )

        if address is None:
            raise UserAddressNotFoundError()

        now = now_utc()

        self.user_address_repository.unset_default_by_user_id(
            user_id,
            now
        )

        address.is_default = True
        address.updated_at = now

        return self.user_address_repository.update(
            address_id,
            address
        )

    def delete(self,
               address_id: UUID,
               user_id: UUID) -> None:
        """
        Remove um endereço pertencente ao usuário.

        Args:
            address_id: Identificador único do endereço.
            user_id: Identificador único do usuário proprietário do endereço.

        Returns:
            None.

        Raises:
            UserAddressNotFoundError: Quando o endereço não existir ou não
                pertencer ao usuário.
        """

        address = self.user_address_repository.get_by_id_and_user_id(
            address_id,
            user_id
        )

        if address is None:
            raise UserAddressNotFoundError()

        self.user_address_repository.delete(
            address_id,
            user_id
        )


def get_user_address_service(
        user_address_repository: UserAddressRepository = Depends(
            get_user_address_repository
        )
) -> UserAddressService:
    """
    Cria e retorna o serviço responsável pelos endereços dos usuários.

    Args:
        user_address_repository: Repositório responsável pela persistência
            dos endereços dos usuários.

    Returns:
        Serviço responsável pelas operações relacionadas aos endereços
        dos usuários.
    """

    return UserAddressService(
        user_address_repository=user_address_repository
    )