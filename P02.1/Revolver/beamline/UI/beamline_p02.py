# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpU0iZfQ.ui'
#
# Created: Thu Oct  3 19:08:59 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.bemaline_setup = QtGui.QGridLayout()
        self.bemaline_setup.setObjectName("bemaline_setup")
        self.gridLayout.addLayout(self.bemaline_setup, 0, 0, 1, 1)
        self.beamline_device_controls = QtGui.QTabWidget(Form)
        self.beamline_device_controls.setObjectName("beamline_device_controls")
        self.gridLayout.addWidget(self.beamline_device_controls, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))

