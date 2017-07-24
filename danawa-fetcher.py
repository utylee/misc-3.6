from selenium import webdriver
import re, datetime
from instapush import App
import asyncio
from peewee import *
from playhouse.apsw_ext import *


# 인터벌 (초)
INTERVAL = 11800 

db = APSWDatabase('prices.db')

class Price(Model):
    date = CharField(null=True)
    localdate = CharField(null=True)
    title = CharField(null=True)
    price = CharField(null=True)
    class Meta:
        database = db

def init():
    try:
        with db.get_conn():
            db.create_tables([Price])
    except:
        pass

async def main():
    init()
    app = App(appid = '5972ed6da4c48a4118de80b2', secret = '3acda6333f7422e45f24ecbc5aa971d5')
    print("loading webdriver...")
    drv = webdriver.PhantomJS()
    while True:
        print("fetching danawa...")
        l = drv.get("http://prod.danawa.com/info/?pcode=1795206&cate=1131401")
        result = drv.find_element_by_xpath('//*[@class="big_price"]')
        date = drv.find_element_by_xpath('//span[@class="product_date"]')
        t = result.text
        t = re.sub(',','',t)
        date = date.text

        print(t)

        with db.get_conn():
            o = Price.select().order_by(Price.id.desc()).limit(3)
        p = []
        for i in o:
            with db.get_conn():
                p.append(i.price)

        if len(p) == 0:
            p.append('0')

        v = int(t) - int(p[-1])

        now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
        d = {'date' : date, 'localdate': now, 'title' : 'Toshiba 3T', 'price' : t}
        #with db.get_conn():
        with db.atomic():
            Price.insert_many([d]).execute()


        msg = "toshiba 3T: {} ( {})\n(<--{}won<---{}won)".format(t, v, p[-1], p[-2])

        # 가격변동이 있을 때만 InstaPushing 합니다
        if v != 0 or int(t) < 90000:
            print('price is different. instapushing!!!')
            app.notify(event_name = 'alarm', trackers={'msg': msg})
        #app.notify(event_name = 'alarm', trackers={'msg': msg})

        
        print('sleep {} secs'.format(INTERVAL))
        # cpu load를 없애기 위함입니다. danawa 페이지 왜저리 자원을 많이 먹죠? ㄷㄷㄷ
        drv.get('192.168.0.1:8888')
        await asyncio.sleep(INTERVAL)
        #sleep(10)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
