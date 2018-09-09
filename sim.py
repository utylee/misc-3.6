import pyperclip
import subprocess
import re
import sys


def sim_myself():
    # 클립보드의 내용을 특정 파일에 기록한후
    
    with open("/home/utylee/temp/simc/engine/utylee.simc", "w") as f:
        s = pyperclip.paste()
        f.write(s)
    
    # simc를 돌립니다
    result = subprocess.check_output(\
            'echo sksmsqnwk11 | sudo -S /home/utylee/temp/simc/engine/simc /home/utylee/temp/simc/engine/utylee.simc', shell=True)
    
    # bytes 값을 스트링으로 변환합니다
    result = result.decode()
    #print(result)
    
    # DPS에 해당하는 숫자열을 가져와서 표시합니다
    lines = result.split('\n', 31)      # 굳이 전체를 다 파싱하진 않고 31열까지만 파싱합니다
    
    # 새 리스트를 선언합니다
    new_lines = []
    target_num = 0
    
    for i in range(0,30):
        line = lines[i]
        m = re.search('DPS Ranking', line)
        
        if m:
            #print('line [{}] : {}'.format(i, m.group()))
            target_num = i
            break
    
    #찾은 다음열에 원하는 값이 들어있습니다.
    print('\n{}'.format(lines[i+1]))
    
    #print(new_lines)
    
    #print(' DPS : {} '.format(dps)) 

def sim_him(him):
    '''
    with open("/home/utylee/temp/simc/engine/him.simc", "w") as f:
        s = pyperclip.paste()
        f.write(s)
        '''
    
    # simc를 돌립니다
    cmd = 'echo sksmsqnwk11 | sudo -S /home/utylee/temp/simc/engine/simc armory=kr,azshara,{}'.format(him)
    #print(cmd)
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
        m = re.search('DPS Ranking', line)
        
        if m:
            #print('line [{}] : {}'.format(i, m.group()))
            target_num = i
            break
    
    #찾은 다음열에 원하는 값이 들어있습니다.
    print('\n{}\n{}'.format(him, lines[i+1]))
    

    
    
if __name__ == "__main__":

    
    # 파라미터가 변수로 입력되면 그 변수를 넣어주고 그 사람의 전장정보실 정보를 이용해 심크를 돌립니다
    if (len(sys.argv) > 1):
        sim_him(sys.argv[1])
    else:
        sim_myself()

'''
    try:
        if (sys.argv[1]):
    except:
        pass
        '''





