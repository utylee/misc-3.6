import os
from mimetypes import guess_type
from aiofiles import open as open_async
import re
from sanic import Sanic
from sanic.response import text, html, file, file_stream, raw, redirect, HTTPResponse, StreamingHTTPResponse
from sanic import request
from jinja2 import Environment, PackageLoader

REMOTE="/home/odroid/media/3001/00-MediaWorld-3001/55-etc/00-bible/"
BUF = 4096

app = Sanic()

env = Environment(loader=PackageLoader(__name__, 'templates'))

@app.route('/', methods=['GET', 'HEAD'])
def index(request):
    #print(request.headers.get('connection'))
    audio = app.url_for('audio')
    video = app.url_for('video')
    return html(env.get_template('index.html').render(audio = audio, video=video))
    #return html(env.get_template('index.html').render(video=video))
    #return text('하하')


@app.route('/audio')
async def audio(request):
    play = app.url_for('play')
    #play = app.url_for('/sample' + '/2577_예언적 시각으로 살펴 본 성경_구원이 왜 필요한가.mp3')
    return html(env.get_template('audio.html').render(play = play))

@app.route('/video')
async def video(request):
    #play = app.url_for('play')
    sample = app.url_for('play_sample')
    #play = app.url_for('/sample' + '/2577_예언적 시각으로 살펴 본 성경_구원이 왜 필요한가.mp3')
    #return html(env.get_template('video.html').render(play = play))
    return html(env.get_template('video.html').render(sample = sample))

@app.route('/play_sample')
async def play_sample(request):
    #return await file_stream('sample/22.mp4')
    #return redirect('sample/11.mp4')
    return redirect('sample/22.mp4')


#@app.route('/play')
@app.get('/play')
async def play(request):
    '''
    location = REMOTE + '11.mp4'
    print(location)
    file_length = os.path.getsize(location)
    chunk_size = 4096
    mime_type = guess_type(location)[0]

    range_start = range_end = None

    try:
        range_ = request.headers['Range'].split('=')[1]
        range_split = range_.split('-')
        range_start = int(range_split[0])
        range_end = int(range_split[1])
    except ValueError:
        pass
    if range_start:
        if not range_end:
            range_end = file_length
        read_length = range_end - range_start
        status_code = 206
    else:
        range_start = 0
        read_length = file_length
        status_code = 200

    class Range():
        start = 0
        end = 0
        size = 0
        total = 0
        def __init__(self, start, end, size, total):
            self.start = start
            self.end = end
            self.size = size
            self.total = total

    _range = Range(range_start, range_end, file_length, file_length) 
    #headers = {'Content-Type': 'video/mp4', 'Accept-Ranges': 'Accept-Ranges: bytes'}
    headers = {}

    _file = await open_async(location, mode='rb')
    '''

    print(f'/play : request headers:\n\t{request.headers}')
    location = REMOTE + '11.mp4'
    size = os.path.getsize(location)

    range_ = request.headers['range'].split('=')[1]
    range_split = range_.split('-')
    start = int(range_split[0])
    end = None
    length = size
    if range_split[1]: 
        end = int(range_split[1])
        length = end - start + 1
    chunk_size = 4096
    filename = os.path.split(location)[-1]
    mime_type = guess_type(filename)[0]
    print(f'mime_type : {mime_type}')
    headers = {'Content-Type': f'{mime_type}', 'Accept-Ranges': 'Accept-Ranges: bytes'}

    with open(location, 'rb') as f:
        f.seek(start)
        data = f.read(min(chunk_size, length))
        print(data)

    async def aio_generate():
        to_send = size
        async with open_async(location, 'rb') as f:
            f.seek(start)
            data = f.read(min(chunk_size, length))

            await asyncio.sleep(1)
            yield data 
            to_send -= min(chunk_size, to_send)

            while to_send:
                send = min(chunk_size, to_send)
                data = f.read(send)
                yield data
                await asyncio.sleep(1)
                to_send -= send
    if range_:
        if end is None:
            end = chunk_size 
        headers['Content-Range'] = f'bytes {start}-{end}/{size}'


    #return HTTPResponse(body_bytes=aio_generate(), status=206, headers=headers, content_type=mime_type)
    return HTTPResponse(body_bytes=data, status=206, headers=headers, content_type=mime_type)

'''
    async def _streaming_fn(response):
        nonlocal _file, chunk_size
        print('_streaming_fn: before try:')
        try:
            if _range:
                print(f'{_range.start}, {_range.end}, {_range.size}')
                chunk_size = min((_range.size, chunk_size))
                print('await')
                await _file.seek(_range.start)
                to_send = _range.size

                print('while to_send')
                while to_send > 0:
                    content = await _file.read(chunk_size)
                    if len(content) < 1:
                        break
                    to_send -= len(content)
                    #print('before write')
                    response.write(content)
                    print(f'{len(content)}', end='')
                    #print('after write')
            else:
                while True:
                    content = await _file.read(chunk_size)
                    if len(content) < 1:
                        break
        finally:
            await _file.close()
        return  # Returning from this fn closes the stream

        #mime_type = mime_type or guess_type(filename)[0] or 'text/plain'
        if _range:
            headers['Content-Range'] = 'bytes %s-%s/%s' % (
                        _range.start, _range.end, _range.total)

    print('return')
    return StreamingHTTPResponse(streaming_fn=_streaming_fn, status=206, headers=headers, content_type=mime_type)
    '''


    #return redirect('/sample')'/2577_예언적 시각으로 살펴 본 성경_구원이 왜 필요한가.mp3')
    #return redirect('/sample/2577_예언적 시각으로 살펴 본 성경_구원이 왜 필요한가.mp3')
    #return file('/sample/2577_예언적 시각으로 살펴 본 성경_구원이 왜 필요한가.mp3')
    #return redirect('/sample')#, content_type='video/mp4')
    #return await file_stream('/sample/11.mp4')
    #return file('/sample/11.mp4')

@app.route('/stream')
async def stream(request):
    #return await file_stream(REMOTE + '0001_창세기_01장.mp3')
    #return await file_stream(REMOTE + '2577_예언적 시각으로 살펴 본 성경_구원이 왜 필요한가.mp3')
    return await raw(REMOTE + '2577_예언적 시각으로 살펴 본 성경_구원이 왜 필요한가.mp3')


if __name__ == "__main__":
    app.static('/static', './static')
    f = REMOTE + '2577_예언적 시각으로 살펴 본 성경_구원이 왜 필요한가.mp3'
    #f = REMOTE + '11.mp4'
    #f = REMOTE + '22.mp4'
    #app.static('/sample', f)
    app.static('/sample', REMOTE, use_content_range=True, stream_large_files=True)
    #app.static('/sample', f, use_content_range=True, stream_large_files=True)
    app.run(host='0.0.0.0', port='7777')

