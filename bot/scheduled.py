# coding=utf-8
import logging
from bot.extensions import scheduler


logger = logging.getLogger(__name__)


def this_job(a, b):
    print(a + b)


def remove_job(id):
    scheduler.remove_job(job_id=id)
    return "job removed"


def pause_scheduler():
    scheduler.pause()
    return "paused scheduler"


def resume_scheduler():
    scheduler.start(paused=True)
    return "resume scheduler"


def start_job(id, type, func, args=None, kwargs=None,
              max_instances=2, misfire_grace_time=240, replace_existing=True, **interval):
    """
    :param int max_instances: maximum number of concurrently running instances allowed for this job
    :param int misfire_grace_time: seconds after the designated runtime that the job is still
        allowed to be run (or ``None`` to allow the job to run no matter how late it is)
    :param bool coalesce: run once instead of many times if the scheduler determines that the
        job should be run more than once in succession
    :param datetime next_run_time: when to first run the job, regardless of the trigger (pass
        ``None`` to add the job as paused)
    :param bool replace_existing: ``True`` to replace an existing job with the same ``id``
        (but retain the number of runs from the existing one)
    date / interval / cron
    trigger="date",
    run_date="2009-11-06 16:30:05",
    trigger="interval",
    seconds=5,
    trigger="cron",
    year="*",
    month="*",
    day="*",
    minute="*",
    args=(1, 2),
    kwargs={"foo": "bar"},
    """
    if type == 'date':
        add_job_params = {
            "trigger": "date",
            "run_date": interval['run_date'],
        }
    elif type == 'interval':
        add_job_params = {
            "trigger": "interval",
            "seconds": interval['seconds'],
        }
    elif type == 'cron':
        add_job_params = {
            "trigger": "cron",
            "year": interval['year'],
            "month": interval['month'],
            "day": interval['day'],
            "minute": interval['minute'],
        }
    if args:
        add_job_params["args"] = args
    if kwargs:
        add_job_params["kwargs"] = kwargs
    add_job_params["max_instances"] = max_instances
    add_job_params["misfire_grace_time"] = misfire_grace_time
    add_job_params["replace_existing"] = replace_existing
    scheduler.add_job(id, func, **add_job_params)

    return "job started"

