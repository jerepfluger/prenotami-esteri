from sqlalchemy import Column, Integer, String

from base import Base


class LoginCredentialsEntity(Base):
    __tablename__ = 'login_credentials'

    id = Column(Integer, primary_key=True)
    username = Column(String(30))
    password = Column(String(100))
