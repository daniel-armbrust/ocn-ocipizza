#
# repositories/order_repository.py
#

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.order import Order, OrderStatus, PaymentStatus


class OrderRepository(ABC):
    """
    Define o contrato de persistência utilizado pelo order-service.

    As implementações concretas podem utilizar Oracle NoSQL, SQLAlchemy ou
    outro provider sem alterar as regras de negócio da camada de serviço.
    """

    @abstractmethod
    def create(self, order: Order) -> Order:
        """
        Persiste um novo pedido.

        Args:
            order: Modelo de domínio que será persistido.

        Returns:
            Pedido persistido.
        """
        pass

    @abstractmethod
    def get_by_id(self,
                  order_id: UUID,
                  user_id: UUID | None = None) -> Order | None:
        """
        Localiza um pedido pelo identificador.

        Args:
            order_id: Identificador UUID do pedido.
            user_id: Identificador do proprietário quando a consulta ocorrer
                no contexto de um usuário autenticado.

        Returns:
            Pedido encontrado ou `None` quando ele não existir.
        """
        pass

    @abstractmethod
    def get_by_idempotency_key(self,
                               user_id: UUID,
                               idempotency_key: UUID) -> Order | None:
        """
        Localiza a tentativa de criação de um pedido pela idempotência.

        A associação com `user_id` impede que a reutilização acidental de uma
        chave por usuários diferentes exponha ou reutilize outro pedido.

        Args:
            user_id: Identificador do usuário proprietário do pedido.
            idempotency_key: Chave associada à tentativa de criação.

        Returns:
            Pedido já associado à chave ou `None` quando ela ainda não tiver
            sido utilizada pelo usuário.
        """
        pass

    @abstractmethod
    def get_by_user_id(self,
                       user_id: UUID,
                       limit: int = 10,
                       offset: int = 0) -> list[Order]:
        """
        Retorna os pedidos pertencentes a um usuário.

        Args:
            user_id: Identificador do usuário proprietário dos pedidos.
            limit: Quantidade máxima de registros retornados.
            offset: Quantidade de registros ignorados antes do retorno.

        Returns:
            Pedidos encontrados para o usuário.
        """
        pass

    @abstractmethod
    def get_all(self,
                order_status: OrderStatus | None = None,
                payment_status: PaymentStatus | None = None,
                limit: int = 10,
                offset: int = 0) -> list[Order]:
        """
        Retorna pedidos para acompanhamento administrativo.

        Args:
            order_status: Estado do pedido utilizado como filtro opcional.
            payment_status: Estado do pagamento utilizado como filtro
                opcional.
            limit: Quantidade máxima de registros retornados.
            offset: Quantidade de registros ignorados antes do retorno.

        Returns:
            Pedidos correspondentes aos filtros informados.
        """
        pass

    @abstractmethod
    def update(self, order: Order) -> Order:
        """
        Persiste as alterações realizadas em um pedido.

        Args:
            order: Modelo de domínio com os dados atualizados.

        Returns:
            Pedido atualizado.
        """
        pass
