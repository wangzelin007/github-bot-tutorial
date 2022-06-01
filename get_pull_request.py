import json
import os
import requests


token = os.getenv('GH_AUTH')

headers = {'Authorization': 'token %s' % token}

issue_id = 17
url = f'https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/{issue_id}'

r = requests.get(url, headers=headers)
print(r)
print(json.loads(r.text)['title'])
print(json.loads(r.text)['body'])

print("================================================================================")

issue_id = 18
url = f'https://api.github.com/repos/wangzelin007/github-bot-tutorial/issues/{issue_id}'

r = requests.get(url, headers=headers)
print(r)
print(json.loads(r.text)['title'])
print(json.loads(r.text)['body'])