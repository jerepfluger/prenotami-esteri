from flask import Blueprint

routes = Blueprint('routes', __name__)

from .basic_controller import *
