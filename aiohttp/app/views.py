from datetime import datetime

from aiohttp.hdrs import METH_POST
from aiohttp.web import json_response, FileResponse, StreamResponse, Response
from aiohttp.web_exceptions import HTTPFound
from aiohttp_jinja2 import template

import os

from aiofiles import open as open_async
from aiopg.sa import create_engine
import sqlalchemy as sa

#@template('index.jinja')
@template('index.html')
async def index(request):
    """
    This is the view handler for the "/" url.

    :param request: the request object see http://aiohttp.readthedocs.io/en/stable/web_reference.html#request
    :return: context for the template.
    """
    # Note: we return a dict not a response because of the @template decorator
    return {
        'title': request.app['name'],
        'intro': "Success! you've setup a basic aiohttp app.",
    }


async def src(request):
    num = request.match_info.get('num', '0007')
    print('came into /src')
    print(f'{request.headers}')   
    chunk_size = 40960
    REMOTE="/home/odroid/media/3001/00-MediaWorld-3001/55-etc/00-bible/"
    location = REMOTE + '0000_11.mp3'
    rng = request.http_range
    size = os.path.getsize(location)
    stop = rng.stop
    if stop is None:
        stop = size
    to_send = min(stop - rng.start, size)
    print(f'\trange:{rng}\n\tfilesize:{size}')

    if to_send < chunk_size:
        # 한방 response
        print('논-스트리밍 모드')
        headers = {'Content-Type': 'audio/mp3', 'Accept-Ranges': 'Accept-Ranges: bytes'}
        #headers['Content-Range'] = f'bytes {rng.start}-{stop - rng.start - 1}/{size}'
        headers['Content-Range'] = f'bytes {rng.start}-{stop - 1}/{size}'
        #headers['Content-Range'] = f'bytes {rng.start}-{rng.start + to_send - 1}/{size}'
        async with open_async(location, 'rb') as f:
            await f.seek(rng.start)
            send = to_send
            data = await f.read(send)
        #print(data)
        #print(headers)
        return Response(body=data, status=200, headers=headers)
    else:
        # 스트리밍 모드
        print('스트리밍 모드')
        headers = {'Content-Type': 'audio/mp3', 'Accept-Ranges': 'Accept-Ranges: bytes'}
        #headers['Content-Range'] = f'bytes {rng.start}-{stop - rng.start - 1}/{size}'
        headers['Content-Range'] = f'bytes {rng.start}-{stop - 1}/{size}'
        #headers['Content-Range'] = f'bytes {rng.start}-{rng.start + to_send - 1}/{size}'
        resp = StreamResponse(headers=headers, status=206)
        await resp.prepare(request)
        print(resp)
        async with open_async(location, 'rb') as f:
            print(f'seek to {rng.start}')
            await f.seek(rng.start)
            #data = f.read(rng.stop-rng.start)
            to_send = stop - rng.start
            while to_send:
                send = min(chunk_size, to_send)
                data = await f.read(send)
            
                resp.write(data)
                await resp.drain()

                to_send -= send
            print('eof')

        return resp

@template('video.html')
async def video(request):
    return {
            'title' : 'video streaming',
    }
@template('audio.html')
async def audio(request):
    return {
            'title' : 'audio streaming',
    }


async def process_form(request):
    new_message, missing_fields = {}, []
    fields = ['username', 'message']
    data = await request.post()
    for f in fields:
        new_message[f] = data.get(f)
        if not new_message[f]:
            missing_fields.append(f)

    if missing_fields:
        return 'Invalid form submission, missing fields: {}'.format(', '.join(missing_fields))

    # hack: if no database is available we use a plain old file to store messages.
    # Don't do this kind of thing in production!
    # This very simple storage uses "|" to split fields so we need to replace "|" in the username
    new_message['username'] = new_message['username'].replace('|', '')
    with request.app['settings'].MESSAGE_FILE.open('a') as f:
        now = datetime.now().isoformat()
        f.write('{username}|{timestamp}|{message}\n'.format(timestamp=now, **new_message))

    raise HTTPFound(request.app.router['messages'].url())


@template('messages.jinja')
async def messages(request):
    if request.method == METH_POST:
        # the 302 redirect is processed as an exception, so if this coroutine returns there's a form error
        form_errors = await process_form(request)
    else:
        form_errors = None
    # we're not using sessions so there's no way to pre-populate the username
    username = ''

    return {
        'title': 'Message board',
        'form_errors': form_errors,
        'username': username,
    }


async def message_data(request):
    """
    As an example of aiohttp providing a non-html response, we load the actual messages for the "messages" view above
    via ajax using this endpoint to get data. see static/message_display.js for details of rendering.
    """
    messages = []
    if request.app['settings'].MESSAGE_FILE.exists():
        # read the message file, process it and populate the "messages" list
        with request.app['settings'].MESSAGE_FILE.open() as msg_file:
            for line in msg_file:
                if not line:
                    # ignore blank lines eg. end of file
                    continue
                # split the line into it constituent parts, see process_form above
                username, ts, message = line.split('|', 2)
                # parse the datetime string and render it in a more readable format.
                ts = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f'))
                messages.append({'username': username, 'timestamp':  ts, 'message': message})
        messages.reverse()
    return json_response(messages)
