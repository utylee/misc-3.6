import pyscreenshot
import asyncio


async def shot():
    im = pyscreenshot.grab()
    im.save('test.png')
    #im.show()
    print('kkk')

loop = asyncio.get_event_loop()
loop.run_until_complete(shot())

