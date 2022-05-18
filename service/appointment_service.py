from dto.base_appointment import Appointment
from helpers.logger import logger
from repositories.appointment_repository import AppointmentRepository


class AppointmentService:
    def __init__(self):
        self.appointment_repository = AppointmentRepository()

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
