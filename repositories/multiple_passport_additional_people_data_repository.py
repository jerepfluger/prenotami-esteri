from base import Session, engine, Base
from repositories.entities.multiple_passport_appointment_entity import MultiplePassportAdditionalPeopleDataEntity

Base.metadata.create_all(engine)


class MultiplePassportAdditionalPeopleDataRepository:
    def __init__(self):
        self.session = Session()

    def get_additional_people_data_by_appointment_id(self, id):
        return self.session.query(MultiplePassportAdditionalPeopleDataEntity).filter(
            MultiplePassportAdditionalPeopleDataEntity.multiple_passport_appointment_id == id).all()
