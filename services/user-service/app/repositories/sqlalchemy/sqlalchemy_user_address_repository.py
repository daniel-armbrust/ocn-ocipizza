#
# repositories/sqlalchemy/sqlalchemy_user_address_repository.py
#

from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.models.user_address import UserAddress
from app.repositories.user_address_repository import UserAddressRepository
from app.repositories.orm.user_address_orm import UserAddressORM
from app.utils.utils import bin_to_uuid, uuid_to_bin


class SQLAlchemyUserAddressRepository(UserAddressRepository):
    """
    Implementação SQLAlchemy do repositório de endereços de usuário.
    """

    def __init__(self, session: Session):
        """
        Inicializa o repositório de endereços de usuário.

        Args:
            session: Sessão SQLAlchemy utilizada para acesso ao banco de dados.
        """

        self.session = session

    def create(self, address: UserAddress) -> UserAddress:
        """
        Cria um novo endereço para o usuário.

        Args:
            address: Endereço que será persistido no banco de dados.

        Returns:
            O endereço persistido.
        """

        orm_address = UserAddressORM(
            id=uuid_to_bin(address.id),
            user_id=uuid_to_bin(address.user_id),
            label=address.label,
            zip_code=address.zip_code,
            street=address.street,
            number=address.number,
            complement=address.complement,
            neighborhood=address.neighborhood,
            city=address.city,
            state=address.state,
            is_default=address.is_default,
            created_at=address.created_at,
            updated_at=address.updated_at
        )

    
        self.session.add(orm_address)

        # Envia as alterações pendentes ao banco sem finalizar a transação.
        # Isso permite validar a operação e sincronizar valores gerados
        # pelo banco.
        self.session.flush()

        # Atualiza o objeto ORM com valores gerados pelo banco.
        self.session.refresh(orm_address)

        return self._to_model(orm_address)

    def get_by_id(self, address_id: UUID) -> UserAddress | None:
        """
        Busca um endereço pelo identificador.

        Args:
            address_id: Identificador único do endereço.

        Returns:
            O endereço encontrado ou None caso não exista.
        """

        stmt = select(UserAddressORM).where(
            UserAddressORM.id == uuid_to_bin(address_id)
        )

        orm_address = self.session.execute(
            stmt
        ).scalar_one_or_none()

        if orm_address is None:
            return None

        return self._to_model(orm_address)

    def get_by_id_and_user_id(self,
                              address_id: UUID,
                              user_id: UUID) -> UserAddress | None:
        """
        Busca um endereço pelo identificador e pelo usuário proprietário.

        Args:
            address_id: Identificador único do endereço.
            user_id: Identificador único do usuário proprietário do endereço.

        Returns:
            O endereço encontrado ou None caso não exista ou não pertença
            ao usuário informado.
        """

        stmt = select(UserAddressORM).where(
            UserAddressORM.id == uuid_to_bin(address_id),
            UserAddressORM.user_id == uuid_to_bin(user_id)
        )

        orm_address = self.session.execute(
            stmt
        ).scalar_one_or_none()

        if orm_address is None:
            return None

        return self._to_model(orm_address)

    def get_by_user_id(self,
                       user_id: UUID) -> list[UserAddress]:
        """
        Retorna todos os endereços pertencentes ao usuário.

        O endereço definido como padrão é retornado primeiro.

        Args:
            user_id: Identificador único do usuário.

        Returns:
            Lista de endereços pertencentes ao usuário.
        """
        
        stmt = (
            select(UserAddressORM)
            .where(
                UserAddressORM.user_id == uuid_to_bin(user_id)
            )
            .order_by(
                UserAddressORM.is_default.desc(),
                UserAddressORM.created_at.asc()
            )
        )

        orm_addresses = self.session.execute(
            stmt
        ).scalars().all()

        return [
            self._to_model(orm_address)
            for orm_address in orm_addresses
        ]

    def get_default_by_user_id(self,
                               user_id: UUID) -> UserAddress | None:
        """
        Retorna o endereço padrão do usuário.

        Args:
            user_id: Identificador único do usuário.

        Returns:
            O endereço padrão do usuário ou None caso não exista.
        """

        stmt = select(UserAddressORM).where(
            UserAddressORM.user_id == uuid_to_bin(user_id),
            UserAddressORM.is_default.is_(True)
        )

        orm_address = self.session.execute(
            stmt
        ).scalar_one_or_none()

        if orm_address is None:
            return None

        return self._to_model(orm_address)

    def update(self,
               address_id: UUID,
               address: UserAddress) -> UserAddress:
        """
        Atualiza os dados de um endereço.

        Args:
            address_id: Identificador único do endereço que será atualizado.
            address: Dados atualizados do endereço.

        Returns:
            O endereço atualizado.
        """

        stmt = (
            update(UserAddressORM)
            .where(
                UserAddressORM.id == uuid_to_bin(address_id)
            )
            .values(
                label=address.label,
                zip_code=address.zip_code,
                street=address.street,
                number=address.number,
                complement=address.complement,
                neighborhood=address.neighborhood,
                city=address.city,
                state=address.state,
                is_default=address.is_default,
                updated_at=address.updated_at
            )
        )

        self.session.execute(stmt)

        # Envia a atualização ao banco sem finalizar a transação.
        self.session.flush()

        return address

    def unset_default_by_user_id(self,
                                 user_id: UUID,
                                 updated_at: datetime) -> None:
        """
        Remove a marcação de endereço padrão dos endereços do usuário.

        Args:
            user_id: Identificador único do usuário.
            updated_at: Data e hora da atualização em UTC.

        Returns:
            None.
        """

        stmt = (
            update(UserAddressORM)
            .where(
                UserAddressORM.user_id == uuid_to_bin(user_id),
                UserAddressORM.is_default.is_(True)
            )
            .values(
                is_default=False,
                updated_at=updated_at
            )
        )

        self.session.execute(stmt)

        # Envia a atualização ao banco sem finalizar a transação.
        self.session.flush()

    def delete(self,
               address_id: UUID,
               user_id: UUID) -> bool:
        """
        Remove um endereço pertencente ao usuário.

        Args:
            address_id: Identificador único do endereço.
            user_id: Identificador único do usuário proprietário do endereço.

        Returns:
            True caso o endereço tenha sido removido ou False caso nenhum
            endereço correspondente tenha sido encontrado.
        """

        stmt = delete(UserAddressORM).where(
            UserAddressORM.id == uuid_to_bin(address_id),
            UserAddressORM.user_id == uuid_to_bin(user_id)
        )

        result = self.session.execute(stmt)

        # Envia a exclusão ao banco sem finalizar a transação.
        self.session.flush()

        return result.rowcount > 0

    @staticmethod
    def _to_model(orm_address: UserAddressORM) -> UserAddress:
        """
        Converte um objeto ORM em um modelo de domínio.

        Args:
            orm_address: Objeto ORM que representa o endereço persistido.

        Returns:
            Modelo de domínio correspondente ao endereço persistido.
        """

        return UserAddress(
            id=bin_to_uuid(orm_address.id),
            user_id=bin_to_uuid(orm_address.user_id),
            label=orm_address.label,
            zip_code=orm_address.zip_code,
            street=orm_address.street,
            number=orm_address.number,
            complement=orm_address.complement,
            neighborhood=orm_address.neighborhood,
            city=orm_address.city,
            state=orm_address.state,
            is_default=orm_address.is_default,
            created_at=orm_address.created_at,
            updated_at=orm_address.updated_at
        )