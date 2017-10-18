import sys
import re


'''<SYNC Start=23112><P Class=ENCC> 
'''


def proc(fname, start_line, end_line):
    full_buf = '' 
    #cur_line = start_line
    #with open("dex.smi", "r+", encoding="cp949") as f:
    with open(fname, "r+", encoding="cp949") as f:
        with open(fname[:-4] + ".edit.smi", "w") as o:
            cur_line = 0
            p = f.readlines()
            if(end_line == -1):
                end_line = len(p)
            assert (end_line >= start_line)
            
            t_flag = 0
            for i in p:
                buf = i
                if((cur_line >= start_line - 1) and (cur_line <=  end_line - 1)):
                    m = re.search('\<SYNC Start=(\d+)\>', i)
                    if(m): 
                        t = m.group(1)
                        s = str(int(t) + diff)
                        buf = re.sub(t, s, buf) 
                full_buf += buf 
                cur_line += 1
            o.write(full_buf)
            #print(o)


if __name__ == "__main__":
    fname = sys.argv[1]
    diff = int(sys.argv[2])
    start_line = 0
    end_line = -1
    try:
        if(sys.argv[3] and sys.argv[4]):
            start_line = int(sys.argv[3])
            end_line = int(sys.argv[4])
    except:
        print('no line argument \n processing full file')
        #import pdb;pdb.set_trace()
    diff = diff * 1000

    print(f'diff: {diff}') 
    print(f'start: {start_line}') 
    proc(fname, start_line, end_line)


