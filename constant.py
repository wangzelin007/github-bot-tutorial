import os


GH_SECRET = os.environ.get("GH_SECRET")
GH_AUTH = os.environ.get("GH_AUTH")
headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': 'token %s' % GH_AUTH}
# headers = {'Authorization': 'token %s' % GH_AUTH}
# headers = {'Authorization': 'Bearer %s' % GH_AUTH}
