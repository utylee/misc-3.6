import uvloop
import aiohttp
from aiohttp import web
import datetime
import asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa
import db_music_idea as db
import random


async def idea(request):
    result = 'music_idea'

    return web.Response(text=result)
'''
tbl_idea = sa.Table('music_idea', meta, 
            sa.Column('id', sa.Integer, primary_key=True), 
            sa.Column('type', sa.Integer),
            sa.Column('content_number', sa.Integer),
            sa.Column('content', sa.String(255)),
            sa.Column('description', sa.String(1024)))
            '''
def transl(content):
    content = content.replace('_u_sp_', ' ')
    content = content.replace('_u_qa_', '?')
    content = content.replace('_u_im_', '&')

    return content

async def add_writing(request):
    cur = round(datetime.datetime.now().timestamp())
    content = request.match_info['content']
    content = transl(content)
    async with request.app['engine'].acquire() as conn:
        # print(len(await conn.execute(db.tbl_idea.select())))

        # writing 항목의 수를 셉니다
        count = 0
        async for r in conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==0)):
            count += 1
        print(f'총 {count}개의 writing 항목이 있습니다')

        exists = []
        punks = []

        templist = range(1, count+1)
        for l in templist:
            async for r in conn.execute(db.tbl_idea.select()
                                        .where(db.tbl_idea.c.type==0)
                                        .where(db.tbl_idea.c.content_number==l)):
                print(f'add_writing 중 {l+1} 이 발견되었습니다')
                exists.append(l)
                break
        print(f'exists={exists}')

        for i in templist:
            if i not in exists:
                punks.append(i)

        # 비어있는 숫자를 경고해줍니다. 나중에 목록추가 숫자설정에 계속 문제를 일으킵니다
        if len(punks):
            print('없는 숫자들은 ', end='')
            for i in punks:
                print(f'{i} ', end='')
            print('입니다')

        number = count + 1 
        if len(punks):
            number = punks[0] 
                                        
        # 없는 숫자중 가장 작은 숫자로 지정하여 입력해줍니다
        #async for r in conn.execute(db.tbl_idea.select()):
        await conn.execute(db.tbl_idea.insert().values(id=cur, 
                                                type=0, 
                                                content_number=number, 
                                                content=content, 
                                                description=''))
    # return 0
    printing = f'입력 Writing {number}. {content}'
    return web.Response(text=printing)

async def add_sounding(request):
    cur = round(datetime.datetime.now().timestamp())
    content = request.match_info['content']
    content = transl(content)
    async with request.app['engine'].acquire() as conn:
        # print(len(await conn.execute(db.tbl_idea.select())))

        # writing 항목의 수를 셉니다
        count = 0
        async for r in conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==1)):
            count += 1
        print(f'총 {count}개의 sounding 항목이 있습니다')

        exists = []
        punks = []

        templist = range(1, count+1)
        for l in templist:
            async for r in conn.execute(db.tbl_idea.select()
                                        .where(db.tbl_idea.c.type==1)
                                        .where(db.tbl_idea.c.content_number==l)):
                print(f'add_sounding 중 {l+1} 이 발견되었습니다')
                exists.append(l)
                break
        print(f'exists={exists}')

        for i in templist:
            if i not in exists:
                punks.append(i)

        # 비어있는 숫자를 경고해줍니다. 나중에 목록추가 숫자설정에 계속 문제를 일으킵니다
        if len(punks):
            print('없는 숫자들은 ', end='')
            for i in punks:
                print(f'{i} ', end='')
            print('입니다')

        number = count + 1 
        if len(punks):
            number = punks[0] 
                                        
        # 없는 숫자중 가장 작은 숫자로 지정하여 입력해줍니다
        #async for r in conn.execute(db.tbl_idea.select()):
        await conn.execute(db.tbl_idea.insert().values(id=cur, 
                                                type=1, 
                                                content_number=number, 
                                                content=content, 
                                                description=''))
    # return 0
    printing = f'입력 Sounding {number}. {content}'
    return web.Response(text=printing)

