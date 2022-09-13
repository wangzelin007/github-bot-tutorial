from bot.utils.request_client import RequestHandler
from flask import g
import logging


logger = logging.getLogger('bot')
requestClient = RequestHandler()


def comment_issue(comment):
    # https://api.github.com/repos/{OWNER}/{REPO}/issues/{NUMBER}/comments
    body = {
        'body': comment,
    }
    r = requestClient.visit('POST', g.comment_url, json=body)


def update_issue(url, **kwargs):
    # https://api.github.com/repos/{OWNER}/{REPO}/issues/{NUMBER}
    body = {}
    milestone = kwargs.pop("milestone", {})
    logger.debug('assign milestone: %s', milestone)
    if milestone:
        # get milestone id
        body['milestone'] = milestone[0]
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
    # https://api.github.com/repos/{OWNER}/{REPO}/issues/32
    return requestClient.visit('GET', issue_url)
