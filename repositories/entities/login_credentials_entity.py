from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, JSON
from sqlalchemy.types import ARRAY

from base import Base


class LoginCredentialsEntity(Base):
    __tablename__ = 'login_credentials'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    def __init__(self, username, password):
        self.username = username
        self.password = password
