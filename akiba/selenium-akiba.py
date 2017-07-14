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
#l = drv.find_element_by_xpath("//a[@class='PreviewTooltip'][contains(@href, '1747531')]")

page_num = 1
next_page_link = drv.find_element_by_xpath("//div[@class='PageNav']/nav/a[@class='text']")
print('next_page_link.drv : {}'.format(next_page_link))
if next_page_link is not None:
    n = next_page_link.get_attribute('outerHTML') 
    print(n)
    next_page_link_is = re.search('Next', n) 

    m = re.search('href=\"(.*/page\-(\d+))\"', n)
    next_page_link_url = '{}/{}'.format(ROOT, m.group(1))
    next_page_num = m.group(2)
    print('nexturl: {}, nextnum : {}'.format(next_page_link_url, next_page_num))



# 페이지별 반복 프로세스
while True:
    l = drv.find_elements_by_xpath("//ol/li[not(contains(@class, 'sticky'))]/div/div/h3/a[@class='PreviewTooltip']")
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
        try:
            entry['title_ko'] = translate(title, 'ko')
        except:
            entry['title_ko'] = entry['title'] 
        entry['code'] = code
        akiba[thread_no] = entry
    #print(li_urls)



    # 페이지내의 쓰레드별 반복 프로세스
    print('visit each sites...')
    for l in li_urls:

        thread_no = l[-8:-1]
        print(thread_no)
        akiba[thread_no]['etc_images'] = []
        akiba[thread_no]['torrents'] = []

        print('{} thread url : {}'.format(thread_no, l))
        print('fetching...')

        # 해당 쓰레드 html 을 가져옵니다
        drv.get(l)
        #임시
        #drv.get('https://www.akiba-online.com/threads/asami_yuma-fhd-collection-pack-vol-5-170711-no-watermark.1748000/')

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

        # main_image 저장 및 지정 프로세스
        m = re.search('<img.*src=\"(.*\.\d+)/*\"', t)
        if m is not None : 
            href = m.group(1)
            f = re.search('attachments/(.*jpg\.\d+)/*', href).group(1) + '.jpg'
            print(f)
            akiba[thread_no]['main_image'] = f
            dir1 = 'static/images'
            #response = session.get('{}/{}'.format(ROOT, href))
            response = session.get(href)
            filename = "{}/{}".format(dir1, f)
            with open(filename, "wb") as w:
                w.write(response.content)

        # code 저장
        print(t)
        #m = re.search('<img.*src=\"(.*)\.\d+/*\"', t)
        o = re.search('alt=\"(\w+\-*\d+)\.*\"', t)
        if o is not None : akiba[thread_no]['code'] = o.group(1)
        #n = re.sub('<img.*\">', '', t, re.MULTILINE)

        # text 저장
        # text 를 추출하기 위한 프로세스입니다. <img 관련 태크, \n 태그, \t 태그 등을 제거합니다
        n = re.sub('<img.*\">', '', t)
        n = re.sub('\t', '', n)
        n = re.sub('\n', '', n)
        akiba[thread_no]['text'] = n 

        # etc_images 및 torrents 저장
        l = drv.find_elements_by_xpath("//ul[starts-with(@class, 'attachmentList')]/li/div/div/h6/a")
        for e in l:
            t1 = e.get_attribute('outerHTML')
            m1 = re.search('href=\"(.*\.\d+/*)\"', t1)
            href = m1.group(1)
            print(t1)
            print(href)
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
