#!/bin/env python

import urllib2
import json
from json import JSONDecoder

url = "https://ics.desy.de//tineinterface.php?action=readall&deviceName=%s"
tlist = ["G02B_2_AStartSrch", "G02B_2_AbrkIntrlk", "closeBS02B_1", "openBS02B_1"]

def hook(d):
    for k in d.keys():
	print(" key: %s; value: %s"%(k, d[k]))

for v in tlist:
    turl = url % v
    res = urllib2.urlopen(turl)
    print(res)
    read = res.read()
    decoder = JSONDecoder(encoding="ascii",  parse_int=int)
    print(decoder.decode(read))