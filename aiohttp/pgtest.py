import asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa

metadata = sa.MetaData()

tbl = sa.Table('tbl', metadata, 
        sa.Column('id', sa.Integer, primary_key = True), 
        sa.Column('val', sa.String(255)))

async def create_table(engine):
    async with engine.acquire() as conn:
        await conn.execute('DROP TABLE IF EXIST tbl')
        await conn.execute('''CREATE TABLE tbl (id serial PRIMARY KEY, val varchar(255))''')

async def go():
    pass

loop = asyncio.get_event_loop()
loop.run_until_complete(go())
