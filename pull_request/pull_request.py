import constant
import logging
import requests
from milestone import milestone


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def pr_opened(event):
    # common comment use issue rest api
    # https://api.github.com/repos/{owner}/{repo}/issues/{number}/
    issue_url = event['pull_request']['issue_url']
    comment_url = issue_url + '/comments'
    author = event['pull_request']['user']['login']
    message = f"Thanks for the contribution @{author}!"
    logger.info("====== message: %s ======" % message)
    pull_request_comment(comment_url, message)
    # get created_at
    created_at = event['pull_request']['created_at']
    logger.info('====== created_at: %s ======' % created_at)
    # select milestone
    msg, ms = milestone.select_milestone(created_at, author, ms_type='pull_request')
    if msg:
        pull_request_comment(comment_url, msg)
    # assign milestone
    # https://api.github.com/repos/{owner}/{repo}/issues/26
    update_pull_request(issue_url, milestone=ms)


def pull_request_comment(url, message):
    body = {
        'body': message,
    }
    try:
        r = requests.post(url, json=body, headers=constant.headers)
    except requests.RequestException as e:
        logger.debug('response: %s', r)
        logger.debug('text: %s', r.text)
        logger.debug('code: %s', r.status_code)
        raise e


def update_pull_request(url, **kwargs):
    body = {}
    milestone = kwargs.pop("milestone", {})
    if milestone:
        body['milestone'] = milestone
    try:
        r = requests.post(url, json=body, headers=constant.headers)
    except requests.RequestException as e:
        logger.debug('response: %s', r)
        logger.debug('text: %s', r.text)
        logger.debug('code: %s', r.status_code)
        raise e