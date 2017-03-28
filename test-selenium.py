from selenium import webdriver
from bs4 import BeautifulSoup

import re
import time
import urllib
import asyncio
#import subprocess
import pycurl, json

print('started at {}'.format(time.strftime('%H:%M')))

# 해당 주소와 패턴을 정의합니다
url = "http://www.hanatour.com/asp/booking/productPackage/pk-12000.asp?pkg_code=ENP306150918AY&promo_doumi_code="
patt = '예약 : (.*)명 / 좌'

# 정규식 패턴을 컴파일합니다
re_pattern = re.compile(patt)

# selenium 드라이버를 숨김 브라우저(PhantomJS)로 정의합니다
print('executing phantomjs...')
phantom_drv = webdriver.PhantomJS()
#driver = webdriver.Firefox()

# asyncio 를 정의합니다
loop = asyncio.get_event_loop()

class FetchReservers():
    def __init__(self):
        self.url = "http://www.hanatour.com/asp/booking/productPackage/pk-12000.asp?pkg_code=ENP306150918AY&promo_doumi_code="
        self.patt = '예약 : (.*)명 / 좌'
        self.file_name = 'current_rsv.dat'
        self.current_num = 0

    @asyncio.coroutine
    def fetchurl(self):
        print('starting fetching process...')
        # 해당주소로 접속합니다
        yield from loop.run_in_executor(None, self.geturl)
        #driver.save_screenshot('screen.png')
        
        # 클래스명을 통해 해당 요소를 찾아냅니다
        print('parsing target...')
        elem = phantom_drv.find_element_by_class_name("table_detail")
        
        i = 0
        found = 0
        
        # 가져온 텍스트를 라인별로 점검하며 정규식과 비교해봅니다
        for line in elem.text.splitlines():
            re_match = re_pattern.match(line)
            #print("{} : {}".format(i, line))
            if re_match:
                self.current_num = re_match.group(1)
                print('---------------------------------------')
                print('* foundedNum : {}'.format(self.current_num))
                print('---------------------------------------')
                found = 1
                break
            i = i + 1
        
        # 찾았을 경우 출력하고 파일에 저장합니다
        if found:
            print('reading db file...')
            with open(self.file_name, 'r') as infile:
                self.before_num = infile.readline().strip()
                

            # 기존 값과 다를 경우 instapush합니다
            if self.current_num != self.before_num:
                # instapush에 메세지를 보냅니다
                print('insta pushing...')
                self.instapush(self.before_num, self.current_num)

            # 새로운 값을 파일에 저장합니다.
            #import pdb;pdb.set_trace()
            print('writing db file...')
            with open(self.file_name, 'w') as outfile:
                outfile.write(self.current_num)


    def geturl(self):
        print('navigating...')
        phantom_drv.get(self.url)

    def instapush(self, before_num, current_num):
        #json_param = '{"event":"newpost", "trackers":{"keyword":"{}"}}'.format(msg,) 
        #json_param = '{"event":"newpost", "trackers":{"keyword":"%s"}}'%(msg,) 

        #data = json.dumps({"event":"newpost", "trackers":{"message":"16"}})
        msg2 = '.북유럽 인원: \n  {}명 --> {}명 '.format(before_num, current_num)
        data = json.dumps({"event":"post", "trackers":{"msg":"{}".format(msg2)}})

        c = pycurl.Curl()
        c.setopt(pycurl.URL, 'https://api.instapush.im/v1/post')
        c.setopt(pycurl.HTTPHEADER, ['x-instapush-appid: 55ebd764a4c48a0a36d6f13a', \
                'x-instapush-appsecret: f19ad88dce7c5f940831bd12d3965cba', \
                'Content-Type: application/json'])
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.perform()
        print('pushed!')


        #cmds = ["curl", "-X" "POST", "-H", "x-instapush-appid: 55ebd764a4c48a0a36d6f13a", \
                #"-H", "x-instapush-appsecret: f19ad88dce7c5f940831bd12d3965cba", \
                #"-H", "Content-Type: application/json", \
                #"-d", json_param, \
                #"https://api.instapush.im/v1/post"]
        #r = subprocess.check_output(cmds, shell=True, universal_newlines=True)
        #r = subprocess.check_output(cmds, shell=True)
        #print(r)
            
fetcher = FetchReservers() 

#with loop:
loop.run_until_complete(fetcher.fetchurl())

print('process closing...')

loop.close()
