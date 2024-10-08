import http.client
from aiopg.sa import create_engine
import httplib2
import os
import random
import sys
import time
import datetime

# cook 루틴을 추가하기 위한 라이브러리들입니다
from aiofiles import open as open_async
import pyperclip
import re

from ytstudio import Studio

# from apiclient.discovery import build
# from apiclient.errors import HttpError
# from apiclient.http import MediaFileUpload
# from oauth2client.client import flow_from_clientsecrets
# from oauth2client.file import Storage
# from oauth2client.tools import argparser, run_flow

import asyncio
import aiohttp
from aiohttp import web
import db_youtube as db
import json
import logging
import logging.handlers
from collections import OrderedDict as od, defaultdict
import copy


# FIXED_PATH = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture/'
FIXED_PATH = '/mnt/8001/97-Capture/'
JSON_PATH = '/home/utylee/login.json'
COOKIE_PATH = f'/mnt/c/Users/utylee/Downloads/cookies.txt'
# PRIVACY = 'PUBLIC'
PRIVACY = 'PRIVATE'


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

    # # etc 에서 제거하는 식으로 변경하는 방법이 제일 나은 것 같습니다.
    # # 혹은 각 게임 플레이리스트에서 모두 한번씩 제거하는 방법도 괜찮은 것 같습니다
    # sonuc = await yt.editVideo(
    #     video_id=vid,
    #     # new playlist, gamelog finals
    #     removeFromPlaylist=["PLT7rBpvz4qpqGkFPec5CQkx0v90fVmbQj"],
    # )


