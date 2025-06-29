import os
#import time
#import shutil
import asyncio
import aiohttp
from aiohttp import web
import aiofiles
import json
#import subprocess
import logging
import logging.handlers
import datetime
import copy
import sys
from ytstudio import Studio

from aiopg.sa import create_engine
#from sqlalchemy import false
# http post 로 신호 전달을 위해 json 객체가 필요합니다
# import json
import db_youtube as db
from collections import OrderedDict as od, defaultdict

URL_UPLOADER_WS_REFRESH = 'http://192.168.1.204:9993/ws_refresh'

TRUNCATE_DAYS = 3
# PATHS = [
#     '/mnt/f/Videos/Apex Legends/',
#     '/mnt/f/Videos/Heroes of the Storm/',
#     '/mnt/f/Videos/Desktop/',
#     '/mnt/f/Videos/Overwatch 2/',
#     '/mnt/f/Videos/The Finals/',
#     '/mnt/f/Videos/Counter-strike 2/',
#     '/mnt/f/Videos/Fpsaimtrainer/',
#     '/mnt/f/Videos/Enshrouded/'
# ]

TRANSFERED_PATHS = ['/Users/utylee/Downloads/_share_mac/_Capture/']

PRIVACY = 'PRIVATE'
INTV = 5                    # watching 확인 주기입니다
# INTV = 1                    # watching 확인 주기입니다
INTV_TRNS = 10              # transfering 확인 주기입니다
INTV_TRNS_TICK = 0.5       # transfering 파일 조각 전송주기입니다
# INTV_TRNS = 1              # transfering 확인 주기입니다
INTV_UPSCL = 3              # upscaling 확인 주기입니다

BOOL_UPSCALE = 1            # 0:None,  1:1440p,  2:2160p
# BOOL_UPSCALE = 0            # 0:None,  1:1440p,  2:2160p
VIDEO_EXT_LIST = ['mp4', 'mkv', 'webm', 'avi', 'mov', 'mpg', 'mpeg', 'wmv']

# SPEED_LOW = 5 * 1024 * 128     # 5K * 128 = 0.6M /sec => 0.5초당 0.6M 입니다
# # SPEED_LOW = 24 * 1024 * 128     # 5K * 128 = 0.6M /sec => 0.5초당 0.6M 입니다
# SPEED_HIGH = 24 * 1024 * 128     # 24K * 128 = 3.2M /sec => 0.5초당 3.2M 입니다
# # SPEED_HIGH = 30 * 1024 * 128     # 24K * 128 = 3.2M /sec => 0.5초당 3.2M 입니다

# REMOTE_PATH = '/mnt/8001/97-Capture'
# # REMOTE_PATH = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture'

JSON_PATH = '/Volumes/5003/login.json'

# SUDO = 'sudo'
# DAVINCI_PATH = '/mnt/c/Program Files/Blackmagic Design/DaVinci Resolve/Resolve.exe'
DAVINCI_PATH = '/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/MacOS/Resolve'

# PYTHONW_PATH = '/mnt/c/Program Files/Python38/python.exe'   # DaVinci 공식지원이 3.6이랍니다
# PYTHONW_PATH = '/mnt/c/Users/utylee/AppData/Local/Programs/Python/Python310/python.exe'
# PYTHONW_PATH = '/mnt/c/Python38/python.exe'
PYTHONW_PATH = '/Users/utylee/.virtualenvs/misc/bin/python'

# DAVINCI_UPSCALE_PY_PATH = '/home/utylee/.virtualenvs/misc/src/DavinciResolveUpscale.py'
# DAVINCI_UPSCALE_PY_PATH = 'c:/Users/utylee/.virtualenvs/misc/src/DavinciResolveUpscale.py'
DAVINCI_UPSCALE_PY_PATH = '/Users/utylee/.virtualenvs/misc/src/DavinciResolveUpscale_mac.py'

# UPSCALING_RES = "2160"
UPSCALING_RES = "1440"
# KILL_DAVINCI_PY_PATH = '/home/utylee/.virtualenvs/misc/src/kill_win32_davinci.py'
# KILL_DAVINCI_PY_PATH = 'c:/Users/utylee/.virtualenvs/misc/src/kill_win32_davinci.py'
KILL_DAVINCI_PY_PATH = '/Users/utylee/.virtualenvs/misc/src/kill_macos_davinci.py'
# UPSCALED_FILE_NAME = '/mnt/c/Users/utylee/Videos/MainTimeline.mp4'
# UPSCALED_GATHER_PATH = '/mnt/c/Users/utylee/Videos/_Upscaled/'
# UPSCALED_FILE_NAME = '/mnt/f/Videos/MainTimeline.mp4'
# UPSCALED_TEMP_FILE_NAME = '/Users/utylee/Movies/MainTimeline.mp4'
UPSCALED_TEMP_FILE_NAME = '/Users/utylee/Downloads/_share_mac/_Capture/_Upscaled/MainTimeline.mp4'
# UPSCALED_GATHER_PATH = '/mnt/f/Videos/_Upscaled/'
UPSCALED_GATHER_PATH = '/Users/utylee/Downloads/_share_mac/_Capture/_Upscaled/'

def progress(yuklenen, toplam):
    # print(f"{round(round(yuklenen / toplam, 2) * 100)}% upload", end="\r")
    print(f"{round(yuklenen / toplam) * 100}% upload", end="\r")


async def edit_playlist(app, yt, vid, playlist):
    # playlist=["PLT7rBpvz4qpqHv8R2SOgimIorltkbH230",
    #           "PLT7rBpvz4qpqGkFPec5CQkx0v90fVmbQj"],

    # .where(db.tbl_youtube_playlists.c.nickname==playlist)):
    playlists = []
    engine = app['db']
    async with engine.acquire() as conn:
        async for r in conn.execute(db.tbl_youtube_playlists.select()):
            #  playlist_id index: 3
            playlists.append(dict(r))
    log.info(f'playlists from db: {playlists}')
    # [ {'nickname':'...',  'id': '...'}, {}, {}... ]

    # etc 의 id를 저장합니다
    etc_id = ''
    try:
        for p in playlists:
            if p['nickname'] == 'etc':
                etc_id = p['playlist_id']
        # 본 작업
        for p in playlists:
            # 다른플레이리스트에서는 모두 제거를 해주고
            if p['nickname'].strip() != playlist.strip():
                log.info(f'video {vid} remove from playlist {p["nickname"]}')
                sonuc = await yt.editVideo(
                    video_id=vid,
                    # new playlist, gamelog finals
                    removeFromPlaylist=[p['playlist_id']],
                )
            # 같은 경우엔 최조의 etc와 함께 추가해줍니다
            else:
                log.info(f'video {vid} move playlist from etc to {p["nickname"]}')
                sonuc = await yt.editVideo(
                    video_id=vid,
                    # new playlist, gamelog finals
                    playlist=[etc_id, p['playlist_id']])
    except Exception as e:
        log.info(f'edit_playlist()::exception {e}')


    # # etc 에서 제거하는 식으로 변경하는 방법이 제일 나은 것 같습니다.
    # # 혹은 각 게임 플레이리스트에서 모두 한번씩 제거하는 방법도 괜찮은 것 같습니다
    # sonuc = await yt.editVideo(
    #     video_id=vid,
    #     # new playlist, gamelog finals
    #     removeFromPlaylist=["PLT7rBpvz4qpqGkFPec5CQkx0v90fVmbQj"],
    # )


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

    log.info(f'UpscalingProc::killing davinci resolve by mac python ...')
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


