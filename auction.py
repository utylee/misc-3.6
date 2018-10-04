import asyncio
import requests
import json
import pycurl


myapi = 'm5u8gdp6qmhbjkhbht3ax9byp62wench'
server = '아즈샤라'
locale = 'ko_KR'

async def proc():
    #battle dev api 로서 api key를 사용해 일단 json 주소를 전송받습니다
    url = 'https://kr.api.battle.net/wow/auction/data/{}?locale={}&apikey={}'.format(server, locale, myapi)

    # .loads 함수인 것을 봅니다. s가 없는 load 함수는 파일포인터를 받더군요
    print('json주소를 받아옵니다')
    load = json.loads(requests.get(url).text)
    js = load['files'][0]['url']

    print('주소:{} \n로부터 json 덤프 파일을 다운로드합니다...\n'.format(js))
    #get_item(95416) #하늘골렘

    # 받아온 json에 옥션 json 파일의 주소를 포함한 리스폰스를 보내줍니다. 해당 주소를 curl로 바이트다운받습니다.
    #requests로 웹페이지로 읽어오니 속도가 너무 느려 이 방법을 사용해보기로 합니다
    c = pycurl.Curl()

    with open("auction.json", "wb") as f:
        c.setopt(c.URL, js)
        c.setopt(c.WRITEDATA, f)
        c.perform()
        c.close()

    print('다운로드 완료!')

    print('\n파싱을 시작합니다')
    with open("auction.json", "r") as f:
        js = json.load(f)
        #print(js['auctions'])

    # 저장된 파일을 읽은 후 한줄씩 탐색합니다
    golems = []
    i = 0
    price = 0
    min = 0
    max = 0
    avg = 0
    sum = 0

    for l in js['auctions']:
        #하늘골렘 아이템의 리스트를 작성합니다
        if l['item'] == 95416:
            d = json.dumps(l, ensure_ascii = False) #ensure_ascii는 유니코드 출력의 한글 문제를 해결해줍니다
            #print(l)
            #print(d)
            i += 1
            price = l['buyout']

            if min == 0:
                min = int(price)
            else:
                if int(price) < min:
                    min = int(price) 

            if max == 0:
                max = int(price)
            else:
                if int(price) > max:
                    max = int(price) 

            sum += price

    print("** 총 {}개의 하늘골렘이 올라와 있습니다".format(i))
    print("최소/최대가격은 각각 {} / {} 골드입니다".format(int(min/10000), int(max/10000)))
    print("평균은 {}골드입니다".format(int((sum/i)/10000)))

    print("\n")



def get_item(id):
    #https://kr.api.battle.net/wow/item/18803?locale=ko_KR&apikey=m5u8gdp6qmhbjkhbht3ax9byp62wench
    r = requests.get('https://kr.api.battle.net/wow/item/{}?locale={}&apikey={}'.format(id, locale, myapi))
    js = json.loads(r.text)
    print(js['name'])



loop = asyncio.get_event_loop()
loop.run_until_complete(proc())
loop.close()
