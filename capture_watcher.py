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
from sqlalchemy import false
# http post 로 신호 전달을 위해 json 객체가 필요합니다
# import json
import db_youtube as db

URL_UPLOADER_WS_REFRESH = 'http://192.168.1.204:9993/ws_refresh'
TRUNCATE_DAYS = 3
PATHS = [
    '/mnt/c/Users/utylee/Videos/World Of Warcraft/',
    '/mnt/c/Users/utylee/Videos/Apex Legends/',
    '/mnt/c/Users/utylee/Videos/Heroes of the Storm/',
    '/mnt/c/Users/utylee/Videos/Desktop/',
    '/mnt/c/Users/utylee/Videos/Overwatch 2/',
    '/mnt/c/Users/utylee/Videos/The Finals/',
    '/mnt/c/Users/utylee/Videos/Counter-strike 2/',
    '/mnt/c/Users/utylee/Videos/Fpsaimtrainer/',
    '/mnt/c/Users/utylee/Videos/Enshrouded/'
]

INTV = 5                    # watching 확인 주기입니다
# INTV = 1                    # watching 확인 주기입니다
INTV_TRNS = 10              # transfering 확인 주기입니다
INTV_TRNS_TICK = 0.5       # transfering 파일 조각 전송주기입니다
# INTV_TRNS = 1              # transfering 확인 주기입니다
INTV_UPSCL = 3              # upscaling 확인 주기입니다

BOOL_UPSCALE = 1            # 0:None,  1:1440p,  2:2160p
# BOOL_UPSCALE = 0            # 0:None,  1:1440p,  2:2160p
VIDEO_EXT_LIST = ['mp4', 'mkv', 'webm', 'avi', 'mov', 'mpg', 'mpeg', 'wmv']

SPEED_LOW = 5 * 1024 * 128     # 5K * 128 = 0.6M /sec => 초당 0.6M 입니다
SPEED_HIGH = 24 * 1024 * 128     # 24K * 128 = 3.2M /sec => 초당 3.2M 입니다

# REMOTE_PATH = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture'
REMOTE_PATH = '/mnt/8001/97-Capture'

# SUDO = 'sudo'
DAVINCI_PATH = '/mnt/c/Program Files/Blackmagic Design/DaVinci Resolve/Resolve.exe'
PYTHONW_PATH = '/mnt/c/Program Files/Python38/python.exe'   # DaVinci 공식지원이 3.6이랍니다
# DAVINCI_UPSCALE_PY_PATH = '/home/utylee/.virtualenvs/misc/src/DavinciResolveUpscale.py'
DAVINCI_UPSCALE_PY_PATH = 'c:/Users/utylee/.virtualenvs/misc/src/DavinciResolveUpscale.py'
# UPSCALING_RES = "2160"
UPSCALING_RES = "1440"
# KILL_DAVINCI_PY_PATH = '/home/utylee/.virtualenvs/misc/src/kill_win32_davinci.py'
KILL_DAVINCI_PY_PATH = 'c:/Users/utylee/.virtualenvs/misc/src/kill_win32_davinci.py'
UPSCALED_FILE_NAME = '/mnt/c/Users/utylee/Videos/MainTimeline.mp4'
UPSCALED_GATHER_PATH = '/mnt/c/Users/utylee/Videos/_Upscaled/'


async def report_upscale(request):
    js = await request.json()

    js = json.loads(js)
    # log.info(f'report_upscale::{js}')

    pct = js['CompletionPercentage']
    eta = 0
    if 'EstimatedTimeRemainingInMs' in js.keys():
        eta = round(js['EstimatedTimeRemainingInMs'] / 1000)
        log.info(f'Upscaling: {pct}%,\tETA: {eta} sec')
    elif 'TimeTakenToRenderInMs' in js.keys():
        eta = round(js['TimeTakenToRenderInMs'] / 1000)
        log.info(f'Upscaling: Complete!,\tTOT: {eta} sec taken')
    # eta = round(js['TimeTakenToRenderInMs'] / 1000)
    # {'JobStatus': Complete'', 'CompletionPercentage': 100, 'TimeTakenToRenderInMs': 17243}

    # 현 진행율을 db에 갱신합니다
    try:
        app['upscale_pct'] = pct
        engine = request.app['db']
        async with engine.acquire() as conn:
            await conn.execute(db.tbl_youtube_files.update()
                               .where(db.tbl_youtube_files.c.filename == request.app['current_upscaling_file'])
                               .values(upscale_pct=pct))

    except Exception as e:
        log.info(f'exception {e} while pct updating')

    # 또한 needRefresh를 호출해줍니다
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(
                    URL_UPLOADER_WS_REFRESH) as resp:
                result = await resp.text()
                log.info(f'call needRefresh: {result}')
    except Exception as e:
        log.info(f'exception {e} while pct needRefreshing')

    return web.json_response([])


