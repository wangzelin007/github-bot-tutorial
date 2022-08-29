import os


GH_SECRET = os.environ.get("GH_SECRET")
GH_AUTH = os.environ.get("GH_AUTH")
HEADERS = {
    'Accept': 'application/vnd.github+json',
    'Authorization': 'token %s' % GH_AUTH}
