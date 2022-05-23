from sqlalchemy import Column, Integer, TIMESTAMP, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from base import Base
from repositories.entities.login_credentials_entity import LoginCredentialsEntity


class MultiplePassportAppointmentEntity(Base):
    __tablename__ = 'multiple_passport_appointment'

    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP)
    last_updated_at = Column(TIMESTAMP)
    login_credentials_id = Column(Integer, ForeignKey(LoginCredentialsEntity.id))
    address = Column(String(50))
    have_kids = Column(String(2))
    marital_status = Column(String(15))
    own_expired_passport = Column(String(2))
    minor_kids_amount = Column(Integer)
    additional_notes = Column(String(100))
    scheduled = Column(Boolean)


class MultiplePassportAdditionalPeopleDataEntity(Base):
    __tablename__ = 'multiple_passport_additional_people_data'

    id = Column(Integer, primary_key=True)
    multiple_passport_appointment_id = Column(Integer, ForeignKey(MultiplePassportAppointmentEntity.id))
    multiple_passport_appointment = relationship(MultiplePassportAppointmentEntity,
                                                 back_populates='additional_people_data')
    last_name = Column(String(30))
    first_name = Column(String(30))
    date_of_birth = Column(String(10))
    relationship = Column(String(15))
    have_kids = Column(String(2))
    marital_status = Column(String(15))
    address = Column(String(50))


MultiplePassportAppointmentEntity.additional_people_data = relationship(
    'MultiplePassportAdditionalPeopleDataEntity',
    order_by=MultiplePassportAdditionalPeopleDataEntity.id,
    back_populates='multiple_passport_appointment'
)
