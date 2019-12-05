import aiohttp
import asyncio

#url = 'https://raider.io/characters/kr/azshara/%EC%9C%A0%ED%83%80%EC%9D%BC%EB%A6%AC'
#url = 'https://raider.io/api/v1/characters/profile?name=%EC%9C%A0%ED%83%80%EC%9D%BC%EB%A6%AC&region=kr&realm=azshara'

url = 'https://raider.io/api/v1/characters/profile?region=kr&realm=azshara&name=유타일리&fields=mythic_plus_scores,mythic_plus_recent_runs,mythic_plus_best_runs,mythic_plus_ranks,mythic_plus_highest_level_runs'

def k(e):
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

async def main():
    recent = ''
    up = ''
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            #html = await response.text()
            json = await response.json()
            #print(html[:100])
            #print(json['mythic_plus_ranks'])
            recent = json['mythic_plus_recent_runs']
            best = json['mythic_plus_best_runs']
            highest = json['mythic_plus_highest_level_runs']
            hnum = up_num(highest[0]['num_keystone_upgrades'])

            #print(json['mythic_plus_recent_runs'][0])
            bnum = up_num(best[0]['num_keystone_upgrades'])
            bnum1 = up_num(best[1]['num_keystone_upgrades'])
            bnum2 = up_num(best[2]['num_keystone_upgrades'])
            num = up_num(recent[0]['num_keystone_upgrades'])
            num1 = up_num(recent[1]['num_keystone_upgrades'])
            num2 = up_num(recent[2]['num_keystone_upgrades'])

            name = json['name']
            active_spec = json['active_spec_role']
            realm = json['realm']
            print('\n')

            # 아이디 정보등을 표시합니다
            print(f'{name}({active_spec}) - {realm}')
            print(json['mythic_plus_scores']['all'])
            print(f'{highest[0]["mythic_level"]}{hnum} / {best[0]["mythic_level"]}{bnum} / {recent[0]["mythic_level"]}{num}')
            print('\n')
            print(f'{k(highest[0]["dungeon"])}\t{highest[0]["mythic_level"]}{hnum}')
            print('\n')
            print(f'{k(best[0]["dungeon"])}\t{best[0]["mythic_level"]}{bnum}')
            print(f'{k(best[1]["dungeon"])}\t{best[1]["mythic_level"]}{bnum1}')
            print(f'{k(best[2]["dungeon"])}\t{best[2]["mythic_level"]}{bnum2}')
            print('\n')
            print(f'{k(recent[0]["dungeon"])}\t{recent[0]["mythic_level"]}{num}')
            #print(recent[1]['dungeon'])


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
