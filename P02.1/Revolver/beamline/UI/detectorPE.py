# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpQYsERc.ui'
#
# Created: Fri Oct  4 15:59:05 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(94, 150)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(217, 217, 217))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, brush)
        Form.setPalette(palette)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.device_button = QtGui.QPushButton(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.device_button.sizePolicy().hasHeightForWidth())
        self.device_button.setSizePolicy(sizePolicy)
        self.device_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.device_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.device_button.setAutoFillBackground(False)
        self.device_button.setStyleSheet("QPushButton#device_button {border:0;background:transparent;margin:0;padding:0} :checked {background-color: transparent;margin:0;padding:0} :pressed {border:0;background-color: transparent;margin:0;padding:0}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/devices/icons/detector.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap(":/devices/icons/detector.png"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/devices/icons/detector.png"), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        self.device_button.setIcon(icon)
        self.device_button.setIconSize(QtCore.QSize(73, 150))
        self.device_button.setCheckable(True)
        self.device_button.setAutoDefault(False)
        self.device_button.setDefault(False)
        self.device_button.setFlat(True)
        self.device_button.setObjectName("device_button")
        self.gridLayout.addWidget(self.device_button, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.device_button, QtCore.SIGNAL("toggled(bool)"), Form.action_device)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Shutter", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
