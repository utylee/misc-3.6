from aiohttp import web
import asyncio


async def files_monitor():
    pass

async def create_bg_tasks(app):
    asyncio.create_task(files_monitor())


if __name__ == "__main__":

    app = web.Application()

    app.on_startup.append(create_bg_tasks)

    web.run_app(app, port=9011)
