# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpqq7xk4.ui'
#
# Created: Thu Oct 17 17:22:44 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(350, 57)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setStyleSheet("#value {\n"
"    background:#00ff00;\n"
"    font-size:20px;\n"
"    font-weight:bold;\n"
"    padding:5px;\n"
"}")
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.gridLayout.setMargin(5)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.value = QtGui.QLabel(Form)
        self.value.setScaledContents(True)
        self.value.setAlignment(QtCore.Qt.AlignCenter)
        self.value.setWordWrap(False)
        self.value.setObjectName("value")
        self.gridLayout.addWidget(self.value, 0, 0, 1, 1)
        self.device_name = QtGui.QLabel(Form)
        self.device_name.setMinimumSize(QtCore.QSize(0, 0))
        self.device_name.setMaximumSize(QtCore.QSize(250, 16777215))
        self.device_name.setStyleSheet("font-weight:bold")
        self.device_name.setObjectName("device_name")
        self.gridLayout.addWidget(self.device_name, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Device value status", None, QtGui.QApplication.UnicodeUTF8))
        self.value.setText(QtGui.QApplication.translate("Form", "VALUE ACTUAL", None, QtGui.QApplication.UnicodeUTF8))
        self.device_name.setText(QtGui.QApplication.translate("Form", "Device name", None, QtGui.QApplication.UnicodeUTF8))

