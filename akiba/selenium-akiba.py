from selenium import webdriver
from bs4 import BeautifulSoup
import time, re
import requests
from peewee import *
# google translate 를 위한
from trans import *

URL = 'https://www.akiba-online.com'
ROOT = 'https://www.akiba-online.com'
LOCAL = '/mnt/c/Users/utylee/'
username = 'seoru'
password = 'akibaqnwk11'

# akiba dict의 key들 입니다
keys = ['thread_no', 'title', 'title_ko', 'date', 'href', 'code', 'main_image', 'etc_images', 'text', 'torrents', 'guess_quality', 'tag']
entry = dict.fromkeys(key for key in keys)
akiba = {}                          # {'글번호': 'entry dict'}

# db 관련 생성 및 초기화

db = SqliteDatabase('akiba.db')

class Akiba(Model):
    thread_no = CharField()         # 쓰레드 넘버입니다 href 제일 마지막 부분 숫자 아닌가 추측합니다
    title = CharField()             # 각 페이지의 제목입니다
    code = CharField()              #  품번명입니다
    main_image = CharField()        # 메인 이미지의 이름입니다
    etc_images = CharField()        # 상세 이미지들을 ; 로 구분하여 이름들을 저장합니다
    date = DateField()              # 글의 생성 날짜입니다
    torrent = CharField()           # 토렌트 파일의 이름입니다
    text = TextField()              # 글의 내용을 html 형식으로 그대로 갖고 있습니다
    guess_quality = CharField()     # 화질을 글의 내용이나 용량을 통해 추측합니다
    tag = CharField()               # tag 등을 ;로 구분하여 저장합니다

    class Meta:
        database = db


db.connect()


# google translate 를 위한 header
agent = {'User-Agent':
            "Mozilla/4.0 (\
            compatible;\
            MSIE 6.0;\
            Windows NT 5.1;\
            SV1;\
            .NET CLR 1.1.4322;\
            .NET CLR 2.0.50727;\
            .NET CLR 3.0.04506.30\
            )"}

#이미 db table이 생성되었을 경우, 에러가 날 때를 대비해 try 합니다
try:
    db.create_tables([Akiba])
except:
    pass


# PhantomJS를 로드해 출발합니다

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
#print('shot')
#drv.save_screenshot('/mnt/c/Users/utylee/out.png')
l.click()
#l.submit()
print('sleep 4')
#time.sleep(4)
#print('shot')
#drv.save_screenshot('/mnt/c/Users/utylee/out.png')

# Jav torrent 클릭
l = drv.find_element_by_xpath("//a[.='JAV Torrents']")
print('clicking JAV Torrents')
l.click()
print('sleep 3')
time.sleep(3)
#drv.save_screenshot('/mnt/c/Users/utylee/out.png')
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
#time.sleep(3)
#drv.save_screenshot('/mnt/c/Users/utylee/out.png')


# requests 다운로드를 위해 webdriver쿠키 전달
session = requests.Session()
cookies = drv.get_cookies()
for c in cookies:
    session.cookies.set(c['name'], c['value'])

li_urls = []
title = ""


for i in l:
    #entry 초기화
    entry = dict.fromkeys(key for key in keys)

    text = i.get_attribute('outerHTML')
    print(text)
    m = re.search('href=\"(.*)\" title=', text)
    href = m.group(1)
    m = re.search('\.(.*)/+', href)
    thread_no = m.group(1)[-7:]
    m = re.search('\">(.*)</a>', text)
    if m is not None: title = m.group(1)
    m = re.search('\[(.*)\]', title) 
    if m is not None: code = m.group(1)

    li_urls.append("{}/{}".format(ROOT, href))
    print("title: {}".format(title))
    entry['thread_no'] = thread_no
    entry['href'] = href
    entry['title'] = title
    entry['title_ko'] = translate(title, 'ko')
    entry['code'] = code
    akiba[thread_no] = entry
#print(li_urls)


print('visit each sites...')
for l in li_urls:
    thread_no = l[-8:-1]
    print('{} thread url : {}'.format(thread_no, l))
    print('fetching...')
    drv.get(l)

    # date 찾기
    l = drv.find_element_by_xpath("//abbr[@class='DateTime']")
    t = l.get_attribute('outerHTML')
    m = re.search('data-time=\"(\d*)\"', t)
    akiba[thread_no]['date'] = m.group(1)

    # text 찾기
    l = drv.find_element_by_xpath("//blockquote[starts-with(@class, 'messageText')]")
    #i = drv.find_element_by_xpath("//img[@class='bbCodeImage']")
    t = l.get_attribute('innerHTML')
    print(t)
    m = re.search('<img.*src=\"(.*)\.\d+/*\"', t)
    o = re.search('alt=\"(\w+\-*\d+)\.*\"', t)
    akiba[thread_no]['main_image'] = m.group(1)
    akiba[thread_no]['code'] = o.group(1)
    #n = re.sub('<img.*\">', '', t, re.MULTILINE)
    # text 를 추출하기 위한 프로세스입니다. <img 관련 태크, \n 태그, \t 태그 등을 제거합니다
    n = re.sub('<img.*\">', '', t)
    n = re.sub('\t', '', n)
    n = re.sub('\n', '', n)
    akiba[thread_no]['text'] = n 
    l = drv.find_elements_by_xpath("//ul[starts-with(@class, 'attachmentList')]/li/div/div/h6/a")
    for e in l:
        '''
        <a href="attachments/cmc-181-torrent.1073552/" target="_blank">cmc-181.torrent</a>
        <a href="attachments/cmc-181a-mp4-jpg.1073553/" target="_blank">cmc-181A.mp4.jpg</a>                                                 <a href="attachments/cmc-181b-mp4-jpg.1073554/" target="_blank">cmc-181B.mp4.jpg</a>
        '''
        t1 = e.get_attribute('outerHTML')
        m1 = re.search('href=\"(.*\.\d+/*)\"', t1)
        href = m1.group(1)
        print(t1)
        print(href)

        dir1 = 'static/images'
        ext = 'jpg'
        if re.search('jpg\.\d+',href) is not None:
            f = re.search('attachments/(.*jpg\.\d+)', href).group(1)
        elif re.search('torrent\.\d+',href) is not None:
            f = re.search('attachments/(.*torrent\.\d+)', href).group(1)
            ext = 'torrent'
            dir1 = 'static/torrents'

        #response = session.get('https://www.akiba-online.com/attachments/nkkd-038_s-jpg.1072048/')
        response = session.get('{}/{}'.format(ROOT, href))
        #print(response.content)
        #filename = "{}/{}.{}".format(LOCAL, href[8:], ext)
        filename = "{}/{}.{}".format(dir1, f, ext)
        #with open("/mnt/c/Users/utylee/temp.jpg", "wb") as w:
        with open(filename, "wb") as w:
            w.write(response.content)
print(akiba)
    
    #print(akiba[thread_no])
    
    #filename = "{}/{}.png".format(LOCAL, thread_no)
    #print('shot : {}'.format(filename))
    #drv.save_screenshot(filename)
    

    #title, main_image, text, etc_images, torrent, guess_quality, tag
    

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
