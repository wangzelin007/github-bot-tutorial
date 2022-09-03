from flask import Flask, request, g
from issues.issues import open_issue
from pull_request.pull_request import open_pull_request
from scheduler import scheduler
import logging
import os
import hmac
import hashlib
# import typing as t
# from apiflask import APIFlask, HTTPBasicAuth
# from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
# app = APIFlask(__name__)
# auth = HTTPBasicAuth()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


# users = {
#     'azclitools': generate_password_hash(os.getenv('GH_SECRET', 'secret string')),
# }


class Config(object):
    SCHEDULER_API_ENABLED = True


def route_base_action(action, event, type):
    """
    route an issue base on action.
    """
    # issues:
    # opened, edited, deleted, pinned, unpinned, closed, reopened, assigned, unassigned,
    # labeled, unlabeled, locked, unlocked, transferred, milestoned, or demilestoned
    # pull requests:
    # assigned, auto_merge_disabled, auto_merge_enabled, closed, converted_to_draft
    # edited, labeled, locked, opened, ready_for_review, reopened, review_request_removed
    # review_requested, synchronize, unassigned, unlabeled, unlocked
    action_map = {
        'issue': {
            'opened': open_issue,
        },
        'pull_request': {
            "opened": open_pull_request,
        }
    }
    logger.info("====== action: %s ======" % action)
    try:
        action_map[type][action](event)
    except Exception as e:
        raise e


@app.route('/webhook', methods=['POST'])
def webhook():
    event_type = request.headers.get('X-GitHub-Event')
    logger.info("====== event type: %s ======" % event_type)
    if event_type in ['pull_request', 'issues']:
        event = request.json
        g.base_url = event['repository']['url']
        logger.info("====== event: %s ======" % event)
        action = event['action']
        if action in ['opened']:
            if 'issue' in event.keys():
                type = 'issue'
            elif 'pull_request' in event.keys():
                type = 'pull_request'
            route_base_action(action, event, type)
            return 'Hello github, I am azure cli bot'
        else:
            logger.info("====== unsupported action: %s %s======", event_type, action)
            return 'Not support action'
    else:
        logger.info("====== unsupported event type: %s ======", event_type)
        return 'Not support type'


# test secret
# for Azure DevOps
# @app.route('/webhook2', methods=['POST'])
# @app.auth_required(auth)
# def webhook2():
#     event = request.json
#     print(event)
#     logger.info("====== event: %s ======", event)
#     return 'Hello azclitools!'


# @auth.verify_password
# def verify_password(username: str, password: str) -> t.Union[str, None]:
#     if (
#         username in users
#         and check_password_hash(users[username], password)
#     ):
#         return username
#     return None


# test secret
# for GitHub sha256

# def verify_signature(payload_body):
#   signature = 'sha256=' + OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new('sha256'), ENV['SECRET_TOKEN'], payload_body)
#   return halt 500, "Signatures didn't match!" unless Rack::Utils.secure_compare(signature, request.env['HTTP_X_HUB_SIGNATURE_256'])


# x-hub-signature-256
def validate_signature():
    key = bytes(os.getenv('GH_SECRET', 'secret string'), 'utf-8')
    expected_signature = hmac.new(key=key, msg=request.data, digestmod=hashlib.sha256).hexdigest()
    x_hub_signature_256 = request.headers.get('x-hub-signature-256')
    if x_hub_signature_256:
        incoming_signature = x_hub_signature_256.split('sha256=')[-1].strip()
        if not hmac.compare_digest(incoming_signature, expected_signature):
            return False
        return True
    return False


# @app.post('/github')
@app.route('/github', methods=['POST'])
def webhook3():
    if validate_signature():
        event = request.json
        print(event)
        logger.info("====== event: %s ======", event)
        return 'Hello azclitools!'
    else:
        return 'Error', 500


if __name__ == '__main__':
    app.secret_key = os.getenv('GH_SECRET', 'secret string')
    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True)
