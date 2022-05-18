from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, JSON
from sqlalchemy.types import ARRAY

from base import Base


class AppointmentEntity(Base):
    __tablename__ = 'appointment'

    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP)
    last_updated = Column(TIMESTAMP)
    username = Column(String)
    password = Column(String)
    appointment_type = Column(String)
    address = Column(String)
    have_kids = Column(String)
    marital_status = Column(String)
    is_passport_expired = Column(String)
    amount_minor_kids = Column(Integer)
    passport_expiry_date = Column(String)
    travel_reason = Column(String)
    height = Column(Integer)
    zip_code = Column(String)
    other_citizenship = Column(String)
    multiple_appointment = Column(Boolean)
    additional_people_data = Column(ARRAY(JSON))
    scheduled_appointment = Column(Boolean)

    def __init__(self, username, password, appointment_type, address, have_kids, marital_status, is_passport_expired,
                 amount_minor_kids, passport_expiry_date, travel_reason, height, zip_code, other_citizenship,
                 multiple_appointment, additional_people_data, scheduled_appointment):
        self.timestamp = datetime.now().strftime('%Y:%m:%d %H:%m:%S')
        self.last_updated = datetime.now().strftime('%Y:%m:%d %H:%m:%S')
        self.username = username
        self.password = password
        self.appointment_type = appointment_type
        self.address = address
        self.have_kids = have_kids
        self.marital_status = marital_status
        self.is_passport_expired = is_passport_expired
        self.amount_minor_kids = amount_minor_kids
        self.passport_expiry_date = passport_expiry_date
        self.travel_reason = travel_reason
        self.height = height
        self.zip_code = zip_code
        self.other_citizenship = other_citizenship
        self.multiple_appointment = multiple_appointment
        self.additional_people_data = additional_people_data
        self.additional_people_amount = len(self.additional_people_data)
        self.scheduled_appointment = scheduled_appointment
