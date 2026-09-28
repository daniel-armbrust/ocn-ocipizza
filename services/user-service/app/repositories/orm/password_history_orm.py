#
# repositories/orm/password_history_orm.py
#

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, BINARY
from sqlalchemy.orm import relationship

from app.repositories.orm.base import Base


class PasswordHistoryORM(Base):
    """
    Modelo ORM utilizado pelo SQLAlchemy para representar a tabela
    password_history.

    A tabela mantém o histórico de hashes de senhas já utilizadas pelo
    usuário, permitindo a implementação futura de políticas que impeçam
    a reutilização de senhas anteriores.
    """

    __tablename__ = 'password_history'

    # Identificador único do registro de histórico de senha.
    id = Column(
        Integer,
        primary_key=True
    )

    # Identificador do usuário ao qual o histórico de senha pertence.
    user_id = Column(
        BINARY(16),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Usuário proprietário deste registro de histórico de senha.
    user = relationship(
        'UserORM',
        back_populates='password_history'
    )  

    # Hash de uma senha anteriormente utilizada pelo usuário.
    # A senha em texto puro nunca deve ser persistida.
    password_hash = Column(
        String(255),
        nullable=False
    )

    # Data e hora em que essa senha passou a fazer parte do histórico.
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    