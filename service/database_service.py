from dto.base_appointment import Appointment
from dto.rest.login_credentials import LoginCredentials
from dto.rest.passport.multiple_passport_appointment import MultiplePassportAppointment
from dto.rest.passport.multiple_passport_data import MultiplePassportAdditionalPeopleData, MultiplePassportData
from helpers.logger import logger
from repositories.appointment_repository import AppointmentRepository
from repositories.login_credentials_repository import LoginCredentialsRepository
from repositories.multiple_passport_additional_people_data_repository import \
    MultiplePassportAdditionalPeopleDataRepository
from repositories.multiple_passport_appointment_repository import MultiplePassportAppointmentRepository


def complete_multiple_passport_appointment_data(credentials, appointment, people_data):
    login_credentials = LoginCredentials(credentials.username, credentials.password)
    additional_people_data = []
    for person in people_data:
        additional_people_data.append(
            MultiplePassportAdditionalPeopleData(person.last_name, person.first_name, person.date_of_birth,
                                                 person.relationship, person.have_kids, person.marital_status,
                                                 person.address))
    multiple_passport_data = MultiplePassportData(appointment.address, appointment.have_kids,
                                                  appointment.marital_status, appointment.own_expired_passport,
                                                  appointment.minor_kids_amount, additional_people_data,
                                                  appointment.additional_notes)
    return MultiplePassportAppointment(login_credentials, multiple_passport_data)


class DatabaseService:
    def __init__(self):
        self.appointment_repository = AppointmentRepository()
        self.multiple_passport_appointment_repository = MultiplePassportAppointmentRepository()
        self.multiple_passport_additional_people_data_repository = MultiplePassportAdditionalPeopleDataRepository()
        self.login_credentials_repository = LoginCredentialsRepository()

    def retrieve_unfinished_appointment_scheduling(self):
        appointment = self.appointment_repository.get_unscheduled_appointment()
        if appointment:
            return Appointment(appointment.username, appointment.password, appointment.appointment_type,
                               appointment.address, appointment.have_kids, appointment.marital_status,
                               appointment.is_passport_expired, appointment.amount_minor_kids,
                               appointment.passport_expiry_date, appointment.travel_reason, appointment.height,
                               appointment.zip_code, appointment.other_citizenship, appointment.multiple_appointment,
                               len(appointment.additional_people_data), appointment.additional_people_data)
        return {}

    def save_new_appointment_in_database(self, appointment_data):
        logger.info('Saving new appointment in database')
        appointment_id = self.appointment_repository.add_new_appointment(appointment_data.username,
                                                                         appointment_data.password,
                                                                         appointment_data.appointment_type,
                                                                         appointment_data.address,
                                                                         appointment_data.have_kids,
                                                                         appointment_data.marital_status,
                                                                         appointment_data.is_passport_expired,
                                                                         appointment_data.amount_minor_kids,
                                                                         appointment_data.passport_expiry_date,
                                                                         appointment_data.travel_reason,
                                                                         appointment_data.height,
                                                                         appointment_data.zip_code,
                                                                         appointment_data.other_citizenship,
                                                                         appointment_data.multiple_appointment,
                                                                         appointment_data.additional_people_data)

        return appointment_id

    def update_appointment_timestamp(self):
        logger.info('Updating appointment timestamp in database')
        self.appointment_repository.update_last_updated_date()

    def set_appointment_scheduled(self):
        logger.info('Setting appointment to scheduled in database')
        self.appointment_repository.set_appointment_scheduled()

    def retrieve_unfinished_multiple_passport_appointment_scheduling(self):
        appointment = self.multiple_passport_appointment_repository.get_unscheduled_multiple_passport_appointment()
        if not appointment:
            return {}

        credentials = self.login_credentials_repository.get_credentials_by_id(appointment.login_credentials_id)
        if not credentials:
            raise Exception('Appointment found but system unable to find login credentials for given appointment')
        additional_people_data = self.multiple_passport_additional_people_data_repository. \
            get_additional_people_data_by_appointment_id(appointment.id)
        if not additional_people_data or len(additional_people_data) == 0:
            raise Exception('Appointment found but system unable to find additional people data')

        return complete_multiple_passport_appointment_data(credentials, appointment, additional_people_data)

    def get_user_credentials(self, username):
        credentials = self.login_credentials_repository.get_credentials(username)
        if credentials:
            return LoginCredentials(credentials.username, credentials.password)
        return {}

    def save_new_credentials(self, username, password):
        return self.login_credentials_repository.save_credentials(username, password)

    def save_new_multiple_passport_appointment(self, credential_id, client_appointment_data):
        appointment = self.multiple_passport_appointment_repository. \
            save_multiple_passport_appointment(credential_id, client_appointment_data)
        return appointment
