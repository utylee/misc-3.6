import sys
import re


'''<SYNC Start=23112><P Class=ENCC> 
'''
# Usage : srt-sync filename +-sec startline(0) endline(-1)

diff = 0

def proc(fname, start_line, end_line):
    full_buf = '' 
    #cur_line = start_line
    #with open("dex.smi", "r+", encoding="cp949") as f:

    '''utf-8로open 시도해보고 실패시 cp949로 오픈합니다'''
    try:
        print('trying open with utf8 codec')
        f = open(fname, 'r+')
        p = f.readlines()
    except:
        print('failed!\n ')
        print('trying open with cp949 codec')
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
                    #m = re.search('\<sync start=(\d+)\>', i.lower())
                    m = re.search('(\d+)\:(\d+):(\d+),(\d+) --> (\d+)\:(\d+):(\d+),(\d+)', i.lower())
                    if(m): 
                        # 각행의 시작/끝 시분초를 각각 할당합니다
                        a1 = int(m.group(1))
                        a2 = int(m.group(2))
                        a3 = int(m.group(3))
                        a4 = int(m.group(4))
                        a3 = a3 * 1000 + a4
                        b1 = int(m.group(5))
                        b2 = int(m.group(6))
                        b3 = int(m.group(7))
                        b4 = int(m.group(8))
                        b3 = b3 * 1000 + b4
                        #print(a1+a2+a3+b1+b2+b3)

                        # 초를 조작후 0보다 작거나 60(60000ms)보다 클 경우 시분까지 연쇄적으로 변경합니다
                        a3 = a3 + diff
                        if a3 >= 60000:
                            a3 = a3 - 60000
                            a2 = a2 + 1
                            if a2 >= 60:
                                a2 = a2 - 60
                                a1 = a1 + 1
                        elif a3 < 0:
                            a3 = a3 + 60000
                            a2 = a2 - 1
                            if a2 < 0:
                                a2 = a2 + 60
                                a1 = a1 - 1
                                # 시간을 빼줄경우는 별도로 0시 이하는0으로 해줘야 합니다
                                if a1 < 0:
                                    a1 = 0

                        b3 = b3 + diff
                        if b3 >= 60000:
                            b3 = b3 - 60000
                            b2 = b2 + 1
                            if b2 >= 60:
                                b2 = b2 - 60
                                b1 = b1 + 1
                        elif b3 < 0:
                            b3 = b3 + 60000
                            b2 = b2 - 1
                            if b2 < 0:
                                b2 = b2 + 60
                                b1 = b1 - 1
                                # 시간을 빼줄경우는 별도로 0시 이하는0으로 해줘야 합니다
                                if b1 < 0:
                                    b1 = 0
                        result_str = str(a1).zfill(2) + ':' + str(a2).zfill(2) + ':' + \
                                str(int(a3/1000)).zfill(2) + ',' + str(a3%1000).zfill(3)  \
                                + ' --> ' + str(b1).zfill(2) + ':' + str(b2).zfill(2) + ':' + \
                                str(int(b3/1000)).zfill(2) + ',' + str(b3%1000).zfill(3) + '\n'
                        buf = result_str
                        #print(result_str)
                        #return
                        # srt 개발중이라 탈출하도록 합니다
                        
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
    #diff = int(diff)

    print(f'diff: {diff}') 
    print(f'start: {start_line}') 
    proc(fname, start_line, end_line)