async def _deletefile(file_name, timestamp):
    start_path = ''
    dest_path = ''

    # start_removed = 0
    # dest_removed = 0

    start_exists = 1
    dest_exists = 1

    # db에서 해당파일의 로컬 및 리모트의 폴더를 가져옵니다
    engine = app['db']
    try:
        async with engine.acquire() as conn:
            async for r in conn.execute(db.tbl_youtube_files.select()
                                        .where(db.sa.and_(db.tbl_youtube_files.c.filename == file_name,
                                                          db.tbl_youtube_files.c.timestamp == timestamp))):
                # db.tbl_youtube_files.c.timestamp == '3'))):
                start_path = r[8]
                dest_path = r[9]
                log.info(f'_deletefile::DB selected::{start_path}, {dest_path}')

        # 또한 transfer_que와 upscale_que 에서의 아이템도 삭제해줍니다
        que = app['transfer_que']['que']
        for q in que:
            que.remove(q) if q[0] == file_name else 0
        que1 = app['upscale_que']['que']
        for q in que1:
            que.remove(q) if q[0] == file_name else 0

    except Exception as e:
        log.info(f'_deletefile()::exception {e}')

    # 만약 start_path, dest_path 가 없으면 응급조치를 실행합니다

    # 파일이름과 폴더를 합칩니다
    # start_path = os.path.join(start_path, js['filename'])
    # dest_path = os.path.join(dest_path, js['filename'])

    log.info(f'_deletefile::fetched::start:{start_path}')
    log.info(f'_deletefile::fetched::dest:{dest_path}')

    try:
        # db에 패스가 없기에 모든 폴더를 적용해지워봅니다
        if (start_path == None):
            for p in PATHS:
                log.info(f'p: {p}')
                temp_path = os.path.join(p, file_name)
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
        if (os.path.exists(os.path.join(start_path, file_name))):
            os.remove(os.path.join(start_path, file_name))
        # else:
        #     if(os.path.exists(os.path.join(start_path, js['filename']))):
        #         os.remove(os.path.join(start_path, js['filename']))

        log.info(f'deleted start paths {file_name}')
    except Exception as e:
        log.info(f'exception while deleting start {file_name}, {e}')

    try:
        if (dest_path == None):
            dest_path = app['target']
        if (os.path.exists(os.path.join(dest_path, file_name))):
            os.remove(os.path.join(dest_path, file_name))

        log.info(f'deleted dest paths {file_name}')
    except Exception as e:
        log.info(f'exception while deleting dest {file_name}, {e}')

    # 삭제됐으면 db의 local과 remote도 업데이트해줍니다
    # if (start_exists == 0
    #         or os.path.exists(os.path.join(start_path, js['filename'])) == False):
    if (os.path.exists(os.path.join(start_path, file_name)) == False):
        # start_removed = 1
        start_exists = 0
        log.info('start no exists')
        try:
            async with engine.acquire() as conn:
                await conn.execute(db.tbl_youtube_files.update()
                                   .where(db.sa.and_(db.tbl_youtube_files.c.filename == file_name,
                                          db.tbl_youtube_files.c.timestamp == timestamp))
                                   .values(local=0))
        except Exception as e:
            log.info(f'_deletefile()::{e}')

    if (os.path.exists(os.path.join(dest_path, file_name)) == False):
        # dest_removed = 1
        dest_exists = 0
        log.info('dest no exists')
        try:
            async with engine.acquire() as conn:
                await conn.execute(db.tbl_youtube_files.update()
                                   .where(db.sa.and_(db.tbl_youtube_files.c.filename == file_name,
                                                     db.tbl_youtube_files.c.timestamp == timestamp))
                                   .values(remote=0))
        except Exception as e:
            log.info(f'_deletefile()::{e}')

    # 둘다 없을 경우에만 db의 해당파일 튜플을 삭제합니다
    # if(start_removed == 1 and dest_removed == 1):
    if (start_exists == 0 and dest_exists == 0):
        try:
            async with engine.acquire() as conn:
                await conn.execute(db.tbl_youtube_files.delete()
                                   .where(db.sa.and_(db.tbl_youtube_files.c.filename == file_name,
                                          db.tbl_youtube_files.c.timestamp == timestamp)))

            # 클라이언트에 needRefresh 를 보냅니다
            async with aiohttp.ClientSession() as sess:
                async with sess.get(URL_UPLOADER_WS_REFRESH):
                    log.info('call needRefresh')

        except Exception as e:
            log.info(f'_deletefile()::{e}')


