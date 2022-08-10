from flask import Flask, request
from issues.issues import issue_opened
from pull_request.pull_request import pr_opened
from scheduler import scheduler
import logging
import os


app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


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
            'opened': issue_opened,
        },
        'pull_request': {
            "opened": pr_opened,
        }
    }
    logger.info("====== action: %s ======" % action)
    try:
        action_map[type][action](event)
    except Exception as e:
        raise e
    # url = event["issue"]["comments_url"]
    # author = event["issue"]["user"]["login"]
    #
    # message = f"Thanks for the report @{author}! I will look into it ASAP! (I'm a bot)."
    # body = {
    #     'body': message,
    # }
    #
    # # https://docs.github.com/en/rest/issues/comments
    # try:
    #     r = requests.post(url, json=body, headers=headers)
    # except requests.RequestException as e:
    #     print(e)


@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.json
    logger.info("====== event: %s ======" % event)
    action = event['action']
    if 'issue' in action.keys():
        type = 'issue'
    elif 'pull_request' in action.keys():
        type = 'pull_request'
    route_base_action(action, event, type)
    return 'Hello github, I am azure cli bot'


if __name__ == '__main__':
    app.secret_key = os.getenv('GH_SECRET', 'secret string')
    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    app.run()