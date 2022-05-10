from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from os import environ as env

load_dotenv()

engine = create_engine(
    '{}://{}:{}@{}:{}/{}'.format(env['DB_ENGINE'], env['DB_USER'], env['DB_PASSWORD'],
                                 env['DB_HOST'], env['DB_PORT'], env['DB_SCHEMA']))
Session = sessionmaker(bind=engine)

Base = declarative_base()