async def deletefile(request):
    js = await request.json()
    js = json.loads(js)
    log.info(f'came into deletefile. js is {js}')
    # log.info(f'js.filename is {js["filename"]}')

    await _deletefile(js['filename'], js['timestamp'])

    # start_path = ''
    # dest_path = ''

    # # start_removed = 0
    # # dest_removed = 0

    # start_exists = 1
    # dest_exists = 1

    # # db에서 해당파일의 로컬 및 리모트의 폴더를 가져옵니다
    # engine = request.app['db']
    # try:
    #     async with engine.acquire() as conn:
    #         async for r in conn.execute(db.tbl_youtube_files.select()
    #                                     .where(db.sa.and_(db.tbl_youtube_files.c.filename == js['filename'],
    #                                                       db.tbl_youtube_files.c.timestamp == js['timestamp']))):
    #             # db.tbl_youtube_files.c.timestamp == '3'))):
    #             start_path = r[8]
    #             dest_path = r[9]
    #             log.info(f'deletefile::DB selected::{start_path}, {dest_path}')

    #     # 또한 transfer_que와 upscale_que 에서의 아이템도 삭제해줍니다
    #     que = request.app['transfer_que']['que']
    #     for q in que:
    #         que.remove(q) if q[0] == js['filename'] else 0
    #     que1 = request.app['upscale_que']['que']
    #     for q in que1:
    #         que.remove(q) if q[0] == js['filename'] else 0

    # except Exception as e:
    #     log.info(f'deletefile()::exception {e}')

    # # 만약 start_path, dest_path 가 없으면 응급조치를 실행합니다

    # # 파일이름과 폴더를 합칩니다
    # # start_path = os.path.join(start_path, js['filename'])
    # # dest_path = os.path.join(dest_path, js['filename'])

    # log.info(f'deletefile::fetched::start:{start_path}')
    # log.info(f'deletefile::fetched::dest:{dest_path}')

    # try:
    #     # db에 패스가 없기에 모든 폴더를 적용해지워봅니다
    #     if (start_path == None):
    #         for p in PATHS:
    #             log.info(f'p: {p}')
    #             temp_path = os.path.join(p, js['filename'])
    #             if (os.path.exists(temp_path)):
    #                 start_path = p
    #                 break

    #         # 모든 폴더에 해당파일이 없다면 지워졌다고 보면됩니다
    #         # 아무거나 넣어주면 이후에 당연히 지워졌다고 판단되고 진행될 것입니다
    #         if (start_path == None):
    #             start_path = PATHS[0]
    #             # start_exists = 0
    #     log.info(f'start_path: {start_path}')

    #     # if(start_removed == 0
    #     # if(start_exists == 1
    #     # and os.path.exists(os.path.join(start_path, js['filename']))):
    #     if (os.path.exists(os.path.join(start_path, js['filename']))):
    #         os.remove(os.path.join(start_path, js['filename']))
    #     # else:
    #     #     if(os.path.exists(os.path.join(start_path, js['filename']))):
    #     #         os.remove(os.path.join(start_path, js['filename']))

    #     log.info(f'deleted start paths {js["filename"]}')
    # except Exception as e:
    #     log.info(f'exception while deleting start {js["filename"]}, {e}')

    # try:
    #     if (dest_path == None):
    #         dest_path = request.app['target']
    #     if (os.path.exists(os.path.join(dest_path, js['filename']))):
    #         os.remove(os.path.join(dest_path, js['filename']))

    #     log.info(f'deleted dest paths {js["filename"]}')
    # except Exception as e:
    #     log.info(f'exception while deleting dest {js["filename"]}, {e}')

    # # 삭제됐으면 db의 local과 remote도 업데이트해줍니다
    # # if (start_exists == 0
    # #         or os.path.exists(os.path.join(start_path, js['filename'])) == False):
    # if (os.path.exists(os.path.join(start_path, js['filename'])) == False):
    #     # start_removed = 1
    #     start_exists = 0
    #     log.info('start no exists')
    #     try:
    #         async with engine.acquire() as conn:
    #             await conn.execute(db.tbl_youtube_files.update()
    #                                .where(db.sa.and_(db.tbl_youtube_files.c.filename == js['filename'],
    #                                                  db.tbl_youtube_files.c.timestamp == js['timestamp']))
    #                                .values(local=0))
    #     except Exception as e:
    #         log.info(f'{e}')

    # if (os.path.exists(os.path.join(dest_path, js['filename'])) == False):
    #     # dest_removed = 1
    #     dest_exists = 0
    #     log.info('dest no exists')
    #     try:
    #         async with engine.acquire() as conn:
    #             await conn.execute(db.tbl_youtube_files.update()
    #                                .where(db.sa.and_(db.tbl_youtube_files.c.filename == js['filename'],
    #                                                  db.tbl_youtube_files.c.timestamp == js['timestamp']))
    #                                .values(remote=0))
    #     except Exception as e:
    #         log.info(f'{e}')

    # # 둘다 없을 경우에만 db의 해당파일 튜플을 삭제합니다
    # # if(start_removed == 1 and dest_removed == 1):
    # if (start_exists == 0 and dest_exists == 0):
    #     try:
    #         async with engine.acquire() as conn:
    #             await conn.execute(db.tbl_youtube_files.delete()
    #                                .where(db.sa.and_(db.tbl_youtube_files.c.filename == js['filename'],
    #                                                  db.tbl_youtube_files.c.timestamp == js['timestamp'])))

    #         # 클라이언트에 needRefresh 를 보냅니다
    #         async with aiohttp.ClientSession() as sess:
    #             async with sess.get(URL_UPLOADER_WS_REFRESH):
    #                 log.info('call needRefresh')

    #     except Exception as e:
    #         log.info(f'{e}')

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
    # candidate = []          # 삭제 후보리스트

    # os.path.getmtime(paths[n] + f)).strftime("%y%m%d%H%M%S")) for f in os.listdir(paths[n])]))
    now = datetime.datetime.now()
    log.info(f'truncate()::now is {datetime.datetime.now()}')
    # 24시간 주기로 실행합니다
    while True:
        async with engine.acquire() as conn:
            async for r in conn.execute(db.tbl_youtube_files.select()):
                try:
                    # 중단된 전송을 초기 큐에 등록하는 프로세스입니다
                    # queueing 이 1인 것들이 예약된 상태로 전송완료가 되지 않은 것들입니다
                    if r[10] == 1:              # queueing
                        log.info(f'truncate()::중단됐던 전송: {r}')

                        #  파일,경로,업스케일완료여부 등을 업스케일큐에 넣습니다,
                        # 물론 파일이 있을 경우에만 넣습니다
                        pathfile = r[8] + r[0]     # start_path + filename
                        log.info(f'truncate()::path/file is : {pathfile}')

                        if (os.path.isfile(pathfile)):
                            app['upscale_que']['que'].append((r[0], r[8], r[13]))
                            q = app['upscale_que']['que'][-1]
                            log.info(
                                f'truncate()::upscale_queueing에 추가된 데이터: {q}')

                            # #  파일,경로 등을 app['transfering'] 큐에 넣습니다,
                            # app['transfer_que']['que'].append(
                            #     (r[0], r[8], r[9]))
                            # q = app['transfer_que']['que'][-1]
                            # log.info(f'queueing 1 추가됨: {q}')

                            # 경과일 계산부
                            t = datetime.datetime.strptime(r[12], "%y%m%d%H%M%S")
                            diff = now - t
                            log.info(f'truncate()::경과일:{diff.days}, {r[0]}')
                            log.info(f'truncate()::경과일:{diff.days}')

                            # 일주일 기간 이상은 삭제합니다
                            # 3일 기간 이상은 삭제합니다
                            # if diff.days > 7:
                            if diff.days > TRUNCATE_DAYS:
                                await conn.execute(db.tbl_youtube_files.delete()
                                                   .where(db.tbl_youtube_files.c.filename == r[0]))
                                # candidate.append(r[0])
                            # log.info(f'{r[8]}')
                        # 파일이 없을 경우는 db및 파일 삭제명령을 내립니다
                        else:
                            await _deletefile(r[0], r[12])

                        # 추가 후의 upscaling que 상태
                        log.info(
                            f'truncate()::upscale_que: {app["upscale_que"]["que"]}')
                except:
                    log.info(f'truncate()::exception')

        await asyncio.sleep(3600*24)  # 24시간 즉 하루에 한번 큐를 검색해줍니다


async def create_bg_tasks(app):
    log.info(f'\n')
    log.info(f'\n')
    log.info(f'=======================================================')
    log.info(f'capture upscaler started::create_bg_tasks()')
    log.info(f'=======================================================')
    log.info(f'\n')
    # aiohttp에서 app.loop 이 사라졌다고 하네요 그냥 아래와같이 하라고 합니다
    # app.loop.create_task(watching(app))
    app['db'] = await create_engine(host='192.168.1.203',
                                    database='youtube_db',
                                    user='postgres',
                                    password='sksmsqnwk11')
    await asyncio.sleep(0.01)


    app['Studio'] = Studio(app['login_file'])

    # 앞에 await 를 안붙였어도 되긴 했던 것 같습니다
    # asyncio.create_task(truncate(app))          # 생성된지 일주일된 자료는 db상 삭제합니다
    # asyncio.create_task(watching(app))
    # asyncio.create_task(transfering(app))

    # 이 watching은 전송을 다 받았는지를 확인하는 watching입니다
    asyncio.create_task(watching(app))
    asyncio.create_task(upscaling(app))

    asyncio.create_task(monitor_upload(app))
    asyncio.create_task(recoverQue(app))

