import sys, os
from selenium import webdriver
import time, re
import requests
from peewee import *
# google translate 를 위한
from trans import *
from playhouse.apsw_ext import *
from myutils import *


URL = 'https://www.akiba-online.com'
ROOT = 'https://www.akiba-online.com'
#LOCAL = '/mnt/c/Users/utylee/'
LOCAL = '/home/pi/.virtualenvs/misc/src/akiba/'
REMOTE = '/home/pi/media/3001/30-flask/python/selenium/akiba/'
username = 'seoru'
password = 'akibaqnwk11'
start_page_num = 1
#start_page_num = 50
if len(sys.argv) > 1:
    start_page_num = int(sys.argv[1])
#DEBUG = True
DEBUG = False

print('cur : {}'.format(os.getpid()))
'''
def temp():
    #for a  in entry:
        #entry[a] = '2'
        #print(a + ':' + entry[a])
    # 테스트 db 인서트
    #with db.get_conn():
    with db.connect():
        with db.atomic():
            Akiba.insert_many([entry]).execute()
            '''


# akiba dict의 key들 입니다
keys = ['thread_no', 'title', 'title_ko', 'date', 'href', 'code', 'main_image', 'etc_images', 
        'text', 'torrents', 'quality', 'size', 'guess_quality', 'tag', 'already_has', 'processing']
entry = dict.fromkeys(key for key in keys)
akiba = {}                          # {'글번호': 'entry dict'}


db = APSWDatabase( LOCAL + 'akiba.db', timeout=3000)
class Akiba(Model):
    #thread_no = CharField(primary_key=True)         # 쓰레드 넘버입니다 href 제일 마지막 부분 숫자 아닌가 추측합니다
    thread_no = CharField(null = True, unique = True)           # 쓰레드 넘버입니다 href 제일 마지막 부분 숫자 아닌가 추측합니다
    title = CharField(null = True)                              # 각 페이지의 제목입니다
    title_ko = CharField(null = True)                           # 각 페이지의 번역한 제목입니다
    date = CharField(null = True)                               # 글의 생성 날짜입니다
    href = CharField(null = True)                               # 글의 쓰레드 주소입니다
    code = CharField(null = True)                               # 품번명입니다
    main_image = CharField(null = True)                         # 메인 이미지의 이름입니다
    etc_images = CharField(null = True)                         # 상세 이미지들을 ; 로 구분하여 이름들을 저장합니다
    text = TextField(null = True)                               # 글의 내용을 html 형식으로 그대로 갖고 있습니다
    torrents = CharField(null = True)                           # 토렌트 파일의 이름입니다
    quality = CharField(null = True)                            # 화질
    size = CharField(null = True)                               # 파일 용량
    guess_quality = CharField(null = True)                  # 화질을 글의 내용이나 용량을 통해 추측합니다
    tag = CharField(null = True)                            # tag 등을 ;로 구분하여 저장합니다
    already_has = CharField(null = True)                    # 이미 성공적으로 긁어오기가 긁어온 쓰레드임을 표시합니다
    processing = CharField(null = True)                    # 이미 성공적으로 긁어오기가 긁어온 쓰레드임을 표시합니다

    class Meta:
        database = db

# 작업중인 thread 가 작업중 종료되었을 경우를 대비한 관리 db입니다
class Hanging(Model):
    thread_no = CharField(null = True, unique=True)
    processing = CharField(null = True)
    pid = CharField(null = True)                            #해당 쓰레드를 작업중인 프로세스의 pid를 가져옵니다

    class Meta:
        #database = db_hanging
        database = db

# db 관련 생성 및 초기화
#db = SqliteDatabase( LOCAL + 'akiba.db')
#db = APSWDatabase( LOCAL + 'akiba.db', timeout=3000, pragmas=[('journal_mode', 'wal')])
#db_hanging = APSWDatabase( LOCAL + 'processing.db', timeout=3000)

#이미 db table이 생성되었을 경우, 에러가 날 때를 대비해 try 합니다
try:
    with db.get_conn():
        db.create_tables([Akiba, Hanging])
except:
    pass


