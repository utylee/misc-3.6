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
start_page_num = 2

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
# 첫페이지부터 시작
l = drv.find_element_by_xpath("//a[.='JAV Torrents']")
print('clicking JAV Torrents')
l.click()
print('sleep 3')
time.sleep(3)
#drv.save_screenshot('/mnt/c/Users/utylee/out.png')
#t = drv.page_source
#t = drv.get_attribute('innerHTML')

# requests다운로드를 위해 webdriver쿠키를 미리 전달해 놓습니다
session = requests.Session()
cookies = drv.get_cookies()
for c in cookies:
    session.cookies.set(c['name'], c['value'])

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
        entry['title_ko'] = translate(title, 'ko')
        entry['code'] = code
        akiba[thread_no] = entry
    #print(li_urls)



    # 페이지내의 쓰레드별 반복 프로세스
    print('visit each sites...')
    for l in li_urls:

        thread_no = l[-8:-1]
        akiba[thread_no]['etc_images'] = []
        akiba[thread_no]['torrents'] = []

        print('{} thread url : {}'.format(thread_no, l))
        print('fetching...')

        # 해당 쓰레드 html 을 가져옵니다
        #임시
        #drv.get(l)
        drv.get('https://www.akiba-online.com/threads/asami_yuma-fhd-collection-pack-vol-5-170711-no-watermark.1748000/')

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

            dir1 = 'static/images'
            #ext = 'jpg'
            if re.search('jpg\.\d+',href) is not None:
                f = re.search('attachments/(.*jpg\.\d+)', href).group(1) + '.jpg'
                akiba[thread_no]['etc_images'].append(f)
            elif re.search('torrent\.\d+',href) is not None:
                f = re.search('attachments/(.*torrent\.\d+)', href).group(1) + '.torrent'
                akiba[thread_no]['torrents'].append(f)
                #ext = 'torrent'
                dir1 = 'static/torrents'

            response = session.get('{}/{}'.format(ROOT, href))
            #print(response.content)
            #filename = "{}/{}.{}".format(LOCAL, href[8:], ext)
            #filename = "{}/{}.{}".format(dir1, f, ext)
            filename = "{}/{}".format(dir1, f)
            with open(filename, "wb") as w:
                w.write(response.content)
        print(akiba[thread_no])

        if akiba[thread_no]['main_image'] is None:
            #첨부 이미지가 하나도 없는 경우, 본문 내 img 태그들 주소를 검색해 모두 다운로드하고 db에 연결합니다
            if not len(akiba[thread_no]['etc_images']):
                ele_images = drv.find_elements_by_xpath("//img[starts-with(@class, 'bbCodeImage')]")     
                for e in ele_images:
                    if e is not None:
                        src = e.get_attribute('outerHTML')
                        print(src)
                        #m = re.search('src=\"(.*/(.+\.w+))\"', src)
                        #if m is not None:
                            #url = m.group(1)
                            #f = m.group(2)
                        url = e.get_attribute('src')
                        print(url)
                        f = url.split('/')[-1]
                        print(f)
                        
                        print("url:{}, f:{}".format(url, f))
                        print("url[:4]:{}".format(url[:4].lower()))

                        dir1 = 'static/images'
                        if (url[:4].lower() == 'http') and (url is not None) and (f is not None):
                            print('came in')
                            response = session.get('{}'.format(url))
                            #print(response.content)
                            #filename = "{}/{}.{}".format(dir1, f, ext)
                            f = "{}-{}".format(thread_no, f)
                            akiba[thread_no]['etc_images'].append(f)
                            filename = "{}/{}".format(dir1, f)
                            print('saving from {} to {}'.format(url, filename))
                            with open(filename, "wb") as w:
                                w.write(response.content)
            if len(akiba[thread_no]['etc_images']):
                akiba[thread_no]['main_image'] = akiba[thread_no]['etc_images'][0]
        print(akiba[thread_no])
    print(akiba)


    print('\n\n################### ended current page ######################\n\n')

    # 다음페이지 탐색
    if next_page_link is None:
        break

    print('starting page-{}'.format(next_page_num))
    print(next_page_link_url)
    drv.get(next_page_link_url)
    
print('!!!!!!!!!!!!!!!!  Come to last page. completed!!!!!!!!!!!!!!!!!')
    


