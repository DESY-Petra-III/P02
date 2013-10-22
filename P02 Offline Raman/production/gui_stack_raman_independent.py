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
(MLEDONOFF, MLEDINTENSITY, MLEDTEMP) = ("LEDOffOn", "Intensity", "Temperature")

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
        self._worker = MWorker( self.processLedRead, self.processLedWrite, self)

        # flag to control when to update slider position and when not (no update while sliding is in progress)
        self._bslide = False

        # flag to control the led light switch
        self._bvaluechanged =  False

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

    # timer switching off led in case of iactivity
    def processIdleOff(self):
        # switch LED Off
        self.processLedWrite(MLEDONOFF, 0)
        return

    # process timer update
    def processLedRead(self):
        #check if value has been changed, exit from reading to initiate writing cycle
        if(self._bvaluechanged):
            return

        # device proxy - establish connection to the device proxy
        dev = DeviceProxy(self._dev)

        # try device it, if it is Running or not, test aditionally timeouts
        try:
            dev.state()
        except DevFailed:
            self.reportErrorMessage("Error: Tango connection Failed (processLedRead - timeout)")
            return
        except DevError:
            self.reportErrorMessage("Error: Tango connection Failed (processLedRead)")
            return

        # read intensity, update it if necessary
        berror = False
        try:
            temp = dev.read_attribute(MLEDINTENSITY).value
        except DevFailed:
            self.reportErrorMessage("Error: Tango Device timeout (processLedRead)")
            berror = True
        except DevError:
            berror = True       # means timeout
            self.reportErrorMessage("Error: Tango connection Failed (processLedRead)")

        # update widget if not timeout occurs and 
        if(not berror and temp != self.slintensity.value() and not self._bslide and not self._bvaluechanged):
            self.leintensity.setText("%i" % temp)
            self.slintensity.setValue(temp)

        # set worker on sleep

        # read temperature
        berror = False
        try:
            temp = dev.read_attribute(MLEDTEMP).value
        except DevFailed:
            self.reportErrorMessage("Error: Tango Device timeout (processLedRead)")
            berror = True
        except DevError:
            berror = True       # means timeout
            self.reportErrorMessage("Error: Tango connection Failed (processLedRead)")

        if(not berror and not self._bvaluechanged):
            self.letemp.setText("%i" % temp)

        # read on/off state
        berror = False
        try:
            temp = dev.read_attribute(MLEDONOFF).value
        except DevFailed:
            self.reportErrorMessage("Error: Tango Device timeout (processLedRead)")
            berror = True
        except DevError:
            berror = True       # means timeout
            self.reportErrorMessage("Error: Tango connection Failed (processLedRead)")

        # process if no error has occured and button has not been pressed
        if(not berror and not self._bvaluechanged):
            if(temp>0):     # ON
                self.btnonoff.setChecked(True)
                self.btnonoff.setText(MLEDON)
            else:           # OFF
                self.btnonoff.setChecked(False)
                self.btnonoff.setText(MLEDOFF)
        return

    # write value to a Led, set a loop which will not finish untill the thread has completed a write cycle
    def processLedWrite(self, attribute, value):
        # device proxy
        dev = DeviceProxy(self._dev)

        # try device
        try:
            dev.state()
        except DevFailed:
            self.reportErrorMessage("Error: Tango connection Failed (processLedRead - timeout)")
            return
        except DevError:
            self.reportErrorMessage("Error: Tango connection Failed (processLedWrite)")
            return

        bcomplete = False
        while(not bcomplete):
            try:
                dev.write_attribute(attribute, value)
                bcomplete = True
            except DevFailed:
                self.reportErrorMessage("Error: Tango Device timeout (processLedWrite)")
                pass
            except DevError:            # timeout error
                self.reportErrorMessage("Error: Tango connection Failed (processLedWrite)")
                pass

        # allow reading from tango server and consequent gui updating
        if(self._bvaluechanged):
           self._bvaluechanged = False


    # process light switching - ON/OFF
    def processLightSwitch(self, bflag):
        # mark the beginnign of the write cycle
        self._bvaluechanged = True

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

        # set flag indicating that value has been changed
        self._bvaluechanged = True

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
        self.processLedWrite(MLEDONOFF, 0)

        # cleanup LED widget, its thread update processing - read/write operation
        if(self._worker is not None and self._worker.isRunning()):
            self._worker.stop()
            self._worker.wait()

###
## MLedWidget class End
###

###
## MWorker class - QThread class for dirty work - to write and previously set data
###
class MWorker(QThread):
    def __init__(self, readoperation, writeoperation, parent=None):
        super(MWorker, self).__init__(parent)

        # mutex to control exit conditions
        self._bstop = False
        self._stopmutex = QMutex()

        # function to process
        self.read = readoperation
        self.write = writeoperation

        # storage for data writing
        self._datawrite = {}
        self._writemutex = QMutex()

    # run specific operation when access mutex allows it
    def run(self):
        while(not self._bstop):
            # write values in the beginning of read cycle
            with(QMutexLocker(self._writemutex)):
                # enumerate through different keys
                for k in self._datawrite.keys():
                    # check values, write value to the Led device (attribute and its value)
                    if(self._datawrite[k] is not None):
                        self.write(k, self._datawrite[k])
                        self._datawrite[k] = None
                        self.msleep(500)
            # read data
            self.read()
            self.msleep(500)
        self.stop()
        return

    def stop(self):
        with(QMutexLocker(self._stopmutex)):
            self._bstop = True

    # make sure only the last attribute value is written - use dictionaries
    def addWritable(self, attribute, value):
        with(QMutexLocker(self._writemutex)):
            self._datawrite[attribute] = value

###
## MWorker class End
###

###
## MTcpSocket - class for direct working with LED
###

class MTcpSocketWrapper(QObject):
    def __init__(self, parent=None):
        super(MTcpSocket, self).__init__(parent)

        self.initVars()
        self.initSelf()
        self.initEvents()

    def initVars(self):
        self._socket = QTcpSocket()
        self._port = 50811
        self._host = "192.168.57.243"

        self._mutex = QMutex()
        return

    def initSelf(self):
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

    # command for blocking read
    def read(self, cmd):
        # try to see if we can read - lock mutex
        if(not self._mutex.tryLock()):
            return
        else
            self._mutex.unlock()

        # read values
        with(QMutexLocker(self._mutex):
            self._socket.connectToHost(self.host, self.port)


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
