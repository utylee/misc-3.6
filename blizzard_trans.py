# 종족 번역함수입니다
def get_kor_rc_name(e):
    e = e.lower()
    ret = ''
    if e == 'blood elf':
        ret = '블엘'
    elif e == 'tauren':
        ret = '타우렌'
    elif e == 'human':
        ret = '인간'
    elif e == 'undead':
        ret = '언데드'
    elif e == 'goblin':
        ret = '고블린'
    elif e == 'pandaren':
        ret = '판다렌'
    elif e == 'orc':
        ret = '오크'
    elif e == 'troll':
        ret = '트롤'
    elif e == 'zandalari troll':
        ret = '잔달라트롤'
    else:
        ret = e

    return ret

def get_kor_dg_name(e):
    #e = e.lower()
    ret = ''
    if e == 'Shrine of the Storm':
        ret = '폭풍의 사원'
    elif e == "Kings' Rest":
        ret = '왕들의 안식처'
    elif e == "Temple of Sethraliss":
        ret = '세스랄리스 사원'
    elif e == "The MOTHERLODE!!":
        ret = '왕노다지 광산'
    elif e == "Siege of Boralus":
        ret = '보랄러스 공성전'
    elif e == "Freehold":
        ret = '자유지대'
    else:
        ret = e

    return ret
def get_kor_name(r):
    r = r.lower()
    name = ''
    if (r == 'deathwing'):
        name = '데스윙'
    elif (r == 'garona'):
        name = '가로나'
    elif (r == 'guldan'):
        name = '굴단'
    elif (r == 'norgannon'):
        name = '노르간논'
    elif (r == 'dalaran'):
        name = '달라란'
    elif (r == 'durotan'):
        name = '듀로탄'
    elif (r == 'rexxar'):
        name = '렉사르'
    elif (r == 'malfurion'):
        name = '말퓨리온'
    elif (r == 'burning'):
        name = '불타는군단-legion'
    elif (r == 'cenarius'):
        name = '세나리우스'
    elif (r == 'stormrage'):
        name = '스톰레이지'
    elif (r == 'azshara'):
        name = '아즈샤라'
    elif (r == 'alexstrasza'):
        name = '알렉스트라자'
    elif (r == 'wildhammer'):
        name = '와일드해머'
    elif (r == 'windrunner'):
        name = '윈드러너'
    elif (r == 'zuljin'):
        name = '줄진'
    elif (r == 'hyjal'):
        name = '하이잘'
    elif (r == 'hellscream'):
        name = '헬스크림'
    #print(name)
    return name

def get_eng_name(r):
    name = ''
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

