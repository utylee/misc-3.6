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


def parse(smi): # smi parsing algorithm written in PYSAMI by g6123 (https://github.com/g6123/PySAMI)
    search = lambda string, pattern: re.search(pattern, string, flags=re.I)
    tags = re.compile('<[^>]+>')

    def split_content(string, tag):
        threshold = '<'+tag

        if tag is 'p':
            standard = threshold + ' Class=' + LANG + '>'
            if standard.upper() not in string.upper():
                idx = string.find('>') + 1
                string = string[:idx] + standard + string[idx:]

        return list(map(
            lambda item: (threshold+item).strip(),
            re.split(threshold, string, flags=re.I)
        ))[1:]

    def remove_tag(matchobj):
        matchtag = matchobj.group().lower()
        keep_tags = ['font', 'b', 'i', 'u']
        for keep_tag in keep_tags:
            if keep_tag in matchtag:
                return matchtag
        return ''

    def parse_p(item):
        lang = search(item, '<p(.+)class=([a-z]+)').group(2)
        content = item[search(item, '<p[^>]+>').end():]
        content = content.replace('\r', '')
        content = content.replace('\n', '')
        content = re.sub('<br ?/?>', '\n', content, flags=re.I)
        content = re.sub('<[^>]+>', remove_tag, content)
        return [lang, content]

    data = []

    try:
        for item in split_content(smi, 'sync'):
            pattern = search(item, '<sync start=([0-9]+)')
            if pattern!=None:
                timecode = pattern.group(1)
                content = dict(map(parse_p, split_content(item, 'p')))
                data.append([timecode, content])
    except:
        print('Conversion ERROR: maybe this file is not supported.')
    
    return data

def convert(data, lang): # written by ncianeo
    if lang not in data[0][1].keys():
        print('lang: %s is not found. will use the first lang in the smi file.' %lang)
        i=0
        while True:
            try:
                lang = list(data[i][1].keys())[0]
                break
            except:
                i+=1
        print('chosen lang: %s' %lang)
    def ms_to_ts(time):
        time = int(time)
        ms = time%1000
        s = int(time/1000)%60
        m = int(time/1000/60)%60
        h = int(time/1000/60/60)
        return (h,m,s,ms)
    srt=''
    sub_nb = 1
    for i in range(len(data)-1):
        try:
            if i>0:
                if data[i][0]<data[i-1][0]:
                    continue
            if data[i][1][lang]!='&nbsp;':
                srt+=str(sub_nb)+'\n'
                sub_nb+=1
                if int(data[i+1][0])>int(data[i][0]):
                    srt+='%02d:%02d:%02d,%03d' %ms_to_ts(data[i][0])+' --> '+'%02d:%02d:%02d,%03d\n' %ms_to_ts(data[i+1][0])
                else:
                    srt+='%02d:%02d:%02d,%03d' %ms_to_ts(data[i][0])+' --> '+'%02d:%02d:%02d,%03d\n' %ms_to_ts(int(data[i][0])+1000)
                srt+=data[i][1][lang]+'\n\n'
        except:
            continue
    return srt

print('media library path:', PATH)
success=[]
fail=[]
print('finding and converting started...')
for p,w,f in os.walk(PATH):
    for file_name in f:
        if file_name[-4:].lower()=='.smi':
            print('processing %s' %os.path.join(p,file_name))
            try:
                with open(os.path.join(p,file_name),'rb') as smi_file:
                    smi_raw = smi_file.read()
                    encoding = cchardet.detect(smi_raw)
                smi = smi_raw.decode(encoding['encoding'], errors=DECODE_ERRORS)
                srt_file = codecs.open(os.path.join(p,os.path.splitext(file_name)[0]+SUFFIX+'.srt'),'w',encoding='utf-8')
                srt_file.write(convert(parse(smi),LANG))
                success.append(file_name)
                if REMOVE_OPTION:
                    os.remove(os.path.join(p,file_name))
            except:
                fail.append(file_name)

smi_list = list(set(success) | set(fail))
print('\nfound .smi subtitles:')
for smi in smi_list:
    print(smi)

print('\nworked .smi subtitles:')
for smi in success:
    print(smi)

print('\nfailed .smi subtitles:')
for smi in fail:
    print(smi)

if REMOVE_OPTION:
    print('\nworked smi files are removed due to removal option')