async def add_arranging(request):
    cur = round(datetime.datetime.now().timestamp())
    content = request.match_info['content']
    content = transl(content)
    async with request.app['engine'].acquire() as conn:
        # print(len(await conn.execute(db.tbl_idea.select())))

        # arranging 항목의 수를 셉니다
        count = 0
        async for r in conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==2)):
            count += 1
        print(f'총 {count}개의 arranging 항목이 있습니다')

        exists = []
        punks = []

        templist = range(1, count+1)
        for l in templist:
            async for r in conn.execute(db.tbl_idea.select()
                                        .where(db.tbl_idea.c.type==2)
                                        .where(db.tbl_idea.c.content_number==l)):
                print(f'add_arranging 중 {l+1} 이 발견되었습니다')
                exists.append(l)
                break
        print(f'exists={exists}')

        for i in templist:
            if i not in exists:
                punks.append(i)

        # 비어있는 숫자를 경고해줍니다. 나중에 목록추가 숫자설정에 계속 문제를 일으킵니다
        if len(punks):
            print('없는 숫자들은 ', end='')
            for i in punks:
                print(f'{i} ', end='')
            print('입니다')

        number = count + 1 
        if len(punks):
            number = punks[0] 
                                        
        # 없는 숫자중 가장 작은 숫자로 지정하여 입력해줍니다
        #async for r in conn.execute(db.tbl_idea.select()):
        await conn.execute(db.tbl_idea.insert().values(id=cur, 
                                                type=2, 
                                                content_number=number, 
                                                content=content, 
                                                description=''))
    printing = f'입력 Arranging {number}. {content}'
    return web.Response(text=printing)
    # return 0


async def add_mixing(request):
    cur = round(datetime.datetime.now().timestamp())
    content = request.match_info['content']
    content = transl(content)
    async with request.app['engine'].acquire() as conn:
        # print(len(await conn.execute(db.tbl_idea.select())))

        # writing 항목의 수를 셉니다
        count = 0
        async for r in conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==3)):
            count += 1
        print(f'총 {count}개의 writing 항목이 있습니다')

        exists = []
        punks = []

        templist = range(1, count+1)
        for l in templist:
            async for r in conn.execute(db.tbl_idea.select()
                                        .where(db.tbl_idea.c.type==3)
                                        .where(db.tbl_idea.c.content_number==l)):
                print(f'add_mixing 중 {l+1} 이 발견되었습니다')
                exists.append(l)
                break
        print(f'exists={exists}')

        for i in templist:
            if i not in exists:
                punks.append(i)

        # 비어있는 숫자를 경고해줍니다. 나중에 목록추가 숫자설정에 계속 문제를 일으킵니다
        if len(punks):
            print('없는 숫자들은 ', end='')
            for i in punks:
                print(f'{i} ', end='')
            print('입니다')

        number = count + 1 
        if len(punks):
            number = punks[0] 
                                        
        # 없는 숫자중 가장 작은 숫자로 지정하여 입력해줍니다
        #async for r in conn.execute(db.tbl_idea.select()):
        await conn.execute(db.tbl_idea.insert().values(id=cur, 
                                                type=3, 
                                                content_number=number, 
                                                content=content, 
                                                description=''))
    printing = f'입력 Mixing {number}. {content}'
    return web.Response(text=printing)

async def remove_writing(request):
    number = int(request.match_info['content'])
    content = ''
    printing = ''
    async with request.app['engine'].acquire() as conn:
        confirm = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==0))).first()
        if confirm is None:
            return web.Response(text='Writing 관련 항목이 없습니다')

        async for p in conn.execute(sa.select([db.tbl_idea.c.content])
                                .where(db.tbl_idea.c.type==0).where(db.tbl_idea.c.content_number==number)):
            content = p[0]
        await conn.execute(db.tbl_idea.delete()
                                .where(db.tbl_idea.c.type==0).where(db.tbl_idea.c.content_number==number))

    # printing += f'\n Mixing {content_number}. {content}'
    printing = f'삭제 Writing {number}. {content}' if len(content) else f'없는 항목입니다'

    # return web.Response(text=f'{content_number}. {content}')
    return web.Response(text=printing)

async def remove_sounding(request):
    number = int(request.match_info['content'])
    content = ''
    printing = ''
    async with request.app['engine'].acquire() as conn:
        confirm = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==1))).first()
        if confirm is None:
            return web.Response(text='Sounding 관련 항목이 없습니다')

        async for p in conn.execute(sa.select([db.tbl_idea.c.content])
                                .where(db.tbl_idea.c.type==1).where(db.tbl_idea.c.content_number==number)):
            content = p[0]
        await conn.execute(db.tbl_idea.delete()
                                .where(db.tbl_idea.c.type==1).where(db.tbl_idea.c.content_number==number))

    # printing += f'\n Mixing {content_number}. {content}'
    printing = f'삭제 Sounding {number}. {content}' if len(content) else f'없는 항목입니다'

    # return web.Response(text=f'{content_number}. {content}')
    return web.Response(text=printing)

