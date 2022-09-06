# coding=utf-8

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask_apscheduler import APScheduler
import logging
import datetime

import bot.constant
from bot.github_api import issues, pull_request, labels, milestone
from flask import g
import os


scheduler = APScheduler()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


USERNAME = os.getenv('BOT_DB_USER', 'secret string')
PASSWORD = os.getenv('BOT_DB_PASS', 'secret string')


class Config(object):
    SCHEDULER_JOBSTORES = {
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://your-username:your-password@localhost/your-schema?ssl_ca=BaltimoreCyberTrustRoot.crt.pem'
        # 'default': SQLAlchemyJobStore(url='sqlite:///flask_context.db')
        'default': SQLAlchemyJobStore(url=f'mysql+pymysql://{USERNAME}:{PASSWORD}@azure-cli-bot-db-dev.mysql.database.azure.com/azure_cli_bot_dev?ssl_ca=.github/DigiCertGlobalRootCA.crt.pem')
    }
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    SCHEDULER_API_ENABLED = True


# Notify reviewer that milestone is less than ten days, need to review it ASAP
# @scheduler.task('interval', id='check_pull_request', seconds=5184000, misfire_grace_time=900)
# def job1():
#     # TODO config
#     url = 'https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues'
#     current_milestone = milestone.get_current_milestone()
#     if milestone.get_remain_days_of_current_milestone(current_milestone, datetime.datetime.now()) < 10:
#         pull_requests = issues.list_issues(url, milestone=current_milestone, state='opened', draft=False, type='pull')
#         for i in pull_requests:
#             # TODO config
#             issue_url = i['html_url']
#             comment_url = issue_url + '/comments'
#             label_url = issue_url + '/labels'
#             if 'need-review' not in i['labels'] and 'ready-for-merge' not in i['labels']:
#                 # if pull_request.is_ready_for_merge():
#                 #     labels.add_label('ready-for-merge')
#                 #     continue
#                 # TODO only get not reviewer
#                 # reviewers = pull_request.get_reviewers_in_pull_request(i)
#                 # comment_url = ''
#                 # msg = ''
#                 # for reviewer in reviewers:
#                 #     msg += f"@{reviewer} "
#                 #     msg += "\nNote that the milestone is coming to an end, " \
#                 #            "please review the pull request when you have time."
#                 msg = "\nNote that the milestone is coming to an end, " \
#                        "please review the pull request when you have time."
#                 issues.comment_issue(comment_url, msg)
#                 labels.add_label(label_url, ['need-review'])
#             else:
#                 # if pull_request.is_ready_for_merge():
#                 #     issues.set_label('need-review', 'ready-for-merge')
#                 pass


# Move unresolved PRs and issues from the previous milestone to the current milestone
# @scheduler.task('interval', id='move_to_next_milestone', seconds=5184000, misfire_grace_time=900)
# def job2():
#     previous_milestone = milestone.get_previous_milestone()
#     current_milestone = milestone.get_current_milestone()
#     issues_url = '/'.join([g.base_url, 'issues'])
#     if previous_milestone:
#         # get PRs and issues in the previous milestone
#         unresolved_items = issues.list_issues(issues_url, milestone=previous_milestone, state='opened')
#         for item in unresolved_items:
#             # set milestone to current_mileston
#             issue_url =  item['url']
#             issues.update_issue(issue_url, milestone=current_milestone)
#             # comment
#             comment_url = '/'.join([issue_url, 'comments'])
#             msg = 'Since this issue/pr was not resolved in the previous milestone, move it to the next milestone.'
#             issues.comment_issue(comment_url, msg)
#     logger.info('Execute crontab move_to_next_milestone success!')
# @scheduler.task('interval', id='test', seconds=5, misfire_grace_time=900)
# def job2():
#     logger.info('Execute crontab test success!')
#     from datetime import datetime
#     logger.info(datetime.now())
