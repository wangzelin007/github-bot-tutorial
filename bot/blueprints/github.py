# -*- coding: utf-8 -*-
from apiflask import APIFlask, HTTPBasicAuth, APIBlueprint
from bot import database
from bot.constant import CONFIG_BASE_URL, CONFIG_URL_POSTFIX
from bot.extensions import db, cache
from bot.mapping import func_mapping
from bot.models import ConfigOutSchema, EnvOutSchema
from bot.request_client import RequestHandler
from bot.scheduled import scheduler
from flask import Flask, request, g, url_for
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import hmac
import json
import logging
import os
import typing as t
from bot import scheduled


github_bp = APIBlueprint('github', __name__)
app = APIFlask('bot')
auth = HTTPBasicAuth()
requestClient = RequestHandler()
logger = logging.getLogger('bot')


users = {
    'azclitools': generate_password_hash(os.getenv('GH_SECRET', 'secret string')),
}


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
        g.config_etag = '_'.join([g.owner, g.repo, 'etag']).replace('-', '_')
        g.config_cache = '_'.join([g.owner, g.repo, 'config']).replace('-', '_')

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


def update_config(owner, repo):
    if cache.get(g.config_etag):
        etag, config = get_file_from_github(g.config_url, cache.get(g.config_etag))
    else:
        etag, config = get_file_from_github(g.config_url)
    if etag and config:
        if cache.get(g.config_etag):
            database.update_env(owner, repo, etag)
            database.update_config(owner, repo, config)
            update_scheduled(config)
        else:
            database.add_env(owner, repo, etag)
            database.add_config(owner, repo, config)
            add_scheduled()
        cache.set(g.config_cache, config)
        cache.set(g.config_etag, etag)
        return
        # TODO: update Schedule job
        # TODO: trigger azure-cli-bot.json 发生变化
        # TODO: 判断是否 scheduled task 发生变化
        # TODO: remove task
        # TODO: add task


def update_scheduled(config):
    scheduled_tasks = [task['taskType'] == 'scheduled' for task in config]
    old_scheduled_tasks = [task['taskType'] == 'scheduled' for task in cache.get(g.config_cache)]
    # tasks (name1, name2)
    # old tasks (name2, name4)
    tasks = set([task['taskName'] for task in scheduled_tasks])
    old_tasks = set([task['taskName'] for task in old_scheduled_tasks])
    add_tasks = tasks - old_tasks
    delete_tasks = old_tasks - tasks
    update_tasks = tasks & old_tasks
    if add_tasks:
        pass

    if delete_tasks:
        pass

    # if scheduled_task == old_scheduled_task
    # skip
    # if scheduled_task != old_scheduled_task
    # delete old scheduled task
    # add scheduled task
    if update_tasks:
        pass


def add_scheduled(config):
    scheduled_tasks = [task['taskType'] == 'scheduled' for task in config]
    for task in scheduled_tasks:
        # add scheduled task
        id = task.pop('taskName')
        task.pop('taskType')
        frequency = task.pop('frequency')
        if frequency['type'] == 'date':
            interval = {
                "run_date": frequency['type']['run_date']
            }
        elif frequency['type'] == 'interval':
            if 'seconds' in frequency:
                seconds = frequency['seconds']
            elif 'minutes' in frequency:
                seconds = frequency['minutes'] * 60
            elif 'hours' in frequency:
                seconds = frequency['hours'] * 3600
            elif 'days' in frequency:
                seconds = frequency['days'] * 86400
            interval = {
                "seconds": seconds
            }
        elif frequency['type'] == 'cron':
            interval = {
                'year': frequency['year'],
                'month': frequency['month'],
                'day': frequency['day'],
                'minute': frequency['minute'],
            }
        func = parse_scheduled
        kwargs = task
        scheduled.add_job(id, type, func, kwargs=kwargs, **interval)


def parse_scheduled(task):
    # TODO test g in scheduled task
    task_id = '0'
    for condition in task['conditions']:
        operator = condition.get('operator', None)
        if operator:
            flag = dfs_op(task_id, condition)
        else:
            func = condition['name']
            parameters = condition['parameters']
            parameters = parse_parameters(task_id, parameters, **g.kwargs)
            p = struct(**parameters)
            r = add_scheduled(func, **parameters)
            flag = True if r else False
            if 'set_variable' in condition:
                for k, v in condition['set_variable'].items():
                    _, variable = get_variable(task_id, k)
                    g.__setattr__(variable, eval(v))
        # flag = True and reversed = False
        if flag and 'actions' in condition:
            for action in condition['actions']:
                reversed = action.get('reversed', False)
                if not reversed:
                    func = action['name']
                    parameters = action['parameters']
                    parameters = parse_parameters(task_id, parameters, **g.kwargs)
                    add_scheduled(func, **parameters)
        # flag = False and reversed = True
        if not flag and 'actions' in condition:
            for action in condition['actions']:
                reversed = action.get('reversed', False)
                if reversed:
                    func = action['name']
                    parameters = action['parameters']
                    parameters = parse_parameters(task_id, parameters, **g.kwargs)
                    add_scheduled(func, **parameters)

    if 'actions' in task:
        for action in task['actions']:
            func = action['name']
            parameters = action['parameters']
            parameters = parse_parameters(task_id, parameters, **g.kwargs)
            add_scheduled(func, **parameters)