async def recoverQue(app):
    # 시작 시 지난 큐 정보를 다시 들고 옵니다
    log.info(f'recoverQue():db inserting...')
    engine = app['db']
    try:
        async with engine.acquire() as conn:
            async for r in conn.execute(db.tbl_youtube_files.select()
                            .where(db.sa.and_(db.tbl_youtube_files.c.youtube_queueing == 1,
                                db.sa.or_(db.tbl_youtube_files.c.copying == 0,
                                            db.tbl_youtube_files.c.copying == 1)))):
                                # db.tbl_youtube_files.c.uploading == 0))):
                app['upload_que'].update({r[0]: [r[1], r[2]]})
                log.info(f'-found...({r[0]}: [{r[1]}, {r[2]}])')
    except Exception as e:
        log.info(f'recoverQue():db insert failed. {e}')
    # log.info(f'playlists from db: {}')


async def monitor_upload(app):
    log.info('came into monitor_upload function')
    yt = app['Studio']
    # result = await yt.login()
    try:
        result = await yt.login()
        log.info(f'login result:{result}')
        print(f'login result:{result}')
    except Exception as e:
        log.info('yt.login() excepted')
        print('yt.login() excepted')
        log.info(f'Exception: {e}')
        print(f'Exception: {e}')

    engine = app['db']
    # 20초마다 api_backend 서버에 현재 대기중인 큐를 요구합니다
    # 유튜브 업로드 중이었다면 끝낸 후일 것이므로

    # login.json파일 변경일도 수집합니다
    float_time = os.stat(JSON_PATH).st_mtime
    readable_time = datetime.datetime.fromtimestamp(float_time)
    # .strftime('%y%m%d-%H:%M:%S')
    readable_time = readable_time.strftime('%y%m%d-%H:%M:%S')
    log.info(f'login.json date: {readable_time}')

    app['login_file_date'] = readable_time

    # youtube api 에 login_file_date 를 보고합니다
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post('http://192.168.1.204/youtube/api/loginjson_date', data=readable_time):
            # async with sess.post('http://localhost/youtube/api/loginjson_date', data=readable_time):
                pass

    except Exception as e:
        log.info(f'exception in loginjson_date post::{e}')

    # 업로드 성공여부 리턴값입니다
    ret = 1
    # url_gimme = 'http://192.168.1.102/uploader/api/gimme_que'
    # url_result = 'http://192.168.1.102/uploader/api/upload_complete'

    # 업로드 서버에 gimme que 요청에서 자체 que 탐색으로 변경합니다
    while True:
        que = app['upload_que']
        video_id = ''

        # # login.json 갱신 작업 종료 여부를 확인합니다
        # if app['process'] != 0:
        #     # log.info(f'login.json 파일 갱신작업 중입니다.AutoHotkey')
        #     # log.info(f'process 넘버: {app["process"]}')
        #     # log.info(f'process return code: {app["process"].returncode}')
        #     # 프로세스가 종료되면 returncode가 None이 아닌 반환값을 보냅니다. 여기선 0
        #     # iex) https://docs.python.org/ko/3/library/asyncio-subprocess.html#asyncio.subprocess.Process.communicate
        #     if app['process'].returncode == 0:
        #     # await app['process'].wait()
        #         log.info(f'login.json 파일 갱신작업 완료.')
        #         # log.info(f'process 종료')
        #         app['process'] = 0

        # log.info(f'[monitor]: {app["process"]}')

        # 5초마다 큐를 탐색합니다
        await asyncio.sleep(5)
        # log.info(f'monitor_upload::while::app[uploading]:{app["uploading"]}, len(que):{len(que)}')

        if app['uploading'] == 0 and len(que) > 0:
            cur_file = ''
            title = ''
            # log.info('sending gimme request')

            que_c = copy.deepcopy(que)

            tup_c = que_c.popitem(last=False)
            temp_file = tup_c[0]
            temp_title = tup_c[1][0]
            temp_playlist = tup_c[1][1]

            log.info(
                f'tup_c: {tup_c}, {temp_file}, {temp_title}, {temp_playlist}')

            continue_ = 0
            async with engine.acquire() as conn:
                async for r in conn.execute(db.tbl_youtube_files.select()
                                            .where(db.tbl_youtube_files.c.filename == temp_file)):
                    # copying이  2 즉 완료가 아니면, 즉 아직 복사중이면 패스합니다
                    log.info(
                        # f'{temp_file} copying check by db. r[4] is {r[4]}')
                        f'{temp_file} copying check by db. r[13] is {r[13]}')
                    # if int(r[4]) != 2:
                    # if r[4] != 2:
                    # if r[4] != 3:
                    if r[13] != 1:
                        log.info(
                            # f'{temp_file} is currently copying. continue next')
                            f'{temp_file} is not upscaled. continue.. ')
                        continue_ = 1
            if (continue_ == 1):
                continue

            tup = que.popitem(last=False)
            cur_file = tup[0]
            title = tup[1][0]
            playlist = tup[1][1]
            log.info(f'tup: {tup}, {cur_file}, {title}, {playlist}')

            # async with aiohttp.ClientSession() as sess:
            #     async with sess.get(url_gimme) as resp:
            #         # log.info('came')
            #         # log.info(f'js resp is {res}')
            #         # res = await resp.json(encoding='UTF-8',
            #         #                       content_type='application/json')
            #         # res = await resp.text()
            #         # log.info(f'text was {res}')
            #         res = await resp.json()
            #         # res = await resp.json(content_type='text/plain')
            #         # res = await resp.json(content_type='application/json')
            #         # res = await resp.json(encoding='utf-8', content_type='application/json')
            #         # res = await resp.json(encoding='utf-8', content_type='text/html')
            #         res = json.loads(res)
            #         log.info(f'res :: {res}')
            #         # log.info(f'await resp.json() did')
            #         if res is not None:
            #             log.info(f'js resp is {res}')
            #             f = res['file']
            #             cur_file = f
            #             title = res['title']
            #             log.info(f'js[file] {f}')

            # 업로드 파일 존재시 유튜브 업로드를 진행합니다

            # if (res['file'] != 0):
            # if (res['file'] != '0'):
            if (cur_file != 0):
                # log.info('js[file] is not None.. upload starts')
                log.info('cur_file is not None.. upload starts')
                # ret = upload(app, res)
                filename = cur_file
                path = f'{UPSCALED_GATHER_PATH}{filename}'
                # title = res['title']

                app['uploading'] = 1

                # db상 copying column을 2로 변경합니다
                try:
                    async with engine.acquire() as conn:
                        async with conn.execute(db.tbl_youtube_files.update()
                                                .where(db.tbl_youtube_files.c.filename == cur_file)
                                                .values(uploading=2)):
                            log.info(f'db copying column to 2')

                    # 변경후 클라이언트들에 리프레시 신호를 보냅니다
                    async with aiohttp.ClientSession() as sess:
                        async with sess.get(
                                URL_UPLOADER_WS_REFRESH) as resp:
                            result = await resp.text()
                            log.info(f'call needRefresh: {result}')

                    # # 변경후 클라이언트들에 리프레시 신호를 보냅니다
                    # await send_ws(app['websockets'], 'needRefresh')
                except:
                    log.info(f'exception:db copying column to 2')

                # asyncio.create_task(asyncupload(app, path, title))
                # await yt.login()
                # privacy='PUBLIC')

                # 'sessionToken': self.cookies['SESSION_TOKEN'],
                if os.path.exists(JSON_PATH):
                    app['login_file'] = json.loads(
                        open(JSON_PATH, 'r').read())
                    # print(app['login_file'])
                    # sessionToken = app['login_file']['SESSION_TOKEN']
                    # sidCc =  app['login_file']['SIDCC']

                    # yt.cookies['SESSION_TOKEN'] = sessionToken
                    # yt.cookies['SIDCC'] = sidCc

                    # log.info(f'SESSION_TOKEN is {sessionToken}')
                    # log.info(f'SIDCC is {sidCc}')
                else:
                    exit('no json file')

                try:
                    log.info(f'app["login_file"]')
                    yt = Studio(app['login_file'])

                    # 업로드 직전 다시 로그인하고
                    await yt.login()
                    log.info(f'yt.login() succeed')
                    log.info(f'yt.uploadVideo starting...')
                    log.info(f'path:{path}, title:{title}')

                    # 업로드를 시작합니다
                    ret = await yt.uploadVideo(
                        path,
                        progress=progress,
                        description='',
                        privacy=PRIVACY,
                        title=title)
                    # ret = json.loads(ret)
                    log.info(
                        f'monitor_upload::yt.uploadVideo::upload completed.\n ret was {ret}')
                    # log.info(f'upload completed. ')

                    video_id = ret["videoId"]
                    log.info(f'-- videoid: {video_id}')

                    # db 상 video_id 를 업데이트해 줍니다
                    try:
                        async with engine.acquire() as conn:
                            async with conn.execute(db.tbl_youtube_files.update()
                                                    .where(db.tbl_youtube_files.c.filename == cur_file)
                                                    .values(video_id=video_id)):
                                log.info(f'video_id db updated')

                    except Exception as E:
                        log.info(f'exception {E} while video_id updating')

                    # 업로드후 playlist에 따라 옮겨줍니다
                    await edit_playlist(app, yt, video_id, playlist)

                    # error 발생했을 경우
                    if 'error' in ret.keys():
                        log.info(f'upload error. ret is {ret}')
                        ret = 1
                    # 성공했을 경우
                    else:
                        ret = 0
                except Exception as e:
                    log.info(f'yt.uploadVideo upload excepted')
                    log.info(f'Exception: {e}')
                    print(f'yt.uploadVideo upload excepted')
                    print(f'Exception: {e}')
                    ret = 1
                # ret = json.loads(ret)

                # SESSION_TOKEN 에 문제가 있을 때의 응답입니다
                '''
                {'error': {'code': 400, 'message': 'Request contains an invalid argument.', 'errors': [{'message': 'Request contains an invalid argument.', 'domain': 'global', 'reason': 'badRequest'}], 'status': 'INVALID_ARGUMENT'}}]
                '''

            # except:
            #    log.info('exeption in monitor')
            #     pass

            # 업로드 성공했으면
            if ret == 0:
                try:
                    async with engine.acquire() as conn:
                        async with conn.execute(db.tbl_youtube_files.update().
                                                where(db.tbl_youtube_files.c.filename == cur_file).
                                                values(uploading=3)):
                            log.info(f'uploading to 3 to db')
                    ret = 1

                except:
                    log.info(f'exception:: on uploading to 3 to db')

                # payload = {"file": cur_file, "result": 0}
                # async with aiohttp.ClientSession() as sess:
                #     async with sess.post(url_result, json=payload) as resp:
                #         log.info(f'upload ok send and response')
                ret = 1
            elif ret == 1:
                try:
                    async with engine.acquire() as conn:
                        async with conn.execute(db.tbl_youtube_files.update().
                                                where(db.tbl_youtube_files.c.filename == cur_file).
                                                values(uploading=4)):
                            log.info(f'erro:uploading to 4 to db')

                except:
                    log.info(f'exception:: on uploading to 4 to db')

            # 또한 needRefresh를 호출해줍니다
            try:
                async with aiohttp.ClientSession() as sess:
                    async with sess.get(
                            URL_UPLOADER_WS_REFRESH) as resp:
                        result = await resp.text()
                        log.info(f'call needRefresh: {result}')
            except Exception as e:
                log.info(f'exception {e} while pct needRefreshing')

            # # 업로드 성공/실패 후  클라이언트들에 리프레시 신호를 보냅니다
            # await send_ws(app['websockets'], 'needRefresh')
            app['uploading'] = 0

        # await asyncio.sleep(5)
        # await asyncio.sleep(20)


