from flask_apscheduler import APScheduler
import datetime
import logging

scheduler = APScheduler()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


# interval examples
@scheduler.task('interval', id='do_job_1', seconds=30, misfire_grace_time=900)
def job1():
    logger.info(str(datetime.datetime.now()) + ' Job 1 executed')
