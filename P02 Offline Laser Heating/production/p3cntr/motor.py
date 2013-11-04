import PyTango
import time
import sys
import numpy

from p3cntr import abstract

class Motor(abstract.TangoDevice):
    def __init__(self,name,desc,tname):
        super(Motor,self).__init__(name,desc,tname)

    def _getposition(self):
        return self._proxy.read_attribute("Position").value    
        #return self._proxy.command_inout("GetPosition")

    def _setposition(self,position):
        return self.move(position)

    def _getuplimit(self):
        return self._proxy.read_attribute("UnitLimitMax").value

    def _getlolimit(self):
        return self._proxy.read_attribute("UnitLimitMin").value


    pos = property(_getposition,_setposition)
    uplim = property(_getuplimit)
    lolim = property(_getlolimit)

    def move(self,value,block=False,dtime=0.2):
        if isinstance(value,float) or isinstance(value,int):
            newpos = float(value)
        else:
            raise ValueError("Motor position must be float or int!")

        oldpos = self.pos
        
        try:
            self._proxy.command_inout("Move",value)
        except PyTango.DevFailed:
            exctype , value = sys.exc_info()[:2]
            print("Failed with exception ! %s " % str(exctype))
            for err in value:
                self.print_error(
                        ("Reason: ", err.reason),
                        ("Description: ", err.desc),
                        ("Origin: ", err.origin),
                        ("Severity: ", err.severity),
                        ("Old position: ", oldpos)
                    )
               
        if block:
            while self._proxy.state() == PyTango.DevState.MOVING:
                time.sleep(dtime)

    # 
    def print_error(self, *tlist):
        print("Error:")
        for (label, error) in tlist:
            print("%s - %s" % (str(label), set(error)))

    def __str__(self):
        ostr = "Motor: %s\n" %self.name
        ostr += "Desc.: %s\n" %self.description
        ostr += "Tango Dev. Name: %s\n" %self.tname
        ostr += "Position: %f\n" %self.pos
        ostr += "Lower limit: %f\n" %self.lolim
        ostr += "Upper limit: %f\n" %self.uplim

        return ostr
