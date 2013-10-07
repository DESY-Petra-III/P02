#!/usr/bin/env python

import sys
# add modules to the list
sys.path.append("/home/p02user/scripts/")
sys.path.append("/home/p02user/scripts/modules")

from  PyTango import *
import pylab
import numpy
import p3cntr
reload(p3cntr)

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Ruby Motors
(MRUBYMOTORX, MRUBYMOTORY, MRUBYMOTORZ) = ("haspp02oh1:10000/p02/motor/eh2b.46", "haspp02oh1:10000/p02/motor/eh2b.47", "haspp02oh1:10000/p02/motor/eh2b.48")

# Led device
MLEDGPDEV = "tango://haspp02oh1:10000/p02/led/exp.04"
(MLEDONOFF, MLEDINTENSITY, MLEDTEMP) = ("LEDOffOn", "Intensity", "Temperature")

# timer timeout for LED values update
MLEDTIMERTIMEOUT = 1000

# LED switch button captions
(MLEDON, MLEDOFF) = ("Led ON", "Led OFF")

# device to check for diode position - updated by LED widget in a single loop
MDIODEDEV = "tango://haspp02oh1:10000/p02/spseh2/eh2a.01"
MDIODEPOS = "GPValve1"

# signal reporting diode position
MSIGNALDIODEINOUT = "isDiodeIn(bool)"


###
## MRubyWidget class - widget controling GP table Ruby microscope movements, collisions, light
###
class MRubyWidget(QMainWindow):
    def __init__(self, parent=None):
        super(MRubyWidget, self).__init__(parent)

        self.initVars()
        self.initSelf()
        self.initEvents()
        return

    # initialize main variables
    def initVars(self):
        # motors widget
        self.wmotors = None
        # LED widget
        self.wled  = None
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
        self.setWindowTitle("Ruby system (GP)")

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

        self.show()
        return

    # initialize events
    def initEvents(self):
        # process signal reporting that diode is in - disable corresponding motor controls
        self.connect(self.wled, SIGNAL(MSIGNALDIODEINOUT), self.processDiodeInOut)
        return

    # initialize Motors widget
    def initMotorsWidget(self):
        wdgt = QGroupBox("Motors")
        layout = QGridLayout(wdgt)

        rubyX = p3cntr.Motor("Ruby X",
                    "Ruby X",
                    MRUBYMOTORX)
        rubyY = p3cntr.Motor("Ruby Y",
                    "Ruby Y",
                    MRUBYMOTORY)
        rubyZ = p3cntr.Motor("Ruby Z",
                    "Ruby Z",
                    MRUBYMOTORZ)

        self.wmotors = p3cntr.ui.MotorWidgetAdvanced([rubyX, rubyY, rubyZ])

        layout.addWidget(self.wmotors, 0, 0)
        return wdgt

    # initialize Led widget
    def initLedWidget(self):
        wdgt = QGroupBox("LED light Intensity")
        layout = QGridLayout(wdgt)

        self.wled = MLedWidget(self)

        layout.addWidget(self.wled, 0, 0)
        return wdgt

    # process signal reporting diode movement - occurs only on state change
    def processDiodeInOut(self, bflag):
        if(bflag):  # diode is in stop all motors for Ruby
            self.wmotors.processStopMotors()

        # disable or enable controls depending on situation
        self.wmotors.setWidgetRowsDisabledByName(bflag, "Ruby X", "Ruby Y", "Ruby Z")
        return

    def closeEvent(self, event):
        event.accept()

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

        # tango device for shutter
        self._devdiode = MDIODEDEV
        self._olddiodepos = 0

        # timer for updates
        self._timer = QTimer()
        self._timer.setInterval(MLEDTIMERTIMEOUT)
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

        # update gui from Tango values
        self.processLedUpdate()

        # show widget
        self.show()
        return

    # initialize events
    def initEvents(self):
        # timer update
        self.connect(self._timer, SIGNAL("timeout()"), self.processLedUpdate)

        # gui events
            # switch on, off
        self.connect(self.btnonoff, SIGNAL("toggled(bool)"), self.processLightSwitch)
            # change intensity
        self.connect(self.leintensity, SIGNAL("returnPressed()"), self.processIntensityChangeText)
        self.connect(self.leintensity, SIGNAL("editingFinished()"), self.processIntensityChangeText)
            # change value by slider
        self.connect(self.slintensity, SIGNAL("valueChanged(int)"), self.processIntensityChangeSlider)

        # start timer
        self._timer.start()
        return

    # correct widgets length in a set
    def setWidgetsMaximumWidth(self, value, *tlist):
        t = type(tlist[0])
        if(t is tuple or t is list):
            tlist = tlist[0]

        for w in tlist:
            w.setMaximumWidth(value)
        return

    # process timer update
    def processLedUpdate(self):
        # device proxy
        dev = DeviceProxy(self._dev)

        # try device
        try:
            dev.state()
        except DevError:
            print("Error: Tango connection Failed")
            return

        # read intensity, update it if necessary
        temp = dev.read_attribute(MLEDINTENSITY).value
        if(temp != self.slintensity.value()):
            self.leintensity.setText("%i" % temp)
            self.slintensity.setValue(temp)

        # read temperature
        temp = dev.read_attribute(MLEDTEMP).value

        self.letemp.setText("%i" % temp)

        # read on/off state
        temp = dev.read_attribute(MLEDONOFF).value
        if(temp>0):     # ON
            self.btnonoff.setChecked(True)
            self.btnonoff.setText(MLEDON)
        else:           # OFF
            self.btnonoff.setChecked(False)
            self.btnonoff.setText(MLEDOFF)

        # check shutter pposition, emit signal if needed
        # device proxy
        dev = DeviceProxy(self._devdiode)

        # try device
        try:
            dev.state()
        except DevError:
            print("Error: Tango connection Failed")
            return

        # report diode position for parent widget - if a change has occured
        temp =  dev.read_attribute(MDIODEPOS).value
        if(temp!=self._olddiodepos):     # change occured

            bflag = False # by default it is out

            if(temp>0):     # position in
                bflag = True

            self.emit(SIGNAL(MSIGNALDIODEINOUT), bflag)
            self._olddiodepos = temp

        return

    # process light switching - ON/OFF
    def processLightSwitch(self, bflag):
        value = 0
        if(bflag):     # ON
            self.btnonoff.setText(MLEDON)
            value = 1
        else:          # OFF
            self.btnonoff.setText(MLEDOFF)

        # device proxy
        dev = DeviceProxy(self._dev)

        # try device
        try:
            dev.state()
        except DevError:
            print("Error: Tango connection Failed")
            return

        # write on/off state
        dev.write_attribute(MLEDONOFF, value)
        return

    # intensity value changed by QLineEdit field
    def processIntensityChangeText(self):
        value = self.leintensity.text()

        try:
            value = int(value)
        except ValueError:
            value = 0

        self.processIntensityChangeSlider(value)
        return

    # intensity value changed by QSlider
    def processIntensityChangeSlider(self, value):
        # device proxy
        dev = DeviceProxy(self._dev)

        # try device
        try:
            dev.state()
        except DevError:
            print("Error: Tango connection Failed")
            return

        # set value
        self.slintensity.setValue(value)
        self.leintensity.setText("%i" % value)
        dev.write_attribute(MLEDINTENSITY, value)
        return

    def closeEvent(self, event):
        event.accept()


###
## MLedWidget class End
###

# possibility to start, debug and test widget
if __name__ == "__main__":
    app = QApplication([])
    form = MRubyWidget()
    app.exec_()