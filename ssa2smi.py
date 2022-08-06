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

def init_smi():
    s = \
    '''<SAMI>
<HEAD>
<TITLE></TITLE>
<STYLE TYPE="text/css">
<!--
P { margin-left:2pt; margin-right:2pt; margin-bottom:1pt;
    margin-top:1pt; font-size:20pt; text-align:center;
    font-family:arial; font-weight:bold; color:white; }
.KRCC { Name:Korean; lang:ko-KR; SAMIType:CC; }
-->
</STYLE>
</HEAD>
<BODY>
'''
    return s

# 숫자를 받아서 00:00:00 포맷으로 분해합니다
def format_total(i):
    i, msec = divmod(int(i), 100)

    hour, minute = divmod(i, 3600)
    minute, seconds = divmod(minute, 60)
    seconds_str = f'{seconds:02}.{msec}'

    s = f'{hour:02}:{minute:02}:{seconds_str}'
    # print(s)

    return s

# string을 받아서 초의 총합을 반납해줍니다
def calc_total(s):
    a, b, c = s.split(':')
    sum = int(a) * 3600000 + int(b) * 60000 + math.trunc(float(c) * 1000)
    return sum

# 행으로 분리해서 리스트로 반납합니다
def parse_ssa(ssa):
    l = ssa.split('\n')

    return l

def convert(ssa): # written by utylee
    smi = init_smi()
    # print(smi)

    #특정기준으로 ssa를 분리합니다
    # print(ssa)
    full = parse_ssa(ssa)
    # print(full)

    '''
    Dialogue: Marked=01,00:03:32.26,00:03:35.96,Default,,0,0,0,,버지니아주, 폴스 교회새벽 3시 26분
    '''

    # 이전 행 endtime과 다음행 starttime이 같을 경우에는 &nbsp;를 추가하지 않기 위해서입니다
    last_time = 0

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

            starttime_conv = calc_total(starttime)
            endtime_conv = calc_total(endtime)
            # txt의 개행문자를 <br>로 변경합니다
            txt = re.sub(r'\\n', '<br>', txt)

            # print(m.group(1), m.group(2))
            # print(f'{starttime_conv}, {endtime_conv}\n{txt}')

            ''' 
            <SYNC Start=19625><P Class=KRCC>
            밀포드 북쪽 방향에선  미끄럼 사고가<br>
            발생해 교통정체가 이어지고 있습니다.
            <SYNC Start=26525><P Class=KRCC>&nbsp;
            <SYNC Start=42015><P Class=KRCC>
            시간됐습니다.
            '''

            # 이전 자막시간과 간격이 있는 경우는 &nbsp;를 추가합니다
            if (last_time != 0 and last_time != starttime_conv):
                buf +=  f'<SYNC Start={last_time}><P Class=KRCC>&nbsp;\n'

            buf += f'<SYNC Start={starttime_conv}><P Class=KRCC>\n{txt}\n'
            # print(buf)

            last_time = endtime_conv
            smi += buf
    smi += '</BODY>\n</SAMI>'
    # print(smi)

    return smi

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
                    smi_file = codecs.open(os.path.join(p,os.path.splitext(file_name)[0]+SUFFIX+'.smi'),'w',encoding='utf-8')

                    # smi_file.write(convert(ssa))

                    # convert(ssa)
                    # smi_file.write(convert_ssa(ssa),LANG)
                    smi_file.write(convert(ssa))

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
        print('\nworked .smi subtitles:')
        for ssa in success:
            print(ssa)

    if len(fail) > 0:
        print('\nfailed .smi subtitles:')
        for ssa in fail:
            print(ssa)

    if REMOVE_OPTION:
        print('\nworked smi files are removed due to removal option')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

