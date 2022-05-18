import json


class Appointment:
    def __init__(self, username, password, appointment_type, address, have_kids, marital_status, is_passport_expired,
                 amount_minor_kids, passport_expiry_date, travel_reason, height, zip_code, other_citizenship,
                 multiple_appointment, additional_people_amount, additional_people_data):
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
        self.additional_people_amount = additional_people_amount
        self.additional_people_data = json.loads(additional_people_data.replace('\'', '\"'))


class AdditionalPeopleData:
    def __init__(self, last_name, first_name, date_of_birth, relationship, have_kids, marital_status, address):
        self.last_name = last_name
        self.first_name = first_name
        self.date_of_birth = date_of_birth
        self.relationship = relationship
        self.have_kids = have_kids
        self.marital_status = marital_status
        self.address = address