def get_file_from_github(config_url, etag=None):
    # send headers with If-None-Match
    # 200 / 304 / TODO
    # TODO: handle no such file
    headers = {'If-None-Match': etag} if etag else None
    r = requestClient.visit(
        'GET',
        config_url,
        headers = headers
    )
    logger.info("====== get_file_from_github status_code %s %s======", r.status_code, r.content)
    etag = r.headers['etag']
    ref = r.json() if r.status_code == 200 else None
    return etag, ref


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


def struct(**entries):
    from types import SimpleNamespace
    if isinstance(entries, dict):
        entries = SimpleNamespace(**entries)
    return entries


def exec_function(func, **parameters):
    func = func_mapping[func]
    ref = func(**parameters)
    if isinstance(ref, dict):
        ref = struct(**ref)
    elif isinstance(ref, list):
        for idx, i in enumerate(ref):
            ref[idx] = struct(**ref[idx])
    return ref


def add_scheduled(func, **parameters):
    func = func_mapping[func]
    ref = func(**parameters)
    if isinstance(ref, dict):
        ref = struct(**ref)
    elif isinstance(ref, list):
        for idx, i in enumerate(ref):
            ref[idx] = struct(**ref[idx])
    return ref

def get_variable(task_id, string):
    import re
    # $(x_days) -> x_days
    regex = r"\$\(.*\)"
    if isinstance(string, str):
        matches = re.finditer(regex, string, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            app.logger.info("====== find variable: %s ======" % string[match.start()+2: match.end()-1])
            variable = string[match.start()+2: match.end()-1]
            # g.owner_repo_1_x_days
            uq_variable = '_'.join([g.owner, g.repo, task_id, variable]).replace('-', '_')
            return variable, uq_variable


def dfs_op(task_id, root):
    if 'operator' not in root:
        func = root['name']
        parameters = root['parameters']
        parameters = parse_parameters(task_id, parameters, **g.kwargs)
        p = struct(**parameters)
        r = exec_function(func, **parameters)
        flag = True if r else False
        if 'set_variable' in root:
            for k, v in root['set_variable'].items():
                _, variable = get_variable(task_id, k)
                g.__setattr__(variable, eval(v))
        if 'actions' in root:
            app.logger.info("====== not support operand action! ======")
            raise Exception
        return flag
    operator = root['operator']
    res = []
    for i in range(len(root['operands'])):
        res.append(dfs_op(task_id, root['operands'][i]))
    if operator == 'and':
        return all(res)
    if operator == 'or':
        return any(res)
    if operator == 'not':
        return not(res[0])


def parse_parameters(task_id, parameters, **kwargs):
    for k, v in parameters.items():
        if isinstance(v, str):
            parameters[k] = parameters[k].format(**kwargs)
        if get_variable(task_id, v):
            ori_variable, variable = get_variable(task_id, v)
            vv = g.__getattr__(variable)
            if not isinstance(vv, (str, int)):
                try:
                    parameters[k] = vv
                except AttributeError:
                    app.logger.info("====== can't get variable %s ======" % variable)
                    raise AttributeError
            else:
                parameters[k] = parameters[k].replace('$('+ori_variable+')', str(vv))
    return parameters


def parse_json(config):
    app.logger.info("====== load config %s ======" % json.dumps(config, indent=2))
    # TODO load parameters to kwargs
    for task_id, task in enumerate(config['tasks']):
        if task['taskType'] == 'trigger' and task['eventType'] == g.event_type:
            task_id = str(task_id)
            for condition in task['conditions']:
                operator = condition.get('operator', None)
                if operator:
                    flag = dfs_op(task_id, condition)
                else:
                    func = condition['name']
                    parameters = condition['parameters']
                    parameters = parse_parameters(task_id, parameters, **g.kwargs)
                    p = struct(**parameters)
                    r = exec_function(func, **parameters)
                    flag = True if r else False
                    if 'set_variable' in condition:
                        for k, v in condition['set_variable'].items():
                            _, variable = get_variable(task_id, k)
                            g.__setattr__(variable, eval(v))
                # flag = True and reversed = False
                if flag and 'actions' in condition:
                    for action in condition['actions']:
                        reversed = action.get('reversed', False)
                        if not reversed:
                            func = action['name']
                            parameters = action['parameters']
                            parameters = parse_parameters(task_id, parameters, **g.kwargs)
                            exec_function(func, **parameters)
                # flag = False and reversed = True
                if not flag and 'actions' in condition:
                    for action in condition['actions']:
                        reversed = action.get('reversed', False)
                        if reversed:
                            func = action['name']
                            parameters = action['parameters']
                            parameters = parse_parameters(task_id, parameters, **g.kwargs)
                            exec_function(func, **parameters)

            if 'actions' in task:
                for action in task['actions']:
                    func = action['name']
                    parameters = action['parameters']
                    parameters = parse_parameters(task_id, parameters, **g.kwargs)
                    exec_function(func, **parameters)


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
    etag, config = get_file_from_github(g.config_url)
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


@github_bp.delete('/schedule/<str:schedule_id>')
def remove_job(schedule_id):
    return scheduled.remove_job(schedule_id)


@github_bp.get('/schedule/<str:schedule_id>')
def get_job(schedule_id):
    return scheduled.get_job(schedule_id)


@github_bp.get('/schedules')
def get_jobs():
    return scheduled.get_jobs()
