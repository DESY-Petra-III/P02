# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpFGSQFi.ui'
#
# Created: Mon Jun 16 09:41:33 2014
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(633, 417)
        Form.setStyleSheet("#controls_frame{\n"
"    border-top: 3px solid #cfcfcf;\n"
"}")
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.controls_frame = QtGui.QFrame(Form)
        self.controls_frame.setStyleSheet("#controls_frame{\n"
"    background-color:#d2e2ed;\n"
"}")
        self.controls_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.controls_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.controls_frame.setObjectName("controls_frame")
        self.gridLayout_3 = QtGui.QGridLayout(self.controls_frame)
        self.gridLayout_3.setContentsMargins(9, -1, -1, -1)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.beamline_device_controls = QtGui.QTabWidget(self.controls_frame)
        self.beamline_device_controls.setStyleSheet("#beamline_device_controls {padding:5px}")
        self.beamline_device_controls.setObjectName("beamline_device_controls")
        self.gridLayout_3.addWidget(self.beamline_device_controls, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtGui.QPushButton(self.controls_frame)
        self.pushButton.setMinimumSize(QtCore.QSize(250, 0))
        self.pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton.setStyleSheet("background:purple;font-weight:bold;color:#fff")
        self.pushButton.setAutoExclusive(False)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.gridLayout_3.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.controls_frame, 4, 0, 1, 1)
        self.bemaline_setup = QtGui.QHBoxLayout()
        self.bemaline_setup.setSpacing(10)
        self.bemaline_setup.setMargin(0)
        self.bemaline_setup.setObjectName("bemaline_setup")
        self.gridLayout.addLayout(self.bemaline_setup, 3, 0, 1, 1)
        self.beamline_controls = QtGui.QWidget(Form)
        self.beamline_controls.setStyleSheet("#beamline_controls {\n"
"    background:#d9d9d9;\n"
"    border-bottom: 3px solid #cfcfcf;\n"
"}")
        self.beamline_controls.setObjectName("beamline_controls")
        self.gridLayout_9 = QtGui.QGridLayout(self.beamline_controls)
        self.gridLayout_9.setMargin(5)
        self.gridLayout_9.setSpacing(5)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.button_expert_mode = QtGui.QPushButton(self.beamline_controls)
        self.button_expert_mode.setCursor(QtCore.Qt.PointingHandCursor)
        self.button_expert_mode.setFocusPolicy(QtCore.Qt.NoFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/devices/icons/expert_mode.png"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        self.button_expert_mode.setIcon(icon)
        self.button_expert_mode.setCheckable(True)
        self.button_expert_mode.setChecked(False)
        self.button_expert_mode.setObjectName("button_expert_mode")
        self.gridLayout_9.addWidget(self.button_expert_mode, 0, 6, 1, 1)
        self.label = QtGui.QLabel(self.beamline_controls)
        self.label.setObjectName("label")
        self.gridLayout_9.addWidget(self.label, 0, 5, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem2, 0, 0, 1, 1)
        self.pushButton_2 = QtGui.QPushButton(self.beamline_controls)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/devices/icons/macro_mode.png"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon1)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_9.addWidget(self.pushButton_2, 0, 4, 1, 1)
        self.pushButton_3 = QtGui.QPushButton(self.beamline_controls)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/devices/icons/mgrp.png"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        self.pushButton_3.setIcon(icon2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_9.addWidget(self.pushButton_3, 0, 2, 1, 1)
        self.label_3 = QtGui.QLabel(self.beamline_controls)
        self.label_3.setObjectName("label_3")
        self.gridLayout_9.addWidget(self.label_3, 0, 3, 1, 1)
        self.label_4 = QtGui.QLabel(self.beamline_controls)
        self.label_4.setObjectName("label_4")
        self.gridLayout_9.addWidget(self.label_4, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.beamline_controls, 2, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), Form.action_halt_all_devices)
        QtCore.QObject.connect(self.beamline_device_controls, QtCore.SIGNAL("currentChanged(int)"), Form.action_controls_changed)
        QtCore.QObject.connect(self.button_expert_mode, QtCore.SIGNAL("clicked(bool)"), Form.action_set_expert_mode)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"), Form.action_open_sardana_macro)
        QtCore.QObject.connect(self.pushButton_3, QtCore.SIGNAL("clicked()"), Form.action_open_mgrp_editor)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Form", "Stop all movements", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Expert mode", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Sardana macro executor", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Measurement group editor", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
