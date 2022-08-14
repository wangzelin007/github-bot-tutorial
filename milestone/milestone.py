import constant
import datetime
import logging
import requests


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def select_milestone(created_at, author, ms_type):
    # Less than three weeks: put into the next milestone with a warning message
    # More than three week: put into the current milestone
    all_milestones, index = get_all_milestones()
    current_milestone = get_current_milestone(all_milestones, index)
    next_milestone = get_current_milestone(all_milestones, index)
    created_at = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
    if ms_type == 'issue':
        if get_remain_days_of_current_milestone(current_milestone, created_at) > 21:
            msg = None
            return current_milestone, msg
        else:
            msg = f"Hi @{author}, Since the current milestone time is less than 21 days, " \
                  f"this issue will be resolved in the next milestone"
            return next_milestone, msg
    # Less than a week: put into the next milestone with a warning message
    # More than a week: put into the current milestone
    if ms_type == 'pull_request':
        if get_remain_days_of_current_milestone(current_milestone, created_at) > 7:
            msg = None
            return current_milestone, msg
        else:
            msg = f"Hi @{author}, Since the current milestone time is less than 7 days, " \
                  f"this pr will be reviewed in the next milestone"
            return next_milestone, msg


def get_all_milestones():
    # NOTE: github API has automatically sorted by due on field
    # GET https://api.github.com/repos/{owner}/{repo}/milestones
    url = 'https://api.github.com/repos/wangzelin007/github-bot-tutorial/milestones'
    try:
        r = requests.get(url, headers=constant.headers)
        logger.debug('response: %s', r)
        logger.debug('text: %s', r.text)
        logger.debug('code: %s', r.status_code)
    except requests.RequestException as e:
        raise e
    all_milestones = []
    for i in r.json():
        number = i['number']
        due_on = datetime.datetime.strptime(i['due_on'], '%Y-%m-%dT%H:%M:%SZ') if i['due_on'] else None
        all_milestones.append([number, due_on])
    index = 0
    for i in all_milestones:
        if i[1] and i[1] > datetime.datetime.now():
            break
        else:
            index += 1
    logger.info('====== all_milestones %s, index: %s ======', all_milestones, index)
    # [[4, None], [1, datetime.datetime(2022, 9, 6, 7, 0)]]
    return all_milestones, index


def get_current_milestone(all_milestones, index):
    # [1, datetime.datetime(2022, 9, 6, 7, 0)]
    return all_milestones[index]


def get_next_milestone(all_milestones, index):
    return all_milestones[index+1]


def get_remain_days_of_current_milestone(current_milestone, created_at):
    # transform
    return (current_milestone[1] - created_at).days


if __name__=='__main__':
    get_all_milestones()