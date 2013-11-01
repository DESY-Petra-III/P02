# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpKSSHI_.ui'
#
# Created: Thu Oct 24 13:05:06 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(695, 251)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout.setObjectName("gridLayout")
        self.detector_input_values = QtGui.QGroupBox(Form)
        self.detector_input_values.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    margin-top: 0.5em;\n"
" font-weight:bold\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 3px 0 3px;\n"
" font-weight:bold\n"
"   \n"
"}")
        self.detector_input_values.setObjectName("detector_input_values")
        self.gridLayout_3 = QtGui.QGridLayout(self.detector_input_values)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtGui.QLabel(self.detector_input_values)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 1, 0, 1, 1)
        self.sample_name = QtGui.QLineEdit(self.detector_input_values)
        self.sample_name.setObjectName("sample_name")
        self.gridLayout_3.addWidget(self.sample_name, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.detector_input_values)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 1)
        self.summed = QtGui.QSpinBox(self.detector_input_values)
        self.summed.setMaximum(9999999)
        self.summed.setProperty("value", 1)
        self.summed.setObjectName("summed")
        self.gridLayout_3.addWidget(self.summed, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.detector_input_values)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 3, 0, 1, 1)
        self.post_trigger = QtGui.QSpinBox(self.detector_input_values)
        self.post_trigger.setMinimum(1)
        self.post_trigger.setMaximum(9999999)
        self.post_trigger.setObjectName("post_trigger")
        self.gridLayout_3.addWidget(self.post_trigger, 3, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.detector_input_values)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 4, 0, 1, 1)
        self.comment = QtGui.QLineEdit(self.detector_input_values)
        self.comment.setObjectName("comment")
        self.gridLayout_3.addWidget(self.comment, 4, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.detector_input_values)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.detector_input_values, 1, 0, 1, 2)
        self.controls = QtGui.QHBoxLayout()
        self.controls.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.controls.setObjectName("controls")
        spacerItem = QtGui.QSpacerItem(40, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.controls.addItem(spacerItem)
        self.button_stop_acquisition = QtGui.QPushButton(Form)
        self.button_stop_acquisition.setObjectName("button_stop_acquisition")
        self.controls.addWidget(self.button_stop_acquisition)
        self.button_take_dark = QtGui.QPushButton(Form)
        self.button_take_dark.setObjectName("button_take_dark")
        self.controls.addWidget(self.button_take_dark)
        self.button_take_shot = QtGui.QPushButton(Form)
        self.button_take_shot.setObjectName("button_take_shot")
        self.controls.addWidget(self.button_take_shot)
        self.gridLayout.addLayout(self.controls, 2, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.detector_motor_layout = QtGui.QGridLayout()
        self.detector_motor_layout.setSpacing(0)
        self.detector_motor_layout.setObjectName("detector_motor_layout")
        self.gridLayout.addLayout(self.detector_motor_layout, 0, 0, 1, 2)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.button_take_dark, QtCore.SIGNAL("clicked()"), Form.action_take_dark_shot)
        QtCore.QObject.connect(self.button_take_shot, QtCore.SIGNAL("clicked()"), Form.action_take_shot)
        QtCore.QObject.connect(self.button_stop_acquisition, QtCore.SIGNAL("clicked()"), Form.action_stop_acquisition)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "PE detector controls", None, QtGui.QApplication.UnicodeUTF8))
        self.detector_input_values.setTitle(QtGui.QApplication.translate("Form", "Detector settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Sample name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Summed", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Post trigger", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Form", "Status", None, QtGui.QApplication.UnicodeUTF8))
        self.button_stop_acquisition.setText(QtGui.QApplication.translate("Form", "Stop acquisition", None, QtGui.QApplication.UnicodeUTF8))
        self.button_take_dark.setText(QtGui.QApplication.translate("Form", "Take dark", None, QtGui.QApplication.UnicodeUTF8))
        self.button_take_shot.setText(QtGui.QApplication.translate("Form", "Take shot", None, QtGui.QApplication.UnicodeUTF8))

