from dto.rest.login_credentials import LoginCredentials
from dto.rest.passport.multiple_passport_data import PassportData


class PassportAppointment:
    def __init__(self, client_login: LoginCredentials, client_appointment_data: PassportData, unlimited_wait=False):
        self.client_login = client_login
        self.client_appointment_data = client_appointment_data
        self.unlimited_wait = unlimited_wait
