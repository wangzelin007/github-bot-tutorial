import logging
from bot.github_api import milestone, issues
from bot.utils.request_client import RequestHandler
from flask import g


logger = logging.getLogger('bot')
requestClient = RequestHandler()


def open_pull_request(event):
    # common comment use issue rest api
    # https://api.github.com/repos/{owner}/{repo}/issues/{number}/
    pull_request_url = event['pull_request']['url']
    issue_url = event['pull_request']['issue_url']
    comment_url = issue_url + '/comments'
    author = event['pull_request']['user']['login']
    message = f"Thanks for the contribution @{author}!"
    logger.info("====== message: %s ======" % message)
    issues.comment_issue(comment_url, message)
    # get created_at
    created_at = event['pull_request']['created_at']
    logger.info('====== created_at: %s ======' % created_at)
    # select milestone
    ms, msg = milestone.select_milestone(created_at, author, ms_type='pull_request')
    if msg:
        issues.comment_issue(comment_url, msg)
    # assign milestone
    # https://api.github.com/repos/{owner}/{repo}/issues/26
    issues.update_issue(issue_url, milestone=ms)
    # TODO: Whether to enable (azure-cli: disable, azure-cli-extensions: enable)
    search_files = ['setup.py', 'HISTORY.rst']
    if not search_files_in_pull_request(pull_request_url, search_files):
        msg = f"Hi @{author},\nIf you want to release the new extension version," \
              f" please write the description of changes into HISTORY.rst and update setup.py."
        issues.comment_issue(comment_url, msg)
    # search_files = ['commands.py', '_params.py']
    # if search_files_in_pull_request(url, search_files):
    #     commands, params, msg, delete_confirmation = regex.detect_new_command()
    #     if commands or params:
    #         issues.comment_issue(comment_url, msg)
    #         issues.lock_issue()
    #         # add need-add-test flag
    #     if delete_confirmation:
    #         msg = f"Hi @{author},\nDo we need to consider adding confirmation=True for the delete operation ?"
    #         issues.comment_issue(comment_url, msg)


def update_pull_request(event):
    # people add added-test flag
    # or
    # people add no-need-test flag
    # unlock issue
    pass


def list_pull_request_files(url):
    # https://api.github.com/repos/{OWNER}/{REPO}/pulls/{NUMBER}/files
    # try:
    #     r = requests.GET(url, headers=constant.HEADERS)
    # except requests.RequestException as e:
    #     logger.debug('response: %s', r)
    #     logger.debug('text: %s', r.text)
    #     logger.debug('code: %s', r.status_code)
    #     raise e
    r = requestClient.visit('GET', url)
    files = [i['filename'] for i in r.json()]
    return files


def search_file_in_pull_request(search_file):
    # https://api.github.com/repos/{OWNER}/{REPO}/pulls/{NUMBER}/files
    pull_request_files = list_pull_request_files(g.pull_request_files_url)
    if search_file in pull_request_files:
        return True
    return False


def search_files_in_pull_request(url, search_files):
    url = '/'.join([url, 'files'])
    # https://api.github.com/repos/{OWNER}/{REPO}/pulls/{NUMBER}/files
    pull_request_files = list_pull_request_files(url)
    for file in search_files:
        if any([file in pull_request_file for pull_request_file in pull_request_files]):
            continue
        else:
            return False
    return True


def is_ready_for_merge():
    pass