async def upscaling(app):
    # que, status = app['transfer_que']['que'], app['transfer_que']['status']
    engine = app['db']

    # 3초에 한번씩 큐 리스트를 탐색합니다
    while True:
        # status가 0(대기중)이며 que 리스트에 항목이 있을 때 작동합니다
        # if status == 0 and len(que):

        que = app['upscale_que']['que']
        ret = 1
        # if len(que) >= 0:
        if len(que) > 0:
            # 첫번째 항목을 큐에서 꺼냅니다

            # 현재 업스케일 큐를 표시합니다
            log.info(f'upscaling()::que: {que}')

            file, path, upscaled = que.pop(0)
            # file = '1.mp4'
            # path = '/Users/utylee/Downloads/_share_mac/_Capture/'
            # upscaled = 0
            log.info(f'upscaling()::pop(0)::(file, path, upscaled)')
            log.info(f'({file}, {path}, {upscaled})')
            pathfile = f'{path}{file}'

            exst = os.path.isfile(pathfile)
            if (exst == 0):
                log.info(f'upscaling()::({pathfile}) is not exists')

            # BOOL_UPSCALE 이 1이면서 upscale이 안되어있을 경우
            # 또한 해당파일이 존재할 경우에만
            # DaVinciResolve 프로세스를 실행합니다
            if (upscaled == 0 and BOOL_UPSCALE and path != UPSCALED_GATHER_PATH):
                # log.info(f'came in')

                log.info(f'sys.path:{sys.path}')
                ver = await asyncio.create_subprocess_exec(PYTHONW_PATH, '--version', stdout=None)
                log.info(f'python ver is {ver}')

                log.info(
                    f'upscaling()::upscaled==0::executing davinciResolve -nogui...')
                app['davinci_proc'] = await asyncio.create_subprocess_exec(DAVINCI_PATH, '-nogui', stdout=None)
                # app['davinci_proc'] = await asyncio.create_subprocess_exec(DAVINCI_PATH, stdout=None)
                log.info(f'upscaling()::davinci_proc: {app["davinci_proc"]}')
                log.info(f'upscaling()::wait for davinci resolve executing...')
                # await asyncio.sleep(2)     # 실행시 10초정도는 기다려줘야하는 것 같습니다
                await asyncio.sleep(10)     # 실행시 10초정도는 기다려줘야하는 것 같습니다
                # await app['davinci_proc'].wait()

                # 업스케일을 실행합니다
                app['current_upscaling_file'] = file  # 현재만들어진 파일명을 갖고있습니다
                # pathfile_win = 'c:' + pathfile[6:]  # wsl의 /mnt/c 를 윈도우 형태로 변환해줍니다
                # wsl의 /mnt/c 를 윈도우 형태로 변환해줍니다
                # pathfile_win = '"' + 'f:' + pathfile[6:] + '"'
                # pathfile_win = 'f:' + pathfile[6:]


                pathfile_mac = pathfile
                log.info(f'upscaling()::pathfile_mac:{pathfile_mac}')
                log.info(f'upscaling()::davinci upscale processing with pythonw...')
                log.info(
                    f'upscaling()::PYTHONW_PATH:{PYTHONW_PATH}, DAVINCI_UPSCALE_PY_PATH:{DAVINCI_UPSCALE_PY_PATH}, pathfile_mac:{pathfile_mac}, UPSCALING_RES: {UPSCALING_RES}')
                proc_upscale = await asyncio.create_subprocess_exec(PYTHONW_PATH, DAVINCI_UPSCALE_PY_PATH, pathfile_mac, UPSCALING_RES, stdout=None)

                ret = await proc_upscale.wait()
                log.info(f'upscaling()::davinci upscale return code: {ret}')
                if ret == 0:
                    log.info(f'upscaling()::Upscale Successed!')

                    # 변환이 성공하였으니 출력파일을 upscale 폴더로 이동해줍니다
                    upscaled_pathfile = UPSCALED_GATHER_PATH + file
                    log.info(
                        f'upscaling()::upscaled_pathfile is {upscaled_pathfile}')
                    # db 상 넣어줄 start_path 를 upscale폴더로 변경해줍니다
                    path = UPSCALED_GATHER_PATH
                    # 생성된파일을 _Upscaled 폴더로 옮기고 원본 파일도 삭제합니다
                    try:
                        os.rename(UPSCALED_TEMP_FILE_NAME, upscaled_pathfile)
                        os.remove(pathfile)
                    except Exception as ose:
                        log.info(
                            f'upscaling()::exception while moving and removing upscaled file\n {ose}')
                    # 또한 변환이 성공하였으니 upscale_pct도 100으로 지정해줍니다
                    app['upscale_pct'] = 100
                    upscaled = 1

                # await asyncio.sleep(20)

                log.info(
                    f'upscaling()::killing davinci resolve by win python.exe ...')
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
                    log.info(f'upscaling()::upscale failed!!')

            #################################################
            #
            # DavinciResolveUpscale 혹은 비처리 패스등을 끝낸 이후
            #
            try:
                # db 에 upscaled 플래그를 넣어줍니다
                # payload = {'file': file, 'status': 2}
                # ret = await send_current_status(payload)
                # _upscaled = int(not ret)

                # 혹시 수동 db삭제등으로 플래그에 문제가 생겼을 경우를 대비해
                # path긑이 _Upscaled/ 라면 upscaled 값을 1로 설정해줍니다
                if (path[-10:-1] == '_Upscaled'):
                    upscaled = 1
                try:
                    # ret 값에 따라 upscaled 값을 넣어줍니다
                    # .values(upscaled=app['bool_upscale'],
                    async with engine.acquire() as conn:
                        await conn.execute(db.tbl_youtube_files.update()
                                           .where(db.tbl_youtube_files.c.filename == file)
                                           .values(upscaled=upscaled,
                                                   upscale_pct=app['upscale_pct'],
                                                   making=2,
                                                   start_path=path))
                        log.info(
                            f'upscaling()::upscaled value from ret is {upscaled}')
                    # 또한 needRefresh를 호출해줍니다
                    async with aiohttp.ClientSession() as sess:
                        async with sess.get(URL_UPLOADER_WS_REFRESH):
                            log.info('upscaling()::call needRefresh')
                except:
                    log.info('upscaling()::db update excepted!!')

                # #  파일,경로 등을 app['transfering'] 큐에 넣습니다
                # # transfering()에서 전송을 담당합니다
                # # upscale 플래그와 결과가 같을 경우만 다음 프로세스인 전송 큐에 삽입해줍니다
                # if (BOOL_UPSCALE == upscaled):
                #     log.info(
                #         f'upscaling()::inserting to transfering que..\n{file}, {path}, {app["target"]}')
                #     app['transfer_que']['que'].append(
                #         (file, path, app['target']))
                #     q = app['transfer_que']['que']
                #     log.info(f'upscaling()::after inserting: {q}')

            except Exception as e:
                log.info(f'upscaling()::exception {e} on upscale()')

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
                    log.info(f'transfering()::exception while db updating')

                print(f'start: {start}\ndesti: {desti}')
                log.info(f'transfering()::copying starting...')
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

            except Exception as e:
                print('exception in copying')
                log.info(f'transfering()::exception in copying...{e}')
                exct = 1

            # 복사완료후 원래 파일을 삭제합니다
            print('copy complete')
            log.info('transfering()::copy complete')
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
                    log.info(f'transfering()::exception {e}')

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
                    log.info(f'transfering()::exception in file deleting... {e}')

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


