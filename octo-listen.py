import asyncio
import subprocess
import RPi.GPIO as GPIO

@asyncio.coroutine
def handle_echo(reader, writer):
    data = yield from reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("Received %r from %r" % (message, addr))

    # message가 off 이 들어오면 gpio 끄는 명령을 실행합니다
    if(message == "off"):
        rmessage = "accepted:off"
        try:
            # gpio off
            GPIO.setup(17, GPIO.OUT)
            GPIO.output(17, False)

        except:
            print('gpio off failed!')
            pass
    # message가 on 이 들어오면 gpio 켜는  명령을 실행합니다
    elif (message == "on"):
        rmessage = "accepted:on"
        try:
            # gpio on
            GPIO.setup(17, GPIO.OUT)
            GPIO.output(17, True)
        except:
            print('gpio on failed!')
            pass

    else:
        rmessage = "no idea"

    print("Send: %r" % rmessage)
    data = rmessage.encode()
    writer.write(data)
    yield from writer.drain()

    print("Close the client socket")
    writer.close()



GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, '0.0.0.0', 5000, loop=loop)
server = loop.run_until_complete(coro)
