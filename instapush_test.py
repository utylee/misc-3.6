#import instapush
#from instapush import App
from instapush import Instapush, App
#import pycurl, json

#instapush.

def push_new():
    app = App(appid = '595713a2a4c48ae3b8b70aa0', secret = '78fbc7d58e750b37773b3dbd13c967c5')
    app.notify(event_name = 'alarm', trackers={'msg': '하핫'})
    print('?????')

def instapush(before_num, current_num):
    #json_param = '{"event":"newpost", "trackers":{"keyword":"{}"}}'.format(msg,) 
    #json_param = '{"event":"newpost", "trackers":{"keyword":"%s"}}'%(msg,) 

    #data = json.dumps({"event":"newpost", "trackers":{"message":"16"}})
    msg2 = '.메세지: \n  {}명 --> {}명 '.format(before_num, current_num)
    data = json.dumps({"event":"alarm", "trackers":{"msg":"{}".format(msg2)}})

    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'https://api.instapush.im/v1/post')
    #595713a2a4c48ae3b8b70aa0
    #78fbc7d58e750b37773b3dbd13c967c5
    '''
    c.setopt(pycurl.HTTPHEADER, ['x-instapush-appid: 55ebd764a4c48a0a36d6f13a', \
            'x-instapush-appsecret: f19ad88dce7c5f940831bd12d3965cba', \
            'Content-Type: application/json'])
    '''
    c.setopt(pycurl.HTTPHEADER, ['x-instapush-appid: 595713a2a4c48ae3b8b70aa0', \
            'x-instapush-appsecret: 78fbc7d58e750b37773b3dbd13c967c5', \
            'Content-Type: application/json'])
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, data)
    c.perform()
    print('pushed!')


    #cmds = ["curl", "-X" "POST", "-H", "x-instapush-appid: 55ebd764a4c48a0a36d6f13a", \
            #"-H", "x-instapush-appsecret: f19ad88dce7c5f940831bd12d3965cba", \
            #"-H", "Content-Type: application/json", \
            #"-d", json_param, \
            #"https://api.instapush.im/v1/post"]
    #r = subprocess.check_output(cmds, shell=True, universal_newlines=True)
    #r = subprocess.check_output(cmds, shell=True)
    #print(r)

if __name__ == "__main__":
    #instapush(1,2)
    push_new()
