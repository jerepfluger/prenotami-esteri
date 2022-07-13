from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from api.citizenship_controller import schedule_manual_run


class TaskSchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def add_citizenship_tasks(self):
        if datetime.today().weekday() not in [1, 6]:
            return
        today_run = datetime.strptime(datetime.now().strftime("%Y-%m-%d") + " 23:50:00", "%Y-%m-%d %H:%M:%S")
        tomorrow_run = datetime.strptime(
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") + " 00:05:00","%Y-%m-%d %H:%M:%S")
        self.scheduler.add_job(schedule_manual_run, next_run_time=today_run)
        self.scheduler.add_job(schedule_manual_run, next_run_time=tomorrow_run)

    # TODO: Here I should have some extra schedulers for passports appoitments and other stuff

    def start(self):
        self.add_citizenship_tasks()
        self.scheduler.start()
