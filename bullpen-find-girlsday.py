
import urllib
from urllib.request import urlopen
from subprocess import Popen, PIPE, check_output, call

import re
import time
import threading
import winsound

class CVisitProc(threading.Thread):
	def __init__(self):
		super().__init__()
		self.url = 'http://mlbpark.donga.com/mbs/articleL.php?mbsC=bullpen2'
		self.encoding = 'cp949' 
		self.found = False 
		self.pattern = '.*유민.*'
		self.be_or_not = True 
		self.interval = 60 
		self.num = 800 
	
	def run(self):
		re_patt = re.compile(self.pattern)	


		while 1:
		#	try:
				print('connecting...')
				page = urlopen(self.url)
				print('parsing for %s...'% self.pattern)
				fulllines = page.readlines()		
	
				for line in fulllines:
					line_decode= line.decode(self.encoding)
					print(line_decode)
					matching = re_patt.match(line_decode)
					if matching:
						print('matching!!')
						print(line_decode)
						self.found = True
						break
					#time.sleep(0.01)
				
				if self.found == self.be_or_not:
					print('found!!')
					winsound.PlaySound("myalarm.wav", winsound.SND_FILENAME)
				else:
					print('no matched')
				#	call(['c:\\program files\\Mozilla Firefox\\firefox.exe', self.url])
				#	break
				
				#call(['c:\\program files (x86)\\Mozilla Firefox\\firefox.exe', self.url3])
				print('wait %d sec..'% self.interval)
				time.sleep(self.interval)
		#	except:
				
				#print('exception occurred!')
				#pass

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
