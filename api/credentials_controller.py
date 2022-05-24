import json
from http import HTTPStatus

from flask import Response as FlaskResponse
from flask import request

from dto.rest.login_credentials import LoginCredentials
from dto.rest.response import Response
from helpers.logger import logger
from service.database_service import DatabaseService
from . import routes


@routes.route('/prenotami-esteri/get_user_credentials', methods=['GET'])
def get_user_credentials():
    user = request.args.get('user')
    if user is None:
        response = Response('failed', 'missing \'user\' query param')
        return FlaskResponse(json.dumps(response.__dict__), status=HTTPStatus.BAD_REQUEST)
    logger.info('Searching for credentials of user {}'.format(user))

    credentials = DatabaseService().get_user_credentials(user)

    return FlaskResponse(json.dumps(credentials, default=lambda o: o.__dict__), status=HTTPStatus.OK)


@routes.route('/prenotami-esteri/save_new_login_credentials', methods=['POST'])
def save_new_login_credentials():
    credentials = LoginCredentials(**json.loads(request.data))
    logger.info('Start credentials saving procedure for user {}'.format(credentials.username))
    credentials_id = DatabaseService().save_new_credentials(credentials.username, credentials.password)
    response = Response('success', 'Successfully saved credentials with id {}'.format(credentials_id))

    return FlaskResponse(json.dumps(response.__dict__), status=HTTPStatus.OK)
