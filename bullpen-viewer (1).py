
import urllib
from urllib.request import urlopen
from subprocess import Popen, PIPE, check_output, call

import re
import time
import threading

class CVisitProc(threading.Thread):
	def __init__(self):
		super().__init__()
		self.url = 'http://mlbpark.donga.com/mbs/articleVC.php?mbsC=bullpen2&mbsIdx=2800947&cpage=9'
		#'http://mlbpark.donga.com/mbs/articleVC.php?mbsC=bullpen2&mbsIdx=1094337&cpage=&mbsW=search&select=stt&opt=1&keyword='
		
		#self.url = 'http://mlbpark.donga.com/mbs/articleVC.php?mbsC=bullpen2&mbsIdx=1044973&cpage=&mbsW=search&select=stt&opt=1&keyword=%EA%B1%B8%EC%8A%A4%EB%8D%B0%EC%9D%B4'#.encode('ascii')#%EA%B1%B8%EC%8A%A4%EB%8D%B0%EC%9D%B4'
		self.url2 = 'http://mlbpark.donga.com/mbs/articleL.php?mbsC=bullpen2'
		self.encoding = 'utf-8' 
		self.found = False
		self.pattern = ''
		self.be_or_not = True 
		self.interval = 0.5 
		self.num = 3000 
	
	def run(self):
		re_patt = re.compile(self.pattern)	


		#while 1:
		for i in range(self.num): 
			try:
				page = urlopen(self.url)
				time.sleep(self.interval)
			except:
				pass
			#try:
				#url = unicode(self.url, "utf-8")
			#	page = urlopen(self.url)
				#fulllines = page.readlines()		
	
				#for line in fulllines:
					#pass
				#	print (line)
					#matching = re_patt.match(line.decode(self.encoding))
					#if matching:
					#	print('matching!!')
					#	self.found = True
					#	break
					#time.sleep(0.01)
				
				#if self.found == self.be_or_not:
				#	call(['c:\\program files\\Mozilla Firefox\\firefox.exe', self.url])
				#	break
				
				#call(['c:\\program files (x86)\\Mozilla Firefox\\firefox.exe', self.url3])
			#except:
				#print('exception occurred!!')

				#time.sleep(self.interval)

				#page2 = urlopen(self.url2)
if __name__ == "__main__":
	site = CVisitProc()
	site.start()
