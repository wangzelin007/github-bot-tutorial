import constant
import logging
import requests


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def issue_opened(event):
    # https://docs.github.com/en/rest/issues/comments
    url = event["issue"]["comments_url"]
    author = event["issue"]["user"]["login"]
    message = f"Thanks for the report @{author}! We will look into it ASAP!"
    logger.info('====== message: %s ======' % message)
    body = {
        'body': message,
    }
    try:
        r = requests.post(url, json=body, headers=constant.headers)
    except requests.RequestException as e:
        raise e
