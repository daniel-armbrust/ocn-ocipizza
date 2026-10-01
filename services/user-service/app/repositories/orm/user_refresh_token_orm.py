#
# repositories/orm/user_refresh_token_orm.py
# 

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, BINARY
from sqlalchemy.orm import relationship

from app.repositories.orm.base import Base


class UserRefreshTokenORM(Base):
    """
    Modelo ORM responsável pela persistência dos refresh tokens
    utilizados nas sessões dos usuários.

    Apenas o hash do refresh token é armazenado no banco de dados.
    O token original é retornado ao cliente e nunca deve ser persistido.
    """

    __tablename__ = 'refresh_tokens'

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment='Identificador interno do refresh token.'
    )

    user_id = Column(
        BINARY(16),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='Identificador UUID do usuário associado ao refresh token.'
    )

    # Relacionamento ORM com o usuário proprietário do refresh token.
    # O atributo correspondente em UserORM é `refresh_tokens`.
    user = relationship(
        'UserORM',
        back_populates='refresh_tokens',
    )

    token_hash = Column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
        comment='Hash SHA-256 do refresh token.'
    )

    created_at = Column(
        DateTime,
        nullable=False,
        comment='Data e hora de criação do refresh token.'
    )

    expires_at = Column(
        DateTime,
        nullable=False,
        comment='Data e hora de expiração do refresh token.'
    )

    revoked_at = Column(
        DateTime,
        nullable=True,
        comment='Data e hora de revogação do refresh token.'
    )