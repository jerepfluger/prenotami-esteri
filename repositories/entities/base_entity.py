from sqlalchemy import Column, Integer

from base import Base


class BaseEntity(Base):
    __tablename__ = 'base_table'

    id = Column(Integer, primary_key=True)

    def __init__(self):
        pass
