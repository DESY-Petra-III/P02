# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpoEEBhw.ui'
#
# Created: Sun Oct 20 11:28:19 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(281, 27)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.formLayout = QtGui.QFormLayout(Form)
        self.formLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.formLayout.setMargin(5)
        self.formLayout.setSpacing(5)
        self.formLayout.setObjectName("formLayout")
        self.status_led = QLed(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status_led.sizePolicy().hasHeightForWidth())
        self.status_led.setSizePolicy(sizePolicy)
        self.status_led.setMinimumSize(QtCore.QSize(15, 15))
        self.status_led.setMaximumSize(QtCore.QSize(15, 15))
        self.status_led.setObjectName("status_led")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.status_led)
        self.device_name = QtGui.QLabel(Form)
        self.device_name.setMinimumSize(QtCore.QSize(150, 0))
        self.device_name.setMaximumSize(QtCore.QSize(250, 16777215))
        self.device_name.setStyleSheet("font-weight:bold")
        self.device_name.setObjectName("device_name")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.device_name)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Device led status", None, QtGui.QApplication.UnicodeUTF8))
        self.device_name.setText(QtGui.QApplication.translate("Form", "Device name", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.display import QLed
