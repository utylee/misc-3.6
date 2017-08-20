from aiohttp import web

async def hello(request):
    return web.Response(text='hello world')


app = web.Application()
app.router.add_get('/', hello)

web.run_app(app)