async def cook(request):
    full = []
    full_dict = dict()

    # 먼저 login.json 에서 SESSION_TOKEN 값은 저장해놓습니다
    # --> pyperclip으로 클립보드 값을 넣어주는 것으로 변경합니다
    # 실행시 번거롭지 않게 바로 login.json에 sessionToken을 반영하도록
    sessionToken = ''
    # try:
    #     async with open_async(JSON_PATH, 'r') as f:
    #         r = await f.readlines()
    #         rr = "".join(r)
    #         # print(r)
    #         # print(rr)
    #         p = json.loads(rr)
    #         # print(p)
    #         print(f'.sessionToken: {p["SESSION_TOKEN"]}')
    #         # sessionToken = p['SESSION_TOKEN']

    # except:
    #     pass

    # clipboard값을 sessionToken에 바로 넣어줍니다
    log.info('pyperclipping')
    try:
        pyperclip.ENCODING = 'cp949'
        sessionToken = pyperclip.paste()

    except Exception as e:
        log.info(f'pyperclip exception: {e}')

    log.info('opening cookies.txt')
    # 쿠키파일을 엽니다
    async with open_async(COOKIE_PATH, 'r') as f:
        full = await f.readlines()

    log.info('cookies.txt read')
    # 파싱하여 dict를 만듭니다
    res = ()
    for i in full:
        s = re.search(r'\S+\s+\S+\s+/\s+\S+\s+\S+\s+(.*)\t(.*)', i)
        if (s):
            res = (s.group(1), s.group(2))
            full_dict[s.group(1)] = s.group(2)
        # print(i)
        # print(res)

    # full_dict['SESSION_TOKEN'] = sessionToken
    # # print(full_dict['VISITOR_INFO1_LIVE'])
    # print(full_dict)

    # 로긴파일을 작성합니다
    async with open_async(JSON_PATH, 'w') as f:
        # await f.write('{\n\t"SESSION_TOKEN": "",')

        # p = json.dumps(full_dict, indent=4)
        # await f.write(p)

        await f.write('{\n')
        # await f.write('\t"SESSION_TOKEN": ""')
        await f.write(f'\t"SESSION_TOKEN": "{sessionToken}"')
        # f-string 최외각을 single-quote ' 로 감싸면 dict형식은 double-quote " 로 감싸면 되고
        # 그 반대도 되네요. 검색해보니
        # i.e. https://stackoverflow.com/questions/43488137/how-can-i-do-a-dictionary-format-with-f-string-in-python-3-6
        # await f.write(f',\n\t"LOGIN_INFO": "{full_dict["LOGIN_INFO"]}"')
        await f.write(f',\n\t"SID": "{full_dict["SID"]}"')
        await f.write(f',\n\t"HSID": "{full_dict["HSID"]}"')
        await f.write(f',\n\t"SSID": "{full_dict["SSID"]}"')
        await f.write(f',\n\t"APISID": "{full_dict["APISID"]}"')
        await f.write(f',\n\t"SAPISID": "{full_dict["SAPISID"]}"')
        await f.write(f',\n\t"LOGIN_INFO": "{full_dict["LOGIN_INFO"]}"')
        await f.write(f',\n\t"__Secure-1PSIDTS": "{full_dict["__Secure-1PSIDTS"]}"')
        await f.write('\n}')

        '''
        await f.write('{\n')
        await f.write('\t"SESSION_TOKEN": ""')
        # f-string 최외각을 single-quote ' 로 감싸면 dict형식은 double-quote " 로 감싸면 되고
        #그 반대도 되네요. 검색해보니
        # i.e. https://stackoverflow.com/questions/43488137/how-can-i-do-a-dictionary-format-with-f-string-in-python-3-6
        await f.write(f',\n\t"VISITOR_INFO1_LIVE": "{full_dict["VISITOR_INFO1_LIVE"]}"')
        # await f.write(f',\n\t"PREF": "{full_dict["PREF"]}"')
        await f.write(f',\n\t"PREF": "f6=40000000&tz=Asia.Seoul"')
        await f.write(f',\n\t"LOGIN_INFO": "{full_dict["LOGIN_INFO"]}"')
        await f.write(f',\n\t"SID": "{full_dict["SID"]}"')
        await f.write(f',\n\t"__Secure-3PSID": "{full_dict["__Secure-3PSID"]}"')
        await f.write(f',\n\t"HSID": "{full_dict["HSID"]}"')
        await f.write(f',\n\t"SSID": "{full_dict["SSID"]}"')
        await f.write(f',\n\t"APISID": "{full_dict["APISID"]}"')
        await f.write(f',\n\t"SAPISID": "{full_dict["SAPISID"]}"')
        await f.write(f',\n\t"__Secure-3PAPISID": "{full_dict["__Secure-3PAPISID"]}"')
        await f.write(f',\n\t"YSC": "{full_dict["YSC"]}"')
        await f.write(f',\n\t"SIDCC": "{full_dict["SIDCC"]}"')
        await f.write('\n}')
        '''

    print('\nlogin.json wrote')
    log.info('login.json wrote')

    r = ''
    rr = ''
    # 완성된 login.json 출력
    try:
        async with open_async(JSON_PATH, 'r') as f:
            r = await f.readlines()
            rr = "".join(r)
            # print(r)
            # print(rr)
    except Exception as e:
        print(f'Exception:{e}')
        log.info(f'Exception:{e}')

    return web.Response(text=rr)


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


async def asyncupload(app, path, title):
    yt = app['Studio']
    log.info(f'asyncupload::path is:{path}')
    ret = await yt.uploadVideo(
        path,
        title=title,
        progress=progress,
        privacy='PUBLIC')
    if ret is not None:
        ret = 0


