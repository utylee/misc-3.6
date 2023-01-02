import pyperclip
import asyncio
import aiofiles
import sys

# 인자로 받은 파일로부터 클립보드에 복사합니다


async def main():
    arg = sys.argv[1]
    clip = ''

    async with aiofiles.open(arg, 'r') as f:
        clip = await f.read()
        # print(clip)

    pyperclip.copy(clip)
    print(f'.copied from file {arg}:\n\n {clip}')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

loop.close()
