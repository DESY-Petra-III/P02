#!/bin/env python

import urllib2
import json
from json import JSONDecoder

url = "https://ics.desy.de//tineinterface.php?action=readall&deviceName=%s"
tlist = ["G02_1_AStartSrch", "G02_1_AbrkIntrlk", "closeABS_BS02_0", "openABS_BS02_0"]

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