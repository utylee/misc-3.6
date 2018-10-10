from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_jinja2 import APP_KEY as JINJA2_APP_KEY
from sqlalchemy.engine.url import URL

from aiopg.sa import create_engine

from .settings import Settings
from .views import index, message_data, messages


THIS_DIR = Path(__file__).parent
BASE_DIR = THIS_DIR.parent


@jinja2.contextfilter
def reverse_url(context, name, **parts):
    """
    jinja2 filter for generating urls,
    see http://aiohttp.readthedocs.io/en/stable/web.html#reverse-url-constructing-using-named-resources

    Usage:

      {{ 'the-view-name'|url }} might become "/path/to/view"

    or with parts and a query

      {{ 'item-details'|url(id=123, query={'active': 'true'}) }} might become "/items/1?active=true

    see app/templates.index.jinja for usage.

    :param context: see http://jinja.pocoo.org/docs/dev/api/#jinja2.contextfilter
    :param name: the name of the route
    :param parts: url parts to be passed to route.url(), if parts includes "query" it's removed and passed seperately
    :return: url as generated by app.route[<name>].url(parts=parts, query=query)
    """
    app = context['app']

    kwargs = {}
    if 'query' in parts:
        kwargs['query'] = parts.pop('query')
    if parts:
        kwargs['parts'] = parts
    return app.router[name].url(**kwargs)


@jinja2.contextfilter
def static_url(context, static_file_path):
    """
    jinja2 filter for generating urls for static files. NOTE: heed the warning in create_app about "static_root_url"
    as this filter uses app['static_root_url'].

    Usage:
      {{ 'styles.css'|static }} might become "http://mycdn.example.com/styles.css"

    see app/templates.index.jinja for usage.

    :param context: see http://jinja.pocoo.org/docs/dev/api/#jinja2.contextfilter
    :param static_file_path: path to static file under static route
    :return: roughly just "<static_root_url>/<static_file_path>"
    """
    app = context['app']
    try:
        static_url = app['static_root_url']
    except KeyError:
        raise RuntimeError('app does not define a static root url "static_root_url"')
    return '{}/{}'.format(static_url.rstrip('/'), static_file_path.lstrip('/'))


def pg_dsn(settings: Settings) -> str:
    """
    :param settings: settings including connection settings
    :return: DSN url suitable for sqlalchemy and aiopg.
    """
    return str(URL(
        database=settings.DB_NAME,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        username=settings.DB_USER,
        drivername='postgres',
    ))


async def startup(app: web.Application):
    app['pg_engine'] = await create_engine(pg_dsn(app['settings']), loop=app.loop)


async def cleanup(app: web.Application):
    app['pg_engine'].close()
    await app['pg_engine'].wait_closed()


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_route('*', '/messages', messages, name='messages')
    app.router.add_get('/messages/data', message_data, name='message-data')


def create_app(loop):
    app = web.Application()
    settings = Settings()
    app.update(
        name='bible',
        settings=settings
    )

    jinja2_loader = jinja2.FileSystemLoader(str(THIS_DIR / 'templates'))
    aiohttp_jinja2.setup(app, loader=jinja2_loader, app_key=JINJA2_APP_KEY)
    app[JINJA2_APP_KEY].filters.update(
        url=reverse_url,
        static=static_url,
    )

    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)

    setup_routes(app)
    return app
