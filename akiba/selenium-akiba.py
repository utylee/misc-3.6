from selenium import webdriver
from bs4 import BeautifulSoup
import time, re
import requests
from peewee import *
# google translate 를 위한
from trans import *
from playhouse.apsw_ext import *

def errhandle(e):
    print('\n\ndb called {} times'.format(e))
    return True

URL = 'https://www.akiba-online.com'
ROOT = 'https://www.akiba-online.com'
#LOCAL = '/mnt/c/Users/utylee/'
#LOCAL = '/home/pi/.virtualenvs/misc/src/akiba/'
LOCAL = '/home/pi/media/3001/30-flask/python/selenium/akiba/'
username = 'seoru'
password = 'akibaqnwk11'
start_page_num = 90
#start_page_num = 50
#DEBUG = True
DEBUG = False

# akiba dict의 key들 입니다
keys = ['thread_no', 'title', 'title_ko', 'date', 'href', 'code', 'main_image', 'etc_images', 
        'text', 'torrents', 'guess_quality', 'tag', 'already_has']
entry = dict.fromkeys(key for key in keys)
akiba = {}                          # {'글번호': 'entry dict'}

# db 관련 생성 및 초기화

#db = SqliteDatabase('akiba.db')
#db = SqliteDatabase( LOCAL + 'akiba.db')
db = APSWDatabase( LOCAL + 'akiba.db', timeout=3000)
#db = APSWDatabase( LOCAL + 'apsw.db')

class Akiba(Model):
    #thread_no = CharField(primary_key=True)         # 쓰레드 넘버입니다 href 제일 마지막 부분 숫자 아닌가 추측합니다
    thread_no = CharField(null = True)         # 쓰레드 넘버입니다 href 제일 마지막 부분 숫자 아닌가 추측합니다
    title = CharField(null = True)             # 각 페이지의 제목입니다
    title_ko = CharField(null = True)          # 각 페이지의 번역한 제목입니다
    date = CharField(null = True)              # 글의 생성 날짜입니다
    href = CharField(null = True)              # 글의 쓰레드 주소입니다
    code = CharField(null = True)              # 품번명입니다
    main_image = CharField(null = True)        # 메인 이미지의 이름입니다
    etc_images = CharField(null = True)        # 상세 이미지들을 ; 로 구분하여 이름들을 저장합니다
    text = TextField(null = True)              # 글의 내용을 html 형식으로 그대로 갖고 있습니다
    torrents = CharField(null = True)           # 토렌트 파일의 이름입니다
    guess_quality = CharField(null = True)     # 화질을 글의 내용이나 용량을 통해 추측합니다
    tag = CharField(null = True)               # tag 등을 ;로 구분하여 저장합니다
    already_has = CharField(null = True)       # 이미 성공적으로 긁어오기가 긁어온 쓰레드임을 표시합니다

    class Meta:
        database = db

#Connection(db)
db_con = apsw.Connection(LOCAL + 'akiba.db')
#db_con = apsw.Connection(db)
#db.connect()
#print(db_con)
db_con.setbusytimeout(3000)
db_con.setbusyhandler(errhandle, e)


#이미 db table이 생성되었을 경우, 에러가 날 때를 대비해 try 합니다
try:
    db.create_tables([Akiba])
except:
    pass

# 임시
if DEBUG:
    print('debug')
    r = Akiba.select()
    for i in r:
        print("{}, {}, {}, \n {}, \n{}, {}, {}".format(i.thread_no, i.title, i.title_ko,
                                    i.text, i.main_image, i.torrents,i.already_has))


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

print('click "yes i have id"')
l = drv.find_element_by_xpath("//input[@id='ctrl_pageLogin_registered'][@name='register']")
l.click()
print('input password')
l = drv.find_element_by_xpath("//input[@id='ctrl_pageLogin_password'][@name='password']")
l.send_keys(password)
print('click "login" button')
l = drv.find_element_by_xpath("//div[@class='xenOverlay']/form/dl/dd/input[@class='button primary'][@value='Log in']")
print('sleep 1')
time.sleep(1)
#print('shot')
#drv.save_screenshot('/mnt/c/Users/utylee/out.png')
l.click()
#time.sleep(4)
#print('shot')
#drv.save_screenshot('/mnt/c/Users/utylee/out.png')


# Jav torrent 클릭
l = drv.find_element_by_xpath("//a[.='JAV Torrents']")
print('clicking JAV Torrents')
l.click()

#start_page_num 이 지정되어 있다면 해당 페이지로 다시 로딩
url = '{}/page-{}'.format(drv.current_url, start_page_num) 
print(' >>>>>>>>>>>> \n starting from page - {}'.format(start_page_num))
drv.get(url)

#drv.save_screenshot('/mnt/c/Users/utylee/out.png')
#t = drv.page_source
#t = drv.get_attribute('innerHTML')

# requests다운로드를 위해 webdriver쿠키를 미리 전달해 놓습니다
session = requests.Session()
cookies = drv.get_cookies()
for c in cookies:
    session.cookies.set(c['name'], c['value'])