'''
with db.get_conn():
    hanging_list = []
    entrys = Hanging.select().get()
    if len(entrys):
        for query in entrys:
            hanging_list.append(query.thread_no)
    # hanging 테이블로 부터 processing 이 1로 설정된 Akiba 테이블 내의 thread_no 들을 불러옵니다
    h_thread_no = Akiba.select().where(Akiba.thread_no == 
    '''



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
    #title = ""

    for i in l:
        href = i.get_attribute('href')
        #li_urls.append("{}/{}".format(ROOT, href))
        li_urls.append(href)

        '''
        # entry 초기화
        code = title = thread_no = href = None 
        entry = dict.fromkeys(key for key in keys)

        # thread_no 파싱
        #text = i.get_attribute('outerHTML')
        href = i.get_attribute('href')
        #print(text)
        #m = re.search('href=\"(.*)\" title=', text)
        #href = m.group(1)
        #m = re.search('\.(.*)/+', href)
        m = re.search('\.(\d{7})/', href)
        thread_no = m.group(1)

        # title 과 code 파싱, 
        title = i.get_attribute('innerHTML')
        #m = re.search('\">(.*)</a>', text)
        #if m is not None: title = m.group(1)
        m = re.search('\[(.*)\]', title) 
        if m is not None: code = m.group(1)
        '''
        #li_urls.append("{}/{}".format(ROOT, href))
        '''
        #일단 loop 내부에서 지정하기로 하고 지워놓습니다
        print("title: {}".format(title))
        entry['thread_no'] = thread_no
        entry['href'] = href
        entry['title'] = title
        #entry['title_ko'] = translate(title, 'ko')
        entry['code'] = code
        akiba[thread_no] = entry
        '''
    print(li_urls)

    # 페이지내의 thread별 반복 프로세스
    print('\n\nvisit each threads...')
    for l in li_urls:        # l 은 href가 각각들어있습니다

        # entry 초기화 후 
        code = title = thread_no = href = None 
        entry = dict.fromkeys(key for key in keys)

        # thread_no 를 파싱해 옵니다
        print('\n\n . 현재 쓰레드 li_urls(cur):{}'.format(l))
        m = re.search('\.(\d{7})/*', l)
        thread_no = m.group(1) 
        print('\n.thread_no : {}'.format(thread_no))

        entry['etc_images'] = []
        entry['torrents'] = []
        entry['thread_no'] = thread_no
        href = l
        entry['href'] = href

        # 가장 먼저 db에서 정보를 가져와 processing 중인지를 판단합니다.
        # processing 중이 아니라면 사용중이라고 설정해주고 작업을 시작합니다
        # 사실 이부분이 알고리즘 상 좀 weak point 이긴 합니다. 겹쳐지면서 그냥 지나치는 오류 발생 가능성이 있습니다
        processing = '0'
        has = '0'
        c_flag = 0
        with db.get_conn():
        #with db.connect():
            #with db.atomic():
            entrys = Akiba.select().where(Akiba.thread_no == thread_no)
            # 해당 thread_no 가 존재할 경우, processing 과 already의 설정을 보고 pass할지를 결정합니다
            if len(entrys):
                for query in entrys:
                    processing = query.processing 
                    has = query.already_has
                    if processing == '1':
                        hang_query = Hanging.select().where(Hanging.thread_no == thread_no).get()
                        # 다른 프로세스가 현재 작업중인 게 맞을 경우,
                        hang_id = hang_query.pid
                        akiba_proc_list = get_akiba_proc_list()
                        print('.proc:\n\tdb:{}, akiba:{}, this:{}'.format(hang_id, akiba_proc_list, os.getpid()))
                        if hang_id in akiba_proc_list:
                            print('................\n이미 다른 프로세스가 작업중입니다. pass 합니다')
                            print('................\n')
                            c_flag = 1
                            break
                        # akiba pid목록에 없는 pid가 들어 있을 경우
                        else:
                            print('vvvvvvvvvvvvvvvvvv\n')
                            print('vvvvvvvvvvvvvvvvvv\n')
                            print('vvvvvvvvvvvvvvvvvv\n')
                            print('\n작업 중 종료가 되었던 것 같습니다. 작업을 이어서 진행하겠습니다')
                            print('vvvvvvvvvvvvvvvvvv\n')
                            print('vvvvvvvvvvvvvvvvvv\n')
                            print('vvvvvvvvvvvvvvvvvv\n')
                            hang_query.pid = '{}'.format(os.getpid())
                            hang_query.save()
                            c_flag = 0
                            break

                    elif has == '1':
                        print('================\n 이전에 완료했던 쓰레드입니다. pass 합니다')
                        print('================\n')
                        c_flag = 1
                        break
                    else:
                        query.processing = '1'
                        query.save()
                if c_flag:
                    continue

            # 해당 thread_no 의 entry가 존재하지 않을 경우, processing에 1을 넣은 채 entry를 생성합니다
            # 또한 hanging 테이블에도 해당 entry를 삽입합니다
            else:
                entry['processing'] = '1' 
                print('\n삽입전 entry:\n{}'.format(entry))
                Akiba.insert_many([entry]).execute()
                d = {'thread_no': thread_no, 'processing': '1', 'pid': os.getpid()}
                Hanging.insert_many([d]).execute()

        # 해당 쓰레드를 로딩합니다
        print('\n\n.loading current thread')
        drv.get(l)

        # title attribute
        title = drv.find_element_by_xpath('//div[@class="titleBar"]/h1').get_attribute('innerHTML')
        entry['title'] = title
        print('title : {}'.format(title))

        # code atrribute
        m = re.search('\[(.*)\]', title) 
        if m is not None: code = m.group(1)
        entry['code'] = code
        print('code : {}'.format(code))

        # title_ko attribute
        #debug시 시간이 너무 소요돼서 일단 이쪽으로 빼놓음
        #또한 종종 에러가 나서 try 구문을 추가함
        try:
            #akiba[thread_no]['title_ko'] = translate(akiba[thread_no]['title'], 'ko')
            title_ko = translate(title, 'ko')
            entry['title_ko'] = title_ko
        except:
            print(' !!! translate error. Passing ')
            pass

        '''
        # 해당 thread_no 가 이미 과거에 완료한 항목일 경우 패스합니다
        #with db.transaction():
        #with db_con:
        with db.get_conn():
            with db.atomic():
                has = 0
                qresult = Akiba.select().where(Akiba.thread_no == thread_no)
                print(qresult)
                for query in qresult:
                    has = query.already_has
                    procesesing = query.processing
                    print('{}:\nalready_has is {}\nprocessing is {}'.format(\
                                    query.thread_no, query.already_has, query.processing))
                if (has == '1') or (processing =='1') :
                    print('\n\n <<< ---- will be passed ---- >> \n')
                    continue

                # 혹은 processing 으로 설정된 경우도 패스합니다
                processing = 0
                qresult = Akiba.select().where(Akiba.thread_no == thread_no)
                print(qresult)
                for query in qresult:
                    has = query.already_has
                    print('{}.already_has is {}'.format(query.thread_no, query.already_has))
                if has == '1':
                    print('\n\n <<< will be passed >> \n')
                    continue
                    '''
        #if akiba[thread_no]['already_has'] == '1':

        #akiba[thread_no]['etc_images'] = []
        #akiba[thread_no]['torrents'] = []

        print('{} thread url : {}'.format(thread_no, l))
        print('\nfetching...')

        # date 찾기
        l = drv.find_element_by_xpath("//*[@class='DateTime']")
        m = l.get_attribute('data-time')
        # 꽤 오랜 쓰레드일 경우 시간을 자세히 표기않고 간략하게 표현하느라 해당 attribute가 없는 경우가 있습니다
        if m is None:
            m = l.get_attribute('title')
        #akiba[thread_no]['date'] = m
        entry['date'] = m

        # text 찾기
        l = drv.find_element_by_xpath("//blockquote[starts-with(@class, 'messageText')]")
        t = l.get_attribute('innerHTML')
        print('.text:\n{}'.format(t))

        # main_image 저장 및 지정 추가 image는 etc_images 에 넣는 프로세스
        im = drv.find_elements_by_xpath("//blockquote[starts-with(@class, 'messageText')]/*/*/img\
                                        |//blockquote[starts-with(@class, 'messageText')]/*/img\
                                        |//blockquote[starts-with(@class, 'messageText')]/img")
        print('.text내의 <img> 개수 (im size) : {}'.format(len(im)))
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
                #filename = LOCAL + 'static/images/' + f
                filename = REMOTE + 'static/images/' + f
                if entry['main_image'] is None: 
                    entry['main_image'] = f
                #if akiba[thread_no]['main_image'] is None: 
                    #akiba[thread_no]['main_image'] = f
                    print('downloading main images...')
                # <img>가 여럿일 경우 두번째부터는 etc_images에 저장합니다
                else:
                    #akiba[thread_no]['etc_images'].append(f) 
                    entry['etc_images'].append(f) 
                    print('downloading etc images...')
                # 현재 image 다운로드
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
        #if o is not None : akiba[thread_no]['code'] = o.group(1)
        if o is not None : entry['code'] = o.group(1)

        # text 저장
        # text 를 추출하기 위한 프로세스입니다. <img 관련 태크, \n 태그, \t 태그 등을 제거합니다
        n = re.sub('<img.*\">', '', t)
        n = re.sub('\t', '', n)
        n = re.sub('\n', '', n)
        #akiba[thread_no]['text'] = n 
        entry['text'] = n 

        # 첨부된 etc_images 및 torrents 저장
        print('.save etc_images and torrents...')
        attach = drv.find_elements_by_xpath("//ul[starts-with(@class, 'attachmentList')]/li/div/div/h6/a")
        for a in attach:
            outer = a.get_attribute('outerHTML')
            m1 = re.search('href=\"(.*\.\d+/*)\"', outer)
            href = m1.group(1)
            print(outer)
            print(href)

            if re.search('jpg\.\d+',href) is not None:
                ext = 'jpg'
                f = re.search('attachments/(.*jpg\.\d+)', href).group(1) + '.' + ext
                #akiba[thread_no]['etc_images'].append(f)
                entry['etc_images'].append(f)
                #dir1 = LOCAL + 'static/images'
                dir1 = REMOTE + 'static/images'
            elif re.search('torrent\.\d+',href) is not None:
                ext = 'torrent'
                f = re.search('attachments/(.*torrent\.\d+)', href).group(1) + '.' + ext
                entry['torrents'].append(f)
                #dir1 = LOCAL + 'static/torrents'
                dir1 = REMOTE + 'static/torrents'
            # 혹시 zip이나 다른 확장자일 경우를 대비해 마련해 놓습니다. 뭔가 zip같은 게 나왔던 기억이 있습니다
            else:
                m = re.search('(w+)\.\d+',href) 
                ext = m.group(1)
                f = re.search('attachments/(.*\.\d+)', href).group(1) + '.' + ext
                entry['etc_images'].append(f)
                dir1 = REMOTE + 'static/images'

            # 해당 파일 다운로드
            response = session.get('{}/{}'.format(ROOT, href))
            #print(response.content)
            #filename = "{}/{}.{}".format(LOCAL, href[8:], ext)
            #filename = "{}/{}.{}".format(dir1, f, ext)
            filename = "{}/{}".format(dir1, f)
            with open(filename, "wb") as w:
                w.write(response.content)
        #print(akiba[thread_no])

        # 본문에 메인 이미지설정이 없어서 main image가 비어있는 경우에 대한 특별 관리입니다
        #if akiba[thread_no]['main_image'] is None:
        if entry['main_image'] is None:
            #해당 프로세스를 이미 main_image 처리중 추가해 놓았습니다
            '''
            #첨부 이미지가 하나도 없는 경우, 본문 내 img 태그들 주소를 검색해 모두 다운로드하고 db에 연결합니다
            if not len(entry['etc_images']):
            #if not len(akiba[thread_no]['etc_images']):
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
            '''
            # 첨부 이미지가 있는 경우 첨부이미지 첫번째를 메인으로 사용합니다
            if len(entry['etc_images']):
                entry['main_image'] = entry['etc_images'][0]
            #if len(akiba[thread_no]['etc_images']):
                #akiba[thread_no]['main_image'] = akiba[thread_no]['etc_images'][0]

        # title, thread_no, (main_image?), torrent 가 있으면 ok 사인을 표시해 놓습니다
        if (entry['title'] is not None) and \
            (entry['torrents'] is not None):
            entry['already_has'] = 1
        print(entry)
        '''
        if (akiba[thread_no]['title'] is not None) and \
            #(akiba[thread_no]['main_image'] is not None) and \
            (akiba[thread_no]['torrents'] is not None):
            akiba[thread_no]['already_has'] = 1
        print(akiba[thread_no])
        '''

        # Akiba 테이블에 완성된 entry삽입, 또한 Hanging 테이블에서 해당 thread_no 엔트리는 삭제
        #with db_con:
        #with db.transaction():
        with db.get_conn():
        #with db.connect():
            #with db.atomic():

            # thread_no key는 없기에 db에 통째로 넣기 위해 임시로 막판에 추가
            #akiba[thread_no]['thread_no'] = thread_no
            entry['processing'] = '0'
            Akiba.update(title = entry['title'], \
                        title_ko = entry['title_ko'],\
                        date = entry['date'],\
                        code = entry['code'],\
                        main_image = entry['main_image'],\
                        etc_images = entry['etc_images'],\
                        text = entry['text'],\
                        torrents = entry['torrents'],\
                        quality = entry['quality'],\
                        size = entry['size'],\
                        guess_quality = entry['guess_quality'],\
                        already_has = entry['already_has'],\
                        processing = entry['processing']
                        ).where(Akiba.thread_no == thread_no).execute()

            #Akiba.insert_many([entry]).execute()
            #Akiba.insert_many(akiba[thread_no]).execute()
            ''' 
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
                    processing = 0
                    )
                    '''
            Hanging.delete().where(Hanging.thread_no == thread_no).execute()

        print('db insert succeeded! ')
            
    #print(akiba)

    print('\n\n\n\n\n\n\n\n\n################### ended current page ######################\n\n\n\n\n\n\n\n\n\n\n')

    # 다음페이지 탐색
    if next_page_link is None:
        break

    print('starting page-{}'.format(next_page_num))
    print(next_page_link_url)
    drv.get(next_page_link_url)
    
print('!!!!!!!!!!!!!!!!  Come to last page. completed!!!!!!!!!!!!!!!!!')
    


