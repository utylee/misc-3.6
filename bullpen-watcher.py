
import urllib
from urllib.request import urlopen
from subprocess import Popen, PIPE, check_output, call

import re
import time
import threading


class CVisitProc(threading.Thread):
    def __init__(self):
    	super().__init__()
    	self.url = ''

    	self.encoding = 'cp949' 
    	self.found = False
    	self.be_or_not = True 
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


class CWatchProc(threading.Thread):
    def __init__(self):
    	super().__init__()

    	# 불펜주소입니다
    	self.url2 = 'http://mlbpark.donga.com/mbs/articleL.php?mbsC=bullpen2'

    	self.encoding = 'cp949' 
    	self.found = False
    	self.pattern = '.*(유라|걸스데이|걸데|민아|소진|혜리|BULLDESS).*'
    	self.urlpattern = '.*href=\'(.*)&cpage'
    	self.be_or_not = True 
    	self.interval = 180 
    	self.target_url = ''
		
	
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
	
                for line in fulllines:
    			#print (line.decode('cp949'))

			#matching = re_patt.match(line.decode(self.encoding))
                    matching = re_patt.match(line.decode('cp949'))
                    if matching:
			#print('matching!!')
			#print(prev_line3)
			#print(prev_line2)
			#print(prev_line)
			#print(line)
                        matching_url = re_urlpatt.match(line.decode('cp949'))

                        if matching_url:
	                    self.found = True
	                    self.target_url = 'http://mlbpark.donga.com/' + matching_url.group(1)
			    #self.target_url = matching_url.group(1)
	                    print(self.target_url)
				
			    #print(self.target_url)
	                    break
		            #time.sleep(0.01)
	                    prev_line3 = prev_line2
	                    prev_line2 = prev_line
	                    prev_line = line
				
    			if self.found == self.be_or_not :
    			    #print('들어옴')
    			    if former_url != self.target_url:
    				# x86과 x64사이의 차이에 의해 나뉩니다
    				#call(['c:\\program files (x86)\\Mozilla Firefox\\firefox.exe', self.target_url])
    				call(['c:\\program files\\Mozilla Firefox\\firefox.exe', self.target_url])

 				#조회수 프로세스는 일단 꺼놓습니다
    				#self.visit(self.target_url, 100, 0.3)
    				former_url = self.target_url
    			else :
    			    print('but pass')

    			    self.found = False
    			    time.sleep(5)
    			    continue

    			time.sleep(self.interval)
    		except:
    			pass

    def visit(self, url, num, interval):
    	print('조회수 프로세스 시작 : 주소 : ' + url)
    	for i in range(num): 
    	    try:
    		page = urlopen(url)
    		time.sleep(interval)
    	    except:
    		pass
    	print('조회 프로세스는 종료. 다시 대기 시작')


if __name__ == "__main__":
    site = CWatchProc()
    site.start()
