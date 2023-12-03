from aiohttp import web
import asyncio
from aiopg.sa import create_engine
import os
import shutil
import datetime
import json
import logging

import db_youtube as db


async def handle(request):
    # print('came into handle')

    # post(), json() 둘다 가능합니다
    # data = await request.post()
    data = await request.json()
    file = data['file']
    status = data['status']
    # print(f'before loads data: {file}, {status}]')
    print(f'before loads data: {file}, {status}]')
    log.info(f'request:: data: {file}, {status}]')

    engine = request.app['db']

    try:
        async with engine.acquire() as conn:
            # making 즉 1일 경우
            if status == 1:
                log.info(f'status=1')
                await conn.execute(db.tbl_youtube_files.update().where(
                        db.tbl_youtube_files.c.filename==file).values(copying=0, making=1))

            # copying 즉 2일 경우
            elif status == 2:
                log.info(f'{conn}')
                log.info(f'status=2')
                await conn.execute(db.tbl_youtube_files.update().where(
                        db.tbl_youtube_files.c.filename==file).values(copying=1, making=0))

            # completed 즉 3일 경우
            elif status == 3:
                log.info(f'status=3')
                await conn.execute(db.tbl_youtube_files.update().where(
                        db.tbl_youtube_files.c.filename==file).values(copying=0, making=0))
            else:
                log.info(f'status=other')

    except:
        pass

    return web.Response(text='')


async def files_monitor(app):
    intv = app['intv']


    # print('came')
    # print(app['files'])

    # db에 접속해서 해당 file name 을 넣어봅니다
    app['db'] = await create_engine(host='192.168.1.203',
                                    database='youtube_db',
                                    user='postgres',
                                    password='sksmsqnwk11')
    print('came')

    engine = app['db']
    '''
    sa.Column('filename', sa.String(255)),
    sa.Column('title', sa.String(255)),
    sa.Column('playlist', sa.String(255)),
    sa.Column('status', sa.String(255)),
    sa.Column('timestamp', sa.String(255)))
    '''

    # 10초에 한번씩 탐색합니다
    while True:
        # 해당 폴더의 파일들을 일단 전부 db에 넣습니다
        for path in app['paths']:
            app['files'].update(dict([(f, datetime.datetime.fromtimestamp(
                os.path.getmtime(path + f)).strftime("%y%m%d%H%M%S")) for f in os.listdir(path)]))
            # print(app['files'])

        # timestamp에 따라 내림차순 정렬을 합니다
        app['files'] = dict(sorted(app['files'].items(),
                            key=lambda x: x[1], reverse=True))

        async with engine.acquire() as conn:
            print('conn')
            files = app['files']
            # for f in app['files']:
            for f in files:
                print(f'file: {f}, time: {int(files[f])}')
                log.info(f'inserting::file: {f}, time: {int(files[f])}')

                # 동일한 파일명을 넣어줄 경우 exception이 나면서 패스되게 합니다
                try:
                    await conn.execute(db.tbl_youtube_files.insert().values(filename=f,
                                                                            timestamp=files[f]))
                    # title='',
                    # playlist='',
                    # status='',
                    # await conn.execute(db.tbl_youtube_files.insert().values(filename=f))
                except:
                    print('exception on inserting db!')

        await asyncio.sleep(intv)

    # return app


async def create_bg_tasks(app):
    asyncio.create_task(files_monitor(app))


if __name__ == "__main__":
    # 로깅 설정입니다
    log_handler = logging.FileHandler('/home/utylee/youtube_file_monitor.log')
    log_handler.setFormatter(logging.Formatter('[%(asctime)s]-%(message)s'))
    # log_handler.setFormatter(logging.Formatter('%[(asctime)s]-%(name)s-%(message)s'))
    log = logging.getLogger('log')
    log.addHandler(log_handler)
    log.setLevel(logging.DEBUG)

    app = web.Application()
    app['paths'] = [
        '/mnt/c/Users/utylee/Videos/Heroes of the Storm/',
        '/mnt/c/Users/utylee/Videos/Desktop/',
        '/mnt/c/Users/utylee/Videos/World Of Warcraft/'
    ]
    app['files'] = dict()
    app['intv'] = 10             # 파일 탐색 주기를 설정합니다.  5초

    app.on_startup.append(create_bg_tasks)

    app.add_routes([
        web.post('/', handle)
    ])

    web.run_app(app, port=9992)
