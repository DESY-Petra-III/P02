# -*- coding: utf-8 -*-
from nxstools.nxsdevicetools import PYTANGO

# Form implementation generated from reading ui file '/tmp/tmpwSQzo7.ui'
#
# Created: Thu Jun  5 13:26:48 2014
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import logging

from Revolver.classes import devices, config

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(533, 641)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.container import TaurusWidget

if __name__ == "__main__":
    from taurus.qt.qtgui.application import TaurusApplication
    import taurus
    import sys
    import PyTango
    import sardana
    import taurus.core
    
    app = TaurusApplication(sys.argv)
    Form = TaurusWidget()
    
    ui = Ui_Form()
    ui.setupUi(Form)
    
    macroserver = PyTango.DeviceProxy("tango://has6117b:10000/p02/macroserver/has6117b")
    #t = macroserver.read_attribute("TypeList")
    door = devices.TangoDevice("tango://has6117b:10000/p02/door/has6117b")
    #t = macroserver.execute_command("RunMacro")
    #t=door.execute_command("RunMacro2", '<sequence><macro name="ascan" id="-17" macro_line="ascan(exp_mot61, 0, 15, 1, 1)"><param value="exp_mot61"/><param value="0"/><param value="15"/><param value="1"/><param value="1"/></macro></sequence>')
    #door = PyTango.DeviceProxy("tango://has6117b:10000/p02/door/has6117b")
    
    t=door.execute_command("RunMacro",['ct'])
    r=door.execute_command("Status")
    #door.execute_command("StopMacro")
    #door.execute_command("AbortMacro")
    #r=macroserver.command_inout("getMacroEnv",["ascan"])
    logging.error(r)
    
    #Form.show()
    sys.exit(app.exec_())

