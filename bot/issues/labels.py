import logging
from bot.common.request_client import RequestHandler


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
requestClient = RequestHandler()


def add_labels_to_issue(url, labels):
    # https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/37/labels
    # {"labels":["need-review","ready-for-merge"]}
    body = {
        "labels": labels
    }
    return requestClient.visit('POST', url, data=body)


def remove_label_from_issue():
    pass


def remove_labels_from_issue():
    pass


def set_labels_for_issue(url, labels):
    # https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/37/labels
    body = {
        "labels": labels
    }
    return requestClient.visit('PUT', url, data=body)


def list_labels_for_issue():
    pass
