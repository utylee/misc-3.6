from selenium import webdriver
from bs4 import BeautifulSoup
import time, re
import requests
from peewee import *
#ctrl_pageLogin_login


# db 관련 생성 및 초기화

db = SqliteDatabase('akiba.db')

class Akiba(Model):
    title = CharField()             # 각 페이지의 제목입니다
    code = CharField()              #  품번명입니다
    title_image = CharField()       # 메인 이미지의 이름입니다
    detail_images = CharField()     # 상세 이미지들을 ; 로 구분하여 이름들을 저장합니다
    date = DateField()              # 글의 생성 날짜입니다
    torrent = CharField()           # 토렌트 파일의 이름입니다
    content = TextField()           # 글의 내용을 html 형식으로 그대로 갖고 있습니다

    class Meta:
        database = db


db.connect()

#이미 db table이 생성되었을 경우, 에러가 날 때를 대비해 try 합니다
try:
    db.create_tables([Akiba])
except:
    pass

URL = 'https://www.akiba-online.com'
ROOT = 'https://www.akiba-online.com'
LOCAL = '/mnt/c/Users/utylee/'
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
drv.save_screenshot('/mnt/c/Users/utylee/out.png')
l.click()
#l.submit()
print('sleep 4')
#time.sleep(4)
print('shot')
drv.save_screenshot('/mnt/c/Users/utylee/out.png')

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
#l = drv.find_element_by_xpath("//a[@class='PreviewTooltip'][contains(@href, '1747531')]")
l = drv.find_elements_by_xpath("//ol/li[not(contains(@class, 'sticky'))]/div/div/h3/a[@class='PreviewTooltip']")
#print(l)
#l.click()
time.sleep(3)
drv.save_screenshot('/mnt/c/Users/utylee/out.png')


session = requests.Session()
cookies = drv.get_cookies()
for c in cookies:
    session.cookies.set(c['name'], c['value'])

li_urls = []

for i in l:
    text = i.get_attribute('outerHTML' )
    print(text)
    m = re.search('href=\"(.*)\" title=', text)
    href = m.group(1)
    li_urls.append("{}/{}".format(ROOT, href))
    '''
    #response = session.get('https://www.akiba-online.com/attachments/nkkd-038_s-jpg.1072048/')
    response = session.get('{}/{}'.format(ROOT, href))
    #print(response.content)
    filename = "{}/{}.jpg".format(LOCAL, href[8:])
    #with open("/mnt/c/Users/utylee/temp.jpg", "wb") as w:
    with open(filename, "wb") as w:
        w.write(response.content)
        '''
print(li_urls)

print('visit each sites...')
for l in li_urls:
    print('site : {}'.format(l))
    drv.get(l)
    filename = "{}/{}.png".format(LOCAL, l[-8:-1])
    print('shot : {}'.format(filename))
    drv.save_screenshot(filename)

    # 각 페이지를 파싱하여, jpg과 torrent 를 가져옵니다
#o = drv.find_element_by_xpath("//ol[@class='discussionListItems']")
#text = o.get_attribute('innerHTML')
#print(text)

'''
#jpg 클릭

l = drv.find_element_by_xpath("//h6/a[contains(@href, '1072048')]")
t = l.get_attribute('outerHTML')


#l.click()
#print(response.content)


time.sleep(3)
drv.save_screenshot('/mnt/c/Users/utylee/out.png')
# sticky가 아닌 목록들만 추출합니다
'''
