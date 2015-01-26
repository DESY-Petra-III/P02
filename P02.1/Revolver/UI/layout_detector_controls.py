# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layout_detector_controls.ui'
#
# Created: Fri Jan 23 16:01:41 2015
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(892, 293)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.detector_motor_layout = QtGui.QGridLayout()
        self.detector_motor_layout.setSpacing(0)
        self.detector_motor_layout.setObjectName(_fromUtf8("detector_motor_layout"))
        self.gridLayout.addLayout(self.detector_motor_layout, 0, 0, 1, 2)
        self.detector_input_values = QtGui.QGroupBox(Form)
        self.detector_input_values.setStyleSheet(_fromUtf8("QGroupBox {\n"
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
"}"))
        self.detector_input_values.setObjectName(_fromUtf8("detector_input_values"))
        self.gridLayout_3 = QtGui.QGridLayout(self.detector_input_values)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label = QtGui.QLabel(self.detector_input_values)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 1, 0, 1, 1)
        self.sample_name = QtGui.QLineEdit(self.detector_input_values)
        self.sample_name.setObjectName(_fromUtf8("sample_name"))
        self.gridLayout_3.addWidget(self.sample_name, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.detector_input_values)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 1)
        self.summed = QtGui.QSpinBox(self.detector_input_values)
        self.summed.setMaximum(9999999)
        self.summed.setProperty("value", 1)
        self.summed.setObjectName(_fromUtf8("summed"))
        self.gridLayout_3.addWidget(self.summed, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.detector_input_values)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_3.addWidget(self.label_3, 3, 0, 1, 1)
        self.post_trigger = QtGui.QSpinBox(self.detector_input_values)
        self.post_trigger.setMinimum(1)
        self.post_trigger.setMaximum(9999999)
        self.post_trigger.setObjectName(_fromUtf8("post_trigger"))
        self.gridLayout_3.addWidget(self.post_trigger, 3, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.detector_input_values)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_3.addWidget(self.label_4, 4, 0, 1, 1)
        self.comment = QtGui.QLineEdit(self.detector_input_values)
        self.comment.setObjectName(_fromUtf8("comment"))
        self.gridLayout_3.addWidget(self.comment, 4, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.detector_input_values)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.detector_input_values, 1, 0, 1, 2)
        self.controls = QtGui.QHBoxLayout()
        self.controls.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.controls.setObjectName(_fromUtf8("controls"))
        spacerItem = QtGui.QSpacerItem(40, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.controls.addItem(spacerItem)
        self.button_stop_acquisition = QtGui.QPushButton(Form)
        self.button_stop_acquisition.setEnabled(True)
        self.button_stop_acquisition.setStyleSheet(_fromUtf8("QPushButton{background:purple;font-weight:bold;color:#fff;}\n"
"QPushButton:disabled{ background:silver;color:grey }"))
        self.button_stop_acquisition.setObjectName(_fromUtf8("button_stop_acquisition"))
        self.controls.addWidget(self.button_stop_acquisition)
        self.button_take_dark = QtGui.QPushButton(Form)
        self.button_take_dark.setEnabled(True)
        self.button_take_dark.setStyleSheet(_fromUtf8("QPushButton{background:#80FF9F}\n"
"QPushButton:disabled{ background:silver;color:grey }"))
        self.button_take_dark.setObjectName(_fromUtf8("button_take_dark"))
        self.controls.addWidget(self.button_take_dark)
        self.button_take_shot = QtGui.QPushButton(Form)
        self.button_take_shot.setStyleSheet(_fromUtf8("QPushButton{background:#80FF9F}\n"
"QPushButton:disabled{ background:silver;color:grey }"))
        self.button_take_shot.setObjectName(_fromUtf8("button_take_shot"))
        self.controls.addWidget(self.button_take_shot)
        self.gridLayout.addLayout(self.controls, 2, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.button_take_dark, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.action_take_dark_shot)
        QtCore.QObject.connect(self.button_take_shot, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.action_take_shot)
        QtCore.QObject.connect(self.button_stop_acquisition, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.action_stop_acquisition)
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

