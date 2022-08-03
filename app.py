from flask import Flask, request
from issues.issues import issue_opened, issue_labeled
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


def route_base_action(action, event):
    """
    route an issue base on action.
    """
    # opened, edited, deleted, pinned, unpinned, closed, reopened, assigned, unassigned,
    # labeled, unlabeled, locked, unlocked, transferred, milestoned, or demilestoned
    action_map = {
        'opened': issue_opened,
        'labeled': issue_labeled,
    }
    logger.info('====== action: %s ======' % action)
    try:
        action_map[action](event)
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
    logger.info('====== event: %s ======' % event)
    action = event["action"]
    route_base_action(action, event)
    return 'Hello github, I am azure cli bot'


if __name__ == '__main__':
    app.secret_key = os.getenv('GH_SECRET', 'secret string')
    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    app.run()