import asyncio
import subprocess

@asyncio.coroutine
def handle_echo(reader, writer):
    data = yield from reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("Received %r from %r" % (message, addr))

    # message가 moving 이 들어오면 lcd전원을 켜는 쉘을 실행합니다
    if(message == "moving"):
        rmessage = "accepted:moving"
        try:
            #lcd on 스크립트를 실행합니다
            subprocess.run(['sudo', 'bash', '/home/pi/bin/turnon.sh'])
        except:
            print('shell run failed!')
            pass
    # 움직임이 종료되었을 경우 stop 스트링이 전송돼 옵니다
    elif (message == "stop"):
        rmessage = "accepted:stop"
        try:
            #lcd off 스크립트를 실행합니다
            subprocess.run(['sudo', 'bash', '/home/pi/bin/turnoff.sh'])
        except:
            print('shell run failed!')
            pass

    else:
        rmessage = "no idea"

    print("Send: %r" % rmessage)
    data = rmessage.encode()
    writer.write(data)
    yield from writer.drain()

    print("Close the client socket")
    writer.close()

loop = asyncio.get_event_loop()
#coro = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
coro = asyncio.start_server(handle_echo, '0.0.0.0', 9083, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
