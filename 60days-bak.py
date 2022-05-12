import aiohttp
import asyncio
import os
from gidgethub.aiohttp import GitHubAPI

from datetime import datetime
from datetime import timezone
from pprint import pprint
import requests
import time
import json

token = os.getenv('GH_AUTH')
ENCODING = 'utf-8'
headers = {'Authorization': 'token %s' % token}


async def main():
    async with aiohttp.ClientSession() as session:
        # create a auth token in github setting page
        # https://github.com/settings/tokens
        gh = GitHubAPI(session, "wangzelin-bot", oauth_token=os.getenv("GH_AUTH"))
        # get 30 issues
        # ref = await gh.getitem("/repos/Azure/azure-cli/issues")
        # for i in ref:
        #     if i['state'] == 'open':
        #             and (datetime.now().astimezone(timezone.utc) - datetime.fromisoformat(i['created_at'][:-1]).astimezone(timezone.utc)).days >= 60:
                # print(i['created_at'])
                # print(i['html_url'])
                # print(i['title'])

        # get all issues very slow
        # issues = []
        # created:YYYY-MM-DD
        # https://api.github.com/repos/Azure/azure-cli/issues?state=open&created:2022-01-07
        # async for i in gh.getiter("/repos/Azure/azure-cli/issues?state=open&created:2022-01-07"):
        #     if i['state'] == 'open' and (datetime.now().astimezone(timezone.utc) - datetime.fromisoformat(i['created_at'][:-1]).astimezone(timezone.utc)).days >= 60:
        #         issues.append(i)
        #     await gh.sleep(0.1)
        # print(issues)


def filter_by_time(issues):
    filter_issues = []
    continue_flag = True
    now = datetime.now().astimezone(timezone.utc)
    for issue in issues:
        created_at = datetime.fromisoformat(issue['created_at'][:-1]).astimezone(timezone.utc)
        period = (now - created_at).days
        if 60 <= period <= 90:
            # azure-cli/azure-cli-extension : issue['labels'][0]['name'] != 'Service Attention' or 'feature-request'
            if issue['labels']:
                for label in issue['labels']:
                    if label['name'] in ['Service Attention', 'feature-request']:
                        break
                else:
                    item = {
                        'created_at': issue['created_at'],
                        'html_url': issue['html_url'],
                        'title': issue['title'],
                    }
                    filter_issues.append(item)
            else:
                item = {
                    'created_at': issue['created_at'],
                    'html_url': issue['html_url'],
                    'title': issue['title'],
                }
                filter_issues.append(item)
        if period > 90:
            continue_flag = False
            break
    return filter_issues, continue_flag


def filter_by_sla(issues):
    filter_issues = []
    continue_flag = True
    now = datetime.now().astimezone(timezone.utc)
    for issue in issues:
        created_at = datetime.fromisoformat(issue['created_at'][:-1]).astimezone(timezone.utc)
        period = (now - created_at).days
        if 1 <= period <= 3:
            if issue['comments'] == 0:
                item = {
                    'created_at': issue['created_at'],
                    'html_url': issue['html_url'],
                    'title': issue['title'],
                }
                filter_issues.append(item)
        if period > 3:
            continue_flag = False
            break
    return filter_issues


def filter_by_sla_pr(pulls):
    filter_prs = []
    continue_flag = True
    now = datetime.now().astimezone(timezone.utc)
    for pull in pulls:
        created_at = datetime.fromisoformat(pull['created_at'][:-1]).astimezone(timezone.utc)
        period = (now - created_at).days
        if 1 <= period <= 3:
            comments = requests.get(pull['_links']['comments']['href'], headers=headers)
            if 'url' not in comments.content.decode('utf-8'):
                item = {
                    'created_at': pull['created_at'],
                    'html_url': pull['html_url'],
                    'title': pull['title'],
                }
                filter_prs.append(item)
        elif period > 3:
            continue_flag = False
            break
    return filter_prs


