# sinutils

A Python Utitlity Modules containing various useful functions.

Install
===============

```
 pip install sinutils
```

Usage
===============

```python
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

```

Output:
```
TEST...
TEST...  5% Finish:4/80 Spent:35ms Speed:112/s Left:676ms Status:C3
TEST... 10% Finish:8/80 Spent:80ms Speed:100/s Left:721ms Status:C7
TEST... 15% Finish:12/80 Spent:124ms Speed:96/s Left:704ms Status:C11
TEST... 20% Finish:16/80 Spent:169ms Speed:94/s Left:679ms Status:C15
TEST... 25% Finish:20/80 Spent:218ms Speed:91/s Left:656ms Status:C19
TEST... 30% Finish:24/80 Spent:266ms Speed:90/s Left:621ms Status:C23
TEST... 35% Finish:28/80 Spent:313ms Speed:89/s Left:583ms Status:C27
TEST... 40% Finish:32/80 Spent:359ms Speed:89/s Left:539ms Status:C31
TEST... 45% Finish:36/80 Spent:405ms Speed:89/s Left:495ms Status:C35
TEST... 50% Finish:40/80 Spent:453ms Speed:88/s Left:453ms Status:C39
TEST... 55% Finish:44/80 Spent:497ms Speed:88/s Left:406ms Status:C43
TEST... 60% Finish:48/80 Spent:543ms Speed:88/s Left:362ms Status:C47
TEST... 65% Finish:52/80 Spent:588ms Speed:88/s Left:316ms Status:C51
TEST... 70% Finish:56/80 Spent:632ms Speed:89/s Left:270ms Status:C55
TEST... 75% Finish:60/80 Spent:677ms Speed:89/s Left:225ms Status:C59
TEST... 80% Finish:64/80 Spent:724ms Speed:88/s Left:181ms Status:C63
TEST... 85% Finish:68/80 Spent:773ms Speed:88/s Left:136ms Status:C67
TEST... 90% Finish:72/80 Spent:821ms Speed:88/s Left:91ms Status:C71
TEST... 95% Finish:76/80 Spent:867ms Speed:88/s Left:45ms Status:C75
TEST...100% Finish:80/80 Spent:916ms Speed:87/s Left:0ms Status:C79
TEST Finished Spent:927ms
handle [0, 1, 2, 3, 4]
handle [5, 6, 7, 8, 9]
handle [10, 11]
hi 43311
```

[Click to view more information!](https://github.com/sintrb/sinutils)