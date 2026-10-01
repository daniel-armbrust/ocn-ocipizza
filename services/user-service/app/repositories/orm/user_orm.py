#
# repositories/orm/user_orm.py
#

from sqlalchemy import Boolean, Column, DateTime, BINARY, String
from sqlalchemy.orm import relationship

from app.repositories.orm.base import Base


class UserORM(Base):
    """
    Modelo ORM utilizado pelo SQLAlchemy para representar a tabela users.
    """

    __tablename__ = 'users'

    id = Column(
        BINARY(16), 
        primary_key=True,
        comment='Identificador UUID do usuário associado ao token.'
    )

    full_name = Column(
        String(200),
        nullable=False,
        comment='Nome completo informado pelo usuário.'
    )

    email = Column(
        String(320),
        nullable=False,
        unique=True,
        index=True,
        comment='Endereço de e-mail do usuário.'
    )

    whatsapp = Column(
        String(30),
        nullable=False,
        unique=True,
        comment='Número de WhatsApp utilizado para contato.'
    )

    password_hash = Column(
        String(255),
        nullable=False,
        comment='Hash criptográfico da senha do usuário.'
    )

    confirmed = Column(
        Boolean,
        nullable=False,
        default=False,
        comment='Indica se o usuário confirmou o endereço de e-mail.'
    )

    is_admin = Column(
        Boolean,
        nullable=False,
        default=False,
        comment='Indica se o usuário possui privilégios administrativos.'
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='Data e hora da criação do usuário em UTC.'
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='Data e hora da última atualização do usuário em UTC.'
    )

    # Tokens utilizados para renovação de sessões autenticadas.
    refresh_tokens = relationship(
        'RefreshTokenORM',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    # Tokens utilizados para confirmação do endereço de e-mail.
    email_confirmation_tokens = relationship(
        'EmailConfirmationTokenORM',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    # Tokens utilizados no fluxo de recuperação e redefinição de senha.
    password_reset_tokens = relationship(
        'PasswordResetTokenORM',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    # Histórico das senhas anteriormente utilizadas pelo usuário.
    password_history = relationship(
        'PasswordHistoryORM',
        back_populates='user',
        cascade='all, delete-orphan'
    )