async def UpscalingProc(file, app):
    log.info(f'UpscalingProc::executing davinci resolve -nogui...')
    app['davinci_proc'] = await asyncio.create_subprocess_exec(DAVINCI_PATH, '-nogui', stdout=None)
    # app['davinci_proc'] = await asyncio.create_subprocess_exec(DAVINCI_PATH, stdout=None)
    log.info(f'davinci_proc: {app["davinci_proc"]}')
    await asyncio.sleep(2)     # 실행시 10초정도는 기다려줘야하는 것 같습니다
    # await app['davinci_proc'].wait()

    # 업스케일을 실행합니다
    log.info(f'file:{file}')
    file_win = 'c:' + file[6:]  # wsl의 /mnt/c 를 윈도우 형태로 변환해줍니다
    log.info(f'file_win:{file_win}')
    log.info(f'davinci upscale executing with pythonw...')
    proc_upscale = await asyncio.create_subprocess_exec(PYTHONW_PATH, DAVINCI_UPSCALE_PY_PATH, file_win, UPSCALING_RES, stdout=None)

    ret = await proc_upscale.wait()
    log.info(f'davinci upscale return code: {ret}')
    if ret == 0:
        log.info(f'Upscale Successed!')
    # await asyncio.sleep(20)

    log.info(f'UpscalingProc::killing davinci resolve by win python.exe ...')
    # await asyncio.create_subprocess_exec('sudo', PYTHONW_PATH, KILL_DAVINCI_PY_PATH, stdout=None)
    # proc = await asyncio.create_subprocess_exec(PYTHONW_PATH, KILL_DAVINCI_PY_PATH, stdout=asyncio.subprocess.PIPE)
    # proc = await asyncio.create_subprocess_exec('sudo', '-S', PYTHONW_PATH, KILL_DAVINCI_PY_PATH, stdout=None)
    proc_killresolve = await asyncio.create_subprocess_exec(PYTHONW_PATH, KILL_DAVINCI_PY_PATH, stdout=None)

    # import psutil
    # for proc in psutil.process_iter():
    #     log.info(f'proc: {proc.name()}')

    await proc_killresolve.wait()
    # await asyncio.sleep(5)

    # ret이 0아 아닐 경우는 업스케일 실패입니다
    return ret


