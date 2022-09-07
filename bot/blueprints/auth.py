from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import jwt
import os
import requests
import time


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

fname = 'azure-cli-bot.2022-08-23.private-key.pem'
cert_str = open(fname, 'r').read()
cert_bytes = cert_str.encode()
private_key = default_backend().load_pem_private_key(cert_bytes, None)


def app_headers():
    time_since_epoch_in_seconds = int(time.time())

    payload = {
        # issued at time
        'iat': time_since_epoch_in_seconds,
        # JWT expiration time (10 minute maximum)
        'exp': time_since_epoch_in_seconds + (10 * 60),
        # GitHub App's identifier
        'iss': os.getenv('app_identify_id')
    }

    actual_jwt = jwt.encode(payload, private_key, algorithm='RS256')
    headers = {"Authorization": "Bearer {}".format(actual_jwt),
               "Accept": "application/vnd.github.machine-man-preview+json"}
    return headers


# resp = requests.get('https://api.github.com/app', headers=app_headers())

installation_id = os.getenv('installation_id')
resp = requests.post('https://api.github.com/app/installations/{}/access_tokens'.format(installation_id),
                     headers=app_headers())
print('Code: ', resp.status_code)
print('Content: ', resp.content.decode())

headers = {"Authorization": "token {}".format(resp.json()['token']),
           "Accept": "application/vnd.github.machine-man-preview+json"}
# print(headers)
resp = requests.get('https://api.github.com/installation/repositories', headers=headers)
print('Code: ', resp.status_code)
print('Content: ', resp.content.decode())

resp = requests.post('https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/1/labels',
                     json=["bug"], headers=headers)
print('Code: ', resp.status_code)
print('Content: ', resp.content.decode())
