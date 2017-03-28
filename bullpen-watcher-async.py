
import urllib
from urllib.request import urlopen
from subprocess import Popen, PIPE, check_output, call

import re
import time
import threading
import asyncio
import os
import pdb
#import quamash


class CVisitProc(threading.Thread):
    def __init__(self):
        super().__init__()
        self.url = ''

        self.encoding = 'cp949' 
        self.found = False
        self.true_or_not = True 
        self.interval = 0.5 
        self.num = 10

    def run(self):
        print('조회수 프로세스 시작 : 주소 : ' + self.url)

        for i in range(self.num): 
            try:
                page = urlopen(self.url)
                time.sleep(self.interval)
            except:
                pass
        
#쓰레드 상속 클래스를 만들었지만, 코루틴으로 수정하기 시작했는데 계속 threading 상속을 받아야하는지 고민이 생겼습니다
class CWatchProc(threading.Thread):
    def __init__(self, loop):
        super().__init__()

        # 하나투어 북유럽투어주소입니다
        #self.url2 = 'http://mlbpark.donga.com/mbs/articleL.php?mbsC=bullpen2'
        self.url2 = 'http://www.hanatour.com/asp/booking/productPackage/pk-12000.asp?pkg_code=ENP306150918AY&promo_doumi_code='

        self.encoding = 'cp949' 
        self.found = False
        self.pattern = '.*(유라|걸스데이|걸데|민아|소진|혜리|BULLDESS).*'
        self.urlpattern = '.*href=\'(.*)&cpage'
        self.true_or_not = True 
        #self.interval = 180 
        self.interval = 5 
        self.target_url = ''
        self.visted_list = []
        self.loop = loop
        self.future = asyncio.Future()
        self.future2 = asyncio.Future()
        
    @asyncio.coroutine
    def run(self):
        re_patt = re.compile(self.pattern)  
        re_urlpatt = re.compile(self.urlpattern)
        former_url = ''

        while 1:
            try:
                page = urlopen(self.url2)
                fulllines = page.readlines()        

                prev_line = ''
                prev_line2 = ''
                prev_line3 = ''

                line_num = 0
    
                for line in fulllines:
                    print(line)
                    line_num = line_num + 1
                    matching = re_patt.match(line.decode('cp949'))
                    if matching:
                        matching_url = re_urlpatt.match(line.decode('cp949'))
                        #print('1')
                        if matching_url:
                            self.found = True
                            self.target_url = 'http://mlbpark.donga.com/' + matching_url.group(1)
                            print(self.target_url, "ln:", line_num)
                
                            #break
                            prev_line3 = prev_line2
                            prev_line2 = prev_line
                            prev_line = line
                
                        if self.found == self.true_or_not :
                            #print('들어옴')
                            #if former_url != self.target_url:
                            # 해당 url이 방문리스트에 있는지 판단합니다
                            if not self.target_url in self.visted_list:
                                # 해당 url를 방문리스트에 추가합니다.
                                self.visted_list.append(self.target_url)

                                # x86과 x64사이의 차이에 의해 나뉩니다
                                #call(['c:\\program files (x86)\\Mozilla Firefox\\firefox.exe', self.target_url])
                                print('firefox에서 해당 페이지를 엽니다')

                                self.future = self.loop.run_in_executor(None, self.call_async, self.target_url)
                                yield from self.future
                                print('firefox에서 페이지 오픈 성공하였습니다')
                                #call(['c:\\program files\\Mozilla Firefox\\firefox.exe', self.target_url])

                                #조회수 프로세스는 일단 꺼놓습니다
                                #self.visit(self.target_url, 100, 0.3)
                                #former_url = self.target_url
                            else :
                                print('이미 방문한 페이지이므로 패스합니다')
                                self.found = False
                                #time.sleep(5)
                    continue

                print('라인 파싱 모두 완료되었습니다')

                time.sleep(self.interval)
            except:
                pass

    def call_async(self, url):
        print('{} 호출성공'.format('call_async'))
        call(['c:\\program files\\Mozilla Firefox\\firefox.exe', self.target_url])
        print('call 실행완료')
        self.future2.set_result(True)

    def visit(self, url, num, interval):
        print('조회수 프로세스 시작 : 주소 : ' + url)
        for i in range(num): 
            try:
                page = urlopen(url)
                time.sleep(interval)
            except:
                pass
        print('조회 프로세스는 종료. 다시 대기 시작')

#######################################################
# 사이트 접속 후 

#######################################################

if __name__ == "__main__":
    if os.name == "nt":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    site = CWatchProc(loop)
    loop.run_until_complete(site.run())
    #site.start()
