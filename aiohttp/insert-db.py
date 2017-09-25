import glob, os.path, re
import asyncio
from aiopg.sa import create_engine
from table_jesus import *


#metadata = sa.MetaData()
#jesus = get_jesus()

# 별도의 파일로 분리를 했습니다. 다른 프로젝트에서도 테이블 구조를 이용할 수 있습니다
'''
jesus = sa.Table('jesus', metadata,
        sa.Column('id', sa.Integer, primary_key = True),
        sa.Column('num', sa.String(8)),
        sa.Column('title', sa.String(255)),
        sa.Column('last_pos', sa.String(255), default="00:00:00"),
        sa.Column('completed', sa.Boolean, default=False))
        '''

async def create_tables(conn):
    await conn.execute('DROP TABLE IF EXISTS jesus')
    await conn.execute('''CREATE TABLE jesus (
        id serial PRIMARY KEY,
        num varchar(8),
        title varchar(255),
        last_pos varchar(255),
        completed boolean)''')


location = r'/home/odroid/media/3001/00-MediaWorld-3001/55-etc/00-bible'

async def proc():
    # connect to Postgres DB
    async with create_engine(host = 'localhost',
                            user = 'postgres', 
                            database = 'jesus_db',
                            password = 'sksmsqnwk11') as engine:
        async with engine.acquire() as conn:
            await create_tables(conn)
                            
        l = sorted(glob.iglob(location + '/*'))

        for i in l:
            print(i)
            m = re.search('(\d{4})_(.+)\.mp[3|4]', i) 
            g = m.groups()  # g[0] = 0235, g[1] = 예수소망 (.mp3)
            async with engine.acquire() as conn:
                print(f'insert: {g[0]}, {g[1]}')
                await conn.execute(jesus.insert().values(num=g[0], title=g[1]))

loop = asyncio.get_event_loop()
loop.run_until_complete(proc())


