#
# services/user_service.py
#

import asyncio

from uuid import UUID

from fastapi import Depends

from app.clients.user_client import UserClient, get_user_client
from app.utils.utils import normalize_zip_code


class UserService:
    """
    Coordena os casos de uso de cadastro e perfil do usuário no BFF.

    O serviço mantém as rotas independentes dos detalhes de comunicação com
    o user-service sem conhecer formulários, templates ou redirects.
    """

    def __init__(self, user_client: UserClient) -> None:
        """
        Inicializa o serviço com o cliente do user-service.

        Args:
            user_client: Cliente utilizado para acessar a API de usuários.

        Returns:
            None.
        """

        self.user_client = user_client

    async def create(self,
                     full_name: str,
                     email: str,
                     whatsapp: str,
                     password: str) -> dict:
        """
        Cadastra um usuário no user-service.

        Args:
            full_name: Nome completo do usuário.
            email: Endereço de e-mail do usuário.
            whatsapp: Número de WhatsApp do usuário.
            password: Senha definida para autenticação.

        Returns:
            Resposta produzida pelo user-service após o cadastro.

        Raises:
            httpx.HTTPStatusError: Caso o user-service rejeite o cadastro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        return await self.user_client.create(
            full_name=full_name,
            email=email,
            whatsapp=whatsapp,
            password=password
        )

    async def get_profile(self, access_token: str) -> dict:
        """
        Compõe os dados do perfil do usuário autenticado.

        O perfil e os endereços são recursos independentes do user-service e
        são consultados em paralelo para reduzir o tempo de carregamento.

        Args:
            access_token: Token JWT do usuário autenticado.

        Returns:
            Dicionário contendo os dados do usuário e seus endereços.

        Raises:
            httpx.HTTPStatusError: Caso o user-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        user, addresses = await asyncio.gather(
            self.user_client.get_profile(access_token=access_token),
            self.user_client.get_addresses(access_token=access_token)
        )

        return {
            'user': user,
            'addresses': addresses
        }

    async def get_account(self, access_token: str) -> dict:
        """
        Obtém os dados da conta do usuário autenticado.

        Args:
            access_token: Token JWT do usuário autenticado.

        Returns:
            Dados pessoais retornados pelo user-service.

        Raises:
            httpx.HTTPStatusError: Caso o user-service rejeite a consulta.
            httpx.RequestError: Caso o user-service esteja indisponível.
        """

        return await self.user_client.get_profile(access_token=access_token)

    async def create_address(self,
                             access_token: str,
                             label: str | None,
                             zip_code: str,
                             street: str,
                             number: str,
                             complement: str | None,
                             neighborhood: str,
                             city: str,
                             state: str,
                             is_default: bool) -> dict:
        """
        Cadastra um endereço para o usuário autenticado.

        Args:
            access_token: Token JWT do usuário autenticado.
            label: Identificação opcional do endereço.
            zip_code: CEP do endereço.
            street: Logradouro do endereço.
            number: Número do imóvel.
            complement: Complemento opcional do endereço.
            neighborhood: Bairro do endereço.
            city: Cidade do endereço.
            state: Sigla do estado.
            is_default: Indica se o endereço será o principal.

        Returns:
            Endereço criado pelo user-service.

        Raises:
            httpx.HTTPStatusError: Caso o user-service rejeite o endereço.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        return await self.user_client.create_address(
            access_token=access_token,
            label=label,
            zip_code=normalize_zip_code(zip_code),
            street=street,
            number=number,
            complement=complement,
            neighborhood=neighborhood,
            city=city,
            state=state,
            is_default=is_default
        )

    async def update_whatsapp(self,
                              access_token: str,
                              whatsapp: str) -> dict:
        """
        Atualiza o WhatsApp do usuário autenticado.

        Args:
            access_token: Token JWT do usuário autenticado.
            whatsapp: Novo número de WhatsApp.

        Returns:
            Resposta produzida pelo user-service após a atualização.

        Raises:
            httpx.HTTPStatusError: Caso o user-service rejeite a atualização.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        return await self.user_client.update_whatsapp(
            access_token=access_token,
            whatsapp=whatsapp
        )

    async def delete_address(self,
                             access_token: str,
                             address_id: UUID) -> None:
        """
        Remove um endereço do usuário autenticado.

        Args:
            access_token: Token JWT do usuário autenticado.
            address_id: Identificador UUID do endereço removido.

        Returns:
            None.

        Raises:
            httpx.HTTPStatusError: Caso o user-service rejeite a remoção.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        await self.user_client.delete_address(
            access_token=access_token,
            address_id=address_id
        )

    async def confirm_email(self, token: str) -> None:
        """
        Confirma o endereço de e-mail do usuário utilizando o token.

        Args:
            token: Token utilizado para confirmar o endereço de e-mail.

        Returns:
            None.

        Raises:
            httpx.HTTPStatusError: Caso o user-service rejeite a confirmação.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        await self.user_client.confirm_email(token=token)

def get_user_service(
    user_client: UserClient = Depends(get_user_client)
) -> UserService:
    """
    Fornece o serviço responsável pelos casos de uso do usuário no BFF.

    Args:
        user_client: Cliente configurado para acessar o user-service.

    Returns:
        Instância configurada de `UserService`.
    """

    return UserService(user_client=user_client)
