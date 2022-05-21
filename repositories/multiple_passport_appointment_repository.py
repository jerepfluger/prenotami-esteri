from base import Session, engine, Base

Base.metadata.create_all(engine)


class MultiplePassportAppointmentRepository:
    def __init__(self):
        self.session = Session()

    def add_record(self):
        pass
