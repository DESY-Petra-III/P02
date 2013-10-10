#!/bin/env python

import urllib2
import json
from json import JSONDecoder

#breaking interlock
urlconfirm = "https://ics.desy.de//tineinterface.php?action=confirm&deviceName=%s"
urlbreak = "https://ics.desy.de//tineinterface.php?action=write&deviceName=%s"
tlist = ["openBS02B_1"]


# simply https://ics.desy.de//tineinterface.php?action=write&deviceName=G02_1_AbrkIntrlk
# does not work - gives no permission

for v in tlist:
#    turl = urlconfirm % v
#    print(turl)
#    res = urllib2.urlopen(turl)
#    print(res.read())
    turl = urlbreak % v
    print(turl)
    res = urllib2.urlopen(turl)
    print(res.read())