# 파일 전송을 다 받았느냐를 확인하는 watching입니다
async def watching(app):
    # path = 'C:/Users/utylee/Videos/World Of Warcraft'

    # # 게임 중이냐 아느냐로 속도 조절을 할 수 있게끔 기준 변수를 넣어봅니다
    # speed_control = 1

    # # 복사 버퍼 크기인데 0.5초 단위의 속도를 의미합니다. 현재 초당 5메가로
    # # 캡쳐과 되고 있기에 그걸 감안해서 설정합니다
    # # cur_length = 24 * 1024 * 100     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # # cur_length = 16 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # # 속도를 더 늦춰봅니다
    # # cur_length = 8 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # cur_length = app['cur_length']

    # # 게임 중이 아니라면 높은속도로 복사합니다
    # if speed_control == 0:
    #     # cur_length = 24 * 1024 * 128      # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    #     cur_length = SPEED_HIGH             # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다

    # # 여러 경로를 감시하게끔 변경합니다
    # # path = '/mnt/c/Users/utylee/Videos/World Of Warcraft/'
    # paths = app['paths']
    paths = TRANSFERED_PATHS
    log.info(f'paths:{paths}')
    #TRANSFERED_PATH = '/Users/utylee/Downloads/_share_mac/_Capture'

    # # target = r'\\192.168.1.202\clark\4002\00-MediaWorld-4002\97-Capture'
    # # target = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture'
    # target = app['target']

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
            # log.info('came into true')
            befores_dict.update(dict([(f, datetime.datetime.fromtimestamp(
                os.path.getmtime(paths[n] + f)).strftime("%y%m%d%H%M%S")) for f in os.listdir(paths[n])]))
        # log.info(f'{befores_dict}')
        # timestamp에 따라 내림차순 정렬을 합니다
        files_dict = dict(sorted(befores_dict.items(),
                                 key=lambda x: x[1], reverse=True))
        befores.append(befores_dict)
        log.info(f'watching()::befores:{befores}')

        # 맥서버 upscaler이므로 db에 넣을 필요가 없습니다
        # # 모든 파일들을 전부 db에 삽입해봅니다
        # async with engine.acquire() as conn:
        #     files = files_dict
        #     # for f in app['files']:
        # # 모든 파일들을 전부 db에 삽입해봅니다
        #     log.info(f'모든 파일들을 전부 db에 삽입해봅니다')
        #     for f in files:
        #         # print(f'file: {f}, time: {int(files[f])}')
        #         log.info(f'insertingDB::file: {f}, time: {int(files[f])}')

        #         # 동일한 파일명을 넣어줄 경우 exception이 나면서 패스되게 합니다
        #         try:
        #             await conn.execute(db.tbl_youtube_files.insert()
        #                                .values(filename=f,
        #                                        timestamp=files[f],
        #                                        local=1, queueing=0))
        #             # title='',
        #             # playlist='',
        #             # status='',
        #             # await conn.execute(db.tbl_youtube_files.insert().values(filename=f))
        #             log.info(f'success')
        #         except:
        #             print('exception on inserting db!')
        #             log.info('exception on inserting db!')

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
                # log.info('while1true')
                afters_dict.update(dict([(f, datetime.datetime.fromtimestamp(
                    os.path.getmtime(paths[n] + f)).strftime("%y%m%d%H%M%S"))
                    for f in os.listdir(paths[n])]))

            # timestamp에 따라 내림차순 정렬을 합니다
            afters[n] = dict(sorted(afters_dict.items(),
                                    key=lambda x: x[1], reverse=True))
            # afters[n] = dict([(f, None) for f in os.listdir(paths[n])])
            # log.info(f'afters_dict:{afters_dict}')

            addeds[n] = dict([(f, afters[n][f])
                             for f in afters[n] if not f in befores[n]])
            # log.info(f'addeds[n]:{addeds[n]}')
            # addeds[n] = [f for f in afters[n] if not f in befores[n]]
            removeds[n] = [f for f in befores[n] if not f in afters[n]]
            if addeds[n]:
                # if added:
                for i in addeds[n]:
                    print(f'added {i}')
                    log.info(f'watching()::while::if::added {i}')
                    log.info(f'afters[n]:{afters[n]}')
                    log.info(f'addeds[n]:{addeds[n]}')

                    t = int(addeds[n][i])

                    # db에 삽입을 하는 것이 아닌 해당 파일명의 copying이 끝났는지를
                    #보고 끝났으면 upscaling que 에 넣습니다
                    # 해당파일명 copying이 2면 업스케일큐에 넣고 
                    #copying을 3으로 바꿔줍니다

                    # 추가된 파일을 db에 삽입을 시도합니다
                    async with engine.acquire() as conn:
                        # log.info(
                        #     f'insertingDB::file: {i}, time: {int(addeds[n][i])}')
                        log.info(
                            # f'findingDB::file: {i}, time: {t}')
                            f'watching()::while::if::async with::findingDB::file: {i}')

                        # 해당파일명의 copying이 2인지를 확인합니다
                        # # 동일한 파일명을 넣어줄 경우 exception이 나면서 패스되게 합니다

                                   # .where(db.sa.and_(db.tbl_youtube_files.c.filename == file_name,
                        try:
                            # db에 copying 2(전송완료)인것을 찾아 3으로 바꿔줍니다
                            log.info(f'came here')
                            await conn.execute(db.tbl_youtube_files.update()
                                    .where(db.sa.and_((db.tbl_youtube_files.c.filename==i), (db.tbl_youtube_files.c.copying==2)))
                                    .values(copying=3))
                            app['current_making_file'] = i  # 현재만들어진 파일명을 갖고있습니다
                            _start_path = paths[n]

                            # upscale 큐에 넣어줍니다
                            # BOOL_UPSCALE 에 상관없이 일단 upscale 큐가 판단한 후
                            # transfer 큐로 넘겨줍니다 (파일명, 폴더명)
                            app['upscale_que']['que'].append((i, _start_path, 0))


                            # await conn.execute(db.tbl_youtube_files.insert()
                            #                    .values(filename=i, timestamp=addeds[n][i],
                            #                            local=1, uploading=0,
                            #                            playlist='etc',
                            #                            upscaled=0,
                            #                            upscale_pct=-1,
                            #                            queueing=1,
                            #                            youtube_queueing=0,
                            #                            making=1, remote=0, copying=0,
                            #                            start_path=paths[n],
                            #                            dest_path=target))

                            # 또한 needRefresh를 호출해줍니다
                            async with aiohttp.ClientSession() as sess:
                                async with sess.get(
                                        URL_UPLOADER_WS_REFRESH) as resp:
                                    result = await resp.text()
                                    log.info(f'call needRefresh: {result}')
                        except Exception as e:
                            print(f'exception {e} on updating copying!')
                            log.info(f'exception {e} on updating copying!')

                    # # 파일이 여러개가 동시에 추가될 경우 파일 한개 밖에 처리하지 못하던 문제 수정
                    # # if i[-3:] == 'mp4' or i[-3:] == 'mkv' or i[-4:] == 'webm':
                    # if i[-5:].split('.')[1].lower() in VIDEO_EXT_LIST:
                    #     exct = 0
                    #     a = f'{paths[n]}{i}'
                    #     # /mnt 이 아닌 \\192..xxx 방식의 위치를 사용해봅니다
                    #     b = f'{target}/{i}'
                    #     # b = f'{target}\\{i}'
                    #     # b = f'{target}/{i}.part'
                    #     # print(i)
                    #     # print(target)

                    #     payload = {'file': i, 'status': 0}

                    #     try:
                    #         before_size = os.path.getsize(a)
                    #         print('size checking start')
                    #         log.info('size checking start')
                    #         while 1:
                    #             # time.sleep(3)
                    #             await asyncio.sleep(3)
                    #             cur_size = os.path.getsize(a)
                    #             print(f'before: {before_size}, cur: {cur_size}')
                    #             log.info(
                    #                 f'before: {before_size}, cur: {cur_size}')
                    #             if before_size == cur_size:
                    #                 print('complete recoding')
                    #                 log.info('complete recoding')
                    #                 break

                    #             before_size = cur_size

                    #         # <--- 녹화완료
                    #         app['current_making_file'] = i  # 현재만들어진 파일명을 갖고있습니다
                    #         _start_path = paths[n]

                    #         # upscale 큐에 넣어줍니다
                    #         # BOOL_UPSCALE 에 상관없이 일단 upscale 큐가 판단한 후
                    #         # transfer 큐로 넘겨줍니다 (파일명, 폴더명)
                    #         app['upscale_que']['que'].append((i, _start_path, 0))


                    #     except:
                    #         print('exception in added file check')
                    #         log.info('exception in added file check')
                    #         exct = 1
                    #         continue

            # before = after
            befores[n] = afters[n]


