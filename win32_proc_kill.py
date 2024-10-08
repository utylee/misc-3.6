import psutil

for proc in psutil.process_iter():
    if proc.name().lower() == 'resolve.exe':
        # print(proc.name())
        ret = proc.kill()
        # print(f'ret: {ret}')

