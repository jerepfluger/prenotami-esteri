from sqlalchemy import Column, Integer, TIMESTAMP, String, Boolean
from sqlalchemy.orm import relationship

from base import Base


class MultiplePassportAppointmentEntity(Base):
    __tablename__ = 'multiple_passport_appointment'

    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP)
    last_updated_at = Column(TIMESTAMP)
    login_credentials_id = Column(Integer)
    address = Column(String)
    have_kids = Column(String)
    marital_status = Column(String)
    own_expired_passport = Column(String)
    minor_kids_amount = Column(Integer)
    additional_notes = Column(String)
    scheduled = Column(Boolean)

    def __init__(self, login_credentials_id,  address, have_kids, marital_status, own_expired_passport,
                 minor_kids_amount, additional_notes, scheduled):
        self.login_credentials_id = login_credentials_id
        self.address = address
        self.have_kids = have_kids
        self.marital_status = marital_status
        self.own_expired_passport = own_expired_passport
        self.minor_kids_amount = minor_kids_amount
        self.additional_notes = additional_notes
        self.scheduled = scheduled


MultiplePassportAppointmentEntity.additional_people_data = relationship(
    'MultiplePassportAdditionalPeopleDataEntity',
    back_populates='multiple_passport_appointment'
)
