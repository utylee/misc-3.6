#import os.path
import os
import glob
import datetime
import time

# 실행주기(시간)
intv = 24

# list of policy tuple [('pattern-formatted-dir-location', 'how-many-days-olded'), ...]
policys = [
    ('/home/pi/media/4001/21-motion2/*mp4', 15),
    ('/home/pi/media/4001/21-motion2/*avi', 15),
    ('/home/pi/media/4001/21-motion2/*jpg', 15),
    ('/home/pi/media/4001/20-motion/*jpg', 7),
    ('/home/pi/media/4001/22-motion3/*avi', 2),
    ('/home/pi/media/4002/99-data/91-transmission-watch/*added', 200)

    ]

def proc():
    cur = datetime.datetime.now().timestamp()
    for p in policys:
        print(p[0] + '/*', cur)
        #n = glob.iglob(p[0] + '/*')
        n = glob.iglob(p[0])
        for it in n:
            diff = cur - os.path.getctime(it)
            #print(os.path.getctime(it), cur)
            if (diff > p[1] * 86400):
                print(it)
                os.remove(it)
    

if __name__ == "__main__":
    while True:
        proc()
        time.sleep(3600 * intv) 
