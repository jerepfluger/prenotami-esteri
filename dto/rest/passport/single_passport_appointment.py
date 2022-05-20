class PassportSingleAppointment:
    def __init__(self, username, password, is_passport_expired, other_citizenship, marital_status, amount_minor_kids,
                 address, additional_notes):
        self.username = username
        self.password = password
        self.is_passport_expired = is_passport_expired
        self.other_citizenship = other_citizenship
        self.marital_status = marital_status
        self.amount_minor_kids = amount_minor_kids
        self.address = address
        self.additional_notes = additional_notes
