import os
import time
import shutil
import asyncio
import aiohttp
from aiohttp import web
import aiofiles
import json
import subprocess
import logging
import logging.handlers
import datetime
import time

from aiopg.sa import create_engine
# http post 로 신호 전달을 위해 json 객체가 필요합니다
# import json
import db_youtube as db

PATHS = [
        '/mnt/c/Users/utylee/Videos/World Of Warcraft/',
        '/mnt/c/Users/utylee/Videos/Apex Legends/',
        '/mnt/c/Users/utylee/Videos/Heroes of the Storm/',
        '/mnt/c/Users/utylee/Videos/Desktop/',
        '/mnt/c/Users/utylee/Videos/Overwatch 2/',
        '/mnt/c/Users/utylee/Videos/The Finals/', 
        '/mnt/c/Users/utylee/Videos/Counter-strike 2/', 
        '/mnt/c/Users/utylee/Videos/Fpsaimtrainer/'   
]

TRUNCATE_DAYS = 3

async def low(request):
    # print('low')
    # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # request.app['cur_length'] = 6 * 1024 * 128
    request.app['cur_length'] = 5 * 1024 * 128
    return web.Response(text='low')


async def high(request):
    # print('high')
    # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # request.app['cur_length'] = 48 * 1024 * 128
    request.app['cur_length'] = 24 * 1024 * 128
    return web.Response(text='high')


# 날짜로 파일 정보를 정리도 하지만 초기에 중단된 전송이 있으면 추가도 합니다
async def truncate(app):
    engine = app['db']
    candidate = []          # 삭제 후보리스트

    # os.path.getmtime(paths[n] + f)).strftime("%y%m%d%H%M%S")) for f in os.listdir(paths[n])]))
    now = datetime.datetime.now()
    log.info(f'{datetime.datetime.now()}')
    # 24시간 주기로 실행합니다
    while True:
        async with engine.acquire() as conn:
            async for r in conn.execute(db.tbl_youtube_files.select()):
                try:
                    # 중단된 전송을 초기 전송큐에 등록합니다
                    # queueing 이 1인 것들이 예약된 상태로 전송완료가 되지 않은 것들입니다
                    log.info(f'초기 select: {r}')
                    if r[10] == 1:
                        #  파일,경로 등을 app['transfering'] 큐에 넣습니다,
                        app['transfer_que']['que'].append(
                            (r[0], r[8], r[9]))
                        q = app['transfer_que']['que'][-1]
                        log.info(f'queueing 1 추가됨: {q}')

                    # 경과일 계산
                    t = datetime.datetime.strptime(r[12], "%y%m%d%H%M%S")
                    diff = now - t
                    log.info(f'경과일:{diff.days}, {r[0]}')
                    log.info(f'경과일:{diff.days}')

                    # 일주일 기간 이상은 삭제합니다
                    # 3일 기간 이상은 삭제합니다
                    # if diff.days > 7:
                    if diff.days > TRUNCATE_DAYS:
                        await conn.execute(db.tbl_youtube_files.delete()
                                           .where(db.tbl_youtube_files.c.filename == r[0]))
                        # candidate.append(r[0])
                    # log.info(f'{r[8]}')

                except:
                    log.info(f'truncation::exception')

        await asyncio.sleep(3600*24)


async def create_bg_tasks(app):
    # aiohttp에서 app.loop 이 사라졌다고 하네요 그냥 아래와같이 하라고 합니다
    # app.loop.create_task(watching(app))
    app['db'] = await create_engine(host='192.168.1.203',
                                    database='youtube_db',
                                    user='postgres',
                                    password='sksmsqnwk11')
    await asyncio.sleep(0.01)

    # 앞에 await 를 안붙였어도 되긴 했던 것 같습니다
    asyncio.create_task(truncate(app))          # 생성된지 일주일된 자료는 db상 삭제합니다
    asyncio.create_task(transfering(app))
    asyncio.create_task(watching(app))


