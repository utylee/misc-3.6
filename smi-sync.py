import sys
import re


'''<SYNC Start=23112><P Class=ENCC> 
'''
# Usage : smi-sync filename +-sec startline(0) endline(-1)

def proc(fname, start_line, end_line):
    full_buf = '' 
    #cur_line = start_line
    #with open("dex.smi", "r+", encoding="cp949") as f:

    '''utf-8로open 시도해보고 실패시 cp949로 오픈합니다'''
    try:
        print('trying open by utf8 codec')
        f = open(fname, 'r+')
        p = f.readlines()
    except:
        print('failed!\n ')
        print('trying open by cp949 codec')
        f = open(fname, "r+", encoding="cp949")
        p = f.readlines()
    else:
        pass

    #o = open(fname, 'r+') 
    #p = f.readlines()
    with f:
        #with open(fname[:-4] + '.edit.smi', 'w') as o:
            cur_line = 0
            if(end_line == -1):
                end_line = len(p)
            assert (end_line >= start_line)
            
            t_flag = 0
            for i in p:
                buf = i
                if((cur_line >= start_line - 1) and (cur_line <=  end_line - 1)):
                    m = re.search('\<sync start=(\d+)\>', i.lower())
                    if(m): 
                        t = m.group(1)
                        s = str(int(t) + diff)
                        buf = re.sub(t, s, buf) 
                full_buf += buf 
                cur_line += 1
            f.seek(0)
            f.truncate()
            f.write(full_buf)
            #o.write(full_buf)
            #print(o)


if __name__ == "__main__":
    fname = sys.argv[1]
    diff = float(sys.argv[2])
    start_line = 0
    end_line = -1
    try:
        if(sys.argv[3] and sys.argv[4]):
            start_line = int(sys.argv[3])
            end_line = int(sys.argv[4])
    except:
        print('no line argument \n processing full file')
        #import pdb;pdb.set_trace()
    diff = int(diff * 1000)

    print(f'diff: {diff}') 
    print(f'start: {start_line}') 
    proc(fname, start_line, end_line)


