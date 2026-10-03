#
# repositories/orm/pizza_orm.py
#

from sqlalchemy import Column, DateTime, Integer, String, BINARY
from sqlalchemy.orm import relationship

from app.repositories.orm.base import Base


class PizzaORM(Base):
    pass