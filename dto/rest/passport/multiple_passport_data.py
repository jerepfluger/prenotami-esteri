from typing import List


class PassportAdditionalPeopleData:
    def __init__(self, last_name, first_name, date_of_birth, relationship, have_kids, marital_status, address):
        self.last_name = last_name
        self.first_name = first_name
        self.date_of_birth = date_of_birth
        self.relationship = relationship
        self.have_kids = have_kids
        self.marital_status = marital_status
        self.address = address


class PassportData:
    def __init__(self, address, have_kids, marital_status, own_expired_passport, minor_kids_amount,
                 additional_people_data: List[PassportAdditionalPeopleData], additional_notes):
        self.address = address
        self.have_kids = have_kids
        self.marital_status = marital_status
        self.own_expired_passport = own_expired_passport
        self.minor_kids_amount = minor_kids_amount
        self.additional_people_data = additional_people_data
        self.additional_notes = additional_notes
