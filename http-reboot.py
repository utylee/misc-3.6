from aiohttp import web
import asyncio
import os
import time
import socket

def getmyip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("192.168.0.1", 80))
        ip = s.getsockname()[0]
        # 아이피 마지막을 얻기위한 방법입니다
        #what = ip.split('.')[-1]
        return s.getsockname()[0]

async def handle(request):
    return web.Response(text='command http site')

async def reboot_5():
    # 5초 후 재붓합니다
    await asyncio.sleep(5)
    #time.sleep(10)
    os.system('echo sksmsqnwk11 | sudo -S reboot')
    return

async def reboot(request):
    # request 에 loop을 넣어줬었군요. 따로 asyncio 를 import 할 필요가 없는 이유였군요
    # 또한await는 코루틴에 걸어줘야하는 것이지 asyncio 메써드에 걸어주면 hang이 걸리고 이상동작합니다
    request.loop.create_task(reboot_5())
    #request.loop.run_in_executor(None, reboot_5)
    #asyncio.ensure_future(reboot_5())
    return web.Response(text='reboot after 5 seconds')

'''
app = web.Application()

app.add_routes([web.get('/', handle),
                web.get('/reboot', reboot)
                ])
                '''

if __name__ == '__main__':
    app = web.Application()

    app.add_routes([web.get('/', handle),
                    web.get('/reboot', reboot)
                    ])

    my_port = '9' + getmyip().split('.')[-1]
    web.run_app(app, port=my_port)

