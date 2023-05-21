import os
import time
import shutil
import asyncio
import aiohttp
from aiohttp import web
import aiofiles
import json
import subprocess
import logging

def main():
    app = web.Application()
    app['log_path'] = f'/home/utylee/capture.log'
    app['cur_length'] = 8 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    app['paths'] = [
                '/mnt/c/Users/utylee/Videos/World Of Warcraft/',
                '/mnt/c/Users/utylee/Videos/Heroes of the Storm/',
                '/mnt/c/Users/utylee/Videos/Desktop/'
            ]
    app[ 'target' ] = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture'

    # watcher 프로시져 함수를 돌립니다
    app.on_startup.append(create_bg_tasks)

    # 웹서버를 엽니다. 히오스가 활성상태인지 확인하는 정보를 받습니다
    app.add_routes([
                    web.get('/low', low),
                    web.get('/high', high)
                    ])
    web.run_app(app, port=8007)

async def low(request):
    # print('low')
    request.app['cur_length'] = 8 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    return web.Response(text='low')

async def high(request):
    # print('high')
    request.app['cur_length'] = 48 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    return web.Response(text='high')

async def create_bg_tasks(app):
    # aiohttp에서 app.loop 이 사라졌다고 하네요 그냥 아래와같이 하라고 합니다
    # app.loop.create_task(watching(app))
    asyncio.create_task(watching(app))

