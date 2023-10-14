import re
import json
import asyncio
from js2py.pyjs import JSON
import uvloop
from aiofiles import open as open_async
import pyperclip
import aiohttp
from aiohttp import web
import argparse
import logging

COOKIE_PATH = f'/mnt/c/Users/utylee/Downloads/cookies.txt'
# COOKIE_PATH = f'/home/utylee/cookies.txt'
# COOKIE_PATH = f'/mnt/c/Users/utylee/Downloads/cookies.firefox-private.txt'
JSON_PATH = f'/home/utylee/login.json'

async def handle(request):
    return web.Response(text='connect to /cook/ to refresh the login.json file')


async def cook(request):
    full = []
    full_dict = dict()

    # 먼저 login.json 에서 SESSION_TOKEN 값은 저장해놓습니다
    # --> pyperclip으로 클립보드 값을 넣어주는 것으로 변경합니다
    # 실행시 번거롭지 않게 바로 login.json에 sessionToken을 반영하도록
    sessionToken = ''
    # try:
    #     async with open_async(JSON_PATH, 'r') as f:
    #         r = await f.readlines()
    #         rr = "".join(r)
    #         # print(r)
    #         # print(rr)
    #         p = json.loads(rr)
    #         # print(p)
    #         print(f'.sessionToken: {p["SESSION_TOKEN"]}')
    #         # sessionToken = p['SESSION_TOKEN']

    # except:
    #     pass

    # clipboard값을 sessionToken에 바로 넣어줍니다
    log.info('pyperclip')
    try:
        pyperclip.ENCODING = 'cp949'
        sessionToken = pyperclip.paste()

    except Exception as e:
        log.info(f'pyperclip exception: {e}')

    log.info('open cookies.txt')
    # 쿠키파일을 엽니다
    async with open_async(COOKIE_PATH, 'r') as f:
        full = await f.readlines()

    log.info('cookies.txt ended')
    # 파싱하여 dict를 만듭니다
    res = ()
    for i in full:
        s = re.search(r'\S+\s+\S+\s+/\s+\S+\s+\S+\s+(.*)\t(.*)', i)
        if (s):
            res = (s.group(1), s.group(2))
            full_dict[s.group(1)] = s.group(2)
        # print(i)
        # print(res)

    # full_dict['SESSION_TOKEN'] = sessionToken
    # # print(full_dict['VISITOR_INFO1_LIVE'])
    # print(full_dict)

    # 로긴파일을 작성합니다
    async with open_async(JSON_PATH, 'w') as f:
        # await f.write('{\n\t"SESSION_TOKEN": "",')

        # p = json.dumps(full_dict, indent=4)
        # await f.write(p)

        await f.write('{\n')
        # await f.write('\t"SESSION_TOKEN": ""')
        await f.write(f'\t"SESSION_TOKEN": "{sessionToken}"')
        # f-string 최외각을 single-quote ' 로 감싸면 dict형식은 double-quote " 로 감싸면 되고
        # 그 반대도 되네요. 검색해보니
        # i.e. https://stackoverflow.com/questions/43488137/how-can-i-do-a-dictionary-format-with-f-string-in-python-3-6
        # await f.write(f',\n\t"LOGIN_INFO": "{full_dict["LOGIN_INFO"]}"')
        await f.write(f',\n\t"SID": "{full_dict["SID"]}"')
        await f.write(f',\n\t"HSID": "{full_dict["HSID"]}"')
        await f.write(f',\n\t"SSID": "{full_dict["SSID"]}"')
        await f.write(f',\n\t"APISID": "{full_dict["APISID"]}"')
        await f.write(f',\n\t"SAPISID": "{full_dict["SAPISID"]}"')
        await f.write(f',\n\t"LOGIN_INFO": "{full_dict["LOGIN_INFO"]}"')
        await f.write(f',\n\t"__Secure-1PSIDTS": "{full_dict["__Secure-1PSIDTS"]}"')
        await f.write('\n}')

        '''
        await f.write('{\n')
        await f.write('\t"SESSION_TOKEN": ""')
        # f-string 최외각을 single-quote ' 로 감싸면 dict형식은 double-quote " 로 감싸면 되고
        #그 반대도 되네요. 검색해보니
        # i.e. https://stackoverflow.com/questions/43488137/how-can-i-do-a-dictionary-format-with-f-string-in-python-3-6
        await f.write(f',\n\t"VISITOR_INFO1_LIVE": "{full_dict["VISITOR_INFO1_LIVE"]}"')
        # await f.write(f',\n\t"PREF": "{full_dict["PREF"]}"')
        await f.write(f',\n\t"PREF": "f6=40000000&tz=Asia.Seoul"')
        await f.write(f',\n\t"LOGIN_INFO": "{full_dict["LOGIN_INFO"]}"')
        await f.write(f',\n\t"SID": "{full_dict["SID"]}"')
        await f.write(f',\n\t"__Secure-3PSID": "{full_dict["__Secure-3PSID"]}"')
        await f.write(f',\n\t"HSID": "{full_dict["HSID"]}"')
        await f.write(f',\n\t"SSID": "{full_dict["SSID"]}"')
        await f.write(f',\n\t"APISID": "{full_dict["APISID"]}"')
        await f.write(f',\n\t"SAPISID": "{full_dict["SAPISID"]}"')
        await f.write(f',\n\t"__Secure-3PAPISID": "{full_dict["__Secure-3PAPISID"]}"')
        await f.write(f',\n\t"YSC": "{full_dict["YSC"]}"')
        await f.write(f',\n\t"SIDCC": "{full_dict["SIDCC"]}"')
        await f.write('\n}')
        '''

    print('\nlogin.json wrote')


    r = ''
    rr = ''
    # 완성된 login.json 출력
    try:
        async with open_async(JSON_PATH, 'r') as f:
            r = await f.readlines()
            rr = "".join(r)
            # print(r)
            print(rr)
    except Exception as e:
        print(f'Exception:{e}')

    return web.Response(text=rr) 