async def monitor_subprocess(app):
    while True:
        # login.json 갱신 작업 종료 여부를 확인합니다
        if app['process'] != 0:         # 작업중일 경우
            # log.info(f'login.json 파일 갱신작업 중입니다.AutoHotkey')
            # log.info(f'process 넘버: {app["process"]}')
            # log.info(f'process return code: {app["process"].returncode}')
            # 프로세스가 종료되면 returncode가 None이 아닌 반환값을 보냅니다. 여기선 0
            # iex) https://docs.python.org/ko/3/library/asyncio-subprocess.html#asyncio.subprocess.Process.communicate
            if app['process'].returncode == 0:
                # await app['process'].wait()
                log.info(f'login.json 파일 갱신작업 완료.')
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
                            'http://localhost/youtube/api/report_loginjson_date', data=readable_time):
                        log.info(f'report loginjson date:{readable_time}')

                app['process'] = 0

                await send_ws(app['websockets'], 'needRefresh')
                await send_ws(app['websockets'], 'finished')

                '''
                try:
                    log.info(f'trying websocket send:finished ...')
                    log.info(f'...to {app["websockets"].keys()}')
                    for ws_pair in app['websockets'].items():
                        # log.info(f'{ws} send_str...')
                        log.info(f'{ws_pair[0]} send_str...')
                        bClosed = ws_pair[1].closed
                        log.info(f'{ws_pair[0]} closed is {bClosed}')
                        if(bClosed != True):
                            await ws_pair[1].send_str('finished')
                except Exception as e:
                    log.info(f'exception in websocket send:finished: {e}')
                    '''

                # for ws in app['websockets']:
                #     # log.info(f'{ws} send_str...')
                #     log.info(f'{app["websockets"][ws]} send_str...')
                #     for w in app['websockets'][ws]:
                #         log.info(f'{w} send_str...')
                #         await w.send_str('finished')

        # log.info(f'[monitor]: {app["process"]}')
        await asyncio.sleep(1)


async def monitor(app):
    app['db'] = await create_engine(host='192.168.1.203',
                                    user='postgres',
                                    password='sksmsqnwk11',
                                    database='youtube_db')
    app['Studio'] = Studio(app['login_file'])
    log.info('came into monitor function')
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
            async with sess.post('http://localhost/youtube/api/loginjson_date', data=readable_time):
                pass

    except Exception as e:
        log.info(f'exception in loginjson_date post::{e}')

    # 업로드 성공여부 리턴값입니다
    ret = 1
    #url_gimme = 'http://192.168.1.102/uploader/api/gimme_que'
    #url_result = 'http://192.168.1.102/uploader/api/upload_complete'

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
                        f'{temp_file} copying check by db. r[4] is {r[4]}')
                    # if int(r[4]) != 2:
                    if r[4] != 2:
                        log.info(
                            f'{temp_file} is currently copying. continue next')
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
                path = f'{FIXED_PATH}{filename}'
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
                    await send_ws(app['websockets'], 'needRefresh')
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

                    await yt.login()
                    log.info(f'yt.login() succeed')
                    log.info(f'yt.uploadVideo starting...')
                    log.info(f'path:{path}, title:{title}')
                    ret = await yt.uploadVideo(
                        path,
                        progress=progress,
                        description='',
                        privacy=PRIVACY,
                        title=title)
                    # ret = json.loads(ret)
                    log.info(f'monitor::yt.uploadVideo::upload completed.\n ret was {ret}')
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

            # 업로드 성공/실패 후  클라이언트들에 리프레시 신호를 보냅니다
            await send_ws(app['websockets'], 'needRefresh')
            app['uploading'] = 0

        # await asyncio.sleep(5)
        # await asyncio.sleep(20)

'''
def upload(app, res):

    ret = 0
    title = res["title"]
    filename = res["file"]
    # initialize_upload(youtube, args)

    # youtube = request.app['youtube']

    args = app['args']
    youtube = get_authenticated_service(args)

    args.file = f'{FIXED_PATH}{filename}'
    args.title = title

    # print(f'file:{args.file}')
    # print(f'title:{args.title}')

    # try:
    #     initialize_upload(youtube, args)
    # except:
    #     result = 'err'

    # 성공하면 0을 실패하면 1을 반납하게 해 봅니다
    ret = initialize_upload(youtube, args)

    return ret
    '''


async def create_bg_tasks(app):
    asyncio.create_task(monitor(app))
    asyncio.create_task(monitor_subprocess(app))


