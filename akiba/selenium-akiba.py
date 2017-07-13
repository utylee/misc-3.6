from selenium import webdriver
from bs4 import BeautifulSoup
import time, re
import requests
from peewee import *
#ctrl_pageLogin_login


db = SqliteDatabase('akiba.db')

class Akiba(Model):
    title = CharField()
    code = CharField()
    title_image = CharField()
    content_images = CharField()
    text = TextField()
    date = DateField()

    class Meta:
        database = db

db.connect()
try:
    db.create_tables([Akiba])
except:
    pass

URL = 'https://www.akiba-online.com'
ROOT = 'https://www.akiba-online.com'
username = 'seoru'
password = 'akibaqnwk11'

drv = webdriver.PhantomJS("/usr/local/bin/phantomjs")
drv.set_window_size(1024, 768)

#접속
print('connecting...')
drv.get(URL)

#로그인
print('log in process :')
l = drv.find_element_by_xpath("//a[@href='login/']")
l.click()
time.sleep(1)
print('input id')
l = drv.find_element_by_xpath("//input[@id='ctrl_pageLogin_login'][@name='login']")
l.send_keys(username)
#time.sleep(1)

print('click "yes i have id"')
l = drv.find_element_by_xpath("//input[@id='ctrl_pageLogin_registered'][@name='register']")
l.click()
print('input password')
l = drv.find_element_by_xpath("//input[@id='ctrl_pageLogin_password'][@name='password']")
l.send_keys(password)
#print('sleep 1')
#time.sleep(1)
print('click "login" button')
l = drv.find_element_by_xpath("//div[@class='xenOverlay']/form/dl/dd/input[@class='button primary'][@value='Log in']")
print('sleep 1')
time.sleep(1)
print('shot')
#drv.save_screenshot('/mnt/c/Users/utylee/out.png')
drv.save_screenshot('out.png')
l.click()
#l.submit()
print('sleep 4')
#time.sleep(4)
print('shot')
#drv.save_screenshot('/mnt/c/Users/utylee/out.png')
drv.save_screenshot('out.png')

# Jav torrent 클릭
l = drv.find_element_by_xpath("//a[.='JAV Torrents']")
print('clicking JAV Torrents')
l.click()
print('sleep 3')
time.sleep(3)
drv.save_screenshot('/mnt/c/Users/utylee/out.png')
#t = drv.page_source
#t = drv.get_attribute('innerHTML')


# Jav torrent 내의 list들을 가진 목록을 가져옵니다
print('fetching JAV torrents list items...')
#o = drv.find_elements_by_xpath("//li[@class='discussionListItem visible*'][not(@class='*sticky ')]")
#o = drv.find_elements_by_xpath("//li[contains(@class, 'discussionListItem visible')]")
l = drv.find_element_by_xpath("//a[@class='PreviewTooltip'][contains(@href, '1747531')]")
#l = drv.find_elements_by_xpath("//a[@class='PreviewTooltip']")
print(l)
l.click()
time.sleep(3)
#drv.save_screenshot('/mnt/c/Users/utylee/out.png')
drv.save_screenshot('out.png')
#for i in o:
    #print(i.get_attribute('outerHTML'))
#print(len(o))
#o = drv.find_element_by_xpath("//ol[@class='discussionListItems']")
#text = o.get_attribute('innerHTML')
#print(text)


#jpg 클릭

l = drv.find_element_by_xpath("//h6/a[contains(@href, '1072048')]")
t = l.get_attribute('outerHTML')

m = re.search('href=\"(.*)/\"', t)
t = m.group(1)
print(t)

session = requests.Session()
cookies = drv.get_cookies()

for c in cookies:
    session.cookies.set(c['name'], c['value'])
#response = session.get('https://www.akiba-online.com/attachments/nkkd-038_s-jpg.1072048/')
response = session.get('{}/{}'.format(ROOT, t))
#print(response.content)

#with open("/mnt/c/Users/utylee/temp.jpg", "wb") as w:
with open("temp.jpg", "wb") as w:
    w.write(response.content)

#l.click()
#print(response.content)


time.sleep(3)
drv.save_screenshot('/mnt/c/Users/utylee/out.png')
# sticky가 아닌 목록들만 추출합니다
