from dto.base_appointment import Appointment
from dto.rest.login_credentials import LoginCredentials
from dto.rest.multiple_passport_appointment import MultiplePassportAppointment
from helpers.logger import logger
from repositories.appointment_repository import AppointmentRepository
from repositories.login_credentials_repository import LoginCredentialsRepository
from repositories.multiple_passport_appointment_repository import MultiplePassportAppointmentRepository


class DatabaseService:
    def __init__(self):
        self.appointment_repository = AppointmentRepository()
        self.multiple_passport_appointment_repository = MultiplePassportAppointmentRepository()
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
        if appointment:
            return MultiplePassportAppointment

    def get_user_credentials(self, username):
        credentials = self.login_credentials_repository.get_credentials(username)
        if credentials:
            return LoginCredentials(credentials.id, credentials.username, credentials.password)
        return {}

    def save_new_credentials(self, username, password):
        return self.login_credentials_repository.save_credentials(username, password)

    def save_new_multiple_passport_appointment(self, credential_id, client_appointment_data):
        appointment = self.multiple_passport_appointment_repository.save_multiple_passport_appointment(credential_id, client_appointment_data)
        return appointment
