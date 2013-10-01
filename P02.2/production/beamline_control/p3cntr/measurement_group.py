import PyTango
from counter import *
from detector import *
from timer import *
import time

class MeasurementGroup():
    def __init__(self,timer,counters,detectors):
        
        if isinstance(timer,Timer):
            self.timer = timer
        elif isinstance(timer,list):
            self.timer = Timer(timer[0],timer[1],timer[2])
        else:
            print "Can not use ",timer
            print "Wrong type:", type(timer)
            print "Should be Timer-Object or List of string(Name,Description,TangoDeviceName)"
        
        self.counters = []
        for counter in counters:
            if isinstance(counter,Counter):
                self.counters += [counter]
            elif isinstance(counter,list):
                self.counters += [Counter(counter[0],counter[1],counter[2])]
            else:
                print "Can not use ",counter
                print "Wrong type:", type(counter)
                print "Should be Counter-Object or List of string(Name,Description,TangoDeviceName)"

        self.detectors = []
        for detector in detectors:
            if isinstance(detector,Detector):
                self.detectors += [detector]
            elif isinstance(detector,list):
                self.detectors += [Detector(detector[0],detector[1],detector[2])]
            else:
                print "Can not use ",detector
                print "Wrong type:", type(detector)
                print "Should be Detector-Object or List of string(Name,Description,TangoDeviceName)"

    def _get_sampletime(self):
        return self.timer._proxy.read_attribute("SampleTime").value

    def _set_sampletime(self,sampletime):
        print "setting with",sampletime
        self.timer._proxy.write_attribute("SampleTime",float(sampletime))
        print sampletime,self.sampletime,self.timer._proxy.read_attribute("SampleTime").value
        while self.sampletime!=sampletime:
            print sampletime,self.sampletime,self.timer._proxy.read_attribute("SampleTime").value
    
    sampletime = property(_get_sampletime,_set_sampletime)

##    def set_sampletime(self,sampletime):
##        self.sampletime=sampletime
    
    def acquire(self,sleep_factor=0.95):
        for counter in self.counters:
            counter.clear()
        for detector in self.detectors:
            detector.clear()
        self.timer._proxy.command_inout("Start")
        while self.timer._proxy.state() != 0:
            print self.timer._proxy.state(),\
                  self.timer._proxy.read_attribute("RemainingTime").value
            time.sleep(sleep_factor*self.timer._proxy.read_attribute("RemainingTime").value)
        counter_data=[]
        for counter in self.counters:
            counter_data+=[counter.read_data()]
        detector_data=[]
        for detector in self.detectors:
            detector_data+=[detector.read_data()]
        return counter_data,detector_data

    def __str__(self):
        ostr = ""
        ostr+= "Timer:\n"
        ostr+= "%s\n"%self.timer
        ostr+= "Sample time: %s\n"%self.sampletime
        ostr+= "\nCounters:\n"
        if len(self.counters)==0:
            ostr+= "None\n"
        else:
            for i in range(len(self.counters)):
                ostr+= "%s\n"%self.counters[i]
            
        ostr+= "\nDetectors:\n"
        if len(self.detectors)==0:
            ostr+= "None\n"
        else:
            for i in range(len(self.detectors)):
                ostr+= "%s\n"%self.detectors[i]
        return ostr
        

        
