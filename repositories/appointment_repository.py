from datetime import datetime

from base import Session, engine, Base
from repositories.entities.appointment_entity import AppointmentEntity

Base.metadata.create_all(engine)


class AppointmentRepository:
    def __init__(self):
        self.session = Session()

    def add_new_appointment(self, username, password, appointment_type, address, have_kids, marital_status,
                            is_passport_expired, amount_minor_kids, passport_expiry_date, travel_reason, height,
                            zip_code, other_citizenship, multiple_appointment, additional_people_data):
        appointment = AppointmentEntity(username, password, appointment_type, address, have_kids, marital_status,
                                        is_passport_expired, amount_minor_kids, passport_expiry_date, travel_reason,
                                        height, zip_code, other_citizenship, multiple_appointment,
                                        str(additional_people_data), False)
        self.session.add(appointment)
        self.session.flush()
        self.session.close()

        return appointment.id

    def update_last_updated_date(self):
        self.session.query(AppointmentEntity) \
            .filter(AppointmentEntity.id == 3) \
            .update({AppointmentEntity.last_updated: datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        self.session.commit()
        self.session.close()

    def set_appointment_scheduled(self):
        self.session.query(AppointmentEntity) \
            .filter(AppointmentEntity.id == 3) \
            .updadate({AppointmentEntity.scheduled_appointment: 1})
        self.session.flush()
        self.session.close()

    def get_unscheduled_appointment(self):
        return self.session.query(AppointmentEntity) \
            .filter(AppointmentEntity.scheduled_appointment == 0) \
            .first()
