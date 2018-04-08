import asyncio


# octo (117)로 power off 신호를 보냅니다
@asyncio.coroutine
def tcp_echo_client(message, loop):
    reader, writer = yield from asyncio.open_connection('192.168.0.117', 9083,
                                                        loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode())

    data = yield from reader.read(100)
    print('Received: %r' % data.decode())

    #print('Close the socket')
    yield from writer.drain()
    writer.close()