async def remove_arranging(request):
    number = int(request.match_info['content'])
    content = ''
    printing = ''
    async with request.app['engine'].acquire() as conn:
        confirm = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==2))).first()
        if confirm is None:
            return web.Response(text='Arranging 관련 항목이 없습니다')

        async for p in conn.execute(sa.select([db.tbl_idea.c.content])
                                .where(db.tbl_idea.c.type==2).where(db.tbl_idea.c.content_number==number)):
            content = p[0]
        await conn.execute(db.tbl_idea.delete()
                                .where(db.tbl_idea.c.type==2).where(db.tbl_idea.c.content_number==number))

    # printing += f'\n Mixing {content_number}. {content}'
    printing = f'삭제 Arranging {number}. {content}' if len(content) else f'없는 항목입니다'

    # return web.Response(text=f'{content_number}. {content}')
    return web.Response(text=printing)

async def remove_mixing(request):
    number = int(request.match_info['content'])
    content = ''
    printing = ''
    async with request.app['engine'].acquire() as conn:
        confirm = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==3))).first()
        if confirm is None:
            return web.Response(text='Mixing 관련 항목이 없습니다')

        async for p in conn.execute(sa.select([db.tbl_idea.c.content])
                                .where(db.tbl_idea.c.type==3).where(db.tbl_idea.c.content_number==number)):
            content = p[0]
        await conn.execute(db.tbl_idea.delete()
                                .where(db.tbl_idea.c.type==3).where(db.tbl_idea.c.content_number==number))

    # printing += f'\n Mixing {content_number}. {content}'
    printing = f'삭제 Mixing {number}. {content}' if len(content) else f'없는 항목입니다'

    # return web.Response(text=f'{content_number}. {content}')
    return web.Response(text=printing)

async def pick_writing(request):
    max = 0
    content_number = 1
    content = ''
    printing = ''
    async with request.app['engine'].acquire() as conn:
        confirm = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==0))).first()
        if confirm is None:
            return web.Response(text='Writing 관련 항목이 없습니다')
        async for r in conn.execute(sa.select([db.tbl_idea.c.content_number]).where(db.tbl_idea.c.type==0)):
            max = r[0] if r[0] > max else max

        number = 1
        while 1:
            number = random.randint(1, max + 1)
            printing += f'랜덤 숫자는 {number}입니다\n'
            print(f'랜덤 숫자는 {number}입니다')
            result = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==0).where(db.tbl_idea.c.content_number==number))).first()
            if result: break
        printing += f'선정된 숫자는 {number}입니다\n'
        print(f'선정된 숫자는 {number}입니다')

        async for p in conn.execute(sa.select([db.tbl_idea.c.content_number, 
                                db.tbl_idea.c.content])
                                .where(db.tbl_idea.c.type==0).where(db.tbl_idea.c.content_number==number)):
            content_number = p[0]
            content = p[1]

    # printing += f'\n Mixing {content_number}. {content}'
    printing = f'Writing {content_number}. {content}'

    # return web.Response(text=f'{content_number}. {content}')
    return web.Response(text=printing)

async def pick_sounding(request):
    max = 0
    content_number = 1
    content = ''
    printing = ''
    async with request.app['engine'].acquire() as conn:
        confirm = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==1))).first()
        if confirm is None:
            return web.Response(text='Writing 관련 항목이 없습니다')
        async for r in conn.execute(sa.select([db.tbl_idea.c.content_number]).where(db.tbl_idea.c.type==1)):
            max = r[0] if r[0] > max else max

        number = 1
        while 1:
            number = random.randint(1, max + 1)
            printing += f'랜덤 숫자는 {number}입니다\n'
            print(f'랜덤 숫자는 {number}입니다')
            result = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==1).where(db.tbl_idea.c.content_number==number))).first()
            if result: break
        printing += f'선정된 숫자는 {number}입니다\n'
        print(f'선정된 숫자는 {number}입니다')

        async for p in conn.execute(sa.select([db.tbl_idea.c.content_number, 
                                db.tbl_idea.c.content])
                                .where(db.tbl_idea.c.type==1).where(db.tbl_idea.c.content_number==number)):
            content_number = p[0]
            content = p[1]

    # printing += f'\n Mixing {content_number}. {content}'
    printing = f'Sounding {content_number}. {content}'

    # return web.Response(text=f'{content_number}. {content}')
    return web.Response(text=printing)

