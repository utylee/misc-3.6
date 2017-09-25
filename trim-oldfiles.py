#import os.path
import os
import glob
import datetime
import time

# 실행주기(시간)
intv = 24

# list of policy tuple [('pattern-formatted-dir-location', 'how-many-days-olded'), ...]
policys = [
    ('/home/odroid/media/3001/21-motion2/*mp4', 15),
    ('/home/odroid/media/3001/21-motion2/*jpg', 15),
    ('/home/odroid/media/3001/22-motion3/*avi', 2),

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
