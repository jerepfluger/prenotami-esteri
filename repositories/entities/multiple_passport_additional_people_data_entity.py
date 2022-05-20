from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship


from base import Base


class MultiplePassportAdditionalPeopleDataEntity(Base):
    __tablename__ = 'multiple_passport_additional_people_data'

    id = Column(Integer, primary_key=True)
    multiple_passport_appointment_id = Column(Integer, ForeignKey('multiple_passport_appointment.id'))
    multiple_passport_appointment = relationship('MultiplePassportAppointmentEntity', back_populates='multiple_passport_additional_people_data')
    last_name = Column(String)
    first_name = Column(String)
    date_of_birth = Column(String)
    relationship = Column(String)
    have_kids = Column(String)
    marital_status = Column(String)
    address = Column(String)

    def __init__(self, multiple_passport_appointment_id, last_name, first_name, date_of_birth, relationship, have_kids,
                 marital_status, address):
        self.multiple_passport_appointment_id = multiple_passport_appointment_id
        self.last_name = last_name
        self.first_name = first_name
        self.date_of_birth = date_of_birth
        self.relationship = relationship
        self.have_kids = have_kids
        self.marital_status = marital_status
        self.address = address
