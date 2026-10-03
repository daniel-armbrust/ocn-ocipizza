#
# repositories/orm/base.py
#

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Classe base declarativa utilizada pelos modelos ORM do SQLAlchemy.

    Todas as classes ORM da aplicação devem herdar desta classe para
    compartilhar o mesmo conjunto de metadados das tabelas.
    """
    pass