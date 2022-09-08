import json
from http import HTTPStatus

from flask import Response as FlaskResponse
from flask import request

from dto.rest.citizenship.citizenship_appointment_data import CitizenshipAppointmentData
from dto.rest.response import Response
from helpers.logger import logger
from service.citizenship_service import CitizenshipService
from . import routes


@routes.route('/prenotami-esteri/schedule_citizenship_appointment', methods=['POST'])
def schedule_citizenship_appointment():
    logger.info('Starting descendant citizenship appointment procedure')
    return schedule_citizenship_appointment_internal(json.loads(request.data))


def schedule_citizenship_appointment_internal(data):
    logger.info('Starting internal descendent citizenship appointment procedure')
    marshalled_data = CitizenshipAppointmentData(**data)
    success = CitizenshipService(marshalled_data.unlimited_wait).schedule_citizenship_appointment(marshalled_data.client_login,
                                                                                  marshalled_data.appointment_data)
    if not success:
        response = Response('failed', 'Unable to schedule descendant citizenship appointment')
        return FlaskResponse(json.dumps(response.__dict__), status=HTTPStatus.OK)

    response = Response('success', 'Successfully scheduled descendant citizenship appointment')
    return FlaskResponse(json.dumps(response.__dict__), status=HTTPStatus.OK)


def schedule_manual_run():
    return schedule_citizenship_appointment_internal(
        {'client_login': {'username': 'marianelapussetto@gmail.com', 'password': 'Mainma12'}, 'unlimited_wait': True})
