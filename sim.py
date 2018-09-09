import pyperclip
import subprocess
import re

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



