import asyncio
import psutil




async def proc():
    fut = asyncio.open_connection('192.168.0.207', 1117, loop=loop)
    try: 
        reader, writer = await asyncio.wait_for(fut, timeout=3)
    except:
        print('exception maybe Timeouted')

    #wbuf = 'what the fuck'
    wbuf = psutil.cpu_percent()
    print(wbuf)
    writer.write(str(wbuf).encode())
    await writer.drain()

loop = asyncio.get_event_loop()
loop.run_until_complete(proc())

loop.close()
