import os, time, shutil

#path = 'f:\\down\\'
#path = 'f:/down/'
path = '/Users/utylee/Downloads/'
#target = 'w:\\99-data\\91-transmission-watch\\'
#target = 'w:/99-data/91-transmission-watch'
#target = '/Volumes/3002/99-data/91-transmission-watch/'
target = '/Volumes/clark/4001/99-data/91-transmission-watch/'
#target_media = 'w:/00-MediaWorld'
#target_media = '/Volumes/3002/00-MediaWorld/'
target_media = '/Volumes/clark/4002/00-MediaWorld-4002/'


before = dict([(f, None) for f in os.listdir(path)])

while 1:
    time.sleep(1)
    after = dict([(f, None) for f in os.listdir(path)])
    added = [f for f in after if not f in before]
    removed = [f for f in before if not f in after]
    if added:
        for i in added:
            #if added[0][-7:] == 'torrent' : 
            if i[-7:] == 'torrent' : 
                # .part 파일로서 다운받고 리네임되면서 뭔가 복사에 오류가 생겨 텀을 줘보기로
                time.sleep(2)
                #a = path + "".join(added) 
                a = path + "".join(i) 
                try:
                    shutil.copy(a, target)
                except:
                    continue
                time.sleep(1)
                os.remove(a)
    
            #elif added[0][-3:] == 'smi' or added[0][-3:] == 'srt' :
            elif i[-3:] == 'smi' or i[-3:] == 'srt' :
                # .part 파일로서 다운받고 리네임되면서 뭔가 복사에 오류가 생겨 텀을 줘보기로
                time.sleep(2)
                #a = path + "".join(added) 
                a = path + "".join(i) 
                try:
                    shutil.copy(a, target_media)
                except:
                    continue
                time.sleep(1)
                #smi 파일은 복사후 삭제하지는 않기로..
                #os.remove(a)
        
        before = after

