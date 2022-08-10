import constant
import logging
import requests


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def pr_opened(event):
    # common comment use issue rest api
    # https://docs.github.com/en/rest/issues/comments
    url = event['pull_request']['issue_url']
    author = event['pull_request']['user']['login']
    message = f"Thanks for the contribution @{author}!"
    logger.info("====== message: %s ======" % message)
    body = {
        'body': message,
    }
    try:
        r = requests.post(url, json=body, headers=constant.headers)
    except requests.RequestException as e:
        raise e
