import asyncio




@asyncio.coroutine
def handle(reader, writer):
    data = yield from reader.read(100)

loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle, '127.0.0.1', 8888, loop=loop) 
server = loop.run_until_complete(coro)

loop.run_forever()

loop.close()