#o = drv.find_elements_by_xpath("//li[@class='discussionListItem visible*'][not(@class='*sticky ')]")
#o = drv.find_elements_by_xpath("//li[contains(@class, 'discussionListItem visible')]")
#l = drv.find_element_by_xpath("//a[@class='PreviewTooltip'][contains(@href, '1747531')]")

'''
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
    '''


# 페이지별 반복 프로세스
while True:
    # 다음페이지주소를 미리 얻어놓습니다
    next_page_link = drv.find_element_by_xpath("//div[@class='PageNav']/nav/a[@class='text'][contains(text(), 'Next')]")
    print('\n\nnext_page_link : {}'.format(next_page_link))
    if next_page_link is not None:
        n = next_page_link.get_attribute('outerHTML') 
        print(n)
        next_page_link_is = re.search('Next', n) 

        m = re.search('href=\"(.*/page\-(\d+))\"', n)
        next_page_link_url = '{}/{}'.format(ROOT, m.group(1))
        next_page_num = m.group(2)
        print('nexturl: {}, nextnum : {}'.format(next_page_link_url, next_page_num))

    # 페이지 내의 thread list들을 가진 목록을 가져옵니다
    print('fetching current page list items...')
    l = drv.find_elements_by_xpath("//ol/li[not(contains(@class, 'sticky'))]/div/div/h3/a[@class='PreviewTooltip']")
    li_urls = []
    title = ""

    for i in l:
        #entry 초기화
        code = title = thread_no = href = None 
        entry = dict.fromkeys(key for key in keys)

        text = i.get_attribute('outerHTML')
        print(text)
        m = re.search('href=\"(.*)\" title=', text)
        href = m.group(1)
        #m = re.search('\.(.*)/+', href)
        #thread_no = m.group(1)[-7:]
        m = re.search('\.(\d{7})/', href)
        thread_no = m.group(1)
        m = re.search('\">(.*)</a>', text)
        if m is not None: title = m.group(1)
        m = re.search('\[(.*)\]', title) 
        if m is not None: code = m.group(1)

        li_urls.append("{}/{}".format(ROOT, href))
        print("title: {}".format(title))
        entry['thread_no'] = thread_no
        entry['href'] = href
        entry['title'] = title
        #entry['title_ko'] = translate(title, 'ko')
        entry['code'] = code
        akiba[thread_no] = entry
    #print(li_urls)



    # 페이지내의 thread별 반복 프로세스
    print('\n\nvisit each threads...')
    for l in li_urls:

        print('\n\nli_urls(cur):{}'.format(l))
        m = re.search('\.(\d{7})/*', l)
        #thread_no = l[-8:-1]
        thread_no = m.group(1) 
        print('thread_no : {}'.format(thread_no))
        #debug시 시간이 너무 소요돼서 일단 이쪽으로 빼놓음
        #또한 종종 에러가 나서 try 구문을 추가함
        try:
            akiba[thread_no]['title_ko'] = translate(akiba[thread_no]['title'], 'ko')
        except:
            print(' !!! translate error. Passing ')
            pass

        # 해당 thread_no 가 이미 과거에 완료한 항목일 경우 패스합니다
        #with db.transaction():
        #with db.get_conn():
        #with db.atomic():
        with db_con:
        #with db.atomic():
            has = 0
            qresult = Akiba.select().where(Akiba.thread_no == thread_no)
            for query in qresult:
                has = query.already_has
                print('{}.already_has is {}'.format(query.thread_no, query.already_has))
            if has == '1':
                print('\n\n <<< will be passed >> \n')
                continue
        #if akiba[thread_no]['already_has'] == '1':

        akiba[thread_no]['etc_images'] = []
        akiba[thread_no]['torrents'] = []

        print('{} thread url : {}'.format(thread_no, l))
        print('\nfetching...')

        # 해당 쓰레드 html 을 가져옵니다
        drv.get(l)
        #임시
        #https://www.akiba-online.com/threads/pgd-919-shiosannotodeu.1747668/
        #drv.get('https://www.akiba-online.com/threads/pgd-919-shiosannotodeu.1747668/')

        # date 찾기
        #l = drv.find_element_by_xpath("//abbr[@class='DateTime']")
        l = drv.find_element_by_xpath("//*[@class='DateTime']")
        m = l.get_attribute('data-time')
        #t = l.get_attribute('outerHTML')
        #m = re.search('data-time=\"(\d*)\"', t)
        if m is None:
            m = l.get_attribute('title')
        #akiba[thread_no]['date'] = m.group(1)
        akiba[thread_no]['date'] = m

        # text 찾기
        l = drv.find_element_by_xpath("//blockquote[starts-with(@class, 'messageText')]")
        #i = drv.find_element_by_xpath("//img[@class='bbCodeImage']")
        t = l.get_attribute('innerHTML')
        print(t)


        # main_image 저장 및 지정 추가 image는 etc_images 에 넣는 프로세스
        im = drv.find_elements_by_xpath("//blockquote[starts-with(@class, 'messageText')]/*/*/img\
                                        |//blockquote[starts-with(@class, 'messageText')]/*/img\
                                        |//blockquote[starts-with(@class, 'messageText')]/img")
        print('im size : {}'.format(len(im)))
        for i in im:
            href = i.get_attribute('src')
            if href is not '' : 
                print('href : ' + href)
                if href[:4] != 'http':
                    href = ROOT + '/' + href
                spl = href.split('/')
                print(spl)
                print(spl[-1])
                print(spl[-2])
                f = spl[-1]
                if f is '':
                    f = spl[-2]
                print('f :' + f + '.')
                f = f + '.jpg'
                filename = LOCAL + 'static/images/' + f
                if akiba[thread_no]['main_image'] is None: 
                    akiba[thread_no]['main_image'] = f
                    print('downloading main images...')
                else:
                    akiba[thread_no]['etc_images'].append(f) 
                    print('downloading etc images...')
                try:
                    response = session.get(href)
                    with open(filename, "wb") as w:
                        w.write(response.content)
                except:
                    print('exception occurred on downloading...')

        '''
        # main_image 저장 및 지정 추가 image는 etc_images 에 넣는 프로세스
        href = l.get_attribute('src')
        print('href : ' + href)
        #m = re.search('<img.*src=\"(.*\.\d+)/*\"', t)
        #if m is not None : 
        if href is not None : 
            print('came in href')
            #href = m.group(1)
            f = re.search('attachments/(.*jpg\.\d+)/*', href).group(1) + '.jpg'
            print(f)
            akiba[thread_no]['main_image'] = f
            dir1 = 'static/images'
            #response = session.get('{}/{}'.format(ROOT, href))
            response = session.get(href)
            filename = "{}/{}".format(dir1, f)
            print('downloading main images...')
            with open(filename, "wb") as w:
                w.write(response.content)
        '''

        # code 저장
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

            dir1 = LOCAL + 'static/images'
            #ext = 'jpg'
            if re.search('jpg\.\d+',href) is not None:
                f = re.search('attachments/(.*jpg\.\d+)', href).group(1) + '.jpg'
                akiba[thread_no]['etc_images'].append(f)
            elif re.search('torrent\.\d+',href) is not None:
                f = re.search('attachments/(.*torrent\.\d+)', href).group(1) + '.torrent'
                akiba[thread_no]['torrents'].append(f)
                #ext = 'torrent'
                dir1 = LOCAL + 'static/torrents'

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

                        dir1 = LOCAL + 'static/images'
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

        # title, thread_no, main_image, torrent 가 있으면 ok 사인을 표시해 놓습니다
        if (akiba[thread_no]['title'] is not None) and \
            (akiba[thread_no]['main_image'] is not None) and \
            (akiba[thread_no]['torrents'] is not None):
            akiba[thread_no]['already_has'] = 1
        print(akiba[thread_no])

        # db 삽입
        with db_con:
        #with db.transaction():
        #with db.atomic():
        #with db.get_conn():
            # thread_no key는 없기에 db에 통째로 넣기 위해 임시로 막판에 추가
            #akiba[thread_no]['thread_no'] = thread_no
            #Akiba.insert_many(akiba[thread_no]).execute()
            #temp = Akiba.create()
            #temp.insert_many(akiba[thread_no]).execute()
            Akiba.create(
                    thread_no = akiba[thread_no]['thread_no'],
                    title = akiba[thread_no]['title'],
                    title_ko = akiba[thread_no]['title_ko'],
                    date = akiba[thread_no]['date'],
                    href = akiba[thread_no]['href'],
                    code = akiba[thread_no]['code'],
                    main_image = akiba[thread_no]['main_image'],
                    etc_images = akiba[thread_no]['etc_images'],
                    text = akiba[thread_no]['text'],
                    torrents = akiba[thread_no]['torrents'],
                    guess_quality = akiba[thread_no]['guess_quality'],
                    tag = akiba[thread_no]['tag'],
                    already_has = akiba[thread_no]['already_has']
                    )

            #cur_akiba.thread_no = akiba[thread_no]['thread_no']
            #cur_akiba.title = akiba[thread_no]['title']
            #cur_akiba.title_ko = akiba[thread_no]['title_ko']
            #cur_akiba.save()
            print('db insert succeeded! ')
            #Akiba.insert(thread_no = akiba[thread_no]['thread_no']).execute()
            #Akiba.insert(title = akiba[thread_no]['title']).execute()
            #Akiba.insert(title_ko = akiba[thread_no]['title_ko']).execute()
            '''
                # akiba dict의 key들 입니다
                keys = ['thread_no', 'title', 'title_ko', 'date', 'href', 'code', 'main_image', 'etc_images', 
                'text', 'torrents', 'guess_quality', 'tag', 'already_has']
            '''
            #db.close()
            
    print(akiba)


    print('\n\n################### ended current page ######################\n\n')

    # 다음페이지 탐색
    if next_page_link is None:
        break

    print('starting page-{}'.format(next_page_num))
    print(next_page_link_url)
    drv.get(next_page_link_url)
    
print('!!!!!!!!!!!!!!!!  Come to last page. completed!!!!!!!!!!!!!!!!!')
    


