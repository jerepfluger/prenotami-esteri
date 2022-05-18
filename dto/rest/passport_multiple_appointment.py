class AdditionalPeopleData:
    def __init__(self, last_name, first_name, date_of_birth, relationship, have_kids, marital_status, address):
        self.last_name = last_name
        self.first_name = first_name
        self.date_of_birth = date_of_birth
        self.relationship = relationship
        self.have_kids = have_kids
        self.marital_status = marital_status
        self.address = address


class PassportMultipleAppointment:
    def __init__(self, username, password, is_passport_expired, other_citizenship, marital_status, amount_minor_kids,
                 address, additional_people_data, additional_notes):
        self.username = username
        self.password = password
        self.is_passport_expired = is_passport_expired
        self.other_citizenship = other_citizenship
        self.marital_status = marital_status
        self.amount_minor_kids = amount_minor_kids
        self.address = address
        self.additional_people_data = additional_people_data
        self.additional_notes = additional_notes
        self.additional_people_amount = len(self.additional_people_data)
