#
# seeds/user_seed.py
#

from uuid import UUID


def get_demo_users() -> list[dict]:
    """
    Retorna os usuários utilizados para popular o ambiente
    de desenvolvimento.

    Os identificadores são fixos para permitir que o processo
    de seed seja reproduzível entre diferentes ambientes locais.

    As senhas presentes neste arquivo existem exclusivamente para
    desenvolvimento e devem ser convertidas para hash antes da
    persistência.

    Returns:
        Lista contendo os dados dos usuários de demonstração.
    """

    return [
        {
            'id': UUID(
                'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
            ),
            'full_name': 'Administrador',
            'email': 'admin@ocipizza.com.br',
            'whatsapp': '+5511900000000',
            'password': 'AdminPassword123!',
            'confirmed': True,
            'is_admin': True
        },
        {
            'id': UUID(
                '11111111-1111-4111-8111-111111111111'
            ),
            'full_name': 'Maria Oliveira',
            'email': 'maria.oliveira@example.com',
            'whatsapp': '+5511999999999',
            'password': 'DemoPassword123!',
            'confirmed': True,
            'is_admin': False
        },
        {
            'id': UUID(
                '22222222-2222-4222-8222-222222222222'
            ),
            'full_name': 'João Silva',
            'email': 'joao.silva@example.com',
            'whatsapp': '+5511988888888',
            'password': 'DemoPassword123!',
            'confirmed': False,
            'is_admin': False
        },
        {
            'id': UUID(
                '33333333-3333-4333-8333-333333333333'
            ),
            'full_name': 'Rita de Cássia',
            'email': 'rita.cassia@example.com',
            'whatsapp': '+5511977777777',
            'password': 'DemoPassword123!',
            'confirmed': True,
            'is_admin': False
        }
    ]