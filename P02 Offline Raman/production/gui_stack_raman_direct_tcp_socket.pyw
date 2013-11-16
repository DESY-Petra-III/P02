#!/usr/bin/env python

# License GPL v3
# author Konstantin Glazyrin (lorcat at gmail.com)



import sys

from  PyTango import *

import p3cntr

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

# Ruby Motors
(MRAMANMOTORX, MRAMANMOTORY, MRAMANMOTORZ) = ("haspllabcl1:10000/llab/motor/mot.01", "haspllabcl1:10000/llab/motor/mot.02", "haspllabcl1:10000/llab/motor/mot.03")


# Raman LED device default params
(LEDHOST, LEDPORT) = ("192.168.57.243", 50811)

# Led device parameters used in read - write operations - basically - the template
(MLEDONOFF, MLEDINTENSITY, MLEDTEMP) = ("&l", "&i", "&ct")

# timer timeout for LED values update
MLEDTIMERTIMEOUT = 3000 
MLEDREADTIMEOUT = 15000

# timer timeout to switch off LED for inactivity - makes sense for offline Raman system
# default - 10 mins
MLEDIDLETIMEOUT = 600000

# LED switch button captions
(MLEDON, MLEDOFF) = ("Led ON", "Led OFF")

# signal to report values and errors
    # from to Tcp socket wrapper
(SIGNALTCPRESPONSE, SIGNALTCPTIMEOUT, SIGNALSTARTLEDREADOUT, SIGNALTCPREADY, SIGNALTCPSTOP) = ("responseReceived", "connectionTimeout(const QString &)", "startLedReadout()", "tcpReady()", "tcpStop()")
    # from to thread doing read - write opearations with LED device
(SIGNALTHREADWRITE, SIGNALTHREADREAD) = ("threadReadTimeout(int)", "threadWriteTimeout(int)")


###
## MRamanWidget class - widget controling Offline Raman system motors and light
###
class MRamanWidget(QMainWindow):
    def __init__(self, app, parent=None):
        super(MRamanWidget, self).__init__(parent)

        self.initVars(app)
        self.initSelf()
        self.initEvents()

        # read settings // such as previous position
        self.readSettings()
        return

    # initialize main variables
    def initVars(self, app):
        self._app = app
        # motors widget
        self.wmotors = None
        # LED widget
        self.wled  = None
        # settings
        self._settings = QSettings(self)
        return

    # initialize gui
    def initSelf(self):
        # background color
        if(self.parent() is None):
            self.setAutoFillBackground(True)
            pal = QPalette()
            pal.setColor(QPalette.Window, QColor('blue').light())
            self.setPalette(pal)

        # title
        self.setWindowTitle("offline Raman system")

        # layout
        wdgt = QWidget(self)
        layout = QGridLayout(wdgt)

        # motors widget
        wmotors = self.initMotorsWidget()

        # led widget
        wled = self.initLedWidget()

        layout.addWidget(wmotors, 0, 0)
        layout.addWidget(wled, 0, 1)

        self.setCentralWidget(wdgt)

        # status bar
        self._status = QStatusBar(self)
        self.setStatusBar(self._status)

        self.show()
        return

    # initialize events
    def initEvents(self):
        self.connect(self.wled, SIGNAL(SIGNALTCPTIMEOUT), self.processLedReport)
        return

    # reading settings
    def readSettings(self):
        # check for Qt version
        if(PYQT_VERSION < 0x40a00):
            value = self._settings.value("Position").toPoint()
        else:
            value = self._settings.value("Position")
        self.move(value)

        return

    # writing settings
    def writingSettings(self):
        self._settings.setValue("Position", self.pos())
        return

    # initialize Motors widget
    def initMotorsWidget(self):
        wdgt = QGroupBox("Motors")
        layout = QGridLayout(wdgt)

        ramanX = p3cntr.Motor("Raman X",
                    "Raman X",
                    MRAMANMOTORX)
        ramanY = p3cntr.Motor("Raman Y",
                    "Raman Y",
                    MRAMANMOTORY)
        ramanZ = p3cntr.Motor("Raman Z",
                    "Raman Z",
                    MRAMANMOTORZ)

        self.wmotors = p3cntr.ui.MotorWidgetAdvanced([ramanX, ramanY, ramanZ])

        layout.addWidget(self.wmotors, 0, 0)
        return wdgt

    # initialize Led widget
    def initLedWidget(self):
        wdgt = QGroupBox("LED light Intensity")
        layout = QGridLayout(wdgt)

        self.wled = MLedWidget(self)

        layout.addWidget(self.wled, 0, 0)
        return wdgt

    # report from LED widget
    def processLedReport(self, msg):
        print(msg)
        self._status.showMessage(msg, 5000)

    # closing event
    def closeEvent(self, event):
        event.accept()

        # cleanup LED widget - thread processing and etc.
        self.wled.close()

        # write settings
        self.writingSettings()

