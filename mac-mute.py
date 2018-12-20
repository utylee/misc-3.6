import asyncio

async def proc():
    fut = asyncio.open_connection('192.168.0.107', 7788, loop=loop)
    try:
        reader, writer = await asyncio.wait_for(fut, timeout=3)
    except:
        print('timeout...')

    writer.write('mute'.encode())
    await writer.drain()


loop = asyncio.get_event_loop()
loop.run_until_complete(proc())
loop.close()
