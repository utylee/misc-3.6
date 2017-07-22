
import os
import re

# 특정 문구를 포함한 pid 리스트들을 반납합니다
def get_akiba_proc_list():
    l = []
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            with open(os.path.join('/proc', pid, 'cmdline'), 'rb') as r:
                m = re.search('selenium-akiba\.py', r.read().decode())
                if m is not None:
                    l.append(pid)
                #l.append((pid, r.read().decode()))
        except:
            pass

    return l
