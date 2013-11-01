#general classes 

import PyTango

class TangoDevice(object):
    def __init__(self,name,desc,tname):
     
        self.name = name
        self.description = desc
        self.tname = tname
        self._proxy = PyTango.DeviceProxy(tname)

## AFAIU just a template for writting a getter-method for any tango-attribute
    def _get_tango_attribute(self):
        pass

    tattr = property(_get_tango_attribute)

    def __str__(self):
        ostr = "Name: %s\n" %self.name
        ostr += "Desc.: %s\n" %self.description
        ostr += "Tango Dev. Name: %s\n" %self.tname
##        ostr += "Proxy (use only if you know what you are doing!!): %s\n" %self._proxy
        return ostr
