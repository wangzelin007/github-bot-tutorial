import requests
from constant import HEADERS
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class RequestHandler:
    def __init__(self):
        self.s = requests.session()
        self.headers = HEADERS

    def visit(self, method, url, params=None, data=None, json=None, **kwargs):
        with self.s:
            try:
                r = requests.session().request(method, url, params=params, data=data, json=json, headers=self.headers,
                                               **kwargs)
                logger.debug('status_code: %s', r.status_code)
            except requests.RequestException as e:
                logger.debug('response: %s', r)
                logger.debug('code: %s', r.status_code)
                if r.text:
                    logger.debug('text: %s', r.text)
                logger.error(e)
                raise e
            return r


if __name__ == '__main__':
    url = 'https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/32'
    params = None
    requestClient = RequestHandler()
    request_data = requestClient.visit('GET', url, params=params)
    print(request_data.text)
