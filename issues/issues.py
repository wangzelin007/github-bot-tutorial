import constant
import requests
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def issue_opened(event):
    url = event["issue"]["comments_url"]
    author = event["issue"]["user"]["login"]
    if not event['labels']:
        message = f"Thanks for the report @{author}! I will look into it ASAP! (I'm a bot)."
    else:
        labels = [i['name'] for i in event["labels"]]
        # TODO 多个 label 如何自动回复
        message = f"Thanks for the report @{author}! Transfer to {labels} team!"
    logger.info('====== message: %s ======' % message)
    body = {
        'body': message,
    }
    # https://docs.github.com/en/rest/issues/comments
    try:
        r = requests.post(url, json=body, headers=constant.headers)
    except requests.RequestException as e:
        raise e


def issue_labeled(event):
    url = event["issue"]["comments_url"]
    author = event["issue"]["user"]["login"]
    labels = [i['name'] for i in event["labels"]]
    message = f"Thanks for the report @{author}! Transfer to {labels} team!"
    logger.info('====== message: %s ======' % message)
    body = {
        'body': message,
    }
    # https://docs.github.com/en/rest/issues/comments
    try:
        r = requests.post(url, json=body, headers=constant.headers)
    except requests.RequestException as e:
        raise e