import logging
from bot.utils.request_client import RequestHandler
from flask import g


logger = logging.getLogger('bot')
requestClient = RequestHandler()


def add_labels_to_issue(url, labels):
    # https://api.github.com/repos/{OWNER}/{REPO}/issues/37/labels
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
    # https://api.github.com/repos/{OWNER}/{REPO}/issues/37/labels
    body = {
        "labels": labels
    }
    return requestClient.visit('PUT', url, data=body)


def list_labels_for_issue():
    pass
