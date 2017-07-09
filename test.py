import PyQt5
import quamash
import asyncio
import aiomysql
import sys

print("??")
qt5_url = "C:/Users/utylee/.virtualenvs/tyTrader-win/Lib/site-packages/PyQt5/Qt/plugins"
PyQt5.QtCore.QCoreApplication.setLibraryPaths([qt5_url])
app = PyQt5.QtWidgets.QApplication(sys.argv)
loop = quamash.QEventLoop(app)
asyncio.set_event_loop(loop)

async def shell(loop):
    asyncio.ensure_future(f(loop))

async def f(loop):
    print('come to f')
    conn = await aiomysql.connect(host='10.211.55.10', port=3306, user='root', password='sksmsqnwk11', db='kiwoom',\
                                    charset='utf8', loop=loop)
    print(conn)

#loop.run_until_complete(asyncio.gather(shell(loop)))
loop.run_until_complete(f(loop))
print('??')