# 사용 안하는 듯 합니다
'''
async def send_complete(fname):
    async with aiohttp.ClientSession() as sess:
        resp = await sess.post('http://192.168.1.202:9202/copyend', json=json.dumps({'file': fname}))
        a = await resp.text()
        print(a)
        return a
        '''


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


async def addque(request):
    res=await request.json()
    res=json.loads(res)
    log.info('came into handle addque')
    log.info(res)
    # title1 = res["title"]
    filename=res["file"]
    title=res["title"]
    playlist=res["playlist"]
    # filename = f'{FIXED_PATH}{filename}'

    # request.app['upload_que'].update({filename: title})
    request.app['upload_que'].update({filename: [title, playlist]})

    # args = request.app['args']
    # youtube = get_authenticated_service(args)

    # args.file = f'{FIXED_PATH}{filename}'
    # args.title = title1

    # print(f'file:{args.file}')
    # print(f'title:{args.title}')

    result='ok'
    # try:
    #     initialize_upload(youtube, args)
    # except:
    #     result = 'err'

    # request.app['uploading'] = 1
    # initialize_upload(youtube, args)
    # request.app['uploading'] = 0

    return web.Response(text=result)

async def ws(request):
    # transport 를 굳이 쓰지 않아도 되게끔 변경했다고 합니다
    # eg)https://github.com/aio-libs/aiohttp/issues/4189
    # peer_info = request.transport.get_extra_info('peername')
    peer_info = request.get_extra_info('peername')
    # (host, port) = request.transport.get_extra_info('peername')
    remote = request.remote
    # forward = request.headers.get('X-FORWARDED-FOR', 2)
    # peer_info = f'{host}:{port}'
    peer_info = f'{peer_info[0]}:{peer_info[1]}'
    # peer_info = f'{remote}'
    # peer_info = f'{host}:{port},{remote},{forward}'
    log.info(f'came into websocket_handlers: {peer_info}')
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # 최초 연결시 현재의 auth process 상태를 전달해줍니다
    if request.app['process'] != 0:
        await ws.send_str('processing')

    # aiohttp 상 예제처럼 set형과 add가 아닌 그냥 int형과 append 조합으로 사용하기로 합니다
    # request.app['websockets'][peer_info].add(ws)
    request.app['websockets'].update({peer_info: ws})
    log.info(f'sockets dict:{app["websockets"]}')

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    log.info(f'ws msg:{msg.data}')
                    if msg.data == 'connect':
                        await ws.send_str(msg.data + ':answer')

                    else:
                        await ws.send_str(msg.data + ':answer')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                log.info(f'websocket msg type error: {ws.exception()})')

    finally:
        # pass
        del request.app['websockets'][peer_info]

    log.info(f'websocket from {peer_info} closed')

    return ws

