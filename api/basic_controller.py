import json

from flask import request
from flask import Response as FlaskResponse

from config.config import settings as config_file
from repositories.base_repository import BaseRepository
from webdrivers.webdriver import WebDriver
from . import routes


@routes.route("/path/to/control", methods=["POST"])
def basic_controller():
    jsonized_data = json.loads(request.data)
    driver = WebDriver().acquire(config_file.crawling.basic_controller_config.webdriver_type)
    BaseRepository().add_record()

    driver.get('http://www.google.com')
    driver.quit()

    return FlaskResponse(
        json.dumps(jsonized_data, default=lambda o: o.__dict__),
        status=200,
        mimetype='application/json'
    )
