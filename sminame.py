
import asyncio
import sys
import os
import re

curdir = '.'
#curdir = '/home/odroid/temp/test'

# 비디오 파일 확장자 후보들입니다
exts = ['mkv', 'avi', 'mp4']

async def makecandi(w):
    return '|'.join(exts)

async def main():
    #mkv나 avi mp4등의 확장자를 비디오 파일로 보고 파일이름을 저장합니다
    #files = [f for f in os.listdir('.') if os.path.isfile(f)]
    #files = [f for f in os.listdir(curdir)]
    thename = ''
    candidates = await makecandi(exts) 
    #print(candidates)

    # 현재 폴더의 파일들을 리스트하고 비디오 파일명을 알아둡니다
    files = [f for f in os.listdir(curdir) if os.path.isfile(os.path.join(curdir,f))]
    #print(files)
    for f in files:
        s = re.search(f'(.*)\.({candidates})', f, re.I)     # 대소문자 구분없이 찾아냅니다 re.I
        #s = re.search(f'(.*)\.({candidates})', f)
        if s is not None:
            thename = s.group(1)
            print(s.group(0))
            break               # 현재는 최초의 하나가 발견되면 그것을 파일이름으로 사용하기로 합니다

    # smi나 srt 파일을 찾아 해당이름으로 변경합니다
    subs = ''
    subs_ext = ''
    for f in files:
        r = re.search('((.*)\.(smi|srt))', f, re.I)
        if r is not None:
            subs = r.group(1)
            subs_ext = r.group(3)
            print(subs)
            #print(subs_ext)
            break

    newsubs = thename + '.' + subs_ext
    os.rename(os.path.join(curdir,subs), os.path.join(curdir, newsubs)) 
    print('')
    print(newsubs)
    print('..로 변환완료되었습니다')

'''
    files = [f for f in os.listdir(curdir) if os.path.isfile(os.path.join(curdir,f))]
    print(files)
    '''

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

#asyncio.run(main())       # 3.7

