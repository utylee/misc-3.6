import asyncio


async def main():
    print('run TradeDiaryHotkeys.ahk')
    proc = await asyncio.create_subprocess_exec(
        '/mnt/c/Program Files/AutoHotkey/AutoHotkeyU64.exe',
        'c:\\Users\\utylee\\bin\\TradeHotKeys\\TradeDiaryHotkeys.ahk')

asyncio.run(main())
