# -*- coding: utf-8 -*-
from apiflask import APIFlask, APIBlueprint
from bot import database
from bot.utils.constant import CONFIG_BASE_URL, CONFIG_URL_POSTFIX
from bot.extensions import db, cache
from bot.models import ConfigOutSchema, EnvOutSchema
from bot.utils.request_client import RequestHandler
from bot.scheduled import scheduler
from flask import request, g
import json
import logging
from bot import scheduled
from bot.orchestration import update_config, parse_json, download_file_from_github
from bot.utils.auth import verify_signature
from bot.utils.case import to_snack_case


github_bp = APIBlueprint('github', __name__)
app = APIFlask('bot')
requestClient = RequestHandler()
logger = logging.getLogger('bot')


@github_bp.before_app_first_request
def init_database():
    db.create_all()


@github_bp.before_request
def init_kwargs():
    g.kwargs = {}
    g.event_type = request.headers.get('X-GitHub-Event')
    event = request.json
    g.action = event['action']
    if (g.event_type == 'issues' and g.action == 'opened') or \
        (g.event_type == 'pull_request' and g.action in ['opened', 'closed']):
        # https://api.github.com/repos/{OWNER}/{REPO}
        g.base_url = event['repository']['url']
        g.owner = g.base_url.split('/')[4]
        g.repo = g.base_url.split('/')[5]
        # https://https://raw.github.com/repos/{OWNER}/{REPO}/HEAD/.github/azure-cli-bot-dev.json
        g.config_url = '/'.join([CONFIG_BASE_URL, g.owner, g.repo, CONFIG_URL_POSTFIX])
        # {OWNER}_{REPO}
        g.config_etag = to_snack_case('_'.join([g.owner, g.repo, 'etag']))
        g.config_cache = to_snack_case('_'.join([g.owner, g.repo, 'config']))

        if g.event_type == 'issues':
            g.kwargs['author'] = event['issue']['user']['login']
            g.created_at = event['issue']['created_at']
            g.issue_url = event['issue']['url']

        elif g.event_type == 'pull_request':
            g.kwargs['author'] = event['pull_request']['user']['login']
            g.created_at = event['pull_request']['created_at']
            g.pull_request_url = event['pull_request']['url']
            g.issue_url = event['pull_request']['issue_url']
            g.pull_request_files_url = '/'.join([g.pull_request_url, 'files'])
        g.milestone_url = g.issue_url
        g.comment_url = g.issue_url

    else:
        app.logger.info("====== unsupported event %s action %s ======", g.event_type, g.action)
        return 'Unsupported GitHub event'


# github webhook with secret
@github_bp.route('/github', methods=['POST'])
@verify_signature
def webhook():
    event = request.json
    if g.event_type in ['pull_request', 'issues'] and g.action == 'opened':
        update_config(g.owner, g.repo)
        parse_json(cache.get(g.config_cache))
        return 'Hello github, I am azure cli bot'
    elif g.event_type == 'pull_request' and g.action == 'closed' and event['pull_request']['merged']:
        # https://raw.github.com/{OWNER}/{REPO}/HEAD/.github/azure-cli-bot-dev.json
        update_config(g.owner, g.repo)


@github_bp.route('/test', methods=['POST'])
@verify_signature
def webhook3():
    app.logger.info("====== event: %s ======", request)
    return 'Hello azclitools!'


@github_bp.get('/configs')
@github_bp.output(ConfigOutSchema(many=True))
def list_config():
    app.logger.info("====== enter list config ======")
    return database.list_config()


@github_bp.get('/config')
@github_bp.output(ConfigOutSchema)
def get_config():
    args = request.args
    owner = args['owner']
    repo = args['repo']
    return database.get_config(owner, repo)


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
    owner = 'xxx'
    repo = 'xxx'
    database.add_config(owner, repo, config)


@github_bp.get('/envs')
@github_bp.output(EnvOutSchema(many=True))
def list_env():
    return database.list_env()


@github_bp.post('/env')
@github_bp.output(EnvOutSchema(many=True))
def add_env():
    config_url = g.config_url
    etag, config = download_file_from_github(g.config_url)
    owner: "wangzelin007"
    repo: "github-bot-tutorial"
    base_url: "g.config_url"
    issue_url: "g.config_url"
    pr_url: "g.config_url"
    return database.add_env(owner, repo, etag, config_url, base_url, issue_url, pr_url)


@github_bp.post('/schedule')
def add_job():
    params = request.json
    job_name = params['id']
    type = params['type']
    func = params['func']
    args = params['args']
    kwargs = params['kwargs']
    interval = params['interval']

    return scheduled.add_job(job_name, type, func, args, kwargs, **interval)


@github_bp.delete('/schedule/<string:schedule_id>')
def remove_job(schedule_id):
    return scheduled.remove_job(schedule_id)


@github_bp.get('/schedule/<string:schedule_id>')
def get_job(schedule_id):
    return scheduled.get_job(schedule_id)


@github_bp.get('/schedules')
def get_jobs():
    return scheduled.get_jobs()
