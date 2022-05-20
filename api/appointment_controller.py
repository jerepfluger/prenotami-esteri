import json
from http import HTTPStatus

from flask import Response as FlaskResponse
from flask import request

from dto.base_appointment import Appointment
from dto.rest.response import Response
from helpers.logger import logger
from service.appointment_service import AppointmentService
from service.database_service import DatabaseService
from . import routes


@routes.route("/prenotami-esteri/run_unscheduled_appointment", methods=["POST"])
def run_unscheduled_appointment():
    logger.info('Searching for unscheduled appointments in database')
    unscheduled_appointment = get_unscheduled_appointment()
    if unscheduled_appointment.status_code == 200 and unscheduled_appointment.data.decode('utf-8') != '{}':
        logger.info('Unscheduled appointment found. Start processing')
        return schedule_appointment_internal(json.loads(unscheduled_appointment.data))
    logger.info('No unscheduled appointments were found')
    response = Response('success', 'No unscheduled appointments found')
    return FlaskResponse(json.dumps(response.__dict__), status=200)


@routes.route("/prenotami-esteri/get_unscheduled_appointment", methods=["GET"])
def get_unscheduled_appointment():
    logger.info('Searching for unscheduled appointments in database')
    result = DatabaseService().retrieve_unfinished_appointment_scheduling()
    return FlaskResponse(json.dumps(result, default=lambda o: o.__dict__), status=HTTPStatus.OK)


@routes.route("/prenotami-esteri/register_appointment_in_database", methods=["POST"])
def schedule_appointment_via_database():
    logger.info('Saving appointment to be scheduled in database')
    appointment_data = Appointment(**json.loads(request.data))
    try:
        result = DatabaseService().save_new_appointment_in_database(appointment_data)
        response = Response('success', 'Successfully saved appointment {} into database'.format(result))
        return FlaskResponse(json.dumps(response.__dict__), status=HTTPStatus.OK)
    except Exception as ex:
        logger.exception(ex)
        response = Response('failed', 'An exception ocurred')
        return FlaskResponse(json.dumps(response.__dict__), status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.route("/prenotami-esteri/schedule_appointment", methods=["POST"])
def schedule_appointment():
    logger.info('Beginning scheduling appointment process from json')
    appointment_data = json.loads(request.data)
    return schedule_appointment_internal(appointment_data)


@routes.route("/prenotami-esteri/schedule_appointment_internal", methods=["POST"])
def schedule_appointment_internal(jsonized_data):
    logger.info('Beginning scheduling appointment process')
    appointment_data = jsonized_data
    # FIXME: Sanitize data here
    success = AppointmentService().schedule_generic_appointment(appointment_data)
    if success:
        response = Response('success', 'Successfully scheduled an appointment')
        return FlaskResponse(json.dumps(response.__dict__), status=HTTPStatus.OK)
    response = Response('failed', 'Unable to schedule the appointment')
    return FlaskResponse(json.dumps(response.__dict__), status=HTTPStatus.NOT_FOUND)
