# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpGmDJle.ui'
#
# Created: Fri Oct 18 17:39:33 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(910, 138)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setMargin(5)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.set_macro_type = QtGui.QComboBox(Form)
        self.set_macro_type.setObjectName("set_macro_type")
        self.set_macro_type.addItem("")
        self.set_macro_type.addItem("")
        self.set_macro_type.addItem("")
        self.gridLayout.addWidget(self.set_macro_type, 0, 1, 1, 1)
        self.label_16 = QtGui.QLabel(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)
        self.label_16.setObjectName("label_16")
        self.gridLayout.addWidget(self.label_16, 0, 0, 1, 1)
        self.line = QtGui.QFrame(Form)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.macro_select = QtGui.QStackedWidget(Form)
        self.macro_select.setObjectName("macro_select")
        self.simple_macro_layout = QtGui.QWidget()
        self.simple_macro_layout.setObjectName("simple_macro_layout")
        self.gridLayout_2 = QtGui.QGridLayout(self.simple_macro_layout)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.macro_select.addWidget(self.simple_macro_layout)
        self.loop_macro_layout = QtGui.QWidget()
        self.loop_macro_layout.setObjectName("loop_macro_layout")
        self.gridLayout_3 = QtGui.QGridLayout(self.loop_macro_layout)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.macro_select.addWidget(self.loop_macro_layout)
        self.time_macro_layout = QtGui.QWidget()
        self.time_macro_layout.setObjectName("time_macro_layout")
        self.gridLayout_4 = QtGui.QGridLayout(self.time_macro_layout)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.macro_select.addWidget(self.time_macro_layout)
        self.gridLayout.addWidget(self.macro_select, 2, 0, 1, 2)

        self.retranslateUi(Form)
        self.macro_select.setCurrentIndex(0)
        QtCore.QObject.connect(self.set_macro_type, QtCore.SIGNAL("currentIndexChanged(int)"), Form.action_macro_type_changed)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Macro", None, QtGui.QApplication.UnicodeUTF8))
        self.set_macro_type.setItemText(0, QtGui.QApplication.translate("Form", "Simple motor macro", None, QtGui.QApplication.UnicodeUTF8))
        self.set_macro_type.setItemText(1, QtGui.QApplication.translate("Form", "Looping motor macro", None, QtGui.QApplication.UnicodeUTF8))
        self.set_macro_type.setItemText(2, QtGui.QApplication.translate("Form", "Time motor macro", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setText(QtGui.QApplication.translate("Form", "Macro type", None, QtGui.QApplication.UnicodeUTF8))

