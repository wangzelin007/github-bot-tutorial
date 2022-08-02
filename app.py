import os
from flask import Flask, request
import requests
from issues.issues import issue_opened, issue_labeled


app = Flask(__name__)
app.secret_key = os.getenv('GH_SECRET', 'secret string')


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
    action_map[action](event)
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
    print(request)
    event = request.json
    action = event["action"]
    route_base_action(action, event)
    return 'Hello github, I am azure cli bot'


if __name__ == '__main__':
   app.run()