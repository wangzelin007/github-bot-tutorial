from flask import Flask, request
from issues.issues import open_issue
from pull_request.pull_request import open_pull_request
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


@app.route('/webhook', methods=['POST'])
def webhook():
    event_type = request.headers.get('X-GitHub-Event')
    logger.info("====== event type: %s ======" % event_type)
    if event_type in ['pull_request', 'issues']:
        event = request.json
        logger.info("====== event: %s ======" % event)
        action = event['action']
        if action in ['opened']:
            if 'issue' in event.keys():
                type = 'issue'
            elif 'pull_request' in event.keys():
                type = 'pull_request'
            route_base_action(action, event, type)
            return 'Hello github, I am azure cli bot'
        else:
            logger.info("====== unsupported action: %s %s======", event_type, action)
            return 'Not support action'
    else:
        logger.info("====== unsupported event type: %s ======", event_type)
        return 'Not support type'


if __name__ == '__main__':
    app.secret_key = os.getenv('GH_SECRET', 'secret string')
    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    app.run()