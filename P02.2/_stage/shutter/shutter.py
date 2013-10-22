#!/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyTango import *

BTNCLOSE = "&Close Shutter"
BTNOPEN = "&Open Shutter"


(DEVINTERLOCK, DEVSHUTTER, DEVINTERLOCKCTRL, DEVSHUTTERCTRL) = ("Interlock", "Shutter",
    "InterlockControl", "ShutterControl")
DEVICES = {
        DEVINTERLOCK : {"link": "haspp02oh1.desy.de:10000/p02/ics/1", "read":"GetInterlockStatus", "readarg":2, "on": 0, "off": 3},
        DEVSHUTTER :  {"link": "haspp02oh1.desy.de:10000/p02/shutter/1", "property" : "BSB1OffenDisplayState", "on":0, "off":3},
        
        DEVSHUTTERCTRL :  {"link": "haspp02oh1.desy.de:10000/p02/shutter/1", "write" : "CloseOpen_BS_1B", "on":1, "off":0},
        DEVINTERLOCKCTRL : {"link": "haspp02oh1.desy.de:10000/p02/ics/1", "write": "BreakInterlock", "off": 2},
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
        
        # stopper object - to avoid excesive while loop processing
        self._stop = MStop(self)
        
        # worker threads
        self._threads = []
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
        self.btnshutter.setDisabled(True)
        grid.addWidget(self.btnshutter, 2, 1)
        
        self.setCentralWidget(wdgt)
        self.show()
        
        self.processTimerUpdate()
        return

    def initEvents(self):
        self.connect(self._timer, SIGNAL("timeout()"), self.processTimerUpdate)
        self.connect(self.btnshutter, SIGNAL("clicked()"), self.processShutterOperation)
        
        self._timer.start()
        return

    def processTimerUpdate(self):
        (resint, resshut) = (None, None)
        
        # update interlock values
        interlock = DEVICES[DEVINTERLOCK]
        res = self.tangoRead(interlock)
        t = type(res)
        format = "%i"
        resint = res
        if(res is None):
            res = str(res)
            format = "%s"
           
        self.leinterlock.setText(format % res)
        
        # update Shutter status
        shutter= DEVICES[DEVSHUTTER]
        res = self.tangoRead(shutter)
        t = type(res)
        format = "%i"
        resshut = res
        if(res is None):
            res = str(res)
            format = "%s"
           
        self.leshutter.setText(format % res)
        
        if(resint is not None and resshut is not None):
            # interlock is on - we can work with shutter
            if(resint==interlock["on"]):
                self.btnshutter.setDisabled(False)
            
            if(resshut==shutter["on"]):
                self.btnshutter.setText(BTNCLOSE)
            elif(resshut==shutter["off"]):
                self.btnshutter.setText(BTNOPEN)
            
        return
    
    def processShutterOperation(self):
        shutter = DEVICES[DEVSHUTTER]
        
        # cleaning up used up threads 
        for i,t in enumerate(self._threads):
            if(t is not None and t.isFinished()):
                self._threads.pop(i)
        
        # get current shutter state
        res = self.tangoRead(shutter)
        while(res is None and not self._stop.stop):
            res = self.tangoRead(shutter)
        
        thread = None
        if(res == shutter["on"]):
            print("Shutter is on")
            self.processCloseShutter()
            thread = MShutterWorker(self.processCloseShutter, [self.btnshutter], self)
            thread.start()
        elif(res == shutter["off"]):
            print("Shutter is Off")
            thread = MShutterWorker(self.processOpenShutter, [self.btnshutter], self)
            thread.start()
        
        if(thread is not None):
            self._threads.append(thread)
        return
    
    def processOpenShutter(self):
        self._timer.stop()
        (shutter, shutterctrl)= (DEVICES[DEVSHUTTER], DEVICES[DEVSHUTTERCTRL])
        print("Shutter is told to open")
        # tell shutter to open
        self.tangoWrite(shutterctrl, shutterctrl["on"])
        # wait until shutter is opened
        res = self.tangoRead(shutter)
        while((res is None or res!=shutter["on"]) and not self._stop.stop):
            res = self.tangoRead(shutter)
            print("Shutter state - %i"%res)
        
        self._timer.start()
        return
    
    def processCloseShutter(self):
        self._timer.stop()
        (shutter, shutterctrl)= (DEVICES[DEVSHUTTER], DEVICES[DEVSHUTTERCTRL])
        
        # tell shutter to close
        self.tangoWrite(shutterctrl, shutterctrl["off"])
        print("Shutter is told to close")
        
        # wait until shutter is closed
        res = self.tangoRead(shutter)
        while((res is None or res!=shutter["off"]) and not self._stop.stop):
            res = self.tangoRead(shutter)
            print("Shutter state - %i"%res)
        
        # tell interlock to close
        # (interlock, interlockctrl) = (DEVICES[DEVINTERLOCK], DEVICES[DEVINTERLOCKCTRL])
        
        # wait until interlock is disabled
        #res = self.tangoRead(interlock)
        #while((res is None or res!=interlock["off"]) and not self._stop.stop):
        #    print("Interlock is told to close")
        #    self.tangoWrite(interlockctrl, interlockctrl["off"])
        #    res = self.tangoRead(interlock)
        #    print("Interlock  state - %i"%res)
        
        self._timer.start()
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
    
    def tangoWrite(self, device, value):
        link = device["link"]
        
        # initialize device control - wait, until a connection is established
        dev = None
        while(dev is None and not self._stop.stop):
            try:
                dev = DeviceProxy(link)
            except DevFailed:
                print("Device %s throws DevFailed exception (device init)" % link)
            except DevError:
                print("Device %s throws DevError exception (device init)" % link)
            
        # discriminate device types - attribute based and command based
        # process device only if we can write to it - make sure we write it
        if(device.has_key("write")):
            bsuccess = False
            while(not bsuccess and not self._stop.stop):
                try:
                    res = dev.command_inout(device["write"], value)
                    bsuccess = True
                except DevFailed:
                    print("Device %s throws DevFailed exception" % link)
                except DevError:
                    print("Device %s throws DevError exception" % link)
        return
    
    def closeEvent(self, event):
        self._stop.stop = True
        
        # exiting, cleaning up threads
        for t in self._threads:
            if(t is not None and t.isRunning()):
                t.wait()
                
        event.accept()
        
class MShutterWorker(QThread):
    def __init__(self, writeop=None, wdgtlist=None, parent = None):
        super(MShutterWorker, self).__init__(parent)
        
        self.initVars(writeop, wdgtlist)
    
    def initVars(self,writeop, wdgtlist):
        # operation to process in QTread cycle
        self._writeop = writeop 
        
        # widgets to work with
        print(wdgtlist)
        self._wgts = wdgtlist
        
        # mutex
        self._stopmutex = QMutex()
        self._bstop = False
        return
    
    def run(self):
        # disable certain widgets
        self.setWidgetsDisabled()
        
        # process write operation
        self._writeop()
        
        # reenable widgets
        self.setWidgetsDisabled(False)
        return
    
    def setWidgetsDisabled(self, value=True):
        t = type(self._wgts)
        if(t is None):
            return
        
        for w in self._wgts:
            w.setDisabled(value)
 
# global stop object - to prevent while loops to go forever
class MStop(QObject):
    def __init__(self, parent=None):
        super(MStop, self).__init__(parent)
        
        self._bstop = False
        self._stopmutex = QMutex()
    
    @property
    def stop(self):
        return self._bstop
    
    @stop.setter
    def stop(self, value):
        with(QMutexLocker(self._stopmutex)):
            self._bstop = value

if(__name__=="__main__"):
    app = QApplication([])
    
    form = MShutter()
    
    app.exec_()
