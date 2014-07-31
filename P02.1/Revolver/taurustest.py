# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpAOjxen.ui'
#
# Created: Thu Jun  5 10:20:07 2014
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import PyQt4
from taurus.qt import Qt
import logging
from taurus import Device
from sardana import macroserver
import time
import PyTango
#from  taurus.core.tango.sardana.macro import SingleParamNode.type

#import taurus.core.tango.sardana.macro.Macro

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(533, 641)
        self.macroserver = PyTango.DeviceProxy("tango://has6117b:10000/p02/macroserver/has6117b")
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.taurusMacroExecutorWidget = TaurusMacroExecutorWidget(Form)
        self.taurusMacroExecutorWidget.setObjectName("taurusMacroExecutorWidget")
        self.gridLayout.addWidget(self.taurusMacroExecutorWidget, 0, 0, 1, 1)
        self.qDoor = Device("tango://has6117b:10000/p02/door/has6117b")
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
    
    def stepper(self, data):
        macro = data[0]
        if macro is None: return        
        data = data[1][0]
        state, range, step, id = data["state"], data["range"], data["step"], data["id"]
        if id is None: return
        id = int(id)
        
        if state == "start":
            ln = self.qDoor.macro_server.getMacroNodeObj("ascan")
            logging.error(ln.params()[0].type())
        #r = SingleParamNode()
        #state, range, step, id = data["state"], data["range"], data["step"], data["id"]
        #ln = self.qDoor.macro_server.getMacroNodeObj("ascan")
        #logging.error(ln.params()[0].type())
        #logging.error("dostal som krok")
    
    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.extra_macroexecutor import TaurusMacroExecutorWidget

if __name__ == "__main__":
    from taurus.qt.qtgui.application import TaurusApplication
    import sys
    
    app = TaurusApplication(sys.argv)
    Form = TaurusWidget()
    
    ui = Ui_Form()
    ui.setupUi(Form)
    
    Qt.QObject.connect(ui.taurusMacroExecutorWidget, Qt.SIGNAL("doorChanged"), ui.taurusMacroExecutorWidget.onDoorChanged)
    
    ui.taurusMacroExecutorWidget.setModel("tango://has6117b:10000/p02/macroserver/has6117b")
    ui.taurusMacroExecutorWidget.emit(Qt.SIGNAL('doorChanged'),"tango://has6117b:10000/p02/door/has6117b")
    
    Qt.QObject.connect(ui.qDoor, Qt.SIGNAL("macroStatusUpdated"), ui.taurusMacroExecutorWidget.onMacroStatusUpdated)
    Qt.QObject.connect(ui.qDoor, Qt.SIGNAL("macroStatusUpdated"), ui.stepper)
    logging.error(ui.taurusMacroExecutorWidget.macroComboBox.count())
    #ui.taurusMacroExecutorWidget.emit(Qt.SIGNAL('doorChanged'),"tango://has6117b:10000/p02/door/has6117b")
    #ui.taurusMacroExecutorWidget.setDoorName("tango://has6117b:10000/p02/door/has6117b")\
    #m = Macro()
    
    logging.error(ui.taurusMacroExecutorWidget.doorName())
    Form.show()
    sys.exit(app.exec_())

