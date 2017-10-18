import time, datetime
from peewee import *
from playhouse.apsw_ext import *



db = APSWDatabase('akiba.db', timeout = 300000)

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


with db.atomic():
    #entry = Akiba.select().limit(3)
    entry = Akiba.select()
    for e in entry:
        try:
            print(e.date)
            #conv = datetime.datetime.strptime(e.date, '%b %d, %Y at %I:%M %p').strftime('%Y-%m-%d %H:%M:%S')
            #print('{} ---> {}'.format(e.date, conv)) 
            #e.date = conv
            #e.save()
        except:
            pass
   
