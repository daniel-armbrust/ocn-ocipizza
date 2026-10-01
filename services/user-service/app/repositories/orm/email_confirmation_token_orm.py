#
# repositories/orm/email_confirmation_tokens_orm.py
#

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, BINARY
from sqlalchemy.orm import relationship

from app.repositories.orm.base import Base


class EmailConfirmationTokenORM(Base):
    """
    Modelo ORM utilizado pelo SQLAlchemy para representar a tabela
    email_confirmation_tokens.
    """

    __tablename__ = 'email_confirmation_tokens'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='Identificador único do registro do token.'
    )

    user_id = Column(
        BINARY(16),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='Identificador UUID do usuário associado ao token.'
    )

    # Usuário proprietário deste token de redefinição de senha.
    user = relationship(
        'UserORM',
        back_populates='email_confirmation_tokens'
    )

    token_hash = Column(
        String(64),
        nullable=False,
        unique=True,
        comment='Hash SHA-256 do token de confirmação.'
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='Data e hora de criação do token em UTC.'
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='Data e hora de expiração do token em UTC.'
    )

    revoked_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='Data e hora em que o token foi revogado em UTC.'
    )

    used_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='Data e hora em que o token foi utilizado.'
    )