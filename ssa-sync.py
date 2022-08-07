import sys
import re
import math

'''

Dialogue: Marked=01,0:43:30.87,0:43:37.50,Default,,0,0,0,,어쩌면.. 그건 내가 아닐지도 몰라요

'''
# Usage : smi-sync filename +-sec starttime('00:00:00') endtime(-1)
#           if range specified two argument all must included
#               : no! if one starttime there, endtime is -1 automatically


# string을 받아서 초의 총합을 반납해줍니다
def calc_total(s):
    a, b, c = s.split(':')
    sum = int(a) * 360000 + int(b) * 6000 + math.trunc(float(c) * 100)
    return sum

# 숫자를 받아서 00:00:00 포맷으로 분해합니다
def format_total(i):
    i, msec = divmod(int(i), 100)

    hour, minute = divmod(i, 3600)
    minute, seconds = divmod(minute, 60)
    seconds_str = f'{seconds:02}.{msec}'

    s = f'{hour:02}:{minute:02}:{seconds_str}'
    # print(s)

    return s

# 00:00:00.000 형식의 시간을 처리하는 함수입니다
# 초의 총합(x100을 해서 소수둘째까지 포함)을 구하고 다시 나누는 방식으로 계산해봅니다
def proc_time(s, diff):
    # hour, minute, seconds = s.split(':')

    # 소수점을 자꾸 반올림하는 미세한 오차가 발생하여 numpy사용없이 하려고 
    #       math까지 동원하였습니다
    # total = 360000 * int(hour) + 6000 * int(minute) + math.trunc(float(seconds) * 100)

    # total = int(total * 100)

    # print('\n')
    print(f'diff:{diff}')
    # print(s)
    # print(f'total: {total} msec')

    # result = round(float(seconds) + float(diff), 2)
    # result = total + diff * 100 
    result = s + diff
    result, msec = divmod(result, 100)

    # 다시 00:00:00 포맷으로 분해합니다
    hour, minute = divmod(result, 3600)
    minute, seconds = divmod(minute, 60)
    seconds_str = f'{seconds:02}.{msec}'

    # s = ':'.join((str(hour), str(minute), seconds_str)) 
    s = f'{hour:02}:{minute:02}:{seconds_str}'

    print(s)

    return s



    ''' 
    # 소수점 과 정수부를 나눠서 계산합니다. 나중에 몫계산시 무한소수점방지
    s_result = str(result)
    s_result_n, s_result_f = s_result.split('.')
    print(s_result_n, s_result_f)

    #60으로 나눈 몫과 나머지를 구합니다
    # 분과 시간에 대해서도 미리 처리해놓습니다
    # d, r = divmod(result, 60)
    d, r = divmod(int(s_result_n), 60)
    d1, r1 = divmod(d, 60)

    seconds = str(r) + '.' + s_result_f
    minute = int(minute) + int(r1)
    hour = int(hour) + int(d1)

    # s = ':'.join((str(hour), str(minute), str(seconds))) 
    s = ':'.join((str(hour), str(minute), seconds)) 

    print(s)

    return s 
    '''


# def proc(fname, start_line, end_line):
def proc(fname, from_time, until_time):
    full_buf = '' 
    # 시작시간을 총량으로 변환해둡니다
    from_time = calc_total(from_time)
    until_time = calc_total(until_time)

    #cur_line = start_line

    '''utf-8로open 시도해보고 실패시 cp949로 오픈합니다'''
    try:
        print('trying open with utf8 codec')
        f = open(fname, 'r+')
        # f = open(fname, 'r')
        p = f.readlines()
    except:
        print('failed!\n ')
        print('trying open with cp949 codec')
        f = open(fname, "r+", encoding="cp949")
        # f = open(fname, "r", encoding="cp949")
        p = f.readlines()
    else:
        pass

    #o = open(fname, 'r+') 
    #p = f.readlines()
    with f:
        #with open(fname[:-4] + '.edit.smi', 'w') as o:
            cur_line = 0
            # if(end_line == -1):
                # end_line = len(p)
            # assert (end_line >= start_line)
            assert (until_time >= from_time)
            
            t_flag = 0
            '''
                Dialogue: Marked=01,0:43:30.87,0:43:37.50,Default,,0,0,0,,어쩌면.. 그건 내가 아닐지도 몰라요
            '''
            for i in p:
                buf = i

                # if((cur_line >= start_line - 1) and (cur_line <=  end_line - 1)):


                # 각 행에서 시간 부분을 추출합니다
                m = re.search('marked=01,(.*),default', i.lower())
                if(m): 
                    # 시작시간, 종료시간으로 분리합니다
                    target_string = m.group(1)
                    # o = re.search('(.*),(.*)', n)
                    # if(o):
                    #     starttime = o.group(1)
                    #     endtime = o.group(2)

                    # 둘다 같은 결과를 가져옵니다 re 모듈 사용여부
                    # starttime, endtime = re.split(',', n)
                    starttime, endtime = target_string.split(',')

                    starttime_con = calc_total(starttime)
                    endtime_con = calc_total(endtime)

                    # 기준 시간보다 클 경우 변환을 시도합니다
                    if (from_time <= starttime_con and until_time >= starttime_con):
                        # print(f'range:: {starttime}-{endtime}')

                        # proc_time 함수를 안쓰고 분해해서 쓰기로 합니다
                        # starttime = proc_time(starttime_con, diff)
                        # endtime = proc_time(endtime_con, diff)

                        starttime = format_total(starttime_con + diff)
                        endtime = format_total(endtime_con + diff)

                        buf = re.sub(target_string, f'{starttime},{endtime}', i) 
                        # print(buf)

                full_buf += buf 
                cur_line += 1
            f.seek(0)
            f.truncate()
            f.write(full_buf)


if __name__ == "__main__":
    fname = sys.argv[1]
    diff = float(sys.argv[2])
    # start_line = 0
    # end_line = -1
    from_time = '0:00:00'
    until_time = '09:00:00'
    # until_time = -1
    try:
        # if(sys.argv[3] and sys.argv[4]):
            # start_line = int(sys.argv[3])
            # end_line = int(sys.argv[4])

        # if (sys.argv[3]):

        if (len(sys.argv) >= 4):
            from_time = sys.argv[3]
            if (len(sys.argv) == 5):
                until_time = sys.argv[4]
                if (until_time == '-1'):
                    until_time = '09:00:00'
    except:
        print('no line argument \n processing full file')
        #import pdb;pdb.set_trace()
    # diff = int(diff * 1000)
    # ssa는 일반적으로 밀리세컨드 즉 소수 둘째자리까지 보존합니다
    diff = int(diff * 100)

    print(f'diff: {diff}') 
    # print(f'start: {start_line}') 
    print(f'start: {from_time}') 
    # proc(fname, start_line, end_line)
    proc(fname, from_time, until_time)


