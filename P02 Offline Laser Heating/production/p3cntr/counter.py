import PyTango
import numpy
import sys
import time

import abstract


class Counter(abstract.TangoDevice):
    def __init__(self,name,desc,tname):
##        super(Counter,self).__init__(self,name,desc,tname)
        super(Counter,self).__init__(name,desc,tname)
        

    def clear(self):
        self._proxy.command_inout("clear")

    def read_data(self):
        data = self._proxy.read_attribute("Value")
        return data.value


