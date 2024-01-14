import sys
import asyncio
import codecs
import re
import cchardet
import os
import argparse

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

def convert(srt): # written by utylee
    ssa = init_ssa() + '\n'

    #기준으로 srt를 분리합니다
    #print(srt)
    pat = '\d+\s*\r*\n(\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+)\s*\r*\n'   # 괄호로 그룹을 지정해주면 re.split 시에도 결과리스트에 추가됩니다
    result = re.split(pat, srt, flags=re.I)
    # 1부터 시작해서 홀수는 시간, 짝수는 자막 컨텐츠가 들어가 있습니다
    #print(result[0:5])
    del result[0]
    #print(result)
    #return 

    ticktock = 1
    l_start = []
    l_end = []
    for l in result:
        # 시간 구간입니다
        if ticktock == 1:
            #print('come')
            #print(l)
            ll = list(map(lambda x:re.split('[:|,]', x), re.split(' --> ', l)))
            #ll = list(map(lambda x:re.split('\W', x), re.split(' --> ', l)))   # \W는 비문자 특수문자를 뜻
            #print(f'll:{ll}')

            l_start = ll[0]
            l_end = ll[1]
            #print(f'l_time:{l_start},l_end:{l_end}')

            ticktock *= -1
        # 자막 텍스트 구간입니다
        else:
            # \n 은 <br> 로 치환해야합니다
            '''
1
00:02:32,280 --> 00:02:36,569
<i>안녕하십니까
뉴욕 뉴스입니다</i>

'''
            cur_ssa = ''
            #print('im here')
            #print(f'l_start:{l_start},l_end:{l_end}')
            cur_ssa += 'Dialogue: Marked=01,%01d:%02d:%02d.%02d' % (int(l_start[0]), int(l_start[1]), int(l_start[2]), int(int(l_start[3])/10)) \
                        + ',%01d:%02d:%02d.%02d,Default,,0,0,0,,' % (int(l_end[0]), int(l_end[1]), int(l_end[2]), int(int(l_end[3])/10)) 

            #content = content.replace('\r', '')
            #content = content.replace('\n', '')
            #content = re.sub('<br ?/?>', '\\N', content, flags=re.I)
            #content = re.sub('<[^>]+>', remove_tag, content)
            l = re.sub('<i>', r'{\\i1}', l, flags=re.I)
            l = re.sub('</i>', r'{\\i0}', l, flags=re.I)
            # i를 제외한 font나 b태그 등은 모두 지우기로 합니다
            l = re.sub('<[^>]+>', '', l, flags=re.I)

            # \r가 사용된 파일일 경우 \n 대신 \r\n 으로 취급합니다
            if '\r' in l:
                # \r\n 들 사이에 공백이 있는 경우가 있었습니다  
                #l = l[:-4]      
                l = l.rstrip('\r\n ')   # 이 세문자를오른쪽에서부터 다른문제발생까지모두삭제
                l = re.sub('\r\n', r'\\N', l, flags=re.I)
                cur_ssa += l

            else:
                #l = l[:-2]      # 마지막의 \n\n을 제거한 후
                #l.replace('\n', '<br>')    # \n을 <br> 로 대치합니다
                l = l.rstrip('\n ')   # 이 세문자를오른쪽에서부터 다른문제발생까지모두삭제
                l = re.sub('\n', r'\\N', l, flags=re.I)
                cur_ssa += l

            # 현재 라인을 출력합니다
            # print(cur_ssa)
            ssa += cur_ssa + '\n'

            ticktock *= -1
    #print(len(result))

    #print(ssa)
    return ssa


def init_ssa():
    s = '''[Script Info] 
; Script generated by utyleesubs
WrapStyle: 0
ScaledBorderAndShadow: yes
Collisions: Normal
ScriptType: v4.0

[V4 Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding
Style: Default,Arial,26.0,16777215,255,0,0,0,0,1,1.5,0.0,2,10,10,10,0,1

[Events]
Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text'''
    return s


async def main():
    ssa = init_ssa()
    #print(ssa)
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
                    # print(f'1: {encoding}')
                    # srt = srt_raw.encode('utf-8')
                    # print('2')

                    # dos encoding srt 파일에서 exception이 발생하는 문제가 있었습니다.
                    # https://stackoverflow.com/a/51351417 해당 해법을 적용해보니 통과가
                    # 되었습니다
                    # srt = srt_raw.decode(encoding['encoding'], errors=DECODE_ERRORS)
                    srt = srt_raw.decode(encoding['encoding'], errors='replace')
                    # print('3')
                    ssa_file = codecs.open(os.path.join(p,os.path.splitext(file_name)[0]+SUFFIX+'.ssa'),'w',encoding='utf-8')
                    #ssa_file.write(convert_ssa(parse(smi),LANG))
                    #convert(srt)
                    # print('4')
                    ssa_file.write(convert(srt))
                    success.append(file_name)
                    if REMOVE_OPTION:
                        os.remove(os.path.join(p,file_name))
                except Exception as e:
                    fail.append(file_name)
                    print(f'excepted by: \n {e}')

    srt_list = list(set(success) | set(fail))
    print('\nfound .srt subtitles:')
    for srt in srt_list:
        print(srt)

    if len(success) > 0:
        print('\nworked .srt subtitles:')
        for srt in success:
            print(srt)

    if len(fail) > 0:
        print('\nfailed .srt subtitles:')
        for srt in fail:
            print(srt)

    if REMOVE_OPTION:
        print('\nworked srt files are removed due to removal option')


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

#with loop:
    #sys.exit(loop.run_until_complete(main()))
