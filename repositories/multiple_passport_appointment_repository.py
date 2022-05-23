from base import Session, engine, Base
from repositories.entities.multiple_passport_appointment_entity import MultiplePassportAppointmentEntity, \
    MultiplePassportAdditionalPeopleDataEntity

Base.metadata.create_all(engine)


def fill_additional_people_data(appointment, additional_people_data):
    for each in additional_people_data:
        appointment.additional_people_data.append(
            MultiplePassportAdditionalPeopleDataEntity(last_name=each['last_name'], first_name=each['first_name'],
                                                       date_of_birth=each['date_of_birth'],
                                                       relationship=each['relationship'], have_kids=each['have_kids'],
                                                       marital_status=each['marital_status'], address=each['address']))


class MultiplePassportAppointmentRepository:
    def __init__(self):
        self.session = Session()

    def add_record(self):
        pass

    def get_unscheduled_multiple_passport_appointment(self):
        return self.session.query(MultiplePassportAppointmentEntity) \
            .filter(MultiplePassportAppointmentEntity.scheduled == 0) \
            .first()

    def save_multiple_passport_appointment(self, credential_id, data):
        appointment = MultiplePassportAppointmentEntity(login_credentials_id=credential_id, address=data['address'], have_kids=data['have_kids'],
                                                        marital_status=data['marital_status'], own_expired_passport=data['own_expired_passport'],
                                                        minor_kids_amount=data['minor_kids_amount'], additional_notes=data['additional_notes'], scheduled=False)
        appointment.additional_people_data = []
        fill_additional_people_data(appointment, data['additional_people_data'])

        self.session.add(appointment)
        self.session.commit()
        self.session.close()

        return appointment
