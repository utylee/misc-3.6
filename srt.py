import sys
import os
import codecs
import re
import cchardet

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


#def convert(data, lang): 
def convert(data): 
    #if lang not in data[0][1].keys():
    print(f'will use the first lang in the smi file.')
    lang = ''
    i = 0
    while True:
        try:
            lang = list(data[i][1].keys())[0]
            break
        except:
            i+=1
    print(f'chosen lang: {lang}')
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

if __name__ == "__main__":
    success=[]
    fail=[]
    file_name = sys.argv[1]
    new_name = ''
    if file_name[-4:].lower()=='.smi':
        print(f'processing {file_name}')
        try:
            #with open(os.path.join(p,file_name),'rb') as smi_file:
            with open(file_name,'rb') as smi_file:
                smi_raw = smi_file.read()
                encoding = cchardet.detect(smi_raw)
            print('1')
            print(encoding)
            #smi = smi_raw.decode(encoding['encoding'], errors=DECODE_ERRORS)
            smi = smi_raw
            print('1')
            new_name = file_name[:-4] + '.srt'
            print(new_name)
            srt_file = codecs.open(file_name[:-4] + '.srt','w',encoding='utf-8')
            srt_file.write(convert(parse(smi)))
            success.append(file_name)
            print('end')
        except:
            print('exception')
            fail.append(file_name)