async def main():
    # uvloop.install()
    full = []
    full_dict = dict()

    # 먼저 login.json 에서 SESSION_TOKEN 값은 저장해놓습니다
    # --> pyperclip으로 클립보드 값을 넣어주는 것으로 변경합니다
    # 실행시 번거롭지 않게 바로 login.json에 sessionToken을 반영하도록
    sessionToken = ''
    # try:
    #     async with open_async(JSON_PATH, 'r') as f:
    #         r = await f.readlines()
    #         rr = "".join(r)
    #         # print(r)
    #         # print(rr)
    #         p = json.loads(rr)
    #         # print(p)
    #         print(f'.sessionToken: {p["SESSION_TOKEN"]}')
    #         # sessionToken = p['SESSION_TOKEN']

    # except:
    #     pass

    # clipboard값을 sessionToken에 바로 넣어줍니다
    pyperclip.ENCODING = 'cp949'
    sessionToken = pyperclip.paste()

    # 쿠키파일을 엽니다
    async with open_async(COOKIE_PATH, 'r') as f:
        full = await f.readlines()

    # 파싱하여 dict를 만듭니다
    res = ()
    for i in full:
        s = re.search(r'\S+\s+\S+\s+/\s+\S+\s+\S+\s+(.*)\t(.*)', i)
        if (s):
            res = (s.group(1), s.group(2))
            full_dict[s.group(1)] = s.group(2)
        # print(i)
        # print(res)

    # full_dict['SESSION_TOKEN'] = sessionToken
    # # print(full_dict['VISITOR_INFO1_LIVE'])
    # print(full_dict)

    # 로긴파일을 작성합니다
    async with open_async(JSON_PATH, 'w') as f:
        # await f.write('{\n\t"SESSION_TOKEN": "",')

        # p = json.dumps(full_dict, indent=4)
        # await f.write(p)

        await f.write('{\n')
        # await f.write('\t"SESSION_TOKEN": ""')
        await f.write(f'\t"SESSION_TOKEN": "{sessionToken}"')
        # f-string 최외각을 single-quote ' 로 감싸면 dict형식은 double-quote " 로 감싸면 되고
        # 그 반대도 되네요. 검색해보니
        # i.e. https://stackoverflow.com/questions/43488137/how-can-i-do-a-dictionary-format-with-f-string-in-python-3-6
        # await f.write(f',\n\t"LOGIN_INFO": "{full_dict["LOGIN_INFO"]}"')
        await f.write(f',\n\t"SID": "{full_dict["SID"]}"')
        await f.write(f',\n\t"HSID": "{full_dict["HSID"]}"')
        await f.write(f',\n\t"SSID": "{full_dict["SSID"]}"')
        await f.write(f',\n\t"APISID": "{full_dict["APISID"]}"')
        await f.write(f',\n\t"SAPISID": "{full_dict["SAPISID"]}"')
        await f.write(f',\n\t"LOGIN_INFO": "{full_dict["LOGIN_INFO"]}"')
        await f.write(f',\n\t"__Secure-1PSIDTS": "{full_dict["__Secure-1PSIDTS"]}"')
        await f.write('\n}')

        '''
        await f.write('{\n')
        await f.write('\t"SESSION_TOKEN": ""')
        # f-string 최외각을 single-quote ' 로 감싸면 dict형식은 double-quote " 로 감싸면 되고
        #그 반대도 되네요. 검색해보니
        # i.e. https://stackoverflow.com/questions/43488137/how-can-i-do-a-dictionary-format-with-f-string-in-python-3-6
        await f.write(f',\n\t"VISITOR_INFO1_LIVE": "{full_dict["VISITOR_INFO1_LIVE"]}"')
        # await f.write(f',\n\t"PREF": "{full_dict["PREF"]}"')
        await f.write(f',\n\t"PREF": "f6=40000000&tz=Asia.Seoul"')
        await f.write(f',\n\t"LOGIN_INFO": "{full_dict["LOGIN_INFO"]}"')
        await f.write(f',\n\t"SID": "{full_dict["SID"]}"')
        await f.write(f',\n\t"__Secure-3PSID": "{full_dict["__Secure-3PSID"]}"')
        await f.write(f',\n\t"HSID": "{full_dict["HSID"]}"')
        await f.write(f',\n\t"SSID": "{full_dict["SSID"]}"')
        await f.write(f',\n\t"APISID": "{full_dict["APISID"]}"')
        await f.write(f',\n\t"SAPISID": "{full_dict["SAPISID"]}"')
        await f.write(f',\n\t"__Secure-3PAPISID": "{full_dict["__Secure-3PAPISID"]}"')
        await f.write(f',\n\t"YSC": "{full_dict["YSC"]}"')
        await f.write(f',\n\t"SIDCC": "{full_dict["SIDCC"]}"')
        await f.write('\n}')
        '''

    print('\nlogin.json wrote')

    # 완성된 login.json 출력
    try:
        async with open_async(JSON_PATH, 'r') as f:
            r = await f.readlines()
            rr = "".join(r)
            # print(r)
            print(rr)

    except:
        pass

    '''
{
  "SESSION_TOKEN": "AZHt5fVoyl9Nwt_LIuVHLkflhUSEyfATBRBnvyygLoMEayZ8yz_-xrneg3ZIqJUpGmc9Umqip-jtTgNprkxL3dnyD4aqLYhVErTtSBJ8U6_hz2zH_Kz5WEhn0m6pWfW_HssZ97R3w4pEa4RnPQt17gtwOSkuB6xw-w==",
  "VISITOR_INFO1_LIVE": "7oAIQkE2mR8",
  "PREF": "f6=40000000&tz=Asia.Seoul",
  "LOGIN_INFO": "AFmmF2swRAIgSwNZzPemXsJPfV3JGshffNUEoyQCVYgw2ruUILeQ1u0CIGBPv-eP3G6Cw4gTZvBrLUuoXuA6pwVAteHU4oE7kndp:QUQ3MjNmd1pSUlNKbDY3SFEybnllNTNKX2hYUmtZWnpYLUs0Y3dOYlBMdVNuTDd4b2g1eDBzOXFGaWd1eEF0amVwVUpleDkyMHhYVHRndHlncjdadnRScGJob000a0hRSW9jMTl1eko4ZkpLcVJmVmhXQllJVTJmYlkzREZnUUpibzZPRV9vdG45UHM4anAwQm44X18tYWhwaDVOMEYzYzBn",
  "SID": "bwiKQMn0X6aXvonXeWZ2mdU_qhxh6hLKS2NYKoaVCC78io2LmBT_h2_pdKimrA-jodd0DA.",
  "__Secure-3PSID": "bwiKQMn0X6aXvonXeWZ2mdU_qhxh6hLKS2NYKoaVCC78io2Le4KAw8IaxFkSx7_RUS9LHg.",
  "HSID": "AwR-5xTvNfEiEV-OJ",
  "SSID": "AKY2H07_EVYSW33td",
  "APISID": "BPHICK05ByTsmI4m/AkHVmUHduaL0Ze7ma",
  "SAPISID": "jTSRC0ONm-dpD2e6/AlKm-olOUWHrOBd40",
  "__Secure-3PAPISID": "jTSRC0ONm-dpD2e6/AlKm-olOUWHrOBd40",
  "YSC": "-p-okffA8Rk",
  "SIDCC": "ACA-OxNCN0GYvdfy3LiDS_cH836RxVmjoqGTCldlB9B_bgMZL-TGmESVD6twRuhpxWDVxq79yA"
}
    '''

    # loop = asycio.get_event_loop()
    # loop.run_until_complete(main())



if __name__ == '__main__':
    uvloop.install()
    print('??')
    parser = argparse.ArgumentParser(description='cookie_changer')
    parser.add_argument('--port')
    parser.add_argument('--path')
    args = parser.parse_args()

    log = logging.getLogger('cookie_changer')
    handler = logging.FileHandler('/home/utylee/cookie_changer.log')
    handler.setFormatter(logging.Formatter('[%(asctime)s-%(message)s]'))
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    log.info('started')

    app = web.Application()

    app.add_routes([
        web.get('/cook', cook),
        web.get('/', handle)
    ])
    print(args.port)

    web.run_app(app, port=args.port, path=args.path)