# ahk를 실행시키는 명령하는 함수입니다
# **작업완료는 monitor_subprocess 함수에서 점검해서 처리합니다
async def loginjson(request):

    result = 'waiting'

    # 작업중이 아닐 때만 실행 명령을 내립니다
    if request.app['process'] == 0:
        process = await asyncio.create_subprocess_exec(
            '/mnt/c/Program Files/AutoHotkey/v1.1.37.01/AutoHotkeyU64.exe',
            'c:\\Users\\utylee\\bin\\cookie_refresher_force.ahk')
        # await process.wait()

        log.info(f'login.json 파일 갱신작업 중입니다. {process}')
        request.app['process'] = process

        # websocket들에 작업중 메세지를 보냅니다
        await send_ws(request.app['websockets'], 'processing')

        '''
        ws_dict = request.app['websockets']
        try:
            log.info(f'trying websocket send:processing...')
            log.info(f'...to {ws_dict.keys()}')
            for ws_pair in ws_dict.items():
                # log.info(f'{ws} send_str...')
                log.info(f'{ws_pair[0]} send_str...')
                bClosed = ws_pair[1].closed
                log.info(f'{ws_pair[0]} closed is {bClosed}')
                if(bClosed != True):
                    await ws_pair[1].send_str('processing')
        except Exception as e:
            log.info(f'exception in websocket sends:processing: {e}')
        '''

    else:
        log.info('already working... exec passed')

    return web.Response(text=result)


async def addque(request):
    res = await request.json()
    res = json.loads(res)
    log.info('came into handle addque')
    log.info(res)
    # title1 = res["title"]
    filename = res["file"]
    title = res["title"]
    playlist = res["playlist"]
    # filename = f'{FIXED_PATH}{filename}'

    # request.app['upload_que'].update({filename: title})
    request.app['upload_que'].update({filename: [title, playlist]})

    # args = request.app['args']
    # youtube = get_authenticated_service(args)

    # args.file = f'{FIXED_PATH}{filename}'
    # args.title = title1

    # print(f'file:{args.file}')
    # print(f'title:{args.title}')

    result = 'ok'
    # try:
    #     initialize_upload(youtube, args)
    # except:
    #     result = 'err'

    # request.app['uploading'] = 1
    # initialize_upload(youtube, args)
    # request.app['uploading'] = 0

    return web.Response(text=result)


async def handle(request):
    return web.Response(text='youtube file uploader')


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
                        http.client.IncompleteRead, http.client.ImproperConnectionState,
                        http.client.CannotSendRequest, http.client.CannotSendHeader,
                        http.client.ResponseNotReady, http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


# def get_authenticated_service(args):
#     flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
#                                    scope=YOUTUBE_UPLOAD_SCOPE,
#                                    message=MISSING_CLIENT_SECRETS_MESSAGE)

#     storage = Storage("%s-oauth2.json" % sys.argv[0])
#     credentials = storage.get()

#     if credentials is None or credentials.invalid:
#         credentials = run_flow(flow, storage, args)

#     return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
#                  http=credentials.authorize(httplib2.Http()))


#def initialize_upload(youtube, options):
#    tags = None
#    if options.keywords:
#        tags = options.keywords.split(",")

#    body = dict(
#        snippet=dict(
#            title=options.title,
#            description=options.description,
#            tags=tags,
#            categoryId=options.category
#        ),
#        status=dict(
#            privacyStatus=options.privacyStatus
#        )
#    )

#    # Call the API's videos.insert method to create and upload the video.
#    insert_request = youtube.videos().insert(
#        part=",".join(list(body.keys())),
#        body=body,
#        # The chunksize parameter specifies the size of each chunk of data, in
#        # bytes, that will be uploaded at a time. Set a higher value for
#        # reliable connections as fewer chunks lead to faster uploads. Set a lower
#        # value for better recovery on less reliable connections.
#        #
#        # Setting "chunksize" equal to -1 in the code below means that the entire
#        # file will be uploaded in a single HTTP request. (If the upload fails,
#        # it will still be retried where it left off.) This is usually a best
#        # practice, but if you're using Python older than 2.6 or if you're
#        # running on App Engine, you should set the chunksize to something like
#        # 1024 * 1024 (1 megabyte).
#        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
#    )

