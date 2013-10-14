#!/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyTango import *

BTNCLOSE = "&Close Shutter"
BTNOPEN = "&Open Shutter"


(DEVINTERLOCK, DEVSHUTTER) = ("Interlock", "Shutter")
DEVICES = {
        DEVINTERLOCK : {"link": "haspp02oh1.desy.de:10000/p02/ics/1", "read":"GetInterlockStatus", "readarg":2, "on": 0, "off": 3, "write": "BreakInterlock", "writearg": 2},
        DEVSHUTTER :  {"link": "haspp02oh1.desy.de:10000/p02/shutter/1", "property" : "BSB1OffenDisplayState", "on":1, "off":0}
        }

class MShutter(QMainWindow):
    def __init__(self, parent=None):
        super(MShutter, self).__init__(parent)
        
        self.initVars()
        self.initSelf()
        self.initEvents()
        return

    def initVars(self):
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        
        
        return

    def initSelf(self):
        wdgt = QWidget(self)
        grid=QGridLayout(wdgt)
        self.setWindowTitle("Shutter control example")
        
        grid.addWidget(QLabel("Interlock status:"), 0, 0)
        
        self.leinterlock = QLabel("")
        grid.addWidget(self.leinterlock, 0, 1)
        
        grid.addWidget(QLabel("Shutter status:"), 1, 0)
        self.leshutter = QLabel("")
        grid.addWidget(self.leshutter, 1, 1)
        
        self.btnshutter = QPushButton(BTNOPEN)
        grid.addWidget(self.btnshutter, 2, 1)
        
        self.setCentralWidget(wdgt)
        self.show()
        return

    def initEvents(self):
        self.connect(self._timer, SIGNAL("timeout()"), self.processTimerUpdate)
        
        self._timer.start()
        return

    def processTimerUpdate(self):
        # update interlock values
        res = self.tangoRead(DEVICES[DEVINTERLOCK])
        t = type(res)
        format = "%i"
        if(res is None):
            res = str(res)
            format = "%s"
           
        self.leinterlock.setText(format % res)
        
        # update Shutter status
        res = self.tangoRead(DEVICES[DEVSHUTTER])
        t = type(res)
        format = "%i"
        if(res is None):
            res = str(res)
            format = "%s"
           
        self.leshutter.setText(format % res)
        
        return
    
    def tangoRead(self, device):
        res = None
        link = device["link"]
        
        dev = None
        try:
            dev = DeviceProxy(link)
        except DevFailed, error:
            print("Device %s throws DevFailed exception" % link)
            print(error)
            return
        except DevError:
            print("Device %s throws DevError exception" % link)
            return
        
        if(dev == None):
            return res
            
        # discriminate device types - attribute based and command based
        if(device.has_key("property")):
            try:
                res = dev.read_attribute(device["property"]).value
            except DevFailed:
                print("Device %s throws DevFailed exception" % link)
            except DevError:
                print("Device %s throws DevError exception" % link)
        elif(device.has_key("read")):
            try:
                res = dev.command_inout(device["read"], device["readarg"])
            except DevFailed:
                print("Device %s throws DevFailed exception" % link)
            except DevError:
                print("Device %s throws DevError exception" % link)
        
        return res
    
    def closeEvent(self, event):
        event.accept()


if(__name__=="__main__"):
    app = QApplication([])
    
    form = MShutter()
    
    app.exec_()
