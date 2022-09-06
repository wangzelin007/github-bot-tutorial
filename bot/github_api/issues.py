from bot import constant
import logging
import requests
from bot.github_api import milestone
from bot.request_client import RequestHandler


logger = logging.getLogger('bot')
requestClient = RequestHandler()


def open_issue(event):
    # https://api.github.com/repos/{OWNER}/{REPO}/issues/{NUMBER}/comments
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
    update_issue(issue_url, milestone=ms)


def comment_issue(url, message):
    # https://api.github.com/repos/{OWNER}/{REPO}/issues/{NUMBER}/comments
    body = {
        'body': message,
    }
    # try:
    #     r = requests.post(url, json=body, headers=constant.HEADERS)
    # except requests.RequestException as e:
    #     logger.debug('response: %s', r)
    #     logger.debug('text: %s', r.text)
    #     logger.debug('code: %s', r.status_code)
    #     raise e
    r = requestClient.visit('POST', url, json=body)


def update_issue(url, **kwargs):
    # https://api.github.com/repos/{OWNER}/{REPO}/issues/{NUMBER}
    body = {}
    milestone = kwargs.pop("milestone", {})
    logger.debug('assign milestone: %s', milestone)
    if milestone:
        # get milestone id
        body['milestone'] = milestone[0]
    # try:
    #     r = requests.patch(url, json=body, headers=constant.HEADERS)
    # except requests.RequestException as e:
    #     logger.debug('response: %s', r)
    #     logger.debug('text: %s', r.text)
    #     logger.debug('code: %s', r.status_code)
    #     raise e
    logger.debug('update_issue: url-> %s, body-> %s', url, body)
    r = requestClient.visit('PATCH', url, json=body)


def list_issues(url, milestone=None, state=None, draft=None, label=None, type='issues'):
    # https://api.github.com/repos/{OWNER}/{REPO}/issues?key=value
    params = {}
    if milestone:
        params['milestone'] = milestone
    if state:
        params['state'] = state
    if label:
        params['label'] = label
    # try:
    #     r = requests.get(url, params=params, headers=constant.HEADERS)
    # except requests.RequestException as e:
    #     logger.debug('response: %s', r)
    #     logger.debug('text: %s', r.text)
    #     logger.debug('code: %s', r.status_code)
    #     raise e
    r = requestClient.visit('GET', url, params=params)
    ref = r.json()
    if type == 'issues':
        ref = filter(is_issue, ref)
    else:
        ref = filter(is_pull_request, ref)
        if draft is False:
            ref = filter(lambda i: i['draft'] is False, ref)
        elif draft is True:
            ref = filter(lambda i: i['draft'] is True, ref)
    return ref


def is_issue(ref):
    for i in ref:
        if i['html_url'].split('/')[-2] == 'issues':
            return True
        else:
            return False


def is_pull_request(ref):
    for i in ref:
        if i['html_url'].split('/')[-2] == 'pull':
            return True
        else:
            return False


def get_issue(issue_url):
    # https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/32
    return requestClient.visit('GET', issue_url)
