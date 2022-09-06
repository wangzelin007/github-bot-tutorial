# coding=utf-8

from flask import Flask
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask_apscheduler import APScheduler
import logging
import datetime

from bot import constant
from bot.blueprints import issues, labels, milestone, pull_request
from bot.route import parse_json_file
import os


scheduler = APScheduler()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
app = Flask(__name__)
scheduler = APScheduler()


USERNAME = os.getenv('BOT_DB_USER', 'secret string')
PASSWORD = os.getenv('BOT_DB_PASS', 'secret string')

class Config(object):
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite:///flask_context.db')
        # 'default': SQLAlchemyJobStore(url=f'mysql+pymysql://{USERNAME}:{PASSWORD}@azure-cli-bot-db-dev.mysql.database.azure.com/azure_cli_bot_dev?ssl_ca=.github/DigiCertGlobalRootCA.crt.pem')
    }
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    SCHEDULER_API_ENABLED = True


def this_job(a, b):
    print(a + b)


@app.route("/")
def index():
    return "Congratulations, it's a web app!"


@app.route("/remove_schedule")
def remove_job():
    scheduler.remove_job(job_id="this_job")
    return "job removed"


@app.route("/pause_scheduler")
def pause_scheduler():
    scheduler.pause()
    return "paused scheduler"


@app.route("/resume_scheduler")
def resume_scheduler():
    scheduler.start(paused=True)
    return "resume scheduler"


@app.route("/schedule")
def start_job():
    parse_json_file()
    scheduler.add_job(
        id="this_job",
        trigger="interval",
        seconds=5,
        func=this_job,
        # trigger="cron",
        # year="*",
        # month="*",
        # day="*",
        # minute="*",
        max_instances=2,
        replace_existing=True,
        misfire_grace_time=240,
        args=(1, 2)
    )
    return "job started"


if __name__ == "__main__":
    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    app.run(host="127.0.0.1", port=8080, debug=True)