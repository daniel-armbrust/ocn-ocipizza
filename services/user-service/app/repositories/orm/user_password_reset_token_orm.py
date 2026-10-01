#
# repositories/orm/user_password_reset_tokens_orm.py
#

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, BINARY
from sqlalchemy.orm import relationship

from app.repositories.orm.base import Base


class UserPasswordResetTokenORM(Base):
    """
    Modelo ORM utilizado pelo SQLAlchemy para representar a tabela password_reset_tokens.
    """

    __tablename__ = 'password_reset_tokens'

    id = Column(
        Integer,
        primary_key=True,
        comment='Identificador único do token de redefinição de senha.'
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
        back_populates='password_reset_tokens'
    )

    token_hash = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment='Hash do token de redefinição de senha.'
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='Data e hora de criação do token em UTC.'
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment='Data e hora de expiração do token em UTC.'
    )

    used_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='Data e hora em que o token foi utilizado em UTC.'
    )

    # Data e hora em que o token foi explicitamente invalidado.
    # Pode ser usado, por exemplo, ao gerar um novo token de reset.
    revoked_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='Data e hora em que o token foi revogado em UTC.'
    )