###
## MRubyWidget class End
###


###
## MLedWidget class - widget controling GP table light
###
class MLedWidget(QWidget):
    def __init__(self, parent=None):
        super(MLedWidget, self).__init__(parent)

        self.initVars()
        self.initSelf()
        self.initEvents()
        return

    # initialize main variables
    def initVars(self):

        # mutex to control LED operation - when to write and when to read
        self._ledmutex = QMutex()

        # wrapper for tcp socket communication
        self._tcp = MTcpSocketWrapper()
            # since we pass socket wrapper to another thread, we have to initialize its events before that
            # get valid response to update gui
        self.connect(self._tcp, SIGNAL(SIGNALTCPRESPONSE), self.processTcpResponse)
            # get error like response from timeouts
        self.connect(self._tcp, SIGNAL(SIGNALTCPTIMEOUT), self.processTcpTimeout)
            # redirect a query for LED values readout to the self._tcp
        self.connect(self, SIGNAL(SIGNALTCPREADY), self._tcp.signalIsReady)
            # tell thread that we are read to process LED values readout
        self.connect(self._tcp, SIGNAL(SIGNALTCPREADY), self.processTcpReadout)
            # tell socket to stop
        self.connect(self, SIGNAL(SIGNALTCPSTOP), self._tcp.stop)

        # single worker thread to read and write values
        self._worker = MWorker(self.parent())
            # have to change socket wrapper affinity to the worker thread
        self._tcp.moveToThread(self._worker)
        self._worker.writer = self.processSetCommand
        self._worker.reader = self.processGetCommand

        # flag to control when to update slider position and when not (no update while sliding is in progress)
        self._bslide = False

        # timer to switch LED off if running for long time without activity
        self._timeroff = QTimer(self)
        self._timeroff.setInterval(MLEDIDLETIMEOUT)

        # timer to make very slow readouts from device
        self._timerread = QTimer(self)
        self._timerread.setInterval(MLEDREADTIMEOUT)
        return

    # initialize gui
    def initSelf(self):
        layout = QGridLayout(self)

        # intensity slider
        self.slintensity = QSlider(Qt.Horizontal)
        self.slintensity.setRange(0, 255)

        # intensity changer
        self.leintensity = QLineEdit("0")
        val = QIntValidator(0, 255, self.leintensity)
        self.leintensity.setValidator(val)

        # temperature of LED
        self.letemp = QLineEdit("0.00")
        self.letemp.setReadOnly(True)

        # button - on/off
        self.btnonoff = QPushButton(MLEDON)
        self.btnonoff.setCheckable(True)

        # labels to indicate read times
        self.lbreadtime = QLabel("")
        self.lbwritetime = QLabel("")

        # finishing layout
        layout.addWidget(QLabel("Value:"), 2, 0)
        layout.addWidget(self.leintensity, 2, 1)
        layout.addWidget(QLabel("Temp:"), 3, 0)
        layout.addWidget(self.letemp, 3, 1)
        layout.addWidget(self.slintensity, 1,0,1,2)
        layout.addWidget(self.btnonoff, 0,0,1,2)
        layout.addWidget(QLabel("Read, ms:"), 5, 0)
        layout.addWidget(self.lbreadtime, 5, 1)
        layout.addWidget(QLabel("Write, ms:"), 6, 0)
        layout.addWidget(self.lbwritetime, 6, 1)

        # adjust style
        self.setWidgetsMaximumWidth(50, self.letemp, self.leintensity)

        layout.setRowMinimumHeight(4, 15)
        layout.setRowStretch(layout.rowCount()+1, 50)

        # show widget
        self.show()
        return

    # initialize events
    def initEvents(self):
        # gui events
            # switch on, off
        self.connect(self.btnonoff, SIGNAL("toggled(bool)"), self.processLightSwitch)
            # change intensity
        self.connect(self.leintensity, SIGNAL("returnPressed()"), self.processIntensityChangeText)
        self.connect(self.leintensity, SIGNAL("editingFinished()"), self.processIntensityChangeText)
            # change value by slider - click events - step change, page change
        # self.connect(self.slintensity, SIGNAL("actionTriggered(int)"), self.processIntensityChangeClick)
            # change value by slider - on release of mouse button after sliding
        self.connect(self.slintensity, SIGNAL("sliderPressed()"), self.processIntensityChangeSlideStart)
        self.connect(self.slintensity, SIGNAL("sliderReleased()"), self.processIntensityChangeSlideFinish)
            # wheel event of the slider
        self.slintensity.wheelEvent = self.processSliderWheelEvent

        # timer controlling idle state
        self.connect(self._timeroff, SIGNAL("timeout()"), self.processIdleOff)
        # timer controlling device readouts state
        self.connect(self._timerread, SIGNAL("timeout()"), self.processTimerReadout)
            # connect signal emited from readout timer with thread operation
        self.connect(self, SIGNAL(SIGNALSTARTLEDREADOUT), self._worker.setReadOperation)

        # process event from thread to discplay times for read - write operations
            # read opearations
        func_callback = lambda dummy=None, w=self.lbreadtime: self.processTimeReports(dummy, w)
        self.connect(self._worker, SIGNAL(SIGNALTHREADREAD), func_callback)
            # write operations
        func_callback = lambda dummy=None, w=self.lbwritetime: self.processTimeReports(dummy, w)
        self.connect(self._worker, SIGNAL(SIGNALTHREADWRITE), func_callback)

        # start thread in this case
        self._worker.start()

        # start timer to control idle state
        self._timeroff.start()
        # start LED readout timer
        self._timerread.start()

        # make thread do inital Led values readout
        self.processTimerReadout()
        return

    # 
    def processTimeReports(self, *tlist):
        (value, wdgt) = tlist
        wdgt.setText(str(value))

    # correct widgets length in a set
    def setWidgetsMaximumWidth(self, value, *tlist):
        t = type(tlist[0])
        if(t is tuple or t is list):
            tlist = tlist[0]

        for w in tlist:
            w.setMaximumWidth(value)
        return

    def processTcpResponse(self, cmdtemplate, cmd, response):
        patt = "%s(\d+)"%cmdtemplate
        re = QRegExp(patt)

        # check if we can extract values transmitted by device
        if(re.indexIn(QString(response))>-1):
            value = str(re.cap(1))
            # discriminate between different commands - responses
                # led on off button
            if(cmdtemplate==MLEDONOFF):
                value = int(str(value))
                if(value>0):
                    value = True
                else:
                    value = False
                self.btnonoff.setChecked(value)
                # led intensity
            elif(cmdtemplate==MLEDINTENSITY):
                value = int(str(value), 16)
                self.leintensity.setText("%i"%value)
                self.slintensity.setValue(value)
                # led temperature
            elif(cmdtemplate==MLEDTEMP):
                value = int(str(value))
                self.letemp.setText("%i"%value)
            return

    def processTcpTimeout(self, msg):
        self.emit(SIGNAL(SIGNALTCPTIMEOUT), msg)

    # timer switching off led in case of inactivity
    def processIdleOff(self):
        # switch LED Off
        self._worker.addWritable(MLEDONOFF, 0)
        self.btnonoff.setChecked(False)
        self.btnonoff.setText(MLEDOFF)
        return

    # process light switching - ON/OFF
    def processLightSwitch(self, bflag):
        value = 0
        if(bflag):     # ON
            self.btnonoff.setText(MLEDON)
            value = 1
        else:          # OFF
            self.btnonoff.setText(MLEDOFF)

        # write values
        self._worker.addWritable(MLEDONOFF, value)

        # restart iddle timer
        self._timeroff.stop()
        self._timeroff.start()
        return

    # intensity value changed by QLineEdit field
    def processIntensityChangeText(self):
        value = self.leintensity.text()

        try:
            value = int(str(value))
        except ValueError:
            value = 0

        # pass value to a right function
        self.processIntensityChangeClick(value)
        return

    # intensity value changed by QSlider - click  event
    def processIntensityChangeClick(self, value):        
        # set value
        self.slintensity.setValue(value)
        self.leintensity.setText("%i" % value)

        # add values to the write cycle
        self._worker.addWritable(MLEDINTENSITY, value)
        return

    # a test if we use slider controls and started sliding it
    def processIntensityChangeSlideStart(self):
        self._bslide = True

    # a test if we use slider controls and finished sliding pass - intensity QSlider value to a write function
    def processIntensityChangeSlideFinish(self):        
        # get value and pass it to the right function
        value = self.slintensity.value()
        self.processIntensityChangeClick(value)
        self._bslide = False
        return

    # mouse wheel event - control it, ignore for now, only mouse sliding movements are taken into account
    def processSliderWheelEvent(self, event):
        event.ignore()
        return

    # report string messages to a parent widget
    def reportErrorMessage(self, msg):
        print(msg)

    # command to set values on LED
    def processSetCommand(self, cmd, value):
        format = "%s%i"
        if(cmd==MLEDINTENSITY):
            format = "%s%02x"
        return self._tcp.send(cmd, format % (cmd,value), write=True)
        
    # command to get values from thread
    def processGetCommand(self, cmd):
        return self._tcp.send(cmd, "%s?"%cmd)

    def processTimerReadout(self):
        self.emit(SIGNAL(SIGNALTCPREADY))

    def processTcpReadout(self):
        self.emit(SIGNAL(SIGNALSTARTLEDREADOUT))

    # close event - clean up things
    def closeEvent(self, event):
        # accept event to close window
        event.accept()

        self._timeroff.stop()
        self._timerread.stop()

        # switch off led
        self._worker.addWritable(MLEDONOFF, 0)

        # cleanup LED widget, its thread update processing - read/write operation
        if(self._worker is not None and self._worker.isRunning()):
            self._worker.stop()
            self._worker.wait()

        # make sure the socket is closed
        self.emit(SIGNAL(SIGNALTCPSTOP))



