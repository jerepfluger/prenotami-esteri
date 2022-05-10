from base import Session, engine, Base
from repositories.entities.base_entity import BaseEntity

Base.metadata.create_all(engine)


class BaseRepository:
    def __init__(self):
        self.session = Session()

    def add_record(self):
        base_object = BaseEntity()
        self.session.add(base_object)
        self.session.commit()
