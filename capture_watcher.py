import os
import time
import shutil
import asyncio
import aiohttp
import aiofiles
import json
import subprocess


async def main():
    #path = 'f:\\down\\'
    #path = 'D:/D_Down/'
    # path = 'E:/Down/'
    # path = 'C:/Users/utylee/Videos/World Of Warcraft'

    # 복사 버퍼 크기인데 0.5초 단위의 속도를 의미합니다. 현재 초당 5메가로
    # 캡쳐과 되고 있기에 그걸 감안해서 설정합니다
    cur_length = 24 * 1024 * 100     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다
    # cur_length = 16 * 1024 * 128     # 16K * 100 = 1.6M /sec => 초당 3.2M 입니다

    path = '/mnt/c/Users/utylee/Videos/World Of Warcraft/'
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
    target = '/mnt/clark/4002/00-MediaWorld-4002/97-Capture'
    backup_target = r'E:/magnets/'

    #target_media = 'u:/3002/00-MediaWorld'
    #target_media = 'u:/4002/00-MediaWorld-4002'
    #target_media = r'\\192.168.0.201\clark\4002\00-MediaWorld-4002'
    # target_media = r'\\192.168.1.205\clark\4002\00-MediaWorld-4002'
    target_media = r'\\192.168.1.202\clark\4002\00-MediaWorld-4002'

    size_table = dict()
    before = dict([(f, None) for f in os.listdir(path)])
    # print(before)

    while 1:
        # 5초 주기입니다
        time.sleep(5)
        after = dict([(f, None) for f in os.listdir(path)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]
        if added:
            # if added:
            for i in added:
                print(f'added {i}')
                # 5초마다 녹화가 끝났는지 용량을 확인합니다
                # 5초 후 전송을 시작합니다
                # time.sleep(3)
                # time.sleep(5)
                # 파일이 여러개가 동시에 추가될 경우 파일 한개 밖에 처리하지 못하던 문제 수정
                # if added[0][-7:] == 'torrent' :
                # if i[-7:] == 'torrent':
                if i[-3:] == 'mp4':
                    # print(i)
                    # print(target)
                    exct = 0
                    a = f'{path}{i}'
                    b = f'{target}/{i}'
                    # b = f'{target}/{i}.part'

                    before_size = os.path.getsize(a)
                    print('size checking start')
                    while 1:
                        time.sleep(3)
                        cur_size = os.path.getsize(a)
                        print(f'before: {before_size}, cur: {cur_size}')
                        if before_size == cur_size:
                            print('complete recoding')
                            break
                        before_size = cur_size

                    print('copy process start')
                    #a = path + "".join(added)
                    # a = path + "".join(i)
                    b_org = f'{target}/{i}'

                    # 2초 후 전송을 시작합니다
                    time.sleep(2)

                    try:
                        async with aiofiles.open(a, mode='rb') as src:
                            async with aiofiles.open(b, mode='wb') as dst:
                                print('async copying')
                                while 1:
                                    buf = await src.read(cur_length)
                                    if not buf:
                                        break
                                    await dst.write(buf)
                                    await asyncio.sleep(0.5)

                    except:
                        print('exception')
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
        before = after


async def send_complete(fname):
    async with aiohttp.ClientSession() as sess:
        resp = await sess.post('http://192.168.1.202:9202/copyend', json=json.dumps({'file': fname}))
        a = await resp.text()
        print(a)
        return a

asyncio.get_event_loop().run_until_complete(main())
