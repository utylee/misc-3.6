import asyncio
from instapush import App
from datetime import datetime
from pushbullet import PushBullet

# pi3 (210)로 모니터 turn on 신호를 보냅니다
@asyncio.coroutine
def tcp_echo_client(message, loop):
    reader, writer = yield from asyncio.open_connection('192.168.0.210', 9083,
                                                        loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode())

    data = yield from reader.read(100)
    print('Received: %r' % data.decode())

    #print('Close the socket')
    yield from writer.drain()
    writer.close()


#102 PC로 메세지를 보냅니다
async def push_pc_started(message, loop):
    fut = asyncio.open_connection('192.168.0.102', 8899,loop=loop)
    try:
        reader, writer = await asyncio.wait_for(fut, timeout=3)
    except asyncio.TimeoutError:
        print('Timeout, skipping!')
        return

    print('Send(to 102): {}'.format(message))
    writer.write(message.encode())
    await writer.drain()
    #yield from writer.drain()
    writer.close()


# instapush에 push명령을 내립니다
async def instapushing():
    try:
        cur = '9' + datetime.now().strftime('%H%M')
        app.notify(event_name = 'alarm', trackers={'msg': cur})
        #print('pushed')
    except:
        pass

# pushbullet에 push명령을 내립니다
async def pushbulleting():
    try:
        cur = '9' + datetime.now().strftime('%H%M')
        push = pb.push_note(cur, "^^")

    except:
        pass


app = App(appid = '595713a2a4c48ae3b8b70aa0', secret = '78fbc7d58e750b37773b3dbd13c967c5')
pb = PushBullet("o.XnzDJuPVFyj0PuCpu5Ibxnzxy0rVqunh")
#message = 'Hello World!'
loop = asyncio.get_event_loop()

# pi3로 moving 메세지를 보냅니다
# octorpint 및 klipper 펌웨어 사용으로 임시로 제거해놓습니다. firefox-esr과 octoprint의 chromium이 충돌하는지
#문제가 생겨서리
#message = 'moving'
#loop.run_until_complete(tcp_echo_client(message, loop))

# pushbullet에 이벤트를 보냅니다
#loop.run_until_complete(instapushing())
loop.run_until_complete(pushbulleting())

# 102 데스크탑으로 coming 메세지를 보냅니다
loop.run_until_complete(push_pc_started('coming', loop))
loop.close()
