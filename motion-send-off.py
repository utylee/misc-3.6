import asyncio
from urllib.request import urlopen
import glob, os.path

# pi3로 stop(lcd off) 메세지를 보냅니다
@asyncio.coroutine
def tcp_echo_client(message, loop):
    reader, writer = yield from asyncio.open_connection('192.168.0.210', 9083,
                                                        loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode())

    data = yield from reader.read(100)
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()

# flask 서버에 recent images 를 업데이트하라는 명령을 보냅니다
async def update_img():
    l = sorted(glob.iglob('/home/pi/media/3001/21-motion2/2*jpg'), key=os.path.getctime)
    print(l[-4:])
    #urlopen('http://localhost:5000/message/1')
    #pi3 flask의 주소를 호출하여 이미지4개를 재배열  업데이트 명령을 전달합니다
    with urlopen('http://192.168.0.210:5001/message/1') as f:
        pass

#102 PC로 알람과 show를 위한 메세지를 보냅니다
async def push_pc_ended(message, loop):
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

#message = 'Hello World!'
loop = asyncio.get_event_loop()
message = 'stop'
loop.run_until_complete(update_img())
loop.run_until_complete(tcp_echo_client(message, loop))
loop.run_until_complete(push_pc_ended('ended', loop))
loop.close()
