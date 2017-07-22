from instapush import App

def push():
    app = App(appid = '595713a2a4c48ae3b8b70aa0', secret = '78fbc7d58e750b37773b3dbd13c967c5')
    app.notify(event_name = 'alarm', trackers={'msg': '하핫'})


if __name__ == "__main__":
    push()
