import pyperclip
import asyncio
import aiofiles
import sys

# 인자로 받은 파일에 클립보드 내용을 저장합니다


async def main():
    arg = sys.argv[1]
    clip = ''

    async with aiofiles.open(arg, 'w') as f:
        s = pyperclip.paste()
        await f.write(s)
        # print(clip)

    print(f'.file {arg} saved from clipboard:\n\n {s}')
    print(clip)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

loop.close()
