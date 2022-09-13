from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import jwt
import os
import requests
import time
from functools import wraps
from flask import request
import hmac
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from apiflask import APIFlask, HTTPBasicAuth
import typing as t


app = APIFlask('bot')
auth = HTTPBasicAuth()
# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# fname = os.path.join(os.path.dirname(__file__), 'azure-cli-bot.2022-08-23.private-key.pem')
dotenv_path = os.path.join(os.path.abspath(os.path.join(os.getcwd())), '.env')
fname = os.path.join(os.path.abspath(os.path.join(os.getcwd())), 'azure-cli-bot.2022-08-23.private-key.pem')


cert_str = open(fname, 'r').read()
cert_bytes = cert_str.encode()
private_key = default_backend().load_pem_private_key(cert_bytes, None)


users = {
    'azclitools': generate_password_hash(os.getenv('GH_SECRET', 'secret string')),
}


# GitHub secret decorator
def verify_signature(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if 'x-hub-signature-256' in request.headers:
            x_hub_signature_256 = request.headers.get('x-hub-signature-256')
        if not x_hub_signature_256:
            return {"message": "x-hub-signature-256 is missing!"}, 401
        try:
            key = bytes(os.getenv('GH_SECRET', 'secret string'), 'utf-8')
            expected_signature = hmac.new(key=key, msg=request.data, digestmod=hashlib.sha256).hexdigest()
            app.logger.info("====== expected signature: %s ======", expected_signature)
            incoming_signature = x_hub_signature_256.split('sha256=')[-1].strip()
            if not hmac.compare_digest(incoming_signature, expected_signature):
                return {"message": "x-hub-signature-256 invalid!"}, 401
        except:
            return {"message": "x-hub-signature-256 invalid!"}, 401
        return f(*args, **kwargs)
    return decorator


@auth.verify_password
def verify_password(username: str, password: str) -> t.Union[str, None]:
    if (
        username in users
        and check_password_hash(users[username], password)
    ):
        return username
    return None


def set_jwt_header():
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


@app.before_request
def refresh_expiring_token():
    pass
    # try:
    #     exp_timestamp = get_jwt()["exp"]
    #     now = datetime.now(timezone.utc)
    #     target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
    #     if target_timestamp > exp_timestamp:
    #         access_token = create_access_token(identity=get_jwt_identity())
    #         set_access_cookies(response, access_token)
    #     return response
    # except (RuntimeError, KeyError):
    #     Case where there is not a valid JWT. Just return the original response
    #     return response


def get_token(installation_id):
    pass
    # get token from cache
    # judge by expires_at
    # if is expire or can_not_get_from_cache:
    #     get_new_token
    #     set_to_cache
    # else:
    #     return cache_token


# installation_id = os.getenv('installation_id')
# resp = requests.post('https://api.github.com/app/installations/{}/access_tokens'.format(installation_id),
#                      headers=set_jwt_header())
# print('Code: ', resp.status_code)
# print('Content: ', resp.content.decode())
#
# headers = {"Authorization": "token {}".format(resp.json()['token']),
#            "Accept": "application/vnd.github.machine-man-preview+json"}
# print(headers)
# resp = requests.get('https://api.github.com/installation/repositories', headers=headers)
# print('Code: ', resp.status_code)
# print('Content: ', resp.content.decode())
#
# resp = requests.post('https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/1/labels',
#                      json=["bug"], headers=headers)
# print('Code: ', resp.status_code)
# print('Content: ', resp.content.decode())
#
#
# {
#  "installation_id": "xxx",
#  "token":"ghs_FccX8xqfsLY9cXleFzojsIhIdiOsMr39aJD7",
#  "expires_at":"2022-09-07T16:31:56Z",
#  "permissions":{"issues":"write","metadata":"read","pull_requests":"write"},
#  "repository_selection":"selected",
#  }
