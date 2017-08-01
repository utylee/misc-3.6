import sys, os
import datetime
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


db = APSWDatabase( LOCAL + 'akiba.db', timeout=30000)
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
    thread_no = CharField(null = True)         # 동시성 제고를 위해 이 테이블에서는 thread_no를 유니크로 노 설정
    #thread_no = CharField(null = True, unique=True)
    title = CharField(null = True)                          # 제목과 쓰레드 주소도 저장해 놓고 추후 재작업할 수 있게 합니다
    href = CharField(null = True)                           # 제목과 쓰레드 주소도 저장해 놓고 추후 재작업할 수 있게 합니다
    code = CharField(null = True)
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
    #with db.get_conn():
    with db.atomic():
        db.create_tables([Akiba, Hanging])
except:
    pass

try:
    #with db.get_conn():
    with db.atomic():
        db.create_tables([Hanging])
except:
    pass


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
print(' >>>>>>>>>>>> \n starting from page - {}\n.url:{}'.format(start_page_num, url))
drv.get(url)
print('.fetched page')

#drv.save_screenshot('/mnt/c/Users/utylee/out.png')
#t = drv.page_source
#t = drv.get_attribute('innerHTML')

# requests다운로드를 위해 webdriver쿠키를 미리 전달해 놓습니다
session = requests.Session()
cookies = drv.get_cookies()
for c in cookies:
    session.cookies.set(c['name'], c['value'])



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
    # 각 쓰레드의 마지막 포스트의 시간들을 가져옵니다. 이를 통해 이미 완료된 쓰레드임에도 변경이 필요한지 결정할 수 있습니다
    date_l = drv.find_elements_by_xpath("//li/div/dl[@class = 'lastPostInfo']/dd/a/*[@class = 'DateTime']")
    li_urls = []
    #title = ""


    # Hanging중인 토렌트를 먼저 작업하기 위해 매페이지마다 처음에 껴 넣어놓습니다 
    print('\n\n try processing Hanging thread...\n\n')
    #with db.get_conn():
    ct1 = datetime.datetime.now()
    with db.atomic():
        entrys = Hanging.select().where(Hanging.processing == '1')
    ct2 = datetime.datetime.now()
    delta = ct2 - ct1
    print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))
    if len(entrys):
        for query in entrys:
            #with db.get_conn():
            with db.atomic():
                q_pid = query.pid
                q_href = query.href
            if q_pid in get_akiba_proc_list():
                continue
            else:
                print('.hanging found! : added to list.\n\thref: {}'.format(q_href))
                #li_urls.append(q_href)
                li_urls.append((q_href, None))

                # 또한 processing 이 0으로 변경된 경우의 오류를 방지하기 위해 각 akiba의 processing도 1로 재설정 해줍니다
                #with db.get_conn():
                ct1 = datetime.datetime.now()
                with db.atomic():
                    #t_thread_no = query.thread_no
                    Akiba.update(processing = '1').where(Akiba.thread_no == query.thread_no).execute()
                ct2 = datetime.datetime.now()
                delta = ct2 - ct1
                print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))

    # DateTime 도 loop로 같이 넘겨줘 매 쓰레드 로딩없이 작업여부를 판단할 수 있게끔 합니다
    idate = 0
    for i in l:
        href = i.get_attribute('href')
        # 일관되게 관리하기 위해 항상 title을 가져오게끔 변경하였습니다
        date_s = date_l[idate].get_attribute('title')
        #date_s = date_l[idate].get_attribute('data-time')
        # 꽤 오랜 쓰레드일 경우 시간을 자세히 표기않고 간략하게 표현하느라 해당 attribute가 없는 경우가 있습니다
        #if date_s is None:
            #date_s = date_l[idate].get_attribute('title')

        #li_urls.append("{}/{}".format(ROOT, href))
        #li_urls.append(href)
        li_urls.append((href, date_s))
        idate = idate + 1

    print(li_urls)

    # 페이지내의 thread별 반복 프로세스
    print('\n\nvisit each threads...')
    for l in li_urls:        # l 은 href가 각각들어있습니다
        download_err_num = 0

        # entry 초기화 후 
        code = title = thread_no = href = None 
        entry = dict.fromkeys(key for key in keys)

        # thread_no 를 파싱해 옵니다
        print('\n\n . 현재 쓰레드 li_urls(cur):{}'.format(l))
        m = re.search('threads/.*\.*(\d{7})/', l[0])
        # thread_no에서 에러가 나면 당장은 저장할 방법이 없기에 확인하기 위해 try로 감싸지 않습니다. 
        thread_no = m.group(1) 
        print('\n.thread_no : {}'.format(thread_no))

        entry['etc_images'] = []
        entry['torrents'] = []
        entry['thread_no'] = thread_no
        href = l[0]
        entry['href'] = href

        # 가장 먼저 db에서 정보를 가져와 processing 중인지를 판단합니다.
        # processing 중이 아니라면 사용중이라고 설정해주고 작업을 시작합니다
        # 사실 이부분이 알고리즘 상 좀 weak point 이긴 합니다. 겹쳐지면서 그냥 지나치는 오류 발생 가능성이 있습니다
        processing = '0'
        has = '0'
        c_flag = 0
        #with db.get_conn():
        with db.atomic():
        #with db.connect():
            #with db.atomic():
            entrys = Akiba.select().where(Akiba.thread_no == thread_no)
        # 해당 thread_no 가 존재할 경우, processing 과 already의 설정을 보고 pass할지를 결정합니다
        if len(entrys):
            for query in entrys:
                #with db.get_conn():
                with db.atomic():
                    processing = query.processing 
                    has = query.already_has
                if processing == '1':
                    # 간혹 hanging 테이블에 entry 생성이전에 다른애가 진입하는 경우가 있는 것 같습니다
                    # 그럴경우 hanging 테이블에 여기서 pid만 변경해서 임시로 생성후 강제종료된 hanging으로 가정하고 진행합니다
                    try:
                        #with db.get_conn():
                        with db.atomic():
                            hang_query = Hanging.select().where(Hanging.thread_no == thread_no).get()
                    except:
                        # pid 에 '0'을 넣어주어 pass되지 않도록 합니다
                        d = {'thread_no': thread_no, 'title': None, 'href': href, 'processing': '1', 'pid': '0'}
                        ct1 = datetime.datetime.now()
                        with db.atomic():
                            Hanging.insert_many([d]).execute()
                        ct2 = datetime.datetime.now()
                        delta = ct2 - ct1
                        print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))
                        #with db.get_conn():
                        with db.atomic():
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
                        #with db.get_conn():
                        ct1 = datetime.datetime.now()
                        with db.atomic():
                            hang_query.pid = '{}'.format(os.getpid())
                            hang_query.save()
                        ct2 = datetime.datetime.now()
                        delta = ct2 - ct1
                        print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))
                        c_flag = 0
                        break

                # 완료 플래그가 설정되어 있더라도, date가 변경이 있으면 플래그를 다시 재설정하고 재작업을 해야합니다
                elif has == '1':
                    #with db.get_conn():
                    with db.atomic():
                        db_date = query.date
                    if db_date == l[1]:
                        print('================\n 이미 완료된 쓰레드입니다. pass 합니다')
                        print('================\n')
                        c_flag = 1
                        break
                    # 현 쓰레드의 date가 db의 값과 달라졌을 경우, 패스하지 않고 그대로 재진행합니다
                    else:
                        print('\n\n* * * * * * * * *')
                        print('\n새글이지만 db에 이전글이 있는 경우입니다')
                        print('포스트가 새로 덧붙여졌을 수 있습니다. 혹은 시간 저장에 오류가 있었을 수도 있습니다')
                        print('작업을 이어서 진행하겠습니다')
                        print('* * * * * * * * *\n\n')
                        # Akiba.processing을 1로 바꾸어 놓고 Hanging에도 추가를 별도로 특별히 해주어야 하는 경우입니다
                        #with db.get_conn():
                        ct1 = datetime.datetime.now()
                        with db.atomic():
                            query.processing = '1'
                            query.save()
                        ct2 = datetime.datetime.now()
                        delta = ct2 - ct1
                        print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))
                        d = {'thread_no': thread_no, 'title': None, 'href': href, 'processing': '1', 'pid': os.getpid()}

                        ct1 = datetime.datetime.now()
                        with db.atomic():
                            Hanging.insert_many([d]).execute()
                        ct2 = datetime.datetime.now()
                        delta = ct2 - ct1
                        print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))

                        c_flag = 0
                        break

                else:
                    ct1 = datetime.datetime.now()
                    #with db.get_conn():
                    with db.atomic():
                        query.processing = '1'
                        query.save()
                    ct2 = datetime.datetime.now()
                    delta = ct2 - ct1
                    print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))
            if c_flag:
                continue

        # 해당 thread_no 의 entry가 존재하지 않을 경우, processing에 1을 넣은 채 entry를 생성합니다
        # 또한 hanging 테이블에도 해당 entry를 삽입합니다
        else:
            d = {'thread_no': thread_no, 'title': None, 'href': href, 'processing': '1', 'pid': os.getpid()}
            ct1 = datetime.datetime.now()
            with db.atomic():
                Hanging.insert_many([d]).execute()
            ct2 = datetime.datetime.now()
            delta = ct2 - ct1
            print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))

            entry['processing'] = '1' 
            print('\n삽입전 entry:\n{}'.format(entry))

            # 거의 동시에 두 프로세스가 모두 통과되어 생성 프로세스에 진입하는 경우가 발견되었습니다
            # 두번째 프로세스는 unique 키 삽입 에러가 발생하게 되므로 일단 통과시키되,
            # err_num 을 표시해 Hanging 테이블에 흔적을 남기게끔 합니다
            # 추후 실행시 다시 챙길 수 있도록..
            try:
                ct1 = datetime.datetime.now()
                with db.atomic():
                    Akiba.insert_many([entry]).execute()
                ct2 = datetime.datetime.now()
                delta = ct2 - ct1
                print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))
            except:
                download_err_num = download_err_num + 1


        # 해당 쓰레드를 로딩합니다
        print('\n\n.loading current thread')
        drv.get(l[0])

        # title attribute
        # title bar 항목이 없는 쓰레드도 발견되었습니다. akiba 예전 db를 자기들이 복구하면서 생긴 문제들일까요?
        try:
            title = drv.find_element_by_xpath('//div[@class="titleBar"]/h1').get_attribute('innerHTML')
            entry['title'] = title
        except:
            entry['title'] = 'error while get xpath:titleBar'

        print('title : {}'.format(title))
        ct1 = datetime.datetime.now()
        #with db.get_conn():
        with db.atomic():
            Hanging.update(title = title).where(Hanging.thread_no == thread_no).execute()
        ct2 = datetime.datetime.now()
        delta = ct2 - ct1
        print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))

        # code atrribute
        m = re.search('\[(.*)\]', title) 
        if m is not None: code = m.group(1)
        entry['code'] = code
        print('code : {}'.format(code))
        ct1 = datetime.datetime.now()
        #with db.get_conn():
        with db.atomic():
            Hanging.update(code = code).where(Hanging.thread_no == thread_no).execute()
        ct2 = datetime.datetime.now()
        delta = ct2 - ct1
        print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))

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

        #if akiba[thread_no]['already_has'] == '1':

        #akiba[thread_no]['etc_images'] = []
        #akiba[thread_no]['torrents'] = []

        print('\n{} thread url : {}'.format(thread_no, l[0]))
        print('\nfetching...')

        # date 찾기
        '''
        l = drv.find_element_by_xpath("//*[@class='DateTime']")
        m = l.get_attribute('data-time')
        # 꽤 오랜 쓰레드일 경우 시간을 자세히 표기않고 간략하게 표현하느라 해당 attribute가 없는 경우가 있습니다
        if m is None:
            m = l.get_attribute('title')
        #akiba[thread_no]['date'] = m
        entry['date'] = m
        '''

        # None일 경우 hanging 목록이라 그런거라서 본문중 가장 마지막 날짜를가져옵니다 
        if l[1]:
            entry['date'] = l[1]
        else:
            l_date = drv.find_elements_by_xpath("//*[@class='DateTime']")
            entry['date'] = l_date[len(l_date) - 1].get_attribute('title')


        # text 찾기
        # text가 없는 오류 글도 있어서 에러가 발생했습니다
        try:
            msg_l = drv.find_element_by_xpath("//blockquote[starts-with(@class, 'messageText')]")
            t = msg_l.get_attribute('innerHTML')
        except:
            print('.messageText get exception')
            t = 'no text'

        print('.text:\n{}'.format(t))


        # main_image 저장 및 지정 추가 image는 etc_images 에 넣는 프로세스
        im = drv.find_elements_by_xpath("//blockquote[starts-with(@class, 'messageText')]/*/*/img\
                                        |//blockquote[starts-with(@class, 'messageText')]/*/img\
                                        |//blockquote[starts-with(@class, 'messageText')]/img")
        print('.text내의 <img> 개수 (im size) : {}'.format(len(im)))
        download_err = False
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
                # 썸네일 등 이미지 주소가 바로 다운로드가 안된다던가 주소가 없어졌다던가 하는 경우가 잇는 것 같습니다
                try:
                    response = session.get(href)
                except:
                    print('except on downloading images')

                r_ok = 0
                write_filename = filename
                for re_try in range(1,10):
                    try:
                        #write_filename = "{}/{}".format(dir1, f)
                        print('({})filename : {}'.format(re_try, write_filename))
                        with open(write_filename, "wb") as w:
                            w.write(response.content)
                        r_ok = 1
                        break
                        
                    except:
                        write_filename = filename + str(re_try)

                if r_ok != 1:
                    download_err = True
                    download_err_num = download_err_num + 1


                #try:
                    #with open(filename, "wb") as w:
                        #w.write(response.content)
                #except:
                    #print('file saving exception')
                    ##print(' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                    ##print(' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                    ##print('.exception while downloading!!! \n proceed to next Thread') 
                    ##print(' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                    ##print(' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                    #download_err = True
                    #download_err_num = download_err_num + 1
                    ##일단 작업은 그대로 진행하게끔 변경합니다
                    #break
        #if download_err:
            #continue


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
        download_err = False
        for a in attach:
            outer = a.get_attribute('outerHTML')
            m1 = re.search('href=\"(.*\.\d+/*)\"', outer)
            href = m1.group(1)
            print('outer: {}'.format(outer))
            print('href: {}'.format(href))

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
                m = re.search('(\w+)\.\d{3,8}/',href)  # 잘 못찾아내는 감이 있어서 좀 더 세밀하게 지정해줘봅니다
                ext = m.group(1)
                f = re.search('attachments/(.*\.\d+)', href).group(1) + '.' + ext
                entry['etc_images'].append(f)
                dir1 = REMOTE + 'static/images'

            # 해당 파일 다운로드
            try:
                response = session.get('{}/{}'.format(ROOT, href))
                print(len(response.content))
            except:
                print('exception on downloading!!')

            #try:
            filename = "{}/{}".format(dir1, f)
            r_ok = 0
            write_filename = filename
            for re_try in range(1,10):
                try:
                    #write_filename = "{}/{}".format(dir1, f)
                    print('filename : {}'.format(write_filename))
                    with open(write_filename, "wb") as w:
                        w.write(response.content)
                    r_ok = 1
                    break
                    
                except:
                    write_filename = filename + str(re_try)

            if r_ok != 1:
                download_err = True
                #일단 작업은 끝까지 진행시켜 봅니다
                download_err_num = download_err_num + 1

            #except:
                #print('exception on Saving!')
                #print(' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                #print(' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                #print('.exception while downloading!!! \n proceed to next Thread') 
                #print(' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                #print(' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
                #download_err = True
                # 일단 작업은 끝까지 진행시켜 봅니다
                #download_err_num = download_err_num + 1
                #break

        #if download_err:
            #continue

        # 본문에 메인 이미지설정이 없어서 main image가 비어있는 경우에 대한 특별 관리입니다
        #if akiba[thread_no]['main_image'] is None:
        if entry['main_image'] is None:
            #해당 프로세스를 이미 main_image 처리중 추가해 놓았습니다
            # 첨부 이미지가 있는 경우 첨부이미지 첫번째를 메인으로 사용합니다
            if len(entry['etc_images']):
                entry['main_image'] = entry['etc_images'][0]
            #if len(akiba[thread_no]['etc_images']):
                #akiba[thread_no]['main_image'] = akiba[thread_no]['etc_images'][0]


        # title, thread_no, (main_image?), torrent 가 있으면 ok 사인을 표시해 놓습니다
        if (entry['title'] is not None) and \
            (entry['torrents'] is not None):
            entry['already_has'] = 1

        # download 에러등의 exception 이 발생했을 경우, processing 플래그를 그대로 1로 설정해 놓습니다
        if download_err_num:
            entry['processing'] = '1'
        else:
            entry['processing'] = '0'

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
        #with db.get_conn():
        #with db.connect():
        ct1 = datetime.datetime.now()
        with db.atomic():
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
        ct2 = datetime.datetime.now()
        delta = ct2 - ct1
        print('### database processing time : {}.{}'.format(delta.seconds, delta.microseconds))

        if download_err_num == 0:
            #with db.get_conn():
            with db.atomic():
                Hanging.delete().where(Hanging.thread_no == thread_no, Hanging.pid == os.getpid()).execute()

        print('\ndb processes succeeded! ')
            
    #print(akiba)

    print('\n\n\n\n\n\n\n\n\n################### ended current page ######################\n\n\n\n\n\n\n\n\n\n\n')

    # 다음페이지 탐색
    if next_page_link is None:
        break

    print('\n\n.starting page-{}\n.loading current page'.format(next_page_num))
    print(next_page_link_url)


    # clear the phantomjs cache 
    drv.execute_script('localStorage.clear();')
    drv.get(next_page_link_url)
    
print('!!!!!!!!!!!!!!!!  Come to last page. completed!!!!!!!!!!!!!!!!!')
    


