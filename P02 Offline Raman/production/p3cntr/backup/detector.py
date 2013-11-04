import PyTango
import numpy
import sys
import time

import counter


class Detector(counter.Counter):
    def __init__(self,name,desc,tname):
##        super(Detector,self).__init__(self,name,desc,tname)
        super(Detector,self).__init__(name,desc,tname)
        
##
##    def clear(self):
##        self._proxy.command_inout("clear")
####
####    def start(self):
####        self._proxy.command_inout("Start")
####
####    def stop(self):
####        self._proxy.command_inout("Stop")


class PointDetector(Detector):
    pass


class MCA(Detector):

    def read(self):
        sraw = self._proxy.read_attribute("Spectrum").value
        return numpy.array(sraw,dtype=numpy.float)


class CCD(Detector):
    pass





