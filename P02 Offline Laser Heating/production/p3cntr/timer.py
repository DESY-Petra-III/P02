import PyTango
import numpy
import sys
import time

import abstract


class Timer(abstract.TangoDevice):
    def __init__(self,name,desc,tname):
##        super(Timer,self).__init__(self,name,desc,tname)
        super(Timer,self).__init__(name,desc,tname)
