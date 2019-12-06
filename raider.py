import aiohttp
import asyncio
#import wow_korean_server
from blizzard_trans import *
import sys
import re

#url = 'https://raider.io/api/v1/characters/profile?region=kr&realm=azshara&name=유타일리&fields=mythic_plus_scores,mythic_plus_recent_runs,mythic_plus_best_runs,mythic_plus_ranks,mythic_plus_highest_level_runs'

def k(e):
    return get_kor_dg_name(e)

def up_num(n):
    ret = ''
    if n == 1:    
        ret = '+'
    elif n == 2:    
        ret = '++'
    elif n == 3:    
        ret = '+++'
    else:
        ret = ''
    return ret

def parse_name(n):
    # ,(쉼표) 여부로 외부서버일 경우 분간하여 처리합니다
    a = b = ''
    r = re.search('(.*)\,(.*)', n)

    # 다른서버일 경우(쉼표있을 경우)
    if (r):
        a = r.group(1)
        b = get_eng_name(r.group(2))

    # 동일 아즈샤라 서버일 경우
    else:
        a = n
        b = 'azshara'
    return a, b


async def main():

    # 아규먼트를 분석합니다

    target = ''
    me = '유타일리'         # 기본 아이디는 유타일리(드루이드)로 합니다
    if(len(sys.argv) <= 1):
        target = me
    else:
        target = sys.argv[1]

    await proc(target)

async def proc(a):
    nm, rm = parse_name(a)      # 서버와 이름을 분리해서 변수에 저장합니다
    cls = pro = ''               # 직업과 전문화 변수입니다
    lvl = 0

    # Blizzard에서 아이템 레벨을 가져옵니다
    async with aiohttp.ClientSession() as session:
        url = f'https://worldofwarcraft.com/ko-kr/character/{rm}/{nm}'
        async with session.get(url) as response:
            html = await response.text()
            txt = re.search('.*meta\sname=\"description\"\scontent=\"(.*)\"/><meta\sproperty=\"fb', html)
            l = re.search('\s(\w+)\s(\w+),\s(\d*)레벨',txt.group(1))
            pro = l.group(1)
            cls = l.group(2)
            lvl = l.group(3)
            #print(l.group(1))
            #print(l.group(2))
            #print(l.group(3))
            #print(txt.group(1))

    # raider.io 에서 정보를 가져와서 처리합니다
    recent = ''
    up = ''
    async with aiohttp.ClientSession() as session:
        url = f'https://raider.io/api/v1/characters/profile?region=kr&realm={rm}&name={nm}&fields=mythic_plus_scores,mythic_plus_recent_runs,mythic_plus_best_runs,mythic_plus_ranks,mythic_plus_highest_level_runs'
        async with session.get(url) as response:
            #html = await response.text()
            json = await response.json()
            #print(html[:100])
            #print(json['mythic_plus_ranks'])
            recent = json['mythic_plus_recent_runs']
            best = json['mythic_plus_best_runs']
            highest = json['mythic_plus_highest_level_runs']
            hnum = up_num(highest[0]['num_keystone_upgrades']) if highest else ''

            #print(json['mythic_plus_recent_runs'][0])
            bnum = up_num(best[0]['num_keystone_upgrades']) if best else ''
            bnum1 = up_num(best[1]['num_keystone_upgrades']) if len(best) > 2 else '' 
            bnum2 = up_num(best[2]['num_keystone_upgrades']) if len(best) > 3 else '' 
            #bnum2 = 'sex' if len(best) > 2 else '' 
            num = up_num(recent[0]['num_keystone_upgrades']) if recent else ''
            num1 = up_num(recent[1]['num_keystone_upgrades']) if len(best) > 2 else '' 
            num2 = up_num(recent[2]['num_keystone_upgrades']) if len(best) > 3 else '' 

            name = json['name']
            active_spec = json['active_spec_role']
            realm = get_kor_name(json['realm'])

            # 아이디 정보등을 표시합니다
            if realm == '아즈샤라':
                print(f'{name}({lvl},{active_spec},{pro}{cls})')
            else:
                print(f'{name}({lvl},{active_spec},{pro}{cls}) - {realm}')
            print(json['mythic_plus_scores']['all'])
            print(f'{highest[0]["mythic_level"]}{hnum} / {best[0]["mythic_level"]}{bnum} / {recent[0]["mythic_level"]}{num}') if highest and best and recent else '' 
            '''
            print(f'{k(highest[0]["dungeon"])}\t{highest[0]["mythic_level"]}{hnum}')
            print(f'{k(best[0]["dungeon"])}\t{best[0]["mythic_level"]}{bnum}')
            print(f'{k(best[1]["dungeon"])}\t{best[1]["mythic_level"]}{bnum1}')
            print(f'{k(best[2]["dungeon"])}\t{best[2]["mythic_level"]}{bnum2}')
            print(f'{k(recent[0]["dungeon"])}\t{recent[0]["mythic_level"]}{num}')
            #print(recent[1]['dungeon'])
            '''

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