async def ws_refresh(request):
    request.app['websockets']
    await send_ws(request.app['websockets'], 'needRefresh')
    '''
    try:
        log.info(f'trying websocket send:needRefresh ...')
        log.info(f'...to {app["websockets"].keys()}')
        for ws_pair in app['websockets'].items():
            log.info(f'{ws_pair[0]} send_str...')
            bClosed = ws_pair[1].closed
            log.info(f'{ws_pair[0]} closed is {bClosed}')
            if(bClosed != True):
                await ws_pair[1].send_str('needRefresh')
    except Exception as e:
        log.info(f'exception in websocket send:needRefresh: {e}')
        '''

    return web.Response(text='ok')

async def ws_phase(request):
    phase = request.match_info['phase']

    # subprocess로 매초 확인하는 작업으로 종료여부를 확인했는데
    # AutoHotkey에서 http client가 가능하다는 것을 안 이후로는 뒤늦게
    # 직접 신호전달로 변경해봅니다
    if (phase == "finished"):
        # if app['process'].returncode == 0:
        # await app['process'].wait()
        log.info(f'login.json 파일 갱신작업 완료.')
        await loginjson_finished()

        await send_ws(app['websockets'], 'finished')
        await send_ws(app['websockets'], 'needRefresh')

    else:
        # await send_ws(request.app['websockets'],  proc_phase)
        await send_ws(request.app['websockets'],  'processing_' + phase)

    return web.Response(text='ok')

async def send_ws(ws, msg):
    try:
        log.info(f'trying websocket send:{msg} ...')
        log.info(f'...to {ws.keys()}')
        for ws_pair in ws.items():
            log.info(f'{ws_pair[0]} send_str...')
            bClosed = ws_pair[1].closed
            log.info(f'{ws_pair[0]} closed is {bClosed}')
            if (bClosed != True):
                await ws_pair[1].send_str(msg)
    except Exception as e:
        log.info(f'exception in websocket send:{msg}: {e}')


async def loginjson_finished():
    # log.info(f'process 종료')

    # 파일 변경일도 수집합니다
    float_time = os.stat(JSON_PATH).st_mtime
    readable_time = datetime.datetime.fromtimestamp(float_time)
    readable_time = readable_time.strftime('%y%m%d-%H:%M:%S')
    log.info(f'login.json date: {readable_time}')
    app['login_file_date'] = readable_time

    # api에 해당시간을 전달해줍니다
    async with aiohttp.ClientSession() as sess:
        async with sess.post(
                # 'http://localhost/youtube/api/report_loginjson_date', data=readable_time):
                'http://192.168.1.204/youtube/api/report_loginjson_date', data=readable_time):
            log.info(f'report loginjson date:{readable_time}')

    app['process'] = 0


if __name__ == '__main__':
    # log_path = f'/home/utylee/capture.log'
    log_path = f'/Users/utylee/capture.log'
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
    # # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # app['cur_length'] = SPEED_HIGH
    # # app['paths'] = [
    # #     '/mnt/c/Users/utylee/Videos/World Of Warcraft/',
    # #     '/mnt/c/Users/utylee/Videos/Heroes of the Storm/',
    # #     '/mnt/c/Users/utylee/Videos/Desktop/'
    # # ]
    # app['paths'] = PATHS
    # app['target'] = REMOTE_PATH
    app['transfer_que'] = dict(que=[],
                               status=0)  # status:: 0: 대기중, 1: 복사중, 2: 복사완료
    app['upscale_que'] = dict(que=[], status=0)

    app['current_copying_file'] = ''
    app['current_making_file'] = ''
    app['current_upscaling_file'] = ''

    app['bool_upscale'] = BOOL_UPSCALE
    app['upscale_pct'] = 0
    app['davinci_proc'] = 0


    # 204의 youtube_uploading 통합하면서 가져온 변수들
    app['uploading']=0
    # app['youtube'] = youtube
    app['login_file']=''
    app['login_file_date']=''
    app['upload_que']=od()
    app['process']=0
    app['websockets']=defaultdict(int)

    # if os.path.exists('./login.json'):
    # SESSION_TOKEN 을 고쳐도 에러가 나서 보니 SIDCC도 변경되었더군요
    if os.path.exists(JSON_PATH):
        app['login_file']=json.loads(open(JSON_PATH, 'r').read())
        print(app['login_file'])
        log.info('login file loaded')
        log.info(app['login_file'])
    else:
        log.info('no json file')
        exit('no json file')

    app.on_startup.append(create_bg_tasks)

    # 웹서버를 엽니다. 히오스가 활성상태인지 확인하는 정보를 받습니다
    app.add_routes([
        web.get('/low', low),
        web.get('/high', high),
        web.post('/deletefile', deletefile),
        web.post('/report_upscale', report_upscale),
        web.post('/addque', addque),
        web.get('/ws', ws),
        web.get('/ws/{phase:.*}', ws_phase),
        web.get('/ws_refresh', ws_refresh),
        # web.get('/deletefile', deletefile)
    ])

    # web.run_app(app, port=8007)
    web.run_app(app, port=9993)

    # main()

# asyncio.get_event_loop().run_until_complete(main())
