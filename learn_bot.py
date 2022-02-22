import asyncio
import os
import aiohttp
from gidgethub.aiohttp import GitHubAPI

async def main():
    async with aiohttp.ClientSession() as session:
        gh = GitHubAPI(session, "wangzelin-bot", oauth_token=os.getenv("GH_AUTH"))
        await gh.post("/repos/wangzelin007/regex/issues",
                      data={"title": "Hello",
                            "body": "Thanks!"})
asyncio.run(main())
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())