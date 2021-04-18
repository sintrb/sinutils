# -*- coding: UTF-8 -*
'''
Created on 2021-04-16
'''
from __future__ import print_function
import time

import sinutils

# 进度显示
count = 80
with sinutils.Progress(total=count, title='TEST') as pg:
    for i in range(count):
        pg.feed(status='C%d' % i)
        time.sleep(.01)


# 任务分割器
def doit(datas):
    print('handle', datas)


with sinutils.Feeder(doit, 5) as fd:
    for i in range(12):
        fd.feed(i)

# watch modules
import testm

testm.test()
mw = sinutils.ModulesWatcher([testm])
while True:
    # edit testm.py to test auto_reload function
    mds = mw.auto_reload()
    if mds:
        print('changed', mds)
        testm.test()
    time.sleep(1)