async def deletefile(request):
    js = await request.json()
    js = json.loads(js)
    log.info(f'came into deletefile. js is {js}')
    # log.info(f'js.filename is {js["filename"]}')

    start_path = ''
    dest_path = ''

    # start_removed = 0
    # dest_removed = 0

    start_exists = 1
    dest_exists = 1

    # db에서 해당파일의 로컬 및 리모트의 폴더를 가져옵니다
    engine = request.app['db']
    try:
        async with engine.acquire() as conn:
            async for r in conn.execute(db.tbl_youtube_files.select()
                                        .where(db.sa.and_(db.tbl_youtube_files.c.filename == js['filename'],
                                                          db.tbl_youtube_files.c.timestamp == js['timestamp']))):
                # db.tbl_youtube_files.c.timestamp == '3'))):
                start_path = r[8]
                dest_path = r[9]
                log.info(f'deletefile::DB selected::{start_path}, {dest_path}')

    except Exception as e:
        log.info(f'exception {e}')

    # 만약 start_path, dest_path 가 없으면 응급조치를 실행합니다

    # 파일이름과 폴더를 합칩니다
    # start_path = os.path.join(start_path, js['filename'])
    # dest_path = os.path.join(dest_path, js['filename'])

    log.info(f'deletefile::fetched::start:{start_path}')
    log.info(f'deletefile::fetched::dest:{dest_path}')

    try:
        # db에 패스가 없기에 모든 폴더를 적용해지워봅니다
        if (start_path == None):
            for p in PATHS:
                log.info(f'p: {p}')
                temp_path = os.path.join(p, js['filename'])
                if (os.path.exists(temp_path)):
                    start_path = p
                    break

            # 모든 폴더에 해당파일이 없다면 지워졌다고 보면됩니다
            # 아무거나 넣어주면 이후에 당연히 지워졌다고 판단되고 진행될 것입니다
            if (start_path == None):
                start_path = PATHS[0]
                # start_exists = 0
        log.info(f'start_path: {start_path}')

        # if(start_removed == 0
        # if(start_exists == 1
        # and os.path.exists(os.path.join(start_path, js['filename']))):
        if (os.path.exists(os.path.join(start_path, js['filename']))):
            os.remove(os.path.join(start_path, js['filename']))
        # else:
        #     if(os.path.exists(os.path.join(start_path, js['filename']))):
        #         os.remove(os.path.join(start_path, js['filename']))

        log.info(f'deleted start paths {js["filename"]}')
    except Exception as e:
        log.info(f'exception while deleting start {js["filename"]}, {e}')

    try:
        if (dest_path == None):
            dest_path = request.app['target']
        if (os.path.exists(os.path.join(dest_path, js['filename']))):
            os.remove(os.path.join(dest_path, js['filename']))

        log.info(f'deleted dest paths {js["filename"]}')
    except Exception as e:
        log.info(f'exception while deleting dest {js["filename"]}, {e}')

    # 삭제됐으면 db의 local과 remote도 업데이트해줍니다
    # if (start_exists == 0
    #         or os.path.exists(os.path.join(start_path, js['filename'])) == False):
    if (os.path.exists(os.path.join(start_path, js['filename'])) == False):
        # start_removed = 1
        start_exists = 0
        log.info('start no exists')
        try:
            async with engine.acquire() as conn:
                await conn.execute(db.tbl_youtube_files.update()
                                   .where(db.sa.and_(db.tbl_youtube_files.c.filename == js['filename'],
                                                     db.tbl_youtube_files.c.timestamp == js['timestamp']))
                                   .values(local=0))
        except Exception as e:
            log.info(f'{e}')

    if (os.path.exists(os.path.join(dest_path, js['filename'])) == False):
        # dest_removed = 1
        dest_exists = 0
        log.info('dest no exists')
        try:
            async with engine.acquire() as conn:
                await conn.execute(db.tbl_youtube_files.update()
                                   .where(db.sa.and_(db.tbl_youtube_files.c.filename == js['filename'],
                                                     db.tbl_youtube_files.c.timestamp == js['timestamp']))
                                   .values(remote=0))
        except Exception as e:
            log.info(f'{e}')

    # 둘다 없을 경우에만 db의 해당파일 튜플을 삭제합니다
    # if(start_removed == 1 and dest_removed == 1):
    if (start_exists == 0 and dest_exists == 0):
        try:
            async with engine.acquire() as conn:
                await conn.execute(db.tbl_youtube_files.delete()
                                   .where(db.sa.and_(db.tbl_youtube_files.c.filename == js['filename'],
                                                     db.tbl_youtube_files.c.timestamp == js['timestamp'])))

            # 클라이언트에 needRefresh 를 보냅니다
            async with aiohttp.ClientSession() as sess:
                async with sess.get(URL_UPLOADER_WS_REFRESH):
                    log.info('call needRefresh')

        except Exception as e:
            log.info(f'{e}')

    return web.Response(text='ok')


async def low(request):
    # print('low')
    log.info('httpget: upload low speed')
    # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # request.app['cur_length'] = 6 * 1024 * 128
    # request.app['cur_length'] = 5 * 1024 * 128
    request.app['cur_length'] = SPEED_LOW
    return web.Response(text='low')


