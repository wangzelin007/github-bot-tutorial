import os
from flask import Flask
import requests
app = Flask(__name__)

GH_SECRET = os.environ.get("GH_SECRET")
GH_AUTH = os.environ.get("GH_AUTH")

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': 'token %s' % GH_AUTH}


def issue_opened_event(event):
    """
    Whenever an issue is opened, greet the author and say thanks.
    """
    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]

    message = f"Thanks for the report @{author}! I will look into it ASAP! (I'm a bot)."
    body = {
        'body': message,
    }

    # https://docs.github.com/en/rest/issues/comments
    try:
        r = requests.post(url, json=body, headers=headers)
    except requests.RequestException as e:
        print(e)


@app.route('/webhook', methods=['POST'])
def webhook(request):
    event = request.read()
    issue_opened_event(event)
    return


if __name__ == '__main__':
   app.run()