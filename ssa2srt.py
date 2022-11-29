import codecs
import re
import cchardet
import os
import argparse
import asyncio
import time
import math
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument("-l", "--language", help="choose language to convert", default="kr")
parser.add_argument("-r", "--remove_original", help="remove original smi file when converting succeed", default=False, action="store_true")
parser.add_argument("-s", "--suffix", help="adding language suffix (e.g. .ko.srt)", default=False, action="store_true")
parser.add_argument("-i", "--ignore", help="ignore decoding error", default=False, action="store_true")
parser.add_argument("dir", help="target directory. ex) ./smi2srt <OPTIONS> ./Movies", default="./")

args = parser.parse_args()

PATH = args.dir
LANG = args.language.upper()+'CC'
REMOVE_OPTION = args.remove_original
SUFFIX = '.'+args.language.lower() if args.suffix else ''
DECODE_ERRORS = 'ignore' if args.ignore else 'strict'

langcodeConvRules = {'.kr':'.ko'}
if(SUFFIX in langcodeConvRules):
    SUFFIX = langcodeConvRules[SUFFIX]

# srt 파일의 시간형식으로 변환합니다
# 00:01:02:03,420
def convert_time(s):
    a, b, c = s.split(':')
    c, d = c.split('.')

    # 00:00:00 부분이 한자리로 넘어오는 경우가 있어서 두자리를 확정해주기 위해 추가합니다
    a = int(a)
    b = int(b)
    c = int(c)

    # 간혹 변환된 ssa 의 msec가 한자리로 오는 경우 추가로 0을 붙여줍니다
    if (len(d) == 1):
        d = d + '0'

    s = f'{a:02}:{b:02}:{c:02},{d}0'

    return s

# 행으로 분리해서 리스트로 반납합니다
def parse_ssa(ssa):
    l = ssa.split('\n')

    return l

def convert(ssa): # written by utylee
    # print(smi)
    srt = ''
    count = 1

    #특정기준으로 ssa를 분리합니다
    # print(ssa)
    full = parse_ssa(ssa)
    # print(full)

    for i in full:
        # print(i)
        buf = ''
        pat = r'dialogue:\s*marked=\d+,(.*),(.*),default,,0,0,0,,(.*)'

        # result = re.split(pat, srt, flags=re.I)
        m = re.search(pat, i.lower())
        if(m):
            starttime = m.group(1)
            endtime = m.group(2)
            txt = m.group(3)

            starttime_conv = convert_time(starttime)
            endtime_conv = convert_time(endtime)

            # txt의 개행문자/N를 /n으로 변경합니다
            txt = re.sub(r'\\n', '\n', txt)

            '''
            Dialogue: Marked=01,00:03:32.26,00:03:35.96,Default,,0,0,0,,버지니아주, 폴스 교회새벽 3시 26분
            '''

            '''
            1
            00:00:07,000 --> 00:00:10,180
            몬타나주 헬레나
            밤 12시58분

            2
            00:00:22,170 --> 00:00:24,080
            12시방향에  비행접시.
            '''

            buf += f'{count}\n{starttime_conv} --> {endtime_conv}\n{txt}\n\n'

            # print(buf)

            srt += buf
            count += 1
    # print(srt)

    return srt

async def main():
    print('media library path:', PATH)
    success=[]
    fail=[]
    print('finding and converting started...')
    for p,w,f in os.walk(PATH):
        for file_name in f:
            if file_name[-4:].lower()=='.ssa':
                print('processing %s' %os.path.join(p,file_name))
                try:
                    with open(os.path.join(p,file_name),'rb') as ssa_file:
                        ssa_raw = ssa_file.read()
                        encoding = cchardet.detect(ssa_raw)
                    ssa = ssa_raw.decode(encoding['encoding'], errors=DECODE_ERRORS)
                    srt_file = codecs.open(os.path.join(p,os.path.splitext(file_name)[0]+SUFFIX+'.srt'),'w',encoding='utf-8')

                    # smi_file.write(convert(ssa))

                    # convert(ssa)
                    srt_file.write(convert(ssa))

                    success.append(file_name)
                    if REMOVE_OPTION:
                        os.remove(os.path.join(p,file_name))
                except:
                    fail.append(file_name)

    ssa_list = list(set(success) | set(fail))
    print('\nfound .ssa subtitles:')
    for ssa in ssa_list:
        print(ssa)

    if len(success) > 0:
        print('\nworked .srt subtitles:')
        for ssa in success:
            print(ssa)

    if len(fail) > 0:
        print('\nfailed .srt subtitles:')
        for ssa in fail:
            print(ssa)

    if REMOVE_OPTION:
        print('\nworked srt files are removed due to removal option')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

