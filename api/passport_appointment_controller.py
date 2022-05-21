import json
from http import HTTPStatus

from flask import Response as FlaskResponse
from flask import request

from dto.rest.multiple_passport_appointment import MultiplePassportAppointment
from dto.rest.response import Response
from helpers.logger import logger
from service.passport_apppointment_service import PassportAppointmentService
from . import routes


@routes.route("/prenotami-esteri/schedule_multiple_passport_appointment", methods=["POST"])
def schedule_multiple_passport_appointment():
    logger.info('Starting multiple passport appointment procedure')
    marshalled_data = MultiplePassportAppointment(**json.loads(request.data))
    success = PassportAppointmentService() \
        .schedule_multiple_passport_appointment(marshalled_data.client_login, marshalled_data.client_appointment_data)
    if success:
        response = Response('success', 'successfully schedule passport appointment for multiple people')
        return FlaskResponse(json.dumps(response.__dict__, status=HTTPStatus.OK))
    response = Response('failed', 'failed to schedule passport appointment for multiple people')
    return FlaskResponse(json.dumps(response.__dict__, status=HTTPStatus.OK))
