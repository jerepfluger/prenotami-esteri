from dto.rest.login_credentials import LoginCredentials
from dto.rest.passport.multiple_passport_data import MultiplePassportData


class MultiplePassportAppointment:
    def __init__(self, client_login: LoginCredentials, client_appointment_data: MultiplePassportData):
        self.client_login = client_login
        self.client_appointment_data = client_appointment_data
