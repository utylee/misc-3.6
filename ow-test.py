# 오버워치 api 테스트입니다

from overwatch_api import *

ow = OverwatchAPI('key')

#print(ow.get_patch_notes())
print(ow.get_stats_all_heroes(PC, KOREA, '부자인생-3741', QUICK))

