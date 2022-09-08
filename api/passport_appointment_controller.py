import json
from http import HTTPStatus

from flask import Response as FlaskResponse
from flask import request

from dto.rest.passport.multiple_passport_appointment import PassportAppointment
from dto.rest.response import Response
from helpers.logger import logger
from service.database_service import DatabaseService
from service.passport_apppointment_service import PassportAppointmentService
from . import routes


@routes.route('/prenotami-esteri/schedule_passport_appointment', methods=['POST'])
def schedule_multiple_passport_appointment():
    logger.info('Starting passport appointment procedure')
    return schedule_passport_appointment_internal(json.loads(request.data))


@routes.route('/prenotami-esteri/run_unscheduled_passport_appointment', methods=['POST'])
def run_unscheduled_multiple_passport_appointment():
    logger.info('Searching for unscheduled passport appointments in database')
    unscheduled_appointment = get_unscheduled_multiple_passport_appointment()
    if unscheduled_appointment.status_code != 200 or unscheduled_appointment.data.decode('utf-8') == '{}':
        logger.info('No unscheduled passport appointments were found')
        response = Response('success', 'No unscheduled passport appointments found')
        return FlaskResponse(json.dumps(response.__dict__), status=200)

    logger.info('Unscheduled passport appointment found. Start processing')
    return schedule_passport_appointment_internal(json.loads(unscheduled_appointment.data))


def schedule_passport_appointment_internal(data):
    logger.info('Starting internal passport appointment procedure')
    marshalled_data = PassportAppointment(**data)
    success = PassportAppointmentService(marshalled_data.unlimited_wait) \
        .schedule_passport_appointment_service(marshalled_data.client_login, marshalled_data.client_appointment_data)
    if not success:
        response = Response('failed', 'failed to schedule passport appointment')
        return FlaskResponse(json.dumps(response.__dict__, status=HTTPStatus.OK))

    response = Response('success', 'successfully schedule passport appointment')
    return FlaskResponse(json.dumps(response.__dict__, status=HTTPStatus.OK))


@routes.route('/prenotami-esteri/get_unscheduled_passport_appointment', methods=['GET'])
def get_unscheduled_multiple_passport_appointment():
    logger.info('Searching for unscheduled passport appointments in database')
    result = DatabaseService().retrieve_unfinished_multiple_passport_appointment_scheduling()
    return FlaskResponse(json.dumps(result, default=lambda o: o.__dict__), status=HTTPStatus.OK)


@routes.route('/prenotami-esteri/save_passport_appointment', methods=['POST'])
def save_multiple_passport_appointment():
    logger.info('Starting passport appointment procedure')
    data = PassportAppointment(**json.loads(request.data))
    appointment = PassportAppointmentService(data.unlimited_wait).save_multiple_passport_appointment(data)
    if not appointment:
        response = Response('failed', 'Something failed while trying to save passport appointment data')
        return FlaskResponse(json.dumps(response.__dict__), HTTPStatus.BAD_REQUEST)

    response = Response('success', 'Successfully saved passport appointment data')
    return FlaskResponse(json.dumps(response.__dict__), HTTPStatus.OK)