async def watching(app):
    # log_path = f'/home/utylee/capture.log'
    log_path = app['log_path']

    # supervisor에 의해 root권한으로 생성되었을 때 혹은 반대의 경우의 권한
    #문제를 위한 해결법입니다
    try:
        os.chmod(log_path, 0o777)
    except:
        pass

    handler = logging.FileHandler(log_path)
    log = logging.getLogger('log')
    log.addHandler(handler)
    # log.terminator = ''
    log.setLevel(logging.DEBUG)

   #logging.basicConfig(filename=log_path,level=logging.INFO)


    #path = 'f:\\down\\'
    #path = 'D:/D_Down/'
    # path = 'E:/Down/'
    # path = 'C:/Users/utylee/Videos/World Of Warcraft'


    # 게임 중이냐 아느냐로 속도 조절을 할 수 있게끔 기준 변수를 넣어봅니다
    speed_control = 1


    # 복사 버퍼 크기인데 0.5초 단위의 속도를 의미합니다. 현재 초당 5메가로
    # 캡쳐과 되고 있기에 그걸 감안해서 설정합니다
    # cur_length = 24 * 1024 * 100     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    #cur_length = 16 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # 속도를 더 늦춰봅니다
    # cur_length = 8 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    cur_length = app['cur_length']

    # 게임 중이 아니라면 높은속도로 복사합니다
    if speed_control == 0:
        cur_length = 24 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다


    # 여러 경로를 감시하게끔 변경합니다
    #path = '/mnt/c/Users/utylee/Videos/World Of Warcraft/'
    paths = app['paths']
    # paths = [
    #             '/mnt/c/Users/utylee/Videos/World Of Warcraft/',
    #             '/mnt/c/Users/utylee/Videos/Heroes of the Storm/',
    #             '/mnt/c/Users/utylee/Videos/Desktop/'
    #         ]

    # path = '/mnt/c/Users/utylee/Videos/Desktop/'

    #path = 'E:\\Down\\'
    #target = 'w:\\99-data\\91-transmission-watch\\'
    #target = 'v:/99-data/91-transmission-watch'
    #target_media = 'v:/00-MediaWorld'
    #target = 'u:/3002/99-data/91-transmission-watch'

    #target = 'u:/4001/99-data/91-transmission-watch'
    #target = r'\\192.168.0.201\clark\4001\99-data\91-transmission-watch'
    # target = r'\\192.168.1.205\clark\4001\99-data\91-transmission-watch'
    # target = r'\\192.168.1.202\clark\4002\00-MediaWorld-4002'
    # target = '/mnt/clark/4002/00-MediaWorld-4002'
    # target = r'\\192.168.1.202\clark\4002\00-MediaWorld-4002\97-Capture'
    # target = r'\\192.168.1.202\clark\4001\99-data\91-transmission-watch'

    # target = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture'
    target = app['target']

    backup_target = r'E:/magnets/'

    #target_media = 'u:/3002/00-MediaWorld'
    #target_media = 'u:/4002/00-MediaWorld-4002'
    #target_media = r'\\192.168.0.201\clark\4002\00-MediaWorld-4002'
    # target_media = r'\\192.168.1.205\clark\4002\00-MediaWorld-4002'
    target_media = r'\\192.168.1.202\clark\4002\00-MediaWorld-4002'

    size_table = dict()
    # before = dict([(f, None) for f in os.listdir(path)])

    befores = []
    afters = []
    addeds = []
    removeds = []
    for n in range(len(paths)):
        # befores[n] = paths[n]
        befores.append(dict([(f, None) for f in os.listdir(paths[n])]))
        afters.append(paths[n])
        addeds.append(paths[n])
        removeds.append(paths[n])

    # before = dict([(f, None) for f in os.listdir(path)])

    # print(before)

    while 1:
        # for path in paths:
        for n in range(len(paths)):
            # 5초 주기입니다
            # time.sleep(5)
            await asyncio.sleep(5)
            # after = dict([(f, None) for f in os.listdir(path)])
            # added = [f for f in after if not f in before]
            afters[n] = dict([(f, None) for f in os.listdir(paths[n])])
            addeds[n] = [f for f in afters[n] if not f in befores[n]]
            removeds[n] = [f for f in befores[n] if not f in afters[n]]
            if addeds[n]:
                # if added:
                for i in addeds[n]:
                    print(f'added {i}')
                    log.info(f'added {i}')
                    # 5초마다 녹화가 끝났는지 용량을 확인합니다
                    # 5초 후 전송을 시작합니다
                    # time.sleep(3)
                    # time.sleep(5)
                    # 파일이 여러개가 동시에 추가될 경우 파일 한개 밖에 처리하지 못하던 문제 수정
                    # if added[0][-7:] == 'torrent' :
                    # if i[-7:] == 'torrent':
                    # if i[-3:] == 'mp4':
                    if i[-3:] == 'mp4' or i[-4:] == 'webm':
                        exct = 0
                        a = f'{paths[n]}{i}'
                        # /mnt 이 아닌 \\192..xxx 방식의 위치를 사용해봅니다 
                        b = f'{target}/{i}'
                        # b = f'{target}\\{i}'
                        # b = f'{target}/{i}.part'
                        # print(i)
                        # print(target)
                        try: 
                            before_size = os.path.getsize(a)
                            print('size checking start')
                            log.info('size checking start')
                            while 1:
                                # time.sleep(3)
                                await asyncio.sleep(3)
                                cur_size = os.path.getsize(a)
                                print(f'before: {before_size}, cur: {cur_size}')
                                log.info(f'before: {before_size}, cur: {cur_size}')
                                if before_size == cur_size:
                                    print('complete recoding')
                                    log.info('complete recoding')
                                    break
                                before_size = cur_size

                            print('copy process start')
                            log.info('copy process start')
                            #a = path + "".join(added)
                            # a = path + "".join(i)
                            b_org = f'{target}/{i}'

                            # 2초 후 전송을 시작합니다
                            time.sleep(2)
                        except:
                            print('exception in added file check')
                            log.info('exception in added file check')
                            exct = 1
                            continue

                        try:
                            print(f'a: {a}\nb: {b}')
                            log.info(f'a: {a}\nb: {b}')
                            async with aiofiles.open(a, mode='rb') as src:
                                async with aiofiles.open(b, mode='wb') as dst:
                                    print('async copying')
                                    while 1:
                                        cur_length = app['cur_length']
                                        buf = await src.read(cur_length)
                                        if not buf:
                                            break
                                        await dst.write(buf)
                                        print(f'{time.time()} wrote:{len(buf)}')
                                        log.info(f'{time.time()} wrote:{len(buf)}')
                                        await asyncio.sleep(0.5)
                        # try:
                        #     print(f'a: {a}\nb: {b}')
                        #     log.info(f'a: {a}\nb: {b}')
                        #     with open(a, mode='rb') as src:
                        #         with open(b, mode='wb') as dst:
                        #             # print('async copying')
                        #             while 1:
                        #                 buf = src.read(cur_length)
                        #                 if not buf:
                        #                     break
                        #                 dst.write(buf)
                        #                 # print(f'{time.time()} wrote:{len(buf)}')
                        #                 log.info(f'{time.time()} wrote:{len(buf)}')
                        #                 time.sleep(0.5)

                        except:
                            print('exception in copying')
                            log.info('exception in copying')
                            exct = 1
                            continue

                        # def _copyfileobj_patched(fsrc, fdst, length=cur_length):
                        #     """Patches shutil copyfileobj method to hugely improve copy speed"""
                        #     print('copyfileobj')
                        #     while 1:
                        #         buf = fsrc.read(length)
                        #         if not buf:
                        #             break
                        #         fdst.write(buf)
                        #         time.sleep(0.5)

                        # # shutil.copyfileobj = _copyfileobj_patched

                        # # src = open(a, 'r+b')
                        # # dst = open(f'{target}/{i}', 'w+b')
                        # with open(a, 'rb') as src:
                        #     # with open(f'{target}/{i}.part', 'w+b') as dst:
                        #     with open(b, 'wb') as dst:
                        #         try:
                        #             # print(a)
                        #             # shutil.copy(a, target)
                        #             # shutil.copyfile(a, target)
                        #             _copyfileobj_patched(src, dst)
                        #         except:
                        #             print('exception')
                        #             exct = 1
                        #             continue
                        # 복사완료후 원래 파일을 삭제합니다
                        print('copy complete')
                        log.info('copy complete')
                        if exct == 0:
                            # exception이 안났을 경우에만 파일이름을 다시 복구합니다. 10초 후
                            # exception이 안났을 경우에만 삭제합니다. 5초 후
                            time.sleep(5)
                            os.remove(a)
                            # client-server 로서 part확장자 등을 이용해 변경해줄 필요가 없어졌
                            # 습니다. 파일 완료후 mp4 moov 정보가 수정된 이후에 전송하기에
                            # ret = await send_complete(i)
                            # if (ret == 'ok'):
                            #     os.remove(a)

                            # renamed = a + '.copied'
                            # os.rename(a, renamed)
                            # os.rename(b, b_org)

                        # 백업 폴더에 torrent 파일을 옮깁니다
                        # shutil.copy(renamed,  backup_target)
                        # os.remove(renamed)
            # before = after
            befores[n] = afters[n]


async def send_complete(fname):
    async with aiohttp.ClientSession() as sess:
        resp = await sess.post('http://192.168.1.202:9202/copyend', json=json.dumps({'file': fname}))
        a = await resp.text()
        print(a)
        return a


if __name__ == '__main__':
    main()

#asyncio.get_event_loop().run_until_complete(main())
