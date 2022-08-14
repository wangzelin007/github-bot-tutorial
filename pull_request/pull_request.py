import logging

import issues.issues
from milestone import milestone
from issues import issues


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def open_pull_request(event):
    # common comment use issue rest api
    # https://api.github.com/repos/{owner}/{repo}/issues/{number}/
    issue_url = event['pull_request']['issue_url']
    comment_url = issue_url + '/comments'
    author = event['pull_request']['user']['login']
    message = f"Thanks for the contribution @{author}!"
    logger.info("====== message: %s ======" % message)
    issues.comment_issue(comment_url, message)
    # get created_at
    created_at = event['pull_request']['created_at']
    logger.info('====== created_at: %s ======' % created_at)
    # select milestone
    msg, ms = milestone.select_milestone(created_at, author, ms_type='pull_request')
    if msg:
        issues.comment_issue(comment_url, msg)
    # assign milestone
    # https://api.github.com/repos/{owner}/{repo}/issues/26
    issues.update_issue(issue_url, milestone=ms)