async def pick_arranging(request):
    max = 0
    content_number = 1
    content = ''
    printing = ''
    async with request.app['engine'].acquire() as conn:
        confirm = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==2))).first()
        if confirm is None:
            return web.Response(text='Arranging 관련 항목이 없습니다')
        async for r in conn.execute(sa.select([db.tbl_idea.c.content_number]).where(db.tbl_idea.c.type==2)):
            max = r[0] if r[0] > max else max

        number = 1
        while 1:
            number = random.randint(1, max + 1)
            printing += f'랜덤 숫자는 {number}입니다\n'
            print(f'랜덤 숫자는 {number}입니다')
            result = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==2).where(db.tbl_idea.c.content_number==number))).first()
            if result: break
        printing += f'선정된 숫자는 {number}입니다\n'
        print(f'선정된 숫자는 {number}입니다')

        async for p in conn.execute(sa.select([db.tbl_idea.c.content_number, 
                                db.tbl_idea.c.content])
                                .where(db.tbl_idea.c.type==2).where(db.tbl_idea.c.content_number==number)):
            content_number = p[0]
            content = p[1]

    # printing += f'\n Mixing {content_number}. {content}'
    printing = f'Arranging {content_number}. {content}'

    # return web.Response(text=f'{content_number}. {content}')
    return web.Response(text=printing)

async def pick_mixing(request):
    max = 0
    content_number = 1
    content = ''
    printing = ''
    async with request.app['engine'].acquire() as conn:
        confirm = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==3))).first()
        if confirm is None:
            return web.Response(text='Mixing 관련 항목이 없습니다')

        async for r in conn.execute(sa.select([db.tbl_idea.c.content_number]).where(db.tbl_idea.c.type==3)):
            max = r[0] if r[0] > max else max

        number = 1
        while 1:
            number = random.randint(1, max + 1)
            printing += f'랜덤 숫자는 {number}입니다\n'
            print(f'랜덤 숫자는 {number}입니다')
            result = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==3).where(db.tbl_idea.c.content_number==number))).first()
            if result: break
        printing += f'선정된 숫자는 {number}입니다\n'
        print(f'선정된 숫자는 {number}입니다')

        async for p in conn.execute(sa.select([db.tbl_idea.c.content_number, 
                                db.tbl_idea.c.content])
                                .where(db.tbl_idea.c.type==3).where(db.tbl_idea.c.content_number==number)):
            content_number = p[0]
            content = p[1]

    # printing += f'\n Mixing {content_number}. {content}'
    printing = f'Mixing {content_number}. {content}'

    # return web.Response(text=f'{content_number}. {content}')
    return web.Response(text=printing)

async def pick_any(request):
    max = 0
    type = 0
    content_number = 1
    content = ''
    printing = ''
    async with request.app['engine'].acquire() as conn:
        confirm = await (await conn.execute(db.tbl_idea.select())).first()
        if confirm is None:
            return web.Response(text='항목이 없습니다')

        # async for r in conn.execute(sa.select([db.tbl_idea.c.content_number]).where(db.tbl_idea.c.type==2)):
        #     max = r[0] if r[0] > max else max

        number = 1
        while 1:
            rnd_type = random.randint(0, 3)
            async for r in conn.execute(sa.select([db.tbl_idea.c.content_number]).where(db.tbl_idea.c.type==rnd_type)):
                max = r[0] if r[0] > max else max

            number = random.randint(1, max + 1)
            printing += f'type은 {rnd_type}이고\n'
            printing += f'랜덤 숫자는 {number}입니다\n'
            print(f'type은 {rnd_type}이고')
            print(f'랜덤 숫자는 {number}입니다')

            result = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==rnd_type).where(db.tbl_idea.c.content_number==number))).first()
            if result: 
                type = rnd_type 
                break
        printing += f'선정된 type은 {type}이고\n'
        printing += f'선정된 숫자는 {number}입니다\n'
        print(f'선정된 type은 {type}이고')
        print(f'선정된 숫자는 {number}입니다')

        # async for p in conn.execute(sa.select([db.tbl_idea.c.content_number, 
        #                         db.tbl_idea.c.content])
        async for p in conn.execute(sa.select([db.tbl_idea.c.content])
                                .where(db.tbl_idea.c.type==type)
                                .where(db.tbl_idea.c.content_number==number)):
            # content_number = p[0]
            content_number = number
            content = p[0]

    # printing += f'\n Mixing {content_number}. {content}'
    type_str = ['Writing',  'Sounding',  'Arranging',  'Mixing']

    # type_str = 'Writing'
    # if type == 1:
    #     type_str = 'Arranging'
    # elif type == 2:
    #     type_str = 'Mixing'
    # printing = f'{type_str} {content_number}. {content}'

    printing = f'{type_str[type]} {content_number}. {content}'

    return web.Response(text=printing)

