import asyncio
import subprocess

mute = 0

async def handle(reader, writer):
    order = await reader.read(100)
    print(order.decode())
    if order.decode() == 'mute':
        global mute
        if mute == 0:
            print('mute')
            subprocess.call("osascript -e 'set volume 0'", shell=True)
            mute = 1
        else:
            print('no mute')
            subprocess.call("osascript -e 'set volume 2'", shell=True)
            mute = 0



loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle, '0.0.0.0', 7788, loop=loop)
server = loop.run_until_complete(coro)

print("starting control server - 0.0.0.0:7788")
loop.run_forever()
loop.close()
