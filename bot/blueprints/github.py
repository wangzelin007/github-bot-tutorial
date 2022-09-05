# -*- coding: utf-8 -*-
import os

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, send_from_directory
from bot.extensions import db
from flask import Flask, request, g, url_for
from bot.issues.issues import open_issue
from bot.pull_request.pull_request import open_pull_request
from bot.scheduler import scheduler
import os
import hmac
import hashlib
import typing as t
from apiflask import APIFlask, HTTPBasicAuth, APIBlueprint
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from bot.models import ConfigModel, ConfigOutSchema, EnvModel, EnvOutSchema
import json
from bot.common.request_client import RequestHandler
from flask_sqlalchemy import SQLAlchemy
import logging


github_bp = APIBlueprint('github', __name__)


app = Flask('bot')
auth = HTTPBasicAuth()
# logging.basicConfig(
#     filename=os.getenv('LOG_FILE', './app.log'),
#     format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]',
#     level = logging.DEBUG,
#     filemode='a',
#     datefmt='%Y-%m-%d %I:%M:%S %p')
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# logger.addHandler(ch)
requestClient = RequestHandler()


users = {
    'azclitools': generate_password_hash(os.getenv('GH_SECRET', 'secret string')),
}


# @app.before_first_request
# def init_database():
#     db.create_all()
#     db_data = url_for('api.list_env')
#     if not db_data:
#         update db_data
        # update_config()
    # else:
    #     For each row, get_file_from_github
    #     update db_data
        # update_config(db_data)
        # pass


def update_config(db_data=None):
    if not db_data:
        db_data = url_for('api.add_env')
        etag, config = get_file_from_github(g.config_url)
        url_for('api.add_config')
    else:
        for row in db_data:
            etag, config = get_file_from_github(row.config_url)
            if etag and config:
                url_for('api.add_config')


def get_file_from_github(config_url, etag=None):
    # send headers with If-None-Match
    headers = {'If-None-Match': etag} if etag else None
    r = requestClient.visit(
        'GET',
        config_url,
        headers = headers
    )
    print(json.dumps(dict(r.headers), sort_keys=False, indent=4))
    print(r.text)
    return r.jons()


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
    app.logger.info("====== action: %s ======" % action)
    try:
        action_map[type][action](event)
    except Exception as e:
        raise e


# github webhook with secret
@app.route('/github', methods=['POST'])
@verify_signature
def webhook():
    event_type = request.headers.get('X-GitHub-Event')
    app.logger.info("====== event type: %s ======" % event_type)
    if event_type in ['pull_request', 'issues']:
        event = request.json
        g.base_url = event['repository']['url']
        app.logger.info("====== event: %s ======" % event)
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
            app.logger.info("====== unsupported action: %s %s======", event_type, action)
            return 'Not support action'
    else:
        app.logger.info("====== unsupported event type: %s ======", event_type)
        return 'Not support type'


# Azure DevOps webhook with username:password
@github_bp.route('/devops', methods=['POST'])
@github_bp.auth_required(auth)
def webhook2():
    event = request.json
    print(event)
    app.logger.info("====== event: %s ======", event)
    return 'Hello azclitools!'


@github_bp.route('/test', methods=['POST'])
@verify_signature
def webhook3():
    event = request.json
    print(event)
    app.logger.info("====== event: %s ======", event)
    return 'Hello azclitools!'


# @app.get('/configs')
@github_bp.get('/configs')
@github_bp.output(ConfigOutSchema(many=True))
def list_config():
    data = ConfigModel.query.all()
    logger.debug('no log xxxx ??????')
    return data


# @app.get('/config')
@github_bp.get('/config')
@github_bp.output(ConfigOutSchema)
def get_config():
    paras = request.json
    owner = paras['owner']
    repo = paras['repo']
    data = ConfigModel.query.filter_by(owner=owner, repo=repo).first()
    return data


@github_bp.post('/config')
@github_bp.output(ConfigOutSchema, 201)
def add_config():
    with open('../.github/fabricbot.json') as f:
        config = json.load(f)
    data = {
        "owner": 1,
        "repo": "azure-cli.json",
        "config": json.dumps(config)
    }
    db_data = ConfigModel(**data)
    db.session.add(db_data)
    db.session.commit()
    return db_data


@github_bp.get('/env')
@github_bp.output(EnvOutSchema(many=True))
def list_env():
    data = EnvModel.query.all()
    return data


@github_bp.post('/env')
@github_bp.output(EnvOutSchema(many=True))
def add_env():
    etag, config = get_file_from_github(g.config_url)
    data = {
        # TODO
        "owner": "wangzelin007",
        "repo": "github-bot-tutorial",
        "etag": etag,
        # TODO
        "config_url": g.config_url,
        # base_url = String(),
        # issue_url = String(),
        # pr_url = String(),
    }
    db_data = EnvModel(**data)
    db.session.add(db_data)
    db.session.commit()
    return db_data


# if __name__ == '__main__':
#     app.secret_key = os.getenv('GH_SECRET', 'secret string')
#     app.config.from_object(Config())
#     scheduler.init_app(app)
#     db.init_app(app)
#     scheduler.start()
#     app.run(debug=True)