###
## MLedWidget class End
###

###
## MWorker class - QThread class for dirty work - to write and previously set data, widgets are disabled until all right commands are executed
###
class MWorker(QThread):
    def __init__(self, parent=None):
        super(MWorker, self).__init__(parent)

        # mutex to control exit conditions
        self._bstop = False
        self._stopmutex = QMutex()

        # function to process
        self._wdgts = None

        # storage for data writing
        self._cmds = {MLEDINTENSITY : None, MLEDONOFF : None, MLEDTEMP : None}
        self._writemutex = QMutex()

        # socket wrapper for operation
        self._tcp = None

        # references fro functions which will be used in reading, writing operations
            # reading
        self._reader = None
            # writing
        self._writer = None

        # flag used to tell thread that we would like to read values from LED
        self._bread = False

    # run specific operation when access mutex allows it
    def run(self):
        print("LED Thread started")
        # proceed untill told to stop
        while(not self._bstop):
            # check if new values should be transfered to the LED, transfer them
            self.doWork()

            # reading is done only on a timer signal or on start up
            if(self._bread):
                self.doWorkRead()

        # cleaning up
            # final cleaning up
        self.stop()
        print("LED Thread stopped")
        return

    def doWork(self):
        # get current time
        time = QTime.currentTime()
        time.start()
        # check how much time we need for reading - writing operations, adjust read waiting time accordingly
        (timestart, timeend) = (0, 0)

        # write values in the beginning of read cycle
        
        # enumerate through different keys
        bwritten = False
        for k in self._cmds.keys():
            # check for stop signal every time
            if(self._bstop):
                return
            # check values, write value to the Led device (attribute and its value)
            if(self._cmds[k] is not None):
                self._writer(k, self._cmds[k])
                with(QMutexLocker(self._writemutex)):
                    self._cmds[k] = None
                bwritten = True

        # after full cycle - enable widgets after sending command to the LED
        if(self._wdgts is not None):
            for w in self._wdgts:
                w.setDisabled(False)

        # check for stop signal every time we need that
        if(self._bstop):
                return
            
        # calculate how much time we spend on one cycle
        timeend = time.elapsed()

        if(bwritten):
            self.emit(SIGNAL(SIGNALTHREADWRITE), timeend)

    def doWorkRead(self):
        time = QTime.currentTime()
        time.start()
        # check how much time we need for reading - writing operations, adjust read waiting time accordingly
        (timestart, timeend) = (0, 0)

        # enumerate through commands, read LED parameters
        for k in self._cmds.keys():
            # check for stop signal every time
            if(self._bstop):
                return

            # read operation
            self._reader(k)

        # calculate how much time we spend on one cycle
        timeend = time.elapsed()

        # make sure we do not read again until a correct event has arrived
        self._bread = False

        # report value from read operation time 
        self.emit(SIGNAL(SIGNALTHREADREAD), timeend)

    # stop function
    def stop(self):
        if(not self._bstop):
            # do final work - set special values on exit
            self.doWork()
            with(QMutexLocker(self._stopmutex)):
                # set a flag for thread loop to exit
                self._bstop = True

    # make sure only the one attribute value is written - use dictionaries
    def addWritable(self, cmd, value):
        with(QMutexLocker(self._writemutex)):
            self._cmds[cmd] = value

        if(self._wdgts is not None):
            for w in self._wdgts:
                w.setDisabled(True)

    # add widgets which should be disabled in order to avoid 
    def addWidgestDisabled(self, *wdgts):
        t = type(wdgts[0])
        if(t is list or t is tuple):
            wdgts = wdgts[0]

        self._wdgts = wdgts

    @property 
    def reader(self):
        return self._reader

    @reader.setter
    def reader(self, value):
        self._reader = value

    @property 
    def writer(self):
        return self._writer

    @writer.setter
    def writer(self, value):
        self._writer = value

    def setReadOperation(self):
        self._bread = True

