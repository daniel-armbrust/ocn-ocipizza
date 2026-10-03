#
# seeds/pizza_seed.py
#

from decimal import Decimal
from uuid import UUID

from app.models.pizza import Pizza, PizzaCategory
from app.utils.utils import now_utc


def get_demo_pizzas() -> list[Pizza]:
    """
    Retorna as pizzas utilizadas para popular o ambiente
    de desenvolvimento.

    Os identificadores são fixos para permitir que o processo
    de seed seja reproduzível entre diferentes ambientes locais.

    Returns:
        Lista contendo as pizzas de demonstração.
    """

    now = now_utc()

    return [
        Pizza(
            id=UUID('11111111-1111-4111-8111-111111111111'),
            name='Abobrinha',
            description=(
                'Molho de tomate, mussarela, abobrinha e temperos.'
            ),
            category=PizzaCategory.VEGETARIANA,
            price=Decimal('49.90'),
            image_name='pizza-abobrinha.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('22222222-2222-4222-8222-222222222222'),
            name='Bauru',
            description=(
                'Molho de tomate, mussarela, presunto e tomate.'
            ),
            category=PizzaCategory.SALGADA,
            price=Decimal('52.90'),
            image_name='pizza-bauru.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('33333333-3333-4333-8333-333333333333'),
            name='Calabresa',
            description=(
                'Molho de tomate, mussarela, calabresa e cebola.'
            ),
            category=PizzaCategory.SALGADA,
            price=Decimal('49.90'),
            image_name='pizza-calabresa.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('44444444-4444-4444-8444-444444444444'),
            name='Frango com Bacon',
            description=(
                'Molho de tomate, mussarela, frango desfiado e bacon.'
            ),
            category=PizzaCategory.SALGADA,
            price=Decimal('56.90'),
            image_name='pizza-fran-bacon.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('55555555-5555-4555-8555-555555555555'),
            name='Frango com Mussarela',
            description=(
                'Molho de tomate, mussarela e frango desfiado.'
            ),
            category=PizzaCategory.SALGADA,
            price=Decimal('54.90'),
            image_name='pizza-frango-mussarela.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('66666666-6666-4666-8666-666666666666'),
            name='Hot Dog',
            description=(
                'Molho de tomate, mussarela, salsicha, milho '
                'e batata palha.'
            ),
            category=PizzaCategory.SALGADA,
            price=Decimal('53.90'),
            image_name='pizza-hot-dog.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('77777777-7777-4777-8777-777777777777'),
            name='Lombinho',
            description=(
                'Molho de tomate, mussarela e lombinho.'
            ),
            category=PizzaCategory.SALGADA,
            price=Decimal('57.90'),
            image_name='pizza-lombinho.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('88888888-8888-4888-8888-888888888888'),
            name='Marguerita',
            description=(
                'Molho de tomate, mussarela, tomate, '
                'manjericão e parmesão.'
            ),
            category=PizzaCategory.VEGETARIANA,
            price=Decimal('51.90'),
            image_name='pizza-marguerita.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('99999999-9999-4999-8999-999999999999'),
            name='Milho com Mussarela',
            description=(
                'Molho de tomate, mussarela e milho.'
            ),
            category=PizzaCategory.VEGETARIANA,
            price=Decimal('48.90'),
            image_name='pizza-milho-mussarela.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'),
            name='Moda da Casa',
            description=(
                'Molho de tomate, mussarela, presunto, calabresa, '
                'milho e cebola.'
            ),
            category=PizzaCategory.SALGADA,
            price=Decimal('59.90'),
            image_name='pizza-moda-da-casa.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'),
            name='Pepperoni',
            description=(
                'Molho de tomate, mussarela e pepperoni.'
            ),
            category=PizzaCategory.SALGADA,
            price=Decimal('58.90'),
            image_name='pizza-peperone.jpg',
            available=True,
            created_at=now,
            updated_at=now
        ),
        Pizza(
            id=UUID('cccccccc-cccc-4ccc-8ccc-cccccccccccc'),
            name='Portuguesa',
            description=(
                'Molho de tomate, mussarela, presunto, ovo, '
                'cebola e azeitonas.'
            ),
            category=PizzaCategory.SALGADA,
            price=Decimal('57.90'),
            image_name='pizza-portuguesa.jpg',
            available=True,
            created_at=now,
            updated_at=now
        )
    ]