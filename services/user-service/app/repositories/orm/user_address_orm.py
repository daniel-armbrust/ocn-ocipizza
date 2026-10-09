#
# repositories/orm/user_address_orm.py
#

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, BINARY
from sqlalchemy.orm import relationship

from app.repositories.orm.base import Base


class UserAddressORM(Base):
    __tablename__ = 'user_addresses'

    id = Column(
        BINARY(16),
        primary_key=True,
        nullable=False,
        comment='Identificador único do endereço.'
    )

    user_id = Column(
        BINARY(16),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='Identificador do usuário proprietário do endereço.'
    )

    user = relationship(
        'UserORM',
        back_populates='addresses'
    )

    label = Column(
        String(50),
        nullable=True,
        comment='Nome utilizado pelo usuário para identificar o endereço.'
    )

    zip_code = Column(
        String(9),
        nullable=False,
        comment='CEP do endereço.'
    )

    street = Column(
        String(255),
        nullable=False,
        comment='Logradouro do endereço.'
    )

    number = Column(
        String(20),
        nullable=False,
        comment='Número do endereço.'
    )

    complement = Column(
        String(100),
        nullable=True,
        comment='Complemento do endereço.'
    )

    neighborhood = Column(
        String(100),
        nullable=False,
        comment='Bairro do endereço.'
    )

    city = Column(
        String(100),
        nullable=False,
        comment='Cidade do endereço.'
    )

    state = Column(
        String(2),
        nullable=False,
        comment='Sigla do estado do endereço.'
    )

    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        comment='Indica se este é o endereço padrão do usuário.'
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='Data e hora de criação do endereço em UTC.'
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='Data e hora da última atualização do endereço em UTC.'
    )