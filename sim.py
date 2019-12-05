import asyncio
import pyperclip
import subprocess
import re
import sys
import requests
import copy


# 's' 옵션을 주면 html을 파싱하여 sample sequence table 의 로테이션을 출력해줍니다 

# 개발중 모드일 때는 pyperclip을 통한 클립보드 복사를 하지 않고 그냥 기존 파일을 통해 합니다
#devel = 1
devel = 0

# 전투시간과 풀버프삭제를 추가할 지를 결정합니다
add_options = 1  
file_report = '/mnt/d/report.html'
seq_num = 35        # sample sequence 표기시 기본 30개만 표현해줍니다
time = 25                # 0일 경우 health 기반 모드로 동작합니다
target_health = 270000

def option_string():
    global add_options
    buff = 0
    # time base일지 target health base 일지에 따라 바뀝니다
    if time:
        #r = '{} {}'.format('max_time={}'.format(time), 'optimal_raid={}'.format(buff)) if add_options else ''
        r = f'max_time={time} optimal_raid={buff}' if add_options else ''
    else:
        r = f'fixed_time=0 override.target_health={target_health} optimal_raid={buff}' if add_options else ''
    return r

# sample sequence 출력 추가 프로세스
def print_sample_sequence():
    #print('sample')
    #print('\n')

    # report html 파일을 열어서 해당문구를 찾아 파싱합니다
    with open(file_report, 'r') as f :
        full = f.readlines()
        num = 0             # 라인넘버를 저장하는 변수입니다
        cond1, cond2, cond3 = 0, 0, 0
        full_br = 0         # loop 탈출 변수
        for l in full:
            if full_br:
                break
            num += 1
            # sample seqence 부분찾기
            m = re.search('Sample Sequence Table', l)
            if m:
                # 해당부터의 리스트로 제한하여 탐색합니다
                frag1 = full[num:]
                frag1_copy = copy.deepcopy(frag1)
                index = 0
                found = 0
                for ll in frag1:
                    m1 = re.search('<td class="right">(.*)</td>', ll)
                    if m1:
                        found += 1
                        m2 = re.search('<td class="left">(.*)</td>', frag1[index+3])
                        skill = m2.group(1)
                        if skill == '&nbsp;':
                            skill = '---wait---'
                        print(f'{m1.group(1)}\t{skill}')
                    index += 1
                    if found >= seq_num:
                        full_br = 1
                        break

def sim_myself(r):

    # 개발모드일 때는 클립보드로부터 파일쓰기를 행하지 않고 기존 파일을 보존해서 작업합니다
    if not devel:
        # 클립보드의 내용을 특정 파일에 기록한후
        with open("/home/utylee/temp/simc/engine/utylee.simc", "w") as f:
            s = pyperclip.paste()
            f.write(s)
    
    # simc를 돌립니다
    # report 출력여부 옵션을 확인합니다
    if (r == 2):
        result = subprocess.check_output(\
            'echo sksmsqnwk11 | sudo -S /home/utylee/temp/simc/engine/simc /home/utylee/temp/simc/engine/utylee.simc {} html=/mnt/d/report.html'.format(option_string()), shell=True)

    elif (r == 3):
        result = subprocess.check_output(\
            f'echo sksmsqnwk11 | sudo -S /home/utylee/temp/simc/engine/simc /home/utylee/temp/simc/engine/utylee.simc {option_string()} html={file_report}', shell=True)


    else:
        result = subprocess.check_output(\
            'echo sksmsqnwk11 | sudo -S /home/utylee/temp/simc/engine/simc /home/utylee/temp/simc/engine/utylee.simc {}'.format(option_string()), shell=True)
    
    # bytes 값을 스트링으로 변환합니다
    result = result.decode()

    print('\n*****************************************************************')
    # 풀 출력
    if(r == 1):
        print(result)
   
    else:
        # DPS에 해당하는 숫자열을 가져와서 표시합니다
        lines = result.split('\n', 31)      # 굳이 전체를 다 파싱하진 않고 31열까지만 파싱합니다
        
        # 새 리스트를 선언합니다
        new_lines = []
        target_num = 0
        
        for i in range(0,30):
            line = lines[i]
            #m = re.search('DPS Ranking', line)
            m = re.search('Player: ', line)
            
            if m:
                #print('line [{}] : {}'.format(i, m.group()))
                print('\n{}'.format(line))
                target_num = i
                break
        
        #찾은 다음열에 원하는 값이 들어있습니다.
        #print('\n{}\n\n{}'.format(lines[i], lines[i+1]))
        print('\n{}\n'.format(lines[i+1]))

        print('*****************************************************************\n')

        # 추가로 t 옵션을 줬을 경우, 샘플 시퀀스를 출력해줍니다
        if (r == 3):
            print_sample_sequence()
        
        #print(new_lines)
        
        #print(' DPS : {} '.format(dps)) 