#    # resumable_upload(insert_request)
#    return resumable_upload(insert_request)

## This method implements an exponential backoff strategy to resume a
## failed upload.


#def resumable_upload(insert_request):
#    # result라는 값을 리턴하도록 합니다. exception 이 발생하면 1을 반납합니다
#    result = 0
#    response = None
#    error = None
#    retry = 0
#    while response is None:
#        try:
#            print("Uploading file...")
#            log.info("Uploading file...")
#            status, response = insert_request.next_chunk()
#            if response is not None:
#                if 'id' in response:
#                    print(("Video id '%s' was successfully uploaded." %
#                          response['id']))
#                else:
#                    exit("The upload failed with an unexpected response: %s" % response)
#        except HttpError as e:
#            if e.resp.status in RETRIABLE_STATUS_CODES:
#                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
#                                                                     e.content)
#            else:
#                raise
#        except RETRIABLE_EXCEPTIONS as e:
#            error = "A retriable error occurred: %s" % e

#        if error is not None:
#            result = 1
#            print(error)
#            retry += 1
#            if retry > MAX_RETRIES:
#                exit("No longer attempting to retry.")

#            max_sleep = 2 ** retry
#            sleep_seconds = random.random() * max_sleep
#            print(("Sleeping %f seconds and then retrying..." % sleep_seconds))
#            time.sleep(sleep_seconds)

#        return result


if __name__ == '__main__':
    # # argparser.add_argument("--file", required=True, help="Video file to upload")
    # argparser.add_argument("--file",  help="Video file to upload")
    # argparser.add_argument("--title", help="Video title", default="Test Title")
    # argparser.add_argument("--description", help="Video description",
    #                        default="Test Description")
    # argparser.add_argument("--category", default="22",
    #                        help="Numeric video category. " +
    #                        "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    # argparser.add_argument("--keywords", help="Video keywords, comma separated",
    #                        default="")
    # argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
    #                        default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
    # args = argparser.parse_args()

    # if not os.path.exists(args.file):
    #     exit("Please specify a valid file using the --file= parameter.")
    '''
    '''
    # # youtube = get_authenticated_service(args)

    # # 주기적으로 큐를 확인하면서 등록된 파일을 순차적으로 업로드 합니다
    # try:
    #     print(args.title)
    #     log.info('-------------------------------------------')
    #     log.info('started')
    #     # initialize_upload(youtube, args)
    # except HttpError as e:
    #     print(("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)))

    # 로그설정입니다
    log_path = f'/home/utylee/youtube_uploading.log'
    handler = logging.handlers.RotatingFileHandler(filename=log_path,
                                                   maxBytes=10*1024*1024,
                                                   backupCount=10)

    # handler = logging.FileHandler('/home/utylee/youtube_uploading.log')
    handler.setFormatter(logging.Formatter('[%(asctime)s-%(message)s]'))
    log = logging.getLogger('logger')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)


    app = web.Application()

    # app['args'] = args
    app['uploading'] = 0
    # app['youtube'] = youtube
    app['login_file'] = ''
    app['login_file_date'] = ''
    app['upload_que'] = od()
    app['process'] = 0
    app['websockets'] = defaultdict(int)

    # if os.path.exists('./login.json'):
    # SESSION_TOKEN 을 고쳐도 에러가 나서 보니 SIDCC도 변경되었더군요
    if os.path.exists(JSON_PATH):
        app['login_file'] = json.loads(open(JSON_PATH, 'r').read())
        print(app['login_file'])
        log.info('login file loaded')
        log.info(app['login_file'])
    else:
        exit('no json file')
        log.info('no json file')

    app.add_routes([
        web.post('/addque', addque),
        web.get('/loginjson', loginjson),
        web.get('/cook', cook),
        web.get('/ws', ws),
        web.get('/ws_refresh', ws_refresh),
        web.get('/', handle)
    ])

    app.on_startup.append(create_bg_tasks)

    # loop = asyncio.get_event_loop()
    web.run_app(app, port=9993)
