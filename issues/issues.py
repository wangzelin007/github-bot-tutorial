import constant
import logging
import requests
from milestone import milestone


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def open_issue(event):
    # https://api.github.com/repos/{owner}/{repo}/issues/{number}/comments
    issue_url = event['issue']['url']
    comment_url = event['issue']['comments_url']
    author = event['issue']['user']['login']
    message = f"Thanks for the report @{author}! We will look into it ASAP!"
    logger.info('====== message: %s ======' % message)
    comment_issue(comment_url, message)
    # get created_at
    created_at =  event['issue']['created_at']
    logger.info('====== created_at: %s ======' % created_at)
    # select milestone
    ms, msg = milestone.select_milestone(created_at, author, ms_type='issue')
    if msg:
        comment_issue(comment_url, msg)
    # assign milestone
    # https://api.github.com/repos/{owner}/{repo}/issues/26
    update_issue(issue_url, milestone=ms)


def comment_issue(url, message):
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


def update_issue(url, **kwargs):
    body = {}
    milestone = kwargs.pop("milestone", {})
    if milestone:
        # get milestone id
        body['milestone'] = milestone[0]
    try:
        r = requests.patch(url, json=body, headers=constant.headers)
    except requests.RequestException as e:
        logger.debug('response: %s', r)
        logger.debug('text: %s', r.text)
        logger.debug('code: %s', r.status_code)
        raise e
