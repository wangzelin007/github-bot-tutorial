import requests
from bot.constant import HEADERS
import logging

logger = logging.getLogger('bot')


class RequestHandler:
    def __init__(self):
        self.s = requests.session()
        self.headers = HEADERS

    def visit(self, method, url, params=None, data=None, json=None, headers=None, **kwargs):
        with self.s:
            try:
                if headers:
                    self.headers = {**self.headers, **headers}
                # logger.info("====== request headers: %s ======", self.headers)
                r = requests.session().request(method, url, params=params, data=data, json=json, headers=self.headers,
                                               **kwargs)
                if r.status_code >= 400:
                    logger.debug('status_code: %s', r.status_code)
                    raise requests.RequestException
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