async def list_type(request):
    type_str = ['Writing', 'Sounding', 'Arranging', 'Mixing']
    printings = ''

    type= int(request.match_info['content']) 

    printings += '\n'
    async with request.app['engine'].acquire() as conn:
        confirm = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==type))).first()
        if confirm is None:
            printings += f'{type_str[type]} 관련 항목이 없습니다\n'

    async with request.app['engine'].acquire() as conn:
        async for r in conn.execute(sa.select([db.tbl_idea.c.content_number,
                                            db.tbl_idea.c.content])
                                            .where(db.tbl_idea.c.type==type)
                                            .order_by(db.tbl_idea.c.content_number)):
            printings += f'{type_str[type]} {r[0]} {r[1]} \n' 

    return web.Response(text=printings)

async def list_all(request):
    types = [0, 1, 2, 3]
    type_str = ['Writing', 'Sounding', 'Arranging', 'Mixing']
    printings = ''

    for i in types:
        printings += '\n'
        async with request.app['engine'].acquire() as conn:
            confirm = await (await conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==i))).first()
            if confirm is None:
                printings += f'{type_str[i]} 관련 항목이 없습니다\n'
                continue

        # async for r in conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==i).order_by(db.tbl_idea.c.content_number)):
        # async for r in conn.execute(sa.select([db.tbl_idea.c.content_number,
        #                                    db.tbl_idea.c.content])
        #                             .where(db.tbl_idea.c.type==i)
        #                             .order_by(db.tbl_idea.c.content_number)):
        async with request.app['engine'].acquire() as conn:
            # async for r in conn.execute(db.tbl_idea.select().where(db.tbl_idea.c.type==i).order_by(db.tbl_idea.c.content_number)):
            async for r in conn.execute(sa.select([db.tbl_idea.c.content_number,
                                                db.tbl_idea.c.content])
                                                .where(db.tbl_idea.c.type==i)
                                                .order_by(db.tbl_idea.c.content_number)):
                printings += f'{type_str[i]} {r[0]} {r[1]} \n' 

    return web.Response(text=printings)


async def create_bg_tasks(app):
    app['engine'] = await create_engine(host='192.168.1.204',
                                database='music_idea',
                                user='utylee', 
                                password='sksmsqnwk11')

async def clean_bg_tasks(app):
    pass


if __name__ == "__main__":
    uvloop.install()
    app = web.Application()
    app['idea'] = [0,0,0]
    app.on_startup.append(create_bg_tasks)
    app.on_cleanup.append(clean_bg_tasks)

    app.add_routes([web.get('/', idea), 
                    web.get('/add/writing/{content:.*}', add_writing),
                    web.get('/add/sounding/{content:.*}', add_sounding),
                    web.get('/add/arranging/{content:.*}', add_arranging),
                    web.get('/add/mixing/{content:.*}', add_mixing),
                    web.get('/remove/writing/{content:.*}', remove_writing),
                    web.get('/remove/sounding/{content:.*}', remove_sounding),
                    web.get('/remove/arranging/{content:.*}', remove_arranging),
                    web.get('/remove/mixing/{content:.*}', remove_mixing),
                    web.get('/pick/writing', pick_writing),
                    web.get('/pick/sounding', pick_sounding),
                    web.get('/pick/arranging', pick_arranging),
                    web.get('/pick/mixing', pick_mixing),
                    web.get('/pick/any', pick_any),

                    web.get('/list_all', list_all),
                    web.get('/list_all/{content:.*}', list_type)
                    ])
                    #web.get('/weather', weather)
                    #])
    web.run_app(app, port=9007)