def main():
    with open(r'C:\Users\zelinwang\OneDrive - Microsoft\Desktop\issues-prs-60-90days.txt', 'w+', encoding=ENCODING) as f:
        f.write("Open between 60~90 days\n")
        f.write("And don't have label Service Attention or feature-request\n")
    with open(r'C:\Users\zelinwang\OneDrive - Microsoft\Desktop\issues-prs-3-days-sla.txt', 'w+', encoding=ENCODING) as f:
        f.write("Not comment more than 2 days\n")

    # get all issues in pages
    # urls = {}
    urls = {
        "Azure-cli": "https://api.github.com/repos/Azure/azure-cli/issues?state=open&per_page=100&page=1",
        "Azure-cli-extension": "https://api.github.com/repos/Azure/azure-cli-extensions/issues?state=open&per_page=100&page=1",
     }
    prs = {
        "Azure-cli": "https://api.github.com/repos/Azure/azure-cli/pulls?state=open&per_page=100&page=1",
        "Azure-cli-extension": "https://api.github.com/repos/Azure/azure-cli-extensions/pulls?state=open&per_page=100&page=1",
    }
    # issues
    for repo, url in urls.items():
        res = requests.get(url, headers=headers)
        issues = res.json()
        filter_issues, continue_flag = filter_by_time(issues)
        filter_issues2 = filter_by_sla(issues)
        while 'next' in res.links.keys():
            time.sleep(0.1)
            res = requests.get(res.links['next']['url'], headers=headers)
            tmp = res.json()
            filter_tmp, continue_flag = filter_by_time(tmp)
            filter_tmp2 = filter_by_sla(tmp)
            if continue_flag:
                filter_issues.extend(filter_tmp)
                if filter_tmp2:
                    filter_issues2.extend(filter_tmp2)
            else:
                break
        # Azure-cli repo: total 94
        with open(r'C:\Users\zelinwang\OneDrive - Microsoft\Desktop\issues-prs-60-90days.txt', 'a', encoding=ENCODING) as f:
            f.write('\n\n')
            f.write("%s repo: total issues %s\n\n\n" % (repo, len(filter_issues)))
            for issue in filter_issues:
                for k, v in issue.items():
                    f.write('%s \n' % v)
        with open(r'C:\Users\zelinwang\OneDrive - Microsoft\Desktop\issues-prs-3-days-sla.txt', 'a', encoding=ENCODING) as f:
            f.write('\n\n')
            f.write("%s repo: total issues %s\n\n\n" % (repo, len(filter_issues2)))
            for issue in filter_issues2:
                for k, v in issue.items():
                    f.write('%s \n' % v)

    # pulls
    for repo, url in prs.items():
        res = requests.get(url, headers=headers)
        pulls = res.json()
        filter_pulls, continue_flag = filter_by_time(pulls)
        filter_pulls2 = filter_by_sla_pr(pulls)
        while 'next' in res.links.keys():
            time.sleep(0.1)
            res = requests.get(res.links['next']['url'], headers=headers)
            tmp = res.json()
            filter_tmp, continue_flag = filter_by_time(tmp)
            filter_tmp2 = filter_by_sla_pr(tmp)
            if continue_flag:
                filter_pulls.extend(filter_tmp)
                if filter_tmp2:
                    filter_pulls2.extend(filter_tmp2)
            else:
                break
        with open(r'C:\Users\zelinwang\OneDrive - Microsoft\Desktop\issues-prs-60-90days.txt', 'a', encoding=ENCODING) as f:
            f.write('\n\n')
            f.write("%s repo: total pulls %s\n\n\n" % (repo, len(filter_pulls)))
            for pull in filter_pulls:
                for k, v in pull.items():
                    f.write('%s \n' % v)
        with open(r'C:\Users\zelinwang\OneDrive - Microsoft\Desktop\issues-prs-3-days-sla.txt', 'a', encoding=ENCODING) as f:
            f.write('\n\n')
            f.write("%s repo: total pulls %s\n\n\n" % (repo, len(filter_pulls2)))
            for pull in filter_pulls2:
                for k, v in pull.items():
                    f.write('%s \n' % v)


def get_limit():
    url = 'https://api.github.com/users/octocat'
    headers = {'Authorization': 'token %s' % token}
    res = requests.get(url, headers=headers)
    pprint(res.headers['X-RateLimit-Limit'])
    pprint(res.headers['X-RateLimit-Remaining'])

def send_email():
    import win32com.client as win32
    try:
        outlook = win32.Dispatch('Outlook.Application')
    except:
        outlook = win32.GetActiveObject('Outlook.Application')
    mail = outlook.CreateItem(0)
    # mail.To = 'zelinwang@microsoft.com'
    mail.To = 'yonzhan@microsoft.com;ychenu@microsoft.com'
    # mail.CC = '12345678@qq.com'
    mail.Subject = 'Issues and PRs Summary'
    mail.Body = 'This email is send by Azure cli bot automatically.'
    # mail.Importance = 2
    mail.Attachments.Add(r'C:\Users\zelinwang\OneDrive - Microsoft\Desktop\issues-prs-60-90days.txt')
    mail.Attachments.Add(r'C:\Users\zelinwang\OneDrive - Microsoft\Desktop\issues-prs-3-days-sla.txt')
    mail.Send()

# curl -I https://api.github.com/users/octocat
# curl -u my_client_id:my_client_secret https://api.github.com/user/repos
# https://docs.github.com/cn/rest/overview/resources-in-the-rest-api#checking-your-rate-limit-status
# curl --header "Authorization: token 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" -I https://api.github.com/users/octocat 还是60
# curl -I https://api.github.com/rate_limit?access_token=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
# 5000
# curl --header "Authorization: token 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" -I https://api.github.com/users/octocat

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
if __name__ == '__main__':
    # get_limit()
    main()
    send_email()