async def transfering(app):
    # que, status = app['transfer_que']['que'], app['transfer_que']['status']
    engine = app['db']

    # 10초에 한번씩 큐 리스트를 탐색합니다
    while True:
        # status가 0(대기중)이며 que 리스트에 항목이 있을 때 작동합니다
        # if status == 0 and len(que):

        que = app['transfer_que']['que']
        if len(que) > 0:
            # 첫번째 항목을 전송합니다

            # 현재 전송 큐를 표시합니다
            log.info(f'transfering::que: {que}')

            file, path, target = que.pop(0)
            log.info(f'file:{file}, path:{path}, target:{target}]')
            start = f'{path}{file}'
            desti = f'{target}/{file}'
            exct = 0

            try:
                # db 에 copying 플래그를 넣어줍니다
                # payload = {'file': file, 'status': 2}
                # ret = await send_current_status(payload)

                try:
                    async with engine.acquire() as conn:
                        # copying 즉 2일 경우
                        log.info(f'status=2')
                        await conn.execute(db.tbl_youtube_files.update().where(
                            db.tbl_youtube_files.c.filename == file).values(copying=1, making=2))
                    # 또한 needRefresh를 호출해줍니다
                    async with aiohttp.ClientSession() as sess:
                        async with sess.get('http://192.168.1.204:9993/ws_refresh'):
                            log.info('call needRefresh')

                except:
                    pass

                print(f'start: {start}\ndesti: {desti}')
                log.info(f'copying startging...')
                log.info(f'start: {start}\ndesti: {desti}')

                # 현재 복사 진행중인 파일명을 갖고 있기로 합니다
                app['current_copying'] = file

                sum = 0
                async with aiofiles.open(start, mode='rb') as src:
                    async with aiofiles.open(desti, mode='wb') as dst:
                        while 1:
                            cur_length = app['cur_length']
                            buf = await src.read(cur_length)
                            if not buf:
                                break
                            await dst.write(buf)
                            sum = sum + cur_length
                            sumk = round(sum / 1000000)
                            wrote = round(len(buf)/1000)
                            # print(f'wrote:{len(buf)}')
                            # log.info(f'wrote:{len(buf)}')
                            # print(f'{file}: {len(buf)} kb')
                            # log.info(f'{file}: {len(buf)} b ')
                            log.info(f'{file}: {wrote} K / {sumk} M')
                            await asyncio.sleep(0.5)

            except:
                print('exception in copying')
                log.info('exception in copying')
                exct = 1

            # 복사완료후 원래 파일을 삭제합니다
            print('copy complete')
            log.info('copy complete')
            if exct == 0:
                # exception이 안났을 경우에만 파일이름을 다시 복구합니다. 10초 후
                # exception이 안났을 경우에만 삭제합니다. 5초 후
                # time.sleep(5)
                await asyncio.sleep(5)

                # 영상을 감상중이라던가해서 삭제가 안될경우 db업데이트 문제로
                # youtube 업로드가 시작되지 않습니다. 따라서 삭제전 나머지 플래그는
                # 설정해주도록 합니다. 로컬 삭제는 안되어도 리모트에서 업로드는 되도록
                try:
                    async with engine.acquire() as conn:
                        # completed 즉 3일 경우
                        log.info(f'status=3')
                        await conn.execute(db.tbl_youtube_files.update().where(
                            db.tbl_youtube_files.c.filename == file)
                            .values(copying=2, uploading=1, queueing=0))

                except Exception as e:
                    log.info(f'exception {e}')

                try:
                    os.remove(start)
                    async with engine.acquire() as conn:
                        log.info(f'set db local=0')
                        await conn.execute(db.tbl_youtube_files.update().where(
                            db.tbl_youtube_files.c.filename == file)
                            .values(local=0))
                    # 또한 needRefresh를 호출해줍니다
                    async with aiohttp.ClientSession() as sess:
                        async with sess.get('http://192.168.1.204:9993/ws_refresh'):
                            log.info('call needRefresh after removing')
                except Exception as e:
                    log.info(f'exception in file deleting... {e}')

                # db 에 completed 플래그를 넣어줍니다
                # payload = {'file': file, 'status': 3}
                # ret = await send_current_status(payload)

                # os.remove 와 try내에 통합합니다
                '''
                try:
                    async with engine.acquire() as conn:
                        log.info(f'set db local=0')
                        await conn.execute(db.tbl_youtube_files.update().where(
                            db.tbl_youtube_files.c.filename == file)
                            .values(local=0))

                except:
                    pass
                '''

        await asyncio.sleep(10)


