import os
from flask import Flask, request, redirect, url_for
import requests


GH_SECRET = os.environ.get("GH_SECRET")
GH_AUTH = os.environ.get("GH_AUTH")
app = Flask(__name__)
app.secret_key = os.getenv('GH_SECRET', 'secret string')

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': 'token %s' % GH_AUTH}


def issue_opened_event(event):
    """
    Whenever an issue is opened, greet the author and say thanks.
    """
    url = event["issue"]["comments_url"]
    author = event["issue"]["user"]["login"]

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
def webhook():
    print(request)
    event = request.json
    issue_opened_event(event)
    return redirect(url_for('hello'))


@app.route('/hello')
def hello():
    response = '<h1>Hello!</h1>'
    return response


if __name__ == '__main__':
   app.run()