###
## MWorker class End
###

###
## MTcpSocket - class for direct working with LED - clocking operation
###

class MTcpSocketWrapper(QObject):
    def __init__(self, parent=None):
        super(MTcpSocketWrapper, self).__init__(parent)

        self.initVars()
        self.initEvents()

    # variables initialization
    def initVars(self):
        # socket with default values
        self._socket = QTcpSocket(self)
        self._port = LEDPORT
        self._host = QString(LEDHOST)

        # mutex for connection control - 1 function call - one connection
        self._mutex = QMutex()

        # flag to distinguish if socket can be used or not
        self._bready = True
        return

    # event if we will need them after
    def initEvents(self):
        return

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value=LEDPORT):
        self._port = int(value)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value=LEDHOST):
        self._host = QString(value)

    # command for blocking operation, write flag is set to distinguish between different modes, when we are interested in the output and when we are not
    def send(self, cmdtemplate, cmd, write=False):
        self._bready = False
        bsuccess = False
        # try to see if we can read - lock mutex
        if(not self._mutex.tryLock()):
            return bsuccess
        else:
            self._mutex.unlock()

        # read values
        with(QMutexLocker(self._mutex)):
            self._socket.connectToHost(QString(self.host), int(self.port))
            # make sure we got connected to the device
            if(self._socket.waitForConnected(MLEDTIMERTIMEOUT)):
                self._socket.write(cmd)
                self._socket.flush()

                # to reduce overhead for reading 
                if(write):
                    self.stop()
                    return

                # we have data to read
                if(self._socket.waitForReadyRead(MLEDTIMERTIMEOUT)):
                    # read data with buffer size of 10, should be enough, pass data as a signal to the tread
                    result = self._socket.readData(10)

                    if(not write):
                        self.emit(SIGNAL(SIGNALTCPRESPONSE), cmdtemplate, cmd, result)

                    bsuccess = True
                else:
                    # timeout during reading operation - that is fine
                    self.emit(SIGNAL(SIGNALTCPTIMEOUT), QString("Tcp Socket Read Operation %s timeout (LED)"%cmd))
            else:
                # no connection is established, sorry
                self.emit(SIGNAL(SIGNALTCPTIMEOUT), QString("Tcp Connection Error (LED) %s:%i" % (self.host, self.port)))

        self.stop()
        self._bready = True
        return bsuccess

    # cleaning up function
    def stop(self):
        if(self._socket.isOpen()):
            self._socket.close()

    def isReady(self):
        return self._bready

    def signalIsReady(self):
        if(self._bready):
            self.emit(SIGNAL(SIGNALTCPREADY))

###
## MTcpSocket - end
###

MAPPLICATION = "BeamlineStack"
MDOMAIN = "desy.de"
MORG = "DESY"

# possibility to start, debug and test widget
if __name__ == "__main__":
    app = QApplication([])

    # initialize values for settings
    app.setOrganizationName(MORG)
    app.setOrganizationDomain(MDOMAIN)
    app.setApplicationName(MAPPLICATION)

    form = MRamanWidget(app)
    app.exec_()
