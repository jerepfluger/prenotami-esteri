import json
from http import HTTPStatus

from flask import Response as FlaskResponse
from flask import request

from dto.rest.multiple_passport_appointment import MultiplePassportAppointment
from dto.rest.response import Response
from helpers.logger import logger
from service.database_service import DatabaseService
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


@routes.route("/prenotami-esteri/get_unscheduled_multiple_passport_appointment", methods=["GET"])
def get_unscheduled_multiple_passport_appointment():
    logger.info('Searching for unscheduled appointments in database')
    result = DatabaseService().retrieve_unfinished_multiple_passport_appointment_scheduling()
    return FlaskResponse(json.dumps(result, default=lambda o: o.__dict__), status=HTTPStatus.OK)


@routes.route("/prenotami-esteri/save_multiple_passport_appointment", methods=["POST"])
def save_multiple_passport_appointment():
    logger.info('Starting multiple passport appointment procedure')
    data = MultiplePassportAppointment(**json.loads(request.data))
    appointment = PassportAppointmentService().save_multiple_passport_appointment(data)
    if not appointment:
        response = Response('failed', 'Something failed while trying to save appointment data')
        return FlaskResponse(json.dumps(response.__dict__), HTTPStatus.BAD_REQUEST)

    response = Response('success', 'Successfully saved appointment data')
    return FlaskResponse(json.dumps(response.__dict__), HTTPStatus.OK)
