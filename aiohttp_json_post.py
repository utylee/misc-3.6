import aiohttp
import asyncio
import json


async def main():
    # print('asdf')
    async with aiohttp.ClientSession() as sess:
        await sess.post('http://192.168.1.202:9202/copyend', json=json.dumps({'test': 'test'}))
        # await sess.post('http://192.168.1.202:9202/copyend', json='{"test": "test"}')
        # await sess.post('http://192.168.1.202:9202/copyend', json="{'test': 'test'}")


asyncio.get_event_loop().run_until_complete(main())