async def high(request):
    # print('high')
    log.info('httpget: upload high speed')
    # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # request.app['cur_length'] = 48 * 1024 * 128
    # request.app['cur_length'] = 24 * 1024 * 128
    request.app['cur_length'] = SPEED_HIGH
    return web.Response(text='high')


# 날짜로 파일 정보를 정리도 하지만 초기에 중단된 전송이 있으면 추가도 합니다
# 또한 upscaling이 중단된 경우라면 upscaling도 다시 진행해줍니다
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
                    # 중단된 전송을 초기 큐에 등록하는 프로세스입니다
                    # queueing 이 1인 것들이 예약된 상태로 전송완료가 되지 않은 것들입니다
                    log.info(f'중단됐던 전송: {r}')
                    if r[10] == 1:
                        #  파일,경로,업스케일완료여부 등을 업스케일큐에 넣습니다,
                        app['upscale_que']['que'].append((r[0], r[8], r[13]))
                        q = app['upscale_que']['que'][-1]
                        log.info(f'upscale_queueing에 추가된 데이터: {q}')

                        # #  파일,경로 등을 app['transfering'] 큐에 넣습니다,
                        # app['transfer_que']['que'].append(
                        #     (r[0], r[8], r[9]))
                        # q = app['transfer_que']['que'][-1]
                        # log.info(f'queueing 1 추가됨: {q}')

                    # 경과일 계산부
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
    asyncio.create_task(watching(app))
    asyncio.create_task(transfering(app))
    asyncio.create_task(upscaling(app))


