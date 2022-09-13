from apiflask import APIFlask
from bot.extensions import db, cache
from bot import database
from flask import request, g
from bot import scheduled
from bot.utils.request_client import RequestHandler
import logging
import json
from bot.mapping import func_mapping
from bot.utils.case import to_snack_case


app = APIFlask('bot')
logger = logging.getLogger('bot')
requestClient = RequestHandler()


def update_config(owner, repo):
    if cache.get(g.config_etag):
        etag, config = download_file_from_github(g.config_url, cache.get(g.config_etag))
    else:
        etag, config = download_file_from_github(g.config_url)
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



def download_file_from_github(config_url, etag=None):
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
            uq_variable = to_snack_case('_'.join([g.owner, g.repo, task_id, variable]))
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
