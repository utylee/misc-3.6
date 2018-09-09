import asyncio
import re
from sanic import Sanic
from sanic.response import html, file, text
from jinja2 import Environment, PackageLoader
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Text, Table, String as Char, select
from sqlalchemy_aio import ASYNCIO_STRATEGY
import socketio

REMOTE = '/home/pi/media/3001/30-flask/python/selenium/akiba/'

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)

engine = create_engine('sqlite:///akiba.db', strategy = ASYNCIO_STRATEGY) 
metadata = MetaData(engine)#, reflect=True)
#metadata = MetaData(engine, reflect=True)


class Akiba():
    def __init__(self):
        self.query = []

Akiba = Akiba()

akiba = Table('sorted', metadata, 
        Column('id', Integer()), 
        Column('thread_no', Char()), 
        Column('title', Char()), 
        Column('title_ko', Char()), 
        Column('date', Char()), 
        Column('href', Char()), 
        Column('code', Char()), 
        Column('main_image', Char()), 
        Column('etc_images', Char()), 
        Column('text', Text()), 
        Column('torrents', Char()), 
        Column('quality', Char()), 
        Column('size', Char()), 
        Column('guess_quality', Char()), 
        Column('tag', Char()), 
        Column('already_has', Char()), 
        Column('processing', Char()), 
        )


#db = APSWDatabase('akiba.db', timeout='300000')

env = Environment(loader=PackageLoader(__name__, 'templates'))


@sio.on('ready', namespace = '/akiba')
async def ready(sid, msg):
    # html 로드가 완료되면 db fetch
    pass

@app.listener('after_server_start')
async def proc(sanic, loop):
    print('db proc starts.')
    conn = await engine.connect()
    result = await conn.execute(select([akiba.c.main_image, 
                            akiba.c.title_ko, 
                            akiba.c.torrents,
                            akiba.c.text,
                            akiba.c.date]).limit(800).offset(0))
    query = await result.fetchall()
    for i in query:
        print(i)
        Akiba.query.append(i)
    await conn.close()
    print('db proc ends.')

@app.route('/', methods=['GET', 'HEAD'])
async def index(request):
    querys = []
    for i in Akiba.query:

        # 요약 성의 새로운 종류의 쓰레드가 있었습니다.
        try:
            print('i[2] : {}'.format(i[2]))
            torrent = re.sub('[\[\]\']', '', i[2])
            urls = torrent.split(',')
            size = len(urls)
            print('urls: {}\nsize: {}'.format(urls, size))
            

            torrents = []
            for url in urls:
                torrents.append(app.url_for('torrent', url=url.strip()))

            query = {'image': app.url_for('image1', n=i[0]), 
                    'title': i[1], 
                    'torrent': torrents,
                    'text': i[3], 
                    'date': i[4]} 
                    

            querys.append(query)
            print('query : {}\n{}\n{}\n\n'.format(query['image'], query['title'], query['torrent']))
        except:
            print('Nonetype exception!!')
            pass
    return html(env.get_template('index.html').render(querys = querys))


'''
@app.route('torrent/<size>/<url>')
async def torrent(requests, size = None, urls = None):
    print('urls: {}\nsize: {}'.format(urls, size))
    if int(size) < 2:
        url = REMOTE + 'static/torrents/' + url
        print('url: {}\nsize: {}'.format(url, size))
        return await file(url)
    else:
        return text('two or more torrent files.. proc not ready yet')
        '''
@app.route('torrent/<url>')
async def torrent(requests, url = None):
    print('url: {}'.format(url))
    url = REMOTE + 'static/torrents/' + url
    return await file(url)


@app.route('/image1/<n>')
async def image1(request, n):
    '''
    conn = await engine.connect()
    result = await conn.execute(select([akiba.c.main_image]).limit(4))
    query = await result.fetchall()
    for i in query:
        print(i)
    await conn.close()
    '''
    img1 = REMOTE + '/static/images/' + n

    #return await file(img1)
    return await file(img1)



if __name__ == "__main__":
    app.static('/static','./static')
    #app.static('/static')
    #app.add_route(index, '/', methods=['GET', 'HEAD'])
    app.run(host='0.0.0.0', port=5000)
