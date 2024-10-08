import asyncio
import uvloop
import aiohttp
from aiohttp import web


URL = "https://studio.youtube.com/channel/UChuMeRm5W5eL27KHXhPkjug"


async def create_bg_tasks(app):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(URL) as resp:
            d = resp.cookies
            print(d)

if __name__ == '__main__':

    uvloop.install()

    app = web.Application()

    loop = asyncio.get_event_loop()

    app.on_startup.append(create_bg_tasks)

    web.run_app(app)

