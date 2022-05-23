from base import Session, engine, Base
from helpers.cipher import Cipher
from repositories.entities.login_credentials_entity import LoginCredentialsEntity

Base.metadata.create_all(engine)


class LoginCredentialsRepository:
    def __init__(self):
        self.session = Session()

    def save_credentials(self, username, password):
        encrypted_password = Cipher().encrypt(password)
        credentials = LoginCredentialsEntity(username=username, password=encrypted_password.decode('utf-8'))
        self.session.add(credentials)
        self.session.commit()

        return credentials

    def get_credentials(self, username):
        credentials = self.session.query(LoginCredentialsEntity).filter(LoginCredentialsEntity.username == username).first()
        if credentials:
            credentials.password = Cipher().decrypt(credentials.password)

        return credentials
