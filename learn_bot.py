import asyncio
import os
import aiohttp
from gidgethub.aiohttp import GitHubAPI

async def main():
    async with aiohttp.ClientSession() as session:
        # create a auth token in github setting page
        # https://github.com/settings/tokens
        gh = GitHubAPI(session, "wangzelin-bot", oauth_token=os.getenv("GH_AUTH"))
        # create an issue
        # await gh.post("/repos/wangzelin007/github-bot-tutorial/issues",
        #               data={"title": "Hello",
        #                     "body": "Thanks!"})
        # reaction for an issue
        # await gh.post("/repos/wangzelin007/github-bot-tutorial/issues/1/reactions",
        #               data={"content": "hooray"},
        #               accept="application/vnd.github.v3+json")
        # Using gidgethub to respond to webhooks
        # https://github-bot-tutorial.readthedocs.io/en/latest/gidgethub-for-webhooks.html
        # add webhooks: https://github.com/wangzelin007/github-bot-tutorial/settings/hooks
        # create a application to receive webhook event: https://www.heroku.com/
        # MSFT: https://portal.azure.com/#create/Microsoft.WebSite
        # use github workflow auto-deploy
        # https://docs.microsoft.com/en-us/azure/app-service/deploy-github-actions?tabs=applevel


# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
