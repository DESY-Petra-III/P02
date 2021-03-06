import PyTango
import time
import sys
import numpy

import abstract

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
            raise ValueError,"Motor position must be float or int!"

        oldpos = self.pos
        
        try:
#            self._proxy.command_inout("Move",value) # old style, not OK for hydramotor or attribute motor
            self._proxy.write_attribute("Position",value)
        except PyTango.DevFailed:
            exctype , value = sys.exc_info()[:2]
            print "Failed with exception ! " , exctype
            for err in value:
                print " reason" , err.reason
                print " description" , err.desc
                print " origin" , err.origin
                print " severity" , err.severity
                print
                print "Old position was:", oldpos
               
        if block:
            while self._proxy.state() == PyTango.DevState.MOVING:
                time.sleep(dtime)


    def __str__(self):
        ostr = "Motor: %s\n" %self.name
        ostr += "Desc.: %s\n" %self.description
        ostr += "Tango Dev. Name: %s\n" %self.tname
        ostr += "Position: %f\n" %self.pos
        ostr += "Lower limit: %f\n" %self.lolim
        ostr += "Upper limit: %f\n" %self.uplim

        return ostr


        

