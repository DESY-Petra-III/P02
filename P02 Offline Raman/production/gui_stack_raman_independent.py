#!/usr/bin/env python

# License GPL v3
# author Konstantin Glazyrin (lorcat at gmail.com)


import sys

from  PyTango import *
import pylab
import numpy
import p3cntr
reload(p3cntr)

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Ruby Motors
(MRAMANMOTORX, MRAMANMOTORY, MRAMANMOTORZ) = ("haspllabcl1:10000/llab/motor/mot.01", "haspllabcl1:10000/llab/motor/mot.02", "haspllabcl1:10000/llab/motor/mot.03")

# Led device
MLEDGPDEV = "tango://haspllabcl1:10000/llab/led/llabcl1.01"
(MLEDONOFF, MLEDINTENSITY, MLEDTEMP) = ("&l", "&i", "&ct")

# timer timeout for LED values update
MLEDTIMERTIMEOUT = 3000

# LED switch button captions
(MLEDON, MLEDOFF) = ("Led ON", "Led OFF")

# signal to report values and errors - 
SIGNALREPORT = "report(QString)"

# timer timeout to switch off LED for inactivity - makes sense for offline Raman system
# default - 10 mins
MLEDIDLETIMEOUT = 600000

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
        self.connect(self.wled, SIGNAL(SIGNALREPORT), self.processLedReport)
        return

    # reading settings
    def readSettings(self):
        value = self._settings.value("Position").toPoint()
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
        # tango device string
        self._dev = MLEDGPDEV

        # mutex to control LED operation - when to write and when to read
        self._ledmutex = QMutex()

        # single worker thread to read and write values
        self._worker = MWorker(self)

        # flag to control when to update slider position and when not (no update while sliding is in progress)
        self._bslide = False

        # timer to switch LED off if running for long time without activity
        self._timeroff = QTimer(self)
        self._timeroff.setInterval(MLEDIDLETIMEOUT)
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

        # finishing layout
        layout.addWidget(QLabel("Value:"), 2, 0)
        layout.addWidget(self.leintensity, 2, 1)
        layout.addWidget(QLabel("Temp:"), 3, 0)
        layout.addWidget(self.letemp, 3, 1)
        layout.addWidget(self.slintensity, 1,0,1,2)
        layout.addWidget(self.btnonoff, 0,0,1,2)

        # adjust style
        self.setWidgetsMaximumWidth(50, self.letemp, self.leintensity)

        layout.setRowStretch(3, 50)

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

        # start thread in this case
        self._worker.start()

        # start timer to control idle state
        # self._timeroff.start()
        return

    # correct widgets length in a set
    def setWidgetsMaximumWidth(self, value, *tlist):
        t = type(tlist[0])
        if(t is tuple or t is list):
            tlist = tlist[0]

        for w in tlist:
            w.setMaximumWidth(value)
        return

    # timer switching off led in case of inactivity
    def processIdleOff(self):
        # switch LED Off
        self._worker.addWritable(MLEDONOFF, 0)
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
            value = int(value)
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

    # close event - clean up things
    def closeEvent(self, event):
        # accept event to close window
        event.accept()

        # switch LED Off
        self._worker.addWritable(MLEDINTENSITY, 0)

        # cleanup LED widget, its thread update processing - read/write operation
        if(self._worker is not None and self._worker.isRunning()):
            self._worker.stop()
            self._worker.wait()

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
        self._tcp = MTcpSocketWrapper(self)

    # run specific operation when access mutex allows it
    def run(self):
        # proceed untill told to stop
        while(not self._bstop):
            # check how much time we need for reading - writing operations, adjust read waiting time accordingly
            (timestart, timeend, timediffall) = (QDateTime.currentMSecsSinceEpoch() , 0, 0)

            # write values in the beginning of read cycle
            
                # enumerate through different keys
            for k in self._cmds.keys():
                # check for stop signal every time
                if(self._bstop):
                    break
                # check values, write value to the Led device (attribute and its value)
                if(self._cmds[k] is not None):
                    self.processSetCommand(k, self._cmds[k])
                    with(QMutexLocker(self._writemutex)):
                        self._cmds[k] = None
                else:
                    self.processGetCommand(self, self._cmds[k])

            # after full cycle - enable widgets after sending command to the LED
            if(self._wdgts is not None):
                for w in self._wdgts:
                    w.setDisabled(False)

            # check for stop signal every time we need that
            if(self._bstop):
                    break
                
            # calculate how much time we spend on one cycle
            timeend = QDateTime.currentMSecsSinceEpoch()
            timediffall = timeend - timestart

            # check every 250 ms if we have new value to write - proceed to writing, otherwise wait for the same time it took us to read+write full setup
            for i in range(timediffall, 250):
                bnewwritable = False
                # see if we have something to write
                for k in self._cmds.keys():
                    # new value is set
                    if(self._cmds[k] is not None):
                        bnewwritable = True
                        break

                if(bnewwritable or self._bstop):
                    break
                self.msleep(250)

        self.stop()
        return

    # stop function
    def stop(self):
        if(not self._bstop):
            with(QMutexLocker(self._stopmutex)):
                # set a flag for thread loop to exit
                self._bstop = True
        
        # close any socket operations if present
        self._tcp.stop()

    # set command
    def processSetCommand(self, cmd, value):
        format = "%s%i"
        if(cmd==MLEDINTENSITY):
            format = "%s%x"
        return self._tcp.send(format % (cmd,value) )
        
    # get command
    def processGetCommand(self, cmd):
        return self._tcp.send("%s?"%cmd)

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

    def initVars(self):
        self._socket = QTcpSocket()
        self._port = 50811
        self._host = "192.168.57.243"

        self._mutex = QMutex()
        return

    def initEvents(self):
        return

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value=50811):
        self._port = int(value)

    @property
    def host(self):
        return self._port

    @host.setter
    def host(self, value="192.168.57.243"):
        self._host = str(value)

    # command for blocking operation
    def send(self, cmd, signal=None):
        bsuccess = False
        # try to see if we can read - lock mutex
        if(not self._mutex.tryLock()):
            return bsuccess
        else:
            self._mutex.unlock()

        # read values
        with(QMutexLocker(self._mutex)):
            self._socket.connectToHost(self.host, self.port)
            # make sure we got connected to the device
            if(self._socket.waitForConnected(MLEDTIMERTIMEOUT)):
                self._socket.write(cmd)
                self._socket.flush()

                # we have data to read
                if(self.waitForReadyRead(MLEDTIMERTIMEOUT)):
                    # read data with buffer size of 10, should be enough, pass data as a signal to the tread
                    result = self._socket.readData(10)
                    self.emit(SIGNAL("responseReceived"), cmd, result)
                    bsuccess = True
                    # disconnect a socket
                    self._socket.close()
                else:
                    self.emit(SIGNAL("timeout(const QString &)"), QString("Reading Operation"))
            else:
                # no connection is established, sorry
                self.emit(SIGNAL("connectionError()"))
        return bsuccess

    # cleaning up function
    def close(self):
        if(self._socket.isOpen()):
            self._socket(close)

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