def sim_him(him):
    '''
    with open("/home/utylee/temp/simc/engine/him.simc", "w") as f:
        s = pyperclip.paste()
        f.write(s)
        '''

    # ,(쉼표) 여부로 외부서버일 경우 분간하여 처리합니다

    r = re.search('(.*)\,(.*)', him)

    # 다른서버일 경우(쉼표있을 경우)
    if (r):
        eng = get_eng_name(r.group(2))
        # 레벨곽 무기레벨을 가져오기 위해 따로 wow 페이지에서 긁어옵니다.
        htm = requests.get('https://worldofwarcraft.com/ko-kr/character/{}/{}'.format(eng, r.group(1)))
        txt = re.search('.*meta\sname=\"description\"\scontent=\"(.*)\"/><meta\sproperty=\"fb', htm.text)
        desc = txt.group(1)
        cmd = 'echo sksmsqnwk11 | sudo -S /home/utylee/temp/simc/engine/simc armory=kr,{},{}'.format(eng, r.group(1))
    # 동일 아즈샤라 서버일 경우
    else:
        htm = requests.get('https://worldofwarcraft.com/ko-kr/character/azshara/{}'.format(him))
        txt = re.search('.*meta\sname=\"description\"\scontent=\"(.*)\"/><meta\sproperty=\"fb', htm.text)
        desc = txt.group(1)
        cmd = 'echo sksmsqnwk11 | sudo -S /home/utylee/temp/simc/engine/simc \
                            armory=kr,azshara,{} {}'.format(him, option_string())

    ''' 
    with open("/home/utylee/temp/simc/engine/web.simc", "w") as f:
        f.write(txt)
    '''

    print('\n*****************************************************************')
    print(desc)
    # simc를 돌립니다
    result = subprocess.check_output(\
            cmd, shell=True)
    
    # bytes 값을 스트링으로 변환합니다
    result = result.decode()

    # DPS에 해당하는 숫자열을 가져와서 표시합니다
    lines = result.split('\n', 31)      # 굳이 전체를 다 파싱하진 않고 31열까지만 파싱합니다
    
    # 새 리스트를 선언합니다
    new_lines = []
    target_num = 0
    
    for i in range(0,30):
        line = lines[i]
        #print(line)
        #m = re.search('DPS Ranking', line)
        m = re.search('Player: ', line)
        
        if m:
            #print('line [{}] : {}'.format(i, m.group()))
            #print('\n{}'.format(line))
            target_num = i
            break
    
    #찾은 다음열에 원하는 값이 들어있습니다.
    # 추가로 wow웹에서 가져온 레벨과 무기레벨 등의 description도 표시합니다
    #print('\n{}\n\n{}'.format(line[i-1], lines[i+1]))
    #print('{}\n{}\n'.format(desc, lines[i+1]))
    print('\n{}\n'.format(lines[i+1]))
    

def get_eng_name(r):
    if (r == '데스윙'):
        name = 'deathwing'
    elif (r == '가로나'):
        name = 'garona'
    elif (r == '굴단'):
        name = 'guldan'
    elif (r == '노르간논'):
        name = 'norgannon'
    elif (r == '달라란'):
        name = 'dalaran'
    elif (r == '듀로탄'):
        name = 'durotan'
    elif (r == '렉사르'):
        name = 'rexxar'
    elif (r == '말퓨리온'):
        name = 'malfurion'
    elif (r == '불타는군단'):
        name = 'burning-legion'
    elif (r == '세나리우스'):
        name = 'cenarius'
    elif (r == '스톰레이지'):
        name = 'stormrage'
    elif (r == '아즈샤라'):
        name = 'azshara'
    elif (r == '알렉스트라자'):
        name = 'alexstrasza'
    elif (r == '와일드해머'):
        name = 'wildhammer'
    elif (r == '윈드러너'):
        name = 'windrunner'
    elif (r == '줄진'):
        name = 'zuljin'
    elif (r == '하이잘'):
        name = 'hyjal'
    elif (r == '헬스크림'):
        name = 'hellscream'

    #print(name)
    return name
    
    
'''
if __name__ == "__main__":

    
    # 파라미터가 변수로 입력되면 그 변수를 넣어주고 그 사람의 전장정보실 정보를 이용해 심크를 돌립니다
    try:
        if (len(sys.argv) > 1):
            sim_him(sys.argv[1])
        else:
            sim_myself()
    except:
        pass

'''

async def main():
    # 파라미터가 변수로 입력되면 그 변수를 넣어주고 그 사람의 전장정보실 정보를 이용해 심크를 돌립니다
    try:
        if (len(sys.argv) == 2):
            if (sys.argv[1] == 'f'):
                sim_myself(1)

            # 출력 후 report 도 기록합니다. html출력을 통해 스킬 로테이션을 살펴보기 위합니다
            elif (sys.argv[1] == 'r'):
                sim_myself(2)

            # html을 파싱하여 sample sequence table 의 로테이션을 출력해줍니다
            elif (sys.argv[1] == 's'):
                sim_myself(3)

            else:
                sim_him(sys.argv[1])
        # 별도의 파라미터없이 클립보드만으로 실행할 경우입니다
        else:
            sim_myself(0)
    except:
        pass
    #print('*****************************************************************\n')



loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()





