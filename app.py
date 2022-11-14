from flask import Flask, request, g
from issues.issues import open_issue
from pull_request.pull_request import open_pull_request
from scheduler import scheduler
import logging
import os
import hmac
import hashlib
import typing as t
from apiflask import APIFlask, HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from db.models import db


# USERNAME = os.getenv('BOT_DB_USER', 'secret string')
# PASSWORD = os.getenv('BOT_DB_PASS', 'secret string')


app = APIFlask(__name__)
auth = HTTPBasicAuth()
logging.basicConfig(
    filename=os.getenv('LOG_FILE', './app.log'),
    format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]',
    level = logging.DEBUG,
    filemode='a',
    datefmt='%Y-%m-%d %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


users = {
    'azclitools': generate_password_hash(os.getenv('GH_SECRET', 'secret string')),
}


class Config(object):
    SCHEDULER_API_ENABLED = True
    # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@azure-cli-bot-db-dev.mysql.database.azure.com/azure_cli_bot_dev?ssl_ca=DigiCertGlobalRootCA.crt.pem'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False


@app.before_first_request
def init_database():
    pass
    # db.create_all()


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


# github webhook with secret
@app.route('/github', methods=['POST'])
@verify_signature
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
                g._author = event['issue']['user']['login']
            elif 'pull_request' in event.keys():
                type = 'pull_request'
                g._author = event['pull_request']['user']['login']
            route_base_action(action, event, type)
            return 'Hello github, I am azure cli bot'
        else:
            logger.info("====== unsupported action: %s %s======", event_type, action)
            return 'Not support action'
    else:
        logger.info("====== unsupported event type: %s ======", event_type)
        return 'Not support type'


# Azure DevOps webhook with username:password
@app.route('/devops', methods=['POST'])
@app.auth_required(auth)
def webhook2():
    event = request.json
    print(event)
    logger.info("====== Run state stage changed: %s ======", event)
    return 'Hello azclitools!'


@app.route('/test', methods=['POST'])
@verify_signature
def webhook3():
    event = request.json
    print(event)
    logger.info("====== event: %s ======", event)
    return 'Hello azclitools!'


if __name__ == '__main__':
    app.secret_key = os.getenv('GH_SECRET', 'secret string')
    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    app.run()