async def watching(app):

    #path = 'f:\\down\\'
    #path = 'D:/D_Down/'
    # path = 'E:/Down/'
    # path = 'C:/Users/utylee/Videos/World Of Warcraft'

    # 게임 중이냐 아느냐로 속도 조절을 할 수 있게끔 기준 변수를 넣어봅니다
    speed_control = 1

    # 복사 버퍼 크기인데 0.5초 단위의 속도를 의미합니다. 현재 초당 5메가로
    # 캡쳐과 되고 있기에 그걸 감안해서 설정합니다
    # cur_length = 24 * 1024 * 100     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # cur_length = 16 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # 속도를 더 늦춰봅니다
    # cur_length = 8 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    cur_length = app['cur_length']

    # 게임 중이 아니라면 높은속도로 복사합니다
    if speed_control == 0:
        cur_length = 24 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다

    # 여러 경로를 감시하게끔 변경합니다
    #path = '/mnt/c/Users/utylee/Videos/World Of Warcraft/'
    paths = app['paths']
    # paths = [
    #             '/mnt/c/Users/utylee/Videos/World Of Warcraft/',
    #             '/mnt/c/Users/utylee/Videos/Heroes of the Storm/',
    #             '/mnt/c/Users/utylee/Videos/Desktop/'
    #         ]

    # path = '/mnt/c/Users/utylee/Videos/Desktop/'

    #path = 'E:\\Down\\'
    #target = 'w:\\99-data\\91-transmission-watch\\'
    #target = 'v:/99-data/91-transmission-watch'
    #target_media = 'v:/00-MediaWorld'
    #target = 'u:/3002/99-data/91-transmission-watch'

    #target = 'u:/4001/99-data/91-transmission-watch'
    #target = r'\\192.168.0.201\clark\4001\99-data\91-transmission-watch'
    # target = r'\\192.168.1.205\clark\4001\99-data\91-transmission-watch'
    # target = r'\\192.168.1.202\clark\4002\00-MediaWorld-4002'
    # target = '/mnt/clark/4002/00-MediaWorld-4002'
    # target = r'\\192.168.1.202\clark\4002\00-MediaWorld-4002\97-Capture'
    # target = r'\\192.168.1.202\clark\4001\99-data\91-transmission-watch'

    # target = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture'
    target = app['target']

    backup_target = r'E:/magnets/'

    #target_media = 'u:/3002/00-MediaWorld'
    #target_media = 'u:/4002/00-MediaWorld-4002'
    #target_media = r'\\192.168.0.201\clark\4002\00-MediaWorld-4002'
    # target_media = r'\\192.168.1.205\clark\4002\00-MediaWorld-4002'
    target_media = r'\\192.168.1.202\clark\4002\00-MediaWorld-4002'

    size_table = dict()
    # before = dict([(f, None) for f in os.listdir(path)])

    # app['db'] = await create_engine(host='192.168.1.203',
    #                                 database='youtube_db',
    #                                 user='postgres',
    #                                 password='sksmsqnwk11')
    engine = app['db']

    befores = []
    afters = []
    addeds = []
    removeds = []
    # befores = dict()
    # afters = dict()
    # addeds = dict()
    # removeds = dict() 
    # log.info('come')
    for n in range(len(paths)):
        befores_dict = dict()
        
        # 해당 디렉토리가 있을 경우만 실행합니다
        if os.path.exists(paths[n]) == True:
            befores_dict.update(dict([(f, datetime.datetime.fromtimestamp(
                os.path.getmtime(paths[n] + f)).strftime("%y%m%d%H%M%S")) for f in os.listdir(paths[n])]))
        # log.info(f'{befores_dict}')
        # timestamp에 따라 내림차순 정렬을 합니다
        files_dict = dict(sorted(befores_dict.items(),
                                 key=lambda x: x[1], reverse=True))
        befores.append(befores_dict)

        # 모든 파일들을 전부 db에 삽입해봅니다
        async with engine.acquire() as conn:
            files = files_dict
            # for f in app['files']:
            for f in files:
                # print(f'file: {f}, time: {int(files[f])}')
                log.info(f'insertingDB::file: {f}, time: {int(files[f])}')

                # 동일한 파일명을 넣어줄 경우 exception이 나면서 패스되게 합니다
                try:
                    await conn.execute(db.tbl_youtube_files.insert()
                                       .values(filename=f,
                                               timestamp=files[f],
                                               local=1, queueing=0))
                    # title='',
                    # playlist='',
                    # status='',
                    # await conn.execute(db.tbl_youtube_files.insert().values(filename=f))
                    log.info(f'success')
                except:
                    print('exception on inserting db!')
                    log.info('exception on inserting db!')


        # befores[n] = paths[n]
        # befores.append(dict([(f, None) for f in os.listdir(paths[n])]))
        afters.append(paths[n])
        addeds.append(paths[n])
        removeds.append(paths[n])
        # print(app['files'])

    # before = dict([(f, None) for f in os.listdir(path)])

    # print(before)

    while 1:
        # for path in paths:
        for n in range(len(paths)):
            # 5초 주기입니다
            # time.sleep(5)
            await asyncio.sleep(5)

            afters_dict = dict()

            # 해당 디렉토리가 있을 경우만 실행합니다
            if os.path.exists(paths[n]) == True:
                afters_dict.update(dict([(f, datetime.datetime.fromtimestamp(
                    os.path.getmtime(paths[n] + f)).strftime("%y%m%d%H%M%S"))
                    for f in os.listdir(paths[n])]))

            # timestamp에 따라 내림차순 정렬을 합니다
            afters[n] = dict(sorted(afters_dict.items(),
                                    key=lambda x: x[1], reverse=True))
            # afters[n] = dict([(f, None) for f in os.listdir(paths[n])])
            # log.info(f'{afters_dict}')

            addeds[n] = dict([(f, afters[n][f])
                             for f in afters[n] if not f in befores[n]])
            # addeds[n] = [f for f in afters[n] if not f in befores[n]]
            removeds[n] = [f for f in befores[n] if not f in afters[n]]
            if addeds[n]:
                # if added:
                for i in addeds[n]:
                    print(f'added {i}')
                    log.info(f'added {i}')
                    log.info(f'{afters[n]}')
                    log.info(f'{addeds[n]}')

                    t = int(addeds[n][i])
                    # 추가된 파일을 db에 삽입을 시도합니다
                    async with engine.acquire() as conn:
                        # log.info(
                        #     f'insertingDB::file: {i}, time: {int(addeds[n][i])}')
                        log.info(
                            f'insertingDB::file: {i}, time: {t}')

                        # 동일한 파일명을 넣어줄 경우 exception이 나면서 패스되게 합니다
                        try:
                            await conn.execute(db.tbl_youtube_files.insert()
                                               .values(filename=i, timestamp=addeds[n][i],
                                                       local=1, uploading=0,
                                                       queueing=1,
                                                       youtube_queueing=0,
                                                       making=1, remote=0, copying=0,
                                                       start_path=paths[n],
                                                       dest_path=target))
                            # 또한 needRefresh를 호출해줍니다
                            async with aiohttp.ClientSession() as sess:
                                async with sess.get(
                                        'http://192.168.1.204:9993/ws_refresh') as resp:
                                    result = await resp.text()
                                    log.info(f'call needRefresh: {result}')
                        except Exception as e:
                            print(f'exception {e} on inserting db!')
                            log.info(f'exception {e} on inserting db!')

                    # 5초마다 녹화가 끝났는지 용량을 확인합니다
                    # 5초 후 전송을 시작합니다
                    # time.sleep(3)
                    # time.sleep(5)
                    # 파일이 여러개가 동시에 추가될 경우 파일 한개 밖에 처리하지 못하던 문제 수정
                    # if added[0][-7:] == 'torrent' :
                    # if i[-7:] == 'torrent':
                    # if i[-3:] == 'mp4':
                    if i[-3:] == 'mp4' or i[-4:] == 'webm':
                        exct = 0
                        a = f'{paths[n]}{i}'
                        # /mnt 이 아닌 \\192..xxx 방식의 위치를 사용해봅니다
                        b = f'{target}/{i}'
                        # b = f'{target}\\{i}'
                        # b = f'{target}/{i}.part'
                        # print(i)
                        # print(target)

                        payload = {'file': i, 'status': 0}

                        try:
                            before_size = os.path.getsize(a)
                            print('size checking start')
                            log.info('size checking start')
                            while 1:
                                # time.sleep(3)
                                await asyncio.sleep(3)
                                cur_size = os.path.getsize(a)
                                print(f'before: {before_size}, cur: {cur_size}')
                                log.info(
                                    f'before: {before_size}, cur: {cur_size}')
                                if before_size == cur_size:
                                    print('complete recoding')
                                    log.info('complete recoding')
                                    break

                                before_size = cur_size

                                # log.info('sending to monitor')

                                # payload = {'file': i, 'status': 1}
                                # ret = await send_current_status(payload)

                                # try:
                                #     async with engine.acquire() as conn:
                                #         # making 즉 1일 경우
                                #         # if status == 1:
                                #         log.info(f'status=1')
                                #         await conn.execute(db.tbl_youtube_files
                                #                            .update()
                                #                            .where(
                                #                             db.tbl_youtube_files.c.filename
                                #                             == i)
                                #                            .values(copying=0, making=1,
                                #                                 uploading=0, remote=0))

                                # except:
                                #     pass

                            # print('copy process start')
                            log.info('inserting que')

                            #a = path + "".join(added)
                            # a = path + "".join(i)

                            # # 2초 후 전송을 시작합니다
                            # # time.sleep(2)
                            # await asyncio.sleep(2)

                            try:
                                async with engine.acquire() as conn:
                                    # making 즉 1일 경우
                                    # if status == 1:
                                    log.info(f'status=1')
                                    await conn.execute(db.tbl_youtube_files
                                                       .update()
                                                       .where(
                                                           db.tbl_youtube_files.c.filename
                                                           == i)
                                                       .values(copying=0, making=2,
                                                               uploading=0, remote=0))
                                    # 또한 needRefresh를 호출해줍니다
                                    async with aiohttp.ClientSession() as sess:
                                        async with sess.get(
                                                'http://192.168.1.204:9993/ws_refresh'):
                                            log.info('call needRefresh')

                            except Exception as e:
                                log.info(f'exception {e}')

                            #  파일,경로 등을 app['transfering'] 큐에 넣고,
                            app['transfer_que']['que'].append(
                                (i, paths[n], target))
                            q = app['transfer_que']['que']
                            log.info(f'que after inserting: {q}')

                        except:
                            print('exception in added file check')
                            log.info('exception in added file check')
                            exct = 1
                            continue

                        '''
                        # ------------------------------------------------
                        # copying process
                        #
                        try:
                            # db 에 copying 플래그를 넣어줍니다
                            payload = {'file': i, 'status': 2}
                            ret = await send_current_status(payload)

                            print(f'a: {a}\nb: {b}')
                            log.info(f'a: {a}\nb: {b}')
                            async with aiofiles.open(a, mode='rb') as src:
                                async with aiofiles.open(b, mode='wb') as dst:
                                    print('async copying')
                                    while 1:
                                        cur_length = app['cur_length']
                                        buf = await src.read(cur_length)
                                        if not buf:
                                            break
                                        await dst.write(buf)
                                        print(f'{time.time()} wrote:{len(buf)}')
                                        log.info(
                                            f'{time.time()} wrote:{len(buf)}')
                                        await asyncio.sleep(0.5)
                        # try:
                        #     print(f'a: {a}\nb: {b}')
                        #     log.info(f'a: {a}\nb: {b}')
                        #     with open(a, mode='rb') as src:
                        #         with open(b, mode='wb') as dst:
                        #             # print('async copying')
                        #             while 1:
                        #                 buf = src.read(cur_length)
                        #                 if not buf:
                        #                     break
                        #                 dst.write(buf)
                        #                 # print(f'{time.time()} wrote:{len(buf)}')
                        #                 log.info(f'{time.time()} wrote:{len(buf)}')
                        #                 time.sleep(0.5)

                        except:
                            print('exception in copying')
                            log.info('exception in copying')
                            exct = 1
                            continue

                        # def _copyfileobj_patched(fsrc, fdst, length=cur_length):
                        #     """Patches shutil copyfileobj method to hugely improve copy speed"""
                        #     print('copyfileobj')
                        #     while 1:
                        #         buf = fsrc.read(length)
                        #         if not buf:
                        #             break
                        #         fdst.write(buf)
                        #         time.sleep(0.5)

                        # # shutil.copyfileobj = _copyfileobj_patched

                        # # src = open(a, 'r+b')
                        # # dst = open(f'{target}/{i}', 'w+b')
                        # with open(a, 'rb') as src:
                        #     # with open(f'{target}/{i}.part', 'w+b') as dst:
                        #     with open(b, 'wb') as dst:
                        #         try:
                        #             # print(a)
                        #             # shutil.copy(a, target)
                        #             # shutil.copyfile(a, target)
                        #             _copyfileobj_patched(src, dst)
                        #         except:
                        #             print('exception')
                        #             exct = 1
                        #             continue
                        # 복사완료후 원래 파일을 삭제합니다
                        print('copy complete')
                        log.info('copy complete')
                        if exct == 0:
                            # exception이 안났을 경우에만 파일이름을 다시 복구합니다. 10초 후
                            # exception이 안났을 경우에만 삭제합니다. 5초 후
                            # time.sleep(5)
                            await asyncio.sleep(5)
                            os.remove(a)

                            # db 에 completed 플래그를 넣어줍니다
                            payload = {'file': i, 'status': 3}
                            ret = await send_current_status(payload)

                            # client-server 로서 part확장자 등을 이용해 변경해줄 필요가 없어졌
                            # 습니다. 파일 완료후 mp4 moov 정보가 수정된 이후에 전송하기에
                            # ret = await send_complete(i)
                            # if (ret == 'ok'):
                            #     os.remove(a)

                            # renamed = a + '.copied'
                            # os.rename(a, renamed)
                            # os.rename(b, b_org)

                        # 백업 폴더에 torrent 파일을 옮깁니다
                        # shutil.copy(renamed,  backup_target)
                        # os.remove(renamed)
                        '''
            # before = after
            befores[n] = afters[n]


async def send_complete(fname):
    async with aiohttp.ClientSession() as sess:
        resp = await sess.post('http://192.168.1.202:9202/copyend', json=json.dumps({'file': fname}))
        a = await resp.text()
        print(a)
        return a


# async def send_current_status(payload):
#     # db 에 making/copying 플래그를 넣어줍니다
#     # --> 직접 db접근 보다는 monitor 프로그램에
#     # 신호를 주는 것으로 변경합니다
#     log.info(f'payload:{payload}')
#     req_url = f'http://localhost:9992/'
#     res = None

#     try:
#         async with aiohttp.ClientSession() as sess:
#             async with sess.post(req_url,
#                                  #  .json파라미터를 바로 써야하는건지
#                                  # json.dumps등은
#                                  # 서버측에서 풀어도 되질 않았습니다
#                                  # data=json.dumps(payload)) as resp:

#                                  # data로 직접 dict를 보내거나 json
#                                  # 파라미터로 전송해주고 받아주고 해야
#                                  # 하는 것 같습니다
#                                  # data=payload) as resp:
#                                  json=payload) as resp:
#                 res = await resp.text()
#                 log.info(f'monitor send result:{res}')
#     except:
#         pass

#     return res


if __name__ == '__main__':
    log_path = f'/home/utylee/capture.log'
    # log_path = app['log_path']

    # supervisor에 의해 root권한으로 생성되었을 때 혹은 반대의 경우의 권한
    # 문제를 위한 해결법입니다
    try:
        os.chmod(log_path, 0o777)
    except:
        pass

    # handler = logging.FileHandler(log_path)
    handler = logging.handlers.RotatingFileHandler(filename=log_path,
                                                   maxBytes=10*1024*1024,
                                                   backupCount=10)
    # handler.setFormatter(logging.Formatter('%[(asctime)s]-%(name)s-%(message)s'))
    handler.setFormatter(logging.Formatter('[%(asctime)s]-%(message)s'))
    log = logging.getLogger('log')
    log.addHandler(handler)
    # log.terminator = ''
    log.setLevel(logging.DEBUG)

    app = web.Application()
    # app['log_path'] = f'/home/utylee/capture.log'
    app['cur_length'] = 8 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # app['paths'] = [
    #     '/mnt/c/Users/utylee/Videos/World Of Warcraft/',
    #     '/mnt/c/Users/utylee/Videos/Heroes of the Storm/',
    #     '/mnt/c/Users/utylee/Videos/Desktop/'
    # ]
    app['paths'] = PATHS
    app['target'] = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture'
    app['transfer_que'] = dict(que=[],
                               status=0)  # status:: 0: 대기중, 1: 복사중, 2: 복사완료

    app['current_copying'] = ''

    # watcher 프로시져 함수를 돌립니다
    app.on_startup.append(create_bg_tasks)

    # 웹서버를 엽니다. 히오스가 활성상태인지 확인하는 정보를 받습니다
    app.add_routes([
        web.get('/low', low),
        web.get('/high', high)
    ])

    web.run_app(app, port=8007)

    # main()

# asyncio.get_event_loop().run_until_complete(main())
