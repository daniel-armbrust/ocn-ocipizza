#
# repositories/orm/refresh_tokens_orm.py
#

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, BINARY
from sqlalchemy.orm import relationship

from app.repositories.orm.base import Base


class RefreshTokenORM(Base):
    """
    Modelo ORM utilizado pelo SQLAlchemy para representar a tabela
    refresh_tokens.
    """

    __tablename__ = 'refresh_tokens'

    # Identificador interno do token.
    id = Column(
        Integer,
        primary_key=True
    )

    # Usuário dono da sessão/token.
    user_id = Column(
        BINARY(16),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    user = relationship(
        'UserORM',
        back_populates="refresh_tokens"
    )

    # Hash do refresh token.
    token_hash = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )

    # Data de quando foi criado.
    created_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    # Data de quando deixa de ser válido.
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Data de quando foi explicitamente revogado.
    revoked_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # Aponta para o novo token quando houver rotação.
    replaced_by_token_id = Column(
        Integer,
        ForeignKey('refresh_tokens.id', ondelete='SET NULL'),
        nullable=True
    )