async def upscaling(app):
    # que, status = app['transfer_que']['que'], app['transfer_que']['status']
    engine = app['db']

    # 3초에 한번씩 큐 리스트를 탐색합니다
    while True:
        # status가 0(대기중)이며 que 리스트에 항목이 있을 때 작동합니다
        # if status == 0 and len(que):

        que = app['upscale_que']['que']
        if len(que) > 0:
            # 첫번째 항목을 큐에서 꺼냅니다

            # 현재 업스케일 큐를 표시합니다
            log.info(f'upscaling::que: {que}')

            file, path, upscaled = que.pop(0)
            log.info(f'file, path, upscaled:{file}, {path}, {upscaled}')
            pathfile = f'{path}{file}'

            # BOOL_UPSCALE 이 1이면서 upscale이 안되어있을 경우
            # DaVinciResolve 프로세스를 실행합니다
            if (upscaled == 0 and BOOL_UPSCALE and path != UPSCALED_GATHER_PATH):
                log.info(
                    f'upscaling()::upscaled==0::executing davinciResolve -nogui...')
                app['davinci_proc'] = await asyncio.create_subprocess_exec(DAVINCI_PATH, '-nogui', stdout=None)
                # app['davinci_proc'] = await asyncio.create_subprocess_exec(DAVINCI_PATH, stdout=None)
                log.info(f'davinci_proc: {app["davinci_proc"]}')
                await asyncio.sleep(2)     # 실행시 10초정도는 기다려줘야하는 것 같습니다
                # await app['davinci_proc'].wait()

                # 업스케일을 실행합니다
                app['current_upscaling_file'] = file  # 현재만들어진 파일명을 갖고있습니다
                pathfile_win = 'c:' + pathfile[6:]  # wsl의 /mnt/c 를 윈도우 형태로 변환해줍니다
                log.info(f'pathfile_win:{pathfile_win}')
                log.info(f'davinci upscale executing with pythonw...')
                proc_upscale = await asyncio.create_subprocess_exec(PYTHONW_PATH, DAVINCI_UPSCALE_PY_PATH, pathfile_win, UPSCALING_RES, stdout=None)

                ret = await proc_upscale.wait()
                log.info(f'davinci upscale return code: {ret}')
                if ret == 0:
                    log.info(f'Upscale Successed!')

                    # 변환이 성공하였으니 출력파일을 upscale 폴더로 이동해줍니다
                    upscaled_pathfile = UPSCALED_GATHER_PATH + file
                    log.info(f'upscaled_pathfile is {upscaled_pathfile}')
                    # db 상 넣어줄 start_path 를 upscale폴더로 변경해줍니다
                    path = UPSCALED_GATHER_PATH
                    # 생성된파일을 _Upscaled 폴더로 옮기고 원본 파일도 삭제합니다
                    try:
                        os.rename(UPSCALED_FILE_NAME, upscaled_pathfile)
                        os.remove(pathfile)
                    except Exception as ose:
                        log.info(
                            f'exception while moving and removing upscaled file\n {ose}')
                    # 또한 변환이 성공하였으니 upscale_pct도 100으로 지정해줍니다
                    app['upscale_pct'] = 100

                # await asyncio.sleep(20)

                log.info(
                    f'UpscalingProc::killing davinci resolve by win python.exe ...')
                # await asyncio.create_subprocess_exec('sudo', PYTHONW_PATH, KILL_DAVINCI_PY_PATH, stdout=None)
                # proc = await asyncio.create_subprocess_exec(PYTHONW_PATH, KILL_DAVINCI_PY_PATH, stdout=asyncio.subprocess.PIPE)
                # proc = await asyncio.create_subprocess_exec('sudo', '-S', PYTHONW_PATH, KILL_DAVINCI_PY_PATH, stdout=None)
                proc_killresolve = await asyncio.create_subprocess_exec(PYTHONW_PATH, KILL_DAVINCI_PY_PATH, stdout=None)

                # import psutil
                # for proc in psutil.process_iter():
                #     log.info(f'proc: {proc.name()}')

                await proc_killresolve.wait()
                # await asyncio.sleep(5)

                # 0이 아닐 경우 업스케일 실패입니다
                if ret != 0:
                    log.info(f'upscale failed!!')

            # DavinciResolveUpscale 혹은 비처리 패스등을 끝낸 이후
            try:
                # db 에 upscaled 플래그를 넣어줍니다
                # payload = {'file': file, 'status': 2}
                # ret = await send_current_status(payload)
                try:
                    async with engine.acquire() as conn:
                        await conn.execute(db.tbl_youtube_files.update()
                                           .where(db.tbl_youtube_files.c.filename == file)
                                           .values(upscaled=app['bool_upscale'],
                                                   upscaling_pct=app['upscale_pct'],
                                                   making=2,
                                                   start_path=path))
                    # 또한 needRefresh를 호출해줍니다
                    async with aiohttp.ClientSession() as sess:
                        async with sess.get(URL_UPLOADER_WS_REFRESH):
                            log.info('call needRefresh')
                except:
                    pass

                #  파일,경로 등을 app['transfering'] 큐에 넣습니다
                # transfering()에서 전송을 담당합니다
                log.info(
                    'upscaling()::inserting to transfering que..{file}, {path}, {app["target"]}')
                app['transfer_que']['que'].append(
                    (file, path, app['target']))
                q = app['transfer_que']['que']
                log.info(f'transfer_que after inserting: {q}')
            except Exception as e:
                log.info('exception {e} on upscale(app)')

        await asyncio.sleep(INTV_UPSCL)


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
            size = round(os.path.getsize(start) / 1000000)

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
                        async with sess.get(URL_UPLOADER_WS_REFRESH):
                            log.info('call needRefresh')

                except:
                    pass

                print(f'start: {start}\ndesti: {desti}')
                log.info(f'copying starting...')
                log.info(f'start: {start}\ndesti: {desti}')

                # 현재 복사 진행중인 파일명을 갖고 있기로 합니다
                app['current_copying_file'] = file

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
                            pct = round(sumk / size * 100)
                            eta = round(
                                ((size - sumk) / (wrote/INTV_TRNS_TICK / 1000))/60)
                            log.info(
                                f'{file}: {round(wrote/INTV_TRNS_TICK)}KB/s / {sumk}M / {size}M ({pct}%/{eta}min)')
                            await asyncio.sleep(INTV_TRNS_TICK)

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
                            .values(copying=2, uploading=1, queueing=0, remote=1))
                        # remote = 1을 추가합니다. 삭제프로세스 보다보니 없어서
                        # .values(copying=2, uploading=1, queueing=0))

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
                        async with sess.get(URL_UPLOADER_WS_REFRESH):
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

        await asyncio.sleep(INTV_TRNS)


async def watching(app):
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
        # cur_length = 24 * 1024 * 128      # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
        cur_length = SPEED_HIGH             # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다

    # 여러 경로를 감시하게끔 변경합니다
    # path = '/mnt/c/Users/utylee/Videos/World Of Warcraft/'
    paths = app['paths']
    # paths = [
    #             '/mnt/c/Users/utylee/Videos/World Of Warcraft/',
    #             '/mnt/c/Users/utylee/Videos/Heroes of the Storm/',
    #             '/mnt/c/Users/utylee/Videos/Desktop/'
    #         ]

    # path = '/mnt/c/Users/utylee/Videos/Desktop/'

    # target = r'\\192.168.1.202\clark\4002\00-MediaWorld-4002\97-Capture'
    # target = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture'
    target = app['target']

    backup_target = r'E:/magnets/'

    # target_media = 'u:/3002/00-MediaWorld'
    # target_media = 'u:/4002/00-MediaWorld-4002'
    # target_media = r'\\192.168.0.201\clark\4002\00-MediaWorld-4002'
    # target_media = r'\\192.168.1.205\clark\4002\00-MediaWorld-4002'
    # target_media = r'\\192.168.1.202\clark\4002\00-MediaWorld-4002'
    # target_media = r'\\192.168.1.202\8001\00-MediaWorld-4002'

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
            await asyncio.sleep(INTV)

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
                                                       playlist='etc',
                                                       upscaled=0,
                                                       upscale_pct=-1,
                                                       queueing=1,
                                                       youtube_queueing=0,
                                                       making=1, remote=0, copying=0,
                                                       start_path=paths[n],
                                                       dest_path=target))
                            # 또한 needRefresh를 호출해줍니다
                            async with aiohttp.ClientSession() as sess:
                                async with sess.get(
                                        URL_UPLOADER_WS_REFRESH) as resp:
                                    result = await resp.text()
                                    log.info(f'call needRefresh: {result}')
                        except Exception as e:
                            print(f'exception {e} on inserting db!')
                            log.info(f'exception {e} on inserting db!')

                    # 파일이 여러개가 동시에 추가될 경우 파일 한개 밖에 처리하지 못하던 문제 수정
                    # if i[-3:] == 'mp4' or i[-3:] == 'mkv' or i[-4:] == 'webm':
                    if i[-5:].split('.')[1].lower() in VIDEO_EXT_LIST:
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

                            # <--- 녹화완료
                            app['current_making_file'] = i  # 현재만들어진 파일명을 갖고있습니다
                            _start_path = paths[n]

                            # upscale 큐에 넣어줍니다
                            # BOOL_UPSCALE 에 상관없이 일단 upscale 큐가 판단한 후
                            # transfer 큐로 넘겨줍니다 (파일명, 폴더명)
                            app['upscale_que']['que'].append((i, _start_path, 0))

                            # # upscaling 루틴
                            # if app['bool_upscale'] > 0:
                            #     ret_upscale = await UpscalingProc(a, app)
                            #     # 0이 아닐 경우 업스케일 실패입니다 중단합니다
                            #     if ret_upscale is not 0:
                            #         raise
                            #     # split_ext = os.path.splitext(i)
                            #     # new_filepath = UPSCALED_GATHER_PATH + \
                            #     #     split_ext[0] + '_up' + split_ext[1]
                            #     new_filepath = UPSCALED_GATHER_PATH + i
                            #     log.info(f'new_filepath is {new_filepath}')
                            #     # 생성된파일을 _Upscaled 폴더로 옮기고 변환전 파일도 삭제합니다
                            #     try:
                            #         os.rename(UPSCALED_FILE_NAME, new_filepath)
                            #         os.remove(a)
                            #     except Exception as ose:
                            #         log.info(f'exception {ose}')

                            #     # 또한 db 업데이트에서의 start_path로 _Upscaled path로
                            #     # 변환해줍니다
                            #     _start_path = UPSCALED_GATHER_PATH

                            # # db를 업데이트합니다. 녹화완료
                            # log.info('db updating... record ended')
                            # try:
                            #     async with engine.acquire() as conn:
                            #         # making 즉 1일 경우
                            #         # if status == 1:
                            #         log.info(f'status=1')
                            #         await conn.execute(db.tbl_youtube_files
                            #                            .update()
                            #                            .where(db.tbl_youtube_files.c.filename
                            #                                   == i)
                            #                            .values(copying=0, making=2,
                            #                                    uploading=0, remote=0,
                            #                                    start_path=_start_path,
                            #                                    upscaled=app['bool_upscale']))
                            #         # 또한 needRefresh를 호출해줍니다
                            #         async with aiohttp.ClientSession() as sess:
                            #             async with sess.get(
                            #                     URL_UPLOADER_WS_REFRESH):
                            #                 log.info('call needRefresh')

                            # except Exception as e:
                            #     log.info(f'exception {e}')

                            # #  파일,경로 등을 app['transfering'] 큐에 넣습니다
                            # # transfering()에서 전송을 담당합니다
                            # log.info('inserting que')

                            # # upscaled 이면 _Upscaled 폴더로 변경지정합니다
                            # # folder = UPSCALED_GATHER_PATH if app['bool_upscale'] \
                            # #     else paths[n]

                            # # 저위에서 upscale 여부에따라 변환하는 파트를 새로 넣어줬습니다
                            # app['transfer_que']['que'].append(
                            #     (i, _start_path, target))
                            # # app['transfer_que']['que'].append(
                            # #     (i, folder, target))
                            # # app['transfer_que']['que'].append(
                            # #     (i, paths[n], target))
                            # q = app['transfer_que']['que']
                            # log.info(f'que after inserting: {q}')

                        except:
                            print('exception in added file check')
                            log.info('exception in added file check')
                            exct = 1
                            continue

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
    # logging.Formatter.default_msec_format = '%s.%03d'
    formatter = logging.Formatter(
        '[%(asctime)s.%(msecs)03d]-%(message)s', "%y%m%d %H:%M:%S")
    # formatter.default_msec_format = '%s.%03d'
    handler.setFormatter(formatter)
    # handler.setFormatter(logging.Formatter(
    # '[%(asctime)s]-%(message)s', "%y-%m-%d %H:%M:%S:%f").default_msec_format('%s.%03d')))
    log = logging.getLogger('log')
    log.addHandler(handler)
    # log.terminator = ''
    log.setLevel(logging.DEBUG)

    app = web.Application()
    # app['log_path'] = f'/home/utylee/capture.log'
    # app['cur_length'] = 8 * 1024 * 128    # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    app['cur_length'] = SPEED_HIGH
    # app['paths'] = [
    #     '/mnt/c/Users/utylee/Videos/World Of Warcraft/',
    #     '/mnt/c/Users/utylee/Videos/Heroes of the Storm/',
    #     '/mnt/c/Users/utylee/Videos/Desktop/'
    # ]
    app['paths'] = PATHS
    app['target'] = REMOTE_PATH
    app['transfer_que'] = dict(que=[],
                               status=0)  # status:: 0: 대기중, 1: 복사중, 2: 복사완료
    app['upscale_que'] = dict(que=[], status=0)

    app['current_copying_file'] = ''
    app['current_making_file'] = ''
    app['current_upscaling_file'] = ''

    app['bool_upscale'] = BOOL_UPSCALE
    app['upscale_pct'] = 0
    app['davinci_proc'] = 0

    # watcher 프로시져 함수를 돌립니다
    app.on_startup.append(create_bg_tasks)

    # 웹서버를 엽니다. 히오스가 활성상태인지 확인하는 정보를 받습니다
    app.add_routes([
        web.get('/low', low),
        web.get('/high', high),
        web.post('/deletefile', deletefile),
        web.post('/report_upscale', report_upscale)
        # web.get('/deletefile', deletefile)
    ])

    web.run_app(app, port=8007)

    # main()

# asyncio.get_event_loop().run_until_complete(main())
