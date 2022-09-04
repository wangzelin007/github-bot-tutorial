from flask import Flask, request, g
from scheduler import scheduler, Config
import os
from constant import HEADERS
import requests
import json


app = Flask(__name__)
kwargs = {'author': 'wangzelin007'}
remain_days = 5
owner = 'Azure'
repo = 'github-bot-tutorial'


def get_file_from_github():
    # If-Modified-Since
    # Last-Modified
    # "ETag": "W/\"2f3a47a5136c897c120c0272c1b5a46470d8202b821e02daf3fa693dde060fc4\"",
    # HEADERS['ETag'] = "W/\"2f3a47a5136c897c120c0272c1b5a46470d8202b821e02daf3fa693dde060fc4\""
    # save ETag
    # send with If-None-Match
    HEADERS['If-None-Match'] = "W/\"2f3a47a5136c897c120c0272c1b5a46470d8202b821e02daf3fa693dde060fc4\""
    r = requests.get('https://raw.github.com/wangzelin007/github-bot-tutorial/demo2/.github/issue_label_bot.yaml', headers=HEADERS)
    import json
    print(json.dumps(dict(r.headers), sort_keys=False, indent=4))
    print(r.text)


def get_variable(task_id, string):
    import re
    regex = r"\$\(.*\)"
    if isinstance(string, str):
        matches = re.finditer(regex, string, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            app.logger.info("====== find variable: %s ======" % string[match.start()+2: match.end()-1])
            variable =  string[match.start()+2: match.end()-1]
            uq_variable = '_'.join([owner, repo, task_id, variable]).replace('-', '_')
            return variable, uq_variable


def dfs_op(task_id, root):
    if 'operator' not in root:
        func = root['name']
        parameters = root['parameters']
        parameters = parse_parameters(task_id, parameters, **kwargs)
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


def parse_json_file(file='.github/azure-cli-bot.json'):
    import json
    with open(file, 'r') as configfile:
        config = json.load(configfile)
        app.logger.info("====== load config %s ======" % json.dumps(config, indent=2))
        # TODO load parameters to kwargs
        for task_id, task in enumerate(config['tasks']):
            if task['taskType'] == 'trigger':
                task_id = str(task_id)
                for condition in task['conditions']:
                    operator = condition.get('operator', None)
                    if operator:
                        flag = dfs_op(task_id, condition)
                    else:
                        func = condition['name']
                        parameters = condition['parameters']
                        parameters = parse_parameters(task_id, parameters, **kwargs)
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
                                parameters = parse_parameters(task_id, parameters, **kwargs)
                                exec_function(func, **parameters)
                    # flag = False and reversed = True
                    if not flag and 'actions' in condition:
                        for action in condition['actions']:
                            reversed = action.get('reversed', False)
                            if reversed:
                                func = action['name']
                                parameters = action['parameters']
                                parameters = parse_parameters(task_id, parameters, **kwargs)
                                exec_function(func, **parameters)

                if 'actions' in task:
                    for action in task['actions']:
                        func = action['name']
                        parameters = action['parameters']
                        parameters = parse_parameters(task_id, parameters, **kwargs)
                        exec_function(func, **parameters)
            elif task['taskType'] == 'scheduled':
                pass
                # TODO: 解析task
                # TODO: 调用start_job


# TODO: trigger azure-cli-bot.json 发生变化
# TODO: 判断是否 scheduled task 发生变化
# TODO: remove task
# TODO: add task


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


def more_than_x_days(x_days=None):
    if remain_days >= x_days:
        return True
    else:
        return False


def set_milestone(urls=None, milestone=None):
    app.logger.debug('====== enter func set_milestone, urls: %s, milestone %s ======', milestone, urls)


def add_reply(urls=None, comment=None):
    app.logger.info('====== enter func add_reply, urls: %s, message: %s ======', urls, comment)


def list_issues(milestone=None, state=None):
    # app.logger.info('====== enter func list_issues ======')
    return [
        {
            "url": "https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/38",
            "user":
                {
                    "login": "wangzelin007"
                }
        },
        {
            "url": "https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/37",
            "user":
                {
                    "login": "wangzelin008"
                }
        },
        {
            "url": "https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/26",
            "user":
                {
                    "login": "wangzelin009"
                }
        }
    ]


def search_file(search_file=None):
    # app.logger.info('====== enter func search_file ======')
    if search_file == 'setup.py':
        return True
    if search_file == 'HISTORY.rst':
        return False
    if search_file == 'index.json':
        return False


func_mapping = {
    "more_than_x_days": more_than_x_days,
    "set_milestone": set_milestone,
    "add_reply": add_reply,
    "search_file": search_file,
    "list_issues": list_issues,
}


def struct(**entries):
    from types import SimpleNamespace
    if isinstance(entries, dict):
        entries = SimpleNamespace(**entries)
    return entries


def test_struct():
    r = [
        {
            "url": "https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/38",
            "user":
                {
                    "login": "wangzelin007"
                }
        },
        {
            "url": "https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/37",
            "user":
                {
                    "login": "wangzelin008"
                }
        },
        {
            "urls": [
                "https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/26",
                "https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/25"
            ],
            "user":
                {
                    "login": "wangzelin009"
                }
        }
    ]
    from types import SimpleNamespace
    if isinstance(r, list):
        for idx, i in enumerate(r):
            r[idx] = SimpleNamespace(**r[idx])
    if isinstance(r, dict):
        r = SimpleNamespace(**r)
    print(r)


def exec_function(func, **parameters):
    func = func_mapping[func]
    ref = func(**parameters)
    if isinstance(ref, dict):
        ref = struct(**ref)
    elif isinstance(ref, list):
        for idx, i in enumerate(ref):
            ref[idx] = struct(**ref[idx])
    return ref


def this_job(*args, **kwargs):
    print('Enter this job!')
    print(args)
    print(kwargs)


@app.route('/', methods=['GET'])
def test():
    parse_json_file()
    return 'OK!!!'


@app.route('/test', methods=['GET'])
def test1():
    job_id = 'wangzelin007_github_bot_tutorial_move_issue_pr_to_next_milestone'
    type = 'interval'
    seconds = 5
    func = this_job
    args = 'a'
    kwargs = {
        'a': 1,
        'b': 'b'
    }
    _add_job(job_id, type, seconds, func, args, kwargs)
    return "job started"


@app.route("/schedule/<job_id>", methods=['get'])
def get_job(job_id):
    job = scheduler.get_job(job_id)
    return str(job)


@app.route("/schedules", methods=['get'])
def get_jobs():
    jobs = scheduler.get_jobs()
    return str(jobs)


@app.route("/schedule/<job_id>", methods=['delete'])
def remove_job(job_id):
    scheduler.remove_job(job_id)
    return "job removed"


@app.route("/schedule", methods=['POST'])
def add_job():
    params = request.json
    job_id = params['job_id']
    type = params['type']
    seconds = params['seconds']
    args = params['args']
    kwargs = params['kwargs']
    func = this_job
    _add_job(job_id, type, seconds, func, args, kwargs)
    return "job started"


def _add_job(job_id, type, seconds, func, args, kwargs):
    scheduler.add_job(
        id=job_id,
        trigger=type,
        seconds=seconds,
        func=func,
        # trigger="cron",
        # year="*",
        # month="*",
        # day="*",
        # minute="*",
        # max_instances=2,
        replace_existing=True,
        misfire_grace_time=240,
        args=args,
        kwargs=kwargs
    )


if __name__ == '__main__':
    from common.log import dictConfig
    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    app.run()
    # test_struct()
    # get_file_from_github()