from time import asctime
import aiohttp
from aiohttp import web
import asyncio
import db_youtube as db
from aiopg.sa import create_engine

import logging
import logging.handlers

async def updatejs(request):


async def listjs(request):
    engine = request.app['db']
    l = []
    async with engine.acquire() as conn:
        async for r in conn.execute(db.tbl_youtube_files.select()):
            # print(r[0])
            l.append(dict(r))

    # log.info(l)
    # 정렬해서 전달합니다
    l.sort(key=lambda x:int(x['timestamp']), reverse=True)

    # return web.Response(text='하핫')
    return web.json_response(l)


async def handle(request):

    return web.Response(text='dddd')


async def create_bg_tasks(app):
    app['db'] = await create_engine(host='192.168.1.203',
                                    user='postgres',
                                    password='sksmsqnwk11',
                                    database='youtube_db')

if __name__ == '__main__':

    # loghandler = logging.FileHandler('/home/utylee/youtube_upload_backend')
    loghandler = logging.handlers.RotatingFileHandler(
        '/home/utylee/youtube_upload_backend.log', maxBytes=5*1024*1024, backupCount=3)
    loghandler.setFormatter(logging.Formatter('[%(asctime)s]-%(message)s'))
    log = logging.getLogger('log')
    log.addHandler(loghandler)
    log.setLevel(logging.DEBUG)

    app = web.Application()

    log.info('ㅎㅎㅎㅎ')

    app.on_startup.append(create_bg_tasks)

    app.add_routes([
        web.get('/listjs', listjs),
        web.post('/updatejs', updatejs),
        web.get('/', handle)
    ])

    web.run_app(app, port=9992)
