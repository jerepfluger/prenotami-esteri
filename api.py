from datetime import datetime, timedelta
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

from api import routes, run_unscheduled_appointment
from config.config import settings

app = Flask(__name__)
app.register_blueprint(routes)


class Api(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._config = settings
        self.name = settings.api.name
        self._port = settings.api.port

    def run(self):
        app.run(host='127.0.0.1', port=self._port)

    @staticmethod
    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    @staticmethod
    @app.route('/health-check')
    def index():
        return 'ok!'

    @staticmethod
    @app.route('/shutdown')
    def shutdown():
        Api.shutdown_server()
        return 'Server shutting down...'


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_unscheduled_appointment,next_run_time=datetime.strptime(datetime.now().strftime("%Y-%m-%d") + " 23:57:00", "%Y-%m-%d %H:%M:%S"))
    scheduler.add_job(run_unscheduled_appointment, next_run_time=datetime.strptime((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") + " 00:07:00", "%Y-%m-%d %H:%M:%S"))
    scheduler.start()

    thread = Api()
    thread.run()
