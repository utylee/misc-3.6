import codecs
import re
import cchardet
import os
import argparse
import asyncio
import time
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
    '''
<SAMI>
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

def convert(srt): # written by utylee
    smi = init_smi()

    #기준으로 srt를 분리합니다
    #print(srt)
    pat = '\d+\s*\r*\n(\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+)\s*\r*\n'   # 괄호로 그룹을 지정해주면 re.split 시에도 결과리스트에 추가됩니다
    result = re.split(pat, srt, flags=re.I)
    # 1부터 시작해서 홀수는 시간, 짝수는 자막 컨텐츠가 들어가 있습니다
    #print(result[0:5])
    del result[0]

    ticktock = 1
    t_start = 0
    t_end = 0
    for l in result:
        # 시간 구간입니다
        if ticktock == 1:
            #print('come')
            #print(l)
            ll = list(map(lambda x:re.split('[:|,]', x), re.split(' --> ', l)))
            #ll = list(map(lambda x:re.split('\W', x), re.split(' --> ', l)))   # \W는 비문자 특수문자를 뜻
            #print(f'll:{ll}')
            t_start = int(ll[0][3]) + (int(ll[0][2])*1000) + (int(ll[0][1])*60000) + (int(ll[0][0])*3600000)
            t_end = int(ll[1][3]) + (int(ll[1][2])*1000) + (int(ll[1][1])*60000) + (int(ll[1][0])*3600000)
            #print(f'stime:{t_start},endtime:{t_end}')
            '''
            time = int(time)
            ms = time%1000
            s = int(time/1000)%60
            m = int(time/1000/60)%60
            h = int(time/1000/60/60)
            '''

            ticktock *= -1
        # 자막 텍스트 구간입니다
        else:
            # \n 은 <br> 로 치환해야합니다
            '''
1
00:02:32,280 --> 00:02:36,569
<i>안녕하십니까
뉴욕 뉴스입니다</i>

<SYNC Start=152280><P Class=KRCC>
<i>안녕하십니까<br>
뉴욕 뉴스입니다</i>
<SYNC Start=156569><P Class=KRCC>&nbsp;
            '''
            # \r가 사용된 파일일 경우 \n 대신 \r\n 으로 취급합니다
            if '\r' in l:
                l = l[:-4]      
                l = re.sub('\r\n', '<br>\n', l, flags=re.I)
                smi += '<SYNC Start=' + str(t_start) + '><P Class=KRCC>\n' + l + '\n<SYNC Start=' + \
                            str(t_end) + '><P Class=KRCC>&nbsp;\n'

            else:
                l = l[:-2]      # 마지막의 \n\n을 제거한 후
                #l.replace('\n', '<br>')    # \n을 <br> 로 대치합니다
                l = re.sub('\n', '<br>\n', l, flags=re.I)
                smi += '<SYNC Start=' + str(t_start) + '><P Class=KRCC>\n' + l + '\n<SYNC Start=' + \
                            str(t_end) + '><P Class=KRCC>&nbsp;\n'
            ticktock *= -1
    #print(len(result))
    smi += '</BODY>\n</SAMI>'

    return smi

async def main():
    print('media library path:', PATH)
    success=[]
    fail=[]
    print('finding and converting started...')
    for p,w,f in os.walk(PATH):
        for file_name in f:
            if file_name[-4:].lower()=='.srt':
                print('processing %s' %os.path.join(p,file_name))
                try:
                    with open(os.path.join(p,file_name),'rb') as srt_file:
                        srt_raw = srt_file.read()
                        encoding = cchardet.detect(srt_raw)
                    srt = srt_raw.decode(encoding['encoding'], errors=DECODE_ERRORS)
                    smi_file = codecs.open(os.path.join(p,os.path.splitext(file_name)[0]+SUFFIX+'.smi'),'w',encoding='utf-8')
                    #smi_file.write(convert(parse(srt),LANG))
                    smi_file.write(convert(srt))
                    success.append(file_name)
                    if REMOVE_OPTION:
                        os.remove(os.path.join(p,file_name))
                except:
                    fail.append(file_name)

    srt_list = list(set(success) | set(fail))
    print('\nfound .srt subtitles:')
    for srt in srt_list:
        print(srt)

    if len(success) > 0:
        print('\nworked .smi subtitles:')
        for srt in success:
            print(srt)

    if len(fail) > 0:
        print('\nfailed .smi subtitles:')
        for srt in fail:
            print(srt)

    if REMOVE_OPTION:
        print('\nworked smi files are removed due to removal option')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

