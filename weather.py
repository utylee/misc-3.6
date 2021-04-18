import aiohttp
from aiohttp import web
import asyncio

# openweathermap 의 api를 이용합니다
url = 'https://api.openweathermap.org/data/2.5/weather?q=Seongnam,kr&units=metric&appid=0b062e642fd30e78ab8786222d510464'
intv = 60              # 1분마다 가져와서 보관해둡니다

async def handle(request):
    return web.Response(text='weather server<br>',content_type='text/html')

async def weather(request):
    w = app['weather'][0]
    t = app['weather'][1]
    h = app['weather'][2]
    result = f'{w},{t}p,{h}%'
    return web.Response(text=result)

async def crawl_weather():
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            result = await resp.json()
            weather = result['weather'][0]['main']
            temp = round(int(result['main']['temp']))
            humid = result['main']['humidity']
            #print(f'날씨:{weather}\n온도:{temp}\n습도:{humid}')
            return [weather, temp, humid]

async def create_bg_tasks(app):
    #app.on_startup에서 파라미터로 넣어주는 위의 app은 뭔가 래핑된 web.Application()의 리턴값과는 다른 객체 같습니다
    app['timer_proc'] = app.loop.create_task(timer_proc(app))

async def clean_bg_tasks(app):
    app['timer_proc'].cancel()
    await app['timer_proc']

async def timer_proc(app):
    while True:
        try:
            app['weather'] = await crawl_weather()
        except:
            app['weather'] = [0,0,0]

        #print(app['weather'])
        await asyncio.sleep(intv)

if __name__ == "__main__":
    app = web.Application()
    app['weather'] = [0,0,0]
    app.on_startup.append(create_bg_tasks)
    app.on_cleanup.append(clean_bg_tasks)

    app.add_routes([web.get('/', weather)])
                    #web.get('/weather', weather)
                    #])
    web.run_app(app, port=9010)
