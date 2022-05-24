from os import environ as env

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

engine = create_engine(
    '{}://{}:{}@{}:{}/{}'.format(env['DB_ENGINE'], env['DB_USER'], env['DB_PASSWORD'],
                                 env['DB_HOST'], env['DB_PORT'], env['DB_SCHEMA']), echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()
