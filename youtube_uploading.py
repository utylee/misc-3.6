import http.client
from aiopg.sa import create_engine
import httplib2
import os
import random
import sys
import time

from ytstudio import Studio

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import asyncio
import aiohttp
from aiohttp import web
import db_youtube as db
import json
import logging
from collections import OrderedDict as od
import copy


FIXED_PATH = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture/'


def progress(yuklenen, toplam):
    # print(f"{round(round(yuklenen / toplam, 2) * 100)}% upload", end="\r")
    print(f"{round(yuklenen / toplam) * 100}% upload", end="\r")


async def asyncupload(app, path, title):
    yt = app['Studio']
    ret = await yt.uploadVideo(
        path,
        title=title,
        progress=progress,
        privacy='PUBLIC')
    if ret is not None:
        ret = 0


async def monitor(app):
    app['db'] = await create_engine(host='192.168.1.203',
                                        user='postgres', 
                                        password='sksmsqnwk11',
                                        database='youtube_db')
    app['Studio'] = Studio(app['login_file'])
    log.info('came into monitor function')
    yt = app['Studio']
    await yt.login()

    engine = app['db']
    # 20초마다 api_backend 서버에 현재 대기중인 큐를 요구합니다
    # 유튜브 업로드 중이었다면 끝낸 후일 것이므로

    # 업로드 성공여부 리턴값입니다
    ret = 1
    url_gimme = 'http://192.168.1.102/uploader/api/gimme_que'
    url_result = 'http://192.168.1.102/uploader/api/upload_complete'

    # 업로드 서버에 gimme que 요청에서 자체 que 탐색으로 변경합니다
    while True:
        que = app['upload_que']

        await asyncio.sleep(5)

        if app['uploading'] == 0 and len(que) > 0:
            cur_file = ''
            title = ''
            # log.info('sending gimme request')

            que_c = copy.deepcopy(que)

            tup_c = que_c.popitem(last=False)
            temp_file = tup_c[0]
            temp_title = tup_c[1]

            log.info(f'tup_c: {tup_c}, {temp_file}, {temp_title}')

            continue_ = 0
            async with engine.acquire() as conn:
                async for r in conn.execute(db.tbl_youtube_files.select()
                        .where(db.tbl_youtube_files.c.filename==temp_file)):
                    #copying이  2 즉 완료가 아니면, 즉 아직 복사중이면 패스합니다
                    log.info(f'{temp_file} copying check by db. r[4] is {r[4]}')
                    if int(r[4]) != 2:
                        log.info(f'{temp_file} is currently copying. continue next')
                        continue_ = 1
            if (continue_ == 1):
                continue

            tup = que.popitem(last=False)
            cur_file = tup[0]
            title = tup[1]
            log.info(f'tup: {tup}, {cur_file}, {title}')

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
                                .where(db.tbl_youtube_files.c.filename==cur_file)
                                .values(uploading=2)):
                            log.info(f'db copying column to 2')
                except:
                    log.info(f'exception:db copying column to 2')


                # asyncio.create_task(asyncupload(app, path, title))
                # await yt.login()
                # privacy='PUBLIC')
                try:
                    ret = await yt.uploadVideo(
                        path,
                        progress=progress,
                        description='',
                        privacy='PUBLIC',
                        title=title)
                    # log.info(f'upload completed. ret was {ret}')
                    log.info(f'upload completed. ')
                except:
                    log.info(f'yt.uploadVideo upload excepted')
                # ret = json.loads(ret)

                # SESSION_TOKEN 에 문제가 있을 때의 응답입니다
                '''
                {'error': {'code': 400, 'message': 'Request contains an invalid argument.', 'errors': [{'message': 'Request contains an invalid argument.', 'domain': 'global', 'reason': 'badRequest'}], 'status': 'INVALID_ARGUMENT'}}]
                '''

                # error 발생했을 경우
                if 'error' in ret.keys():
                    log.info(f'upload error. ret is {ret}')
                    ret = 1
                # 성공했을 경우
                else:
                    ret = 0

                # if ret is not None:
                #     ret = 0

            # except:
            #    log.info('exeption in monitor')
            #     pass

            # 업로드 성공했으면
            if ret == 0:
                # if ret is not None:
                payload = {"file": cur_file, "result": 0}
                async with aiohttp.ClientSession() as sess:
                    async with sess.post(url_result, json=payload) as resp:
                        log.info(f'upload ok send and response')
                ret = 1

            app['uploading'] = 0

        # await asyncio.sleep(5)
        # await asyncio.sleep(20)


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


async def create_bg_tasks(app):
    asyncio.create_task(monitor(app))


async def addque(request):
    log.info(f'came into addque')
    res = await request.json()
    res = json.loads(res)
    log.info('came into handle addque')
    log.info(res)
    # title1 = res["title"]
    filename = res["file"]
    title = res["title"]
    # filename = f'{FIXED_PATH}{filename}'

    request.app['upload_que'].update({filename: title})

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


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(list(body.keys())),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    # resumable_upload(insert_request)
    return resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.


def resumable_upload(insert_request):
    # result라는 값을 리턴하도록 합니다. exception 이 발생하면 1을 반납합니다
    result = 0
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            log.info("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print(("Video id '%s' was successfully uploaded." %
                          response['id']))
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            result = 1
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print(("Sleeping %f seconds and then retrying..." % sleep_seconds))
            time.sleep(sleep_seconds)

        return result


if __name__ == '__main__':
    # argparser.add_argument("--file", required=True, help="Video file to upload")
    argparser.add_argument("--file",  help="Video file to upload")
    argparser.add_argument("--title", help="Video title", default="Test Title")
    argparser.add_argument("--description", help="Video description",
                           default="Test Description")
    argparser.add_argument("--category", default="22",
                           help="Numeric video category. " +
                           "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", help="Video keywords, comma separated",
                           default="")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
                           default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
    args = argparser.parse_args()

    # if not os.path.exists(args.file):
    #     exit("Please specify a valid file using the --file= parameter.")
    '''
    '''

    # 로그설정입니다
    log = logging.getLogger('logger')
    handler = logging.FileHandler('/home/utylee/youtube_uploading.log')
    handler.setFormatter(logging.Formatter('[%(asctime)s-%(message)s]'))
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    # youtube = get_authenticated_service(args)

    # 주기적으로 큐를 확인하면서 등록된 파일을 순차적으로 업로드 합니다
    try:
        print(args.title)
        log.info('-------------------------------------------')
        log.info('started')
        # initialize_upload(youtube, args)
    except HttpError as e:
        print(("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)))

    app = web.Application()

    app['args'] = args
    app['uploading'] = 0
    # app['youtube'] = youtube
    app['login_file'] = ''
    app['upload_que'] = od()
    if os.path.exists('./login.json'):
        app['login_file'] = json.loads(open('./login.json', 'r').read())
        print(app['login_file'])
    else:
        exit('no json file')

    app.add_routes([
        web.post('/addque', addque),
        web.get('/', handle)
    ])

    app.on_startup.append(create_bg_tasks)

    # loop = asyncio.get_event_loop()
    web.run_app(app, port=9993)
