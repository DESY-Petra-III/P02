# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpB39KR5.ui'
#
# Created: Wed Oct 16 14:56:50 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.setEnabled(True)
        Dialog.resize(497, 470)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(Dialog)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setStyleSheet("QGroupBox {\n"
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
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.macro_input_sampleName = QtGui.QLineEdit(self.groupBox)
        self.macro_input_sampleName.setObjectName("macro_input_sampleName")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.macro_input_sampleName)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.macro_input_summed = QtGui.QSpinBox(self.groupBox)
        self.macro_input_summed.setMinimum(1)
        self.macro_input_summed.setMaximum(999999999)
        self.macro_input_summed.setObjectName("macro_input_summed")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.macro_input_summed)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.macro_input_filesafter = QtGui.QSpinBox(self.groupBox)
        self.macro_input_filesafter.setMaximum(999999999)
        self.macro_input_filesafter.setProperty("value", 1)
        self.macro_input_filesafter.setObjectName("macro_input_filesafter")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.macro_input_filesafter)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.macro_input_comment = QtGui.QLineEdit(self.groupBox)
        self.macro_input_comment.setMaxLength(900)
        self.macro_input_comment.setObjectName("macro_input_comment")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.macro_input_comment)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setStyleSheet("QGroupBox {\n"
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
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.label_5.setAutoFillBackground(False)
        self.label_5.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.label_5.setObjectName("label_5")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_5)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.macro_select_discrete = QtGui.QRadioButton(self.groupBox_2)
        self.macro_select_discrete.setCursor(QtCore.Qt.PointingHandCursor)
        self.macro_select_discrete.setChecked(True)
        self.macro_select_discrete.setObjectName("macro_select_discrete")
        self.horizontalLayout_4.addWidget(self.macro_select_discrete)
        self.macro_select_interval = QtGui.QRadioButton(self.groupBox_2)
        self.macro_select_interval.setCursor(QtCore.Qt.PointingHandCursor)
        self.macro_select_interval.setObjectName("macro_select_interval")
        self.horizontalLayout_4.addWidget(self.macro_select_interval)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)
        self.macro_input_position = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.macro_input_position.setDecimals(5)
        self.macro_input_position.setMinimum(-99999.0)
        self.macro_input_position.setMaximum(99999.0)
        self.macro_input_position.setObjectName("macro_input_position")
        self.gridLayout_2.addWidget(self.macro_input_position, 2, 0, 1, 1)
        self.macro_interval_controls = QtGui.QWidget(self.groupBox_2)
        self.macro_interval_controls.setMaximumSize(QtCore.QSize(16777215, 27))
        self.macro_interval_controls.setObjectName("macro_interval_controls")
        self.lay1 = QtGui.QHBoxLayout(self.macro_interval_controls)
        self.lay1.setSpacing(0)
        self.lay1.setMargin(0)
        self.lay1.setObjectName("lay1")
        self.macro_value_from = QtGui.QDoubleSpinBox(self.macro_interval_controls)
        self.macro_value_from.setDecimals(5)
        self.macro_value_from.setMinimum(-99999.0)
        self.macro_value_from.setMaximum(99999.0)
        self.macro_value_from.setObjectName("macro_value_from")
        self.lay1.addWidget(self.macro_value_from)
        self.macro_value_to = QtGui.QDoubleSpinBox(self.macro_interval_controls)
        self.macro_value_to.setDecimals(5)
        self.macro_value_to.setMinimum(-99999.0)
        self.macro_value_to.setMaximum(99999.0)
        self.macro_value_to.setObjectName("macro_value_to")
        self.lay1.addWidget(self.macro_value_to)
        self.macro_value_step = QtGui.QDoubleSpinBox(self.macro_interval_controls)
        self.macro_value_step.setDecimals(5)
        self.macro_value_step.setMinimum(-99999.0)
        self.macro_value_step.setMaximum(99999.0)
        self.macro_value_step.setObjectName("macro_value_step")
        self.lay1.addWidget(self.macro_value_step)
        self.gridLayout_2.addWidget(self.macro_interval_controls, 1, 0, 1, 1)
        self.formLayout_2.setLayout(1, QtGui.QFormLayout.FieldRole, self.gridLayout_2)
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_6)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.macro_input_motor = QtGui.QLineEdit(self.groupBox_2)
        self.macro_input_motor.setEnabled(False)
        self.macro_input_motor.setObjectName("macro_input_motor")
        self.horizontalLayout_3.addWidget(self.macro_input_motor)
        self.macro_button_select_motor = QtGui.QToolButton(self.groupBox_2)
        self.macro_button_select_motor.setCursor(QtCore.Qt.PointingHandCursor)
        self.macro_button_select_motor.setObjectName("macro_button_select_motor")
        self.horizontalLayout_3.addWidget(self.macro_button_select_motor)
        self.formLayout_2.setLayout(0, QtGui.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        self.groupBox_3.setStyleSheet("QGroupBox {\n"
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
        self.groupBox_3.setObjectName("groupBox_3")
        self.formLayout_3 = QtGui.QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_7 = QtGui.QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_7)
        self.macro_wait_time = QtGui.QSpinBox(self.groupBox_3)
        self.macro_wait_time.setMaximum(999999999)
        self.macro_wait_time.setObjectName("macro_wait_time")
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.macro_wait_time)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.check_take_dark = QtGui.QCheckBox(self.groupBox_3)
        self.check_take_dark.setObjectName("check_take_dark")
        self.horizontalLayout_5.addWidget(self.check_take_dark)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.formLayout_3.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout_5)
        self.label_8 = QtGui.QLabel(self.groupBox_3)
        self.label_8.setObjectName("label_8")
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_8)
        self.verticalLayout_3.addWidget(self.groupBox_3)
        spacerItem2 = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.macro_button_reset = QtGui.QPushButton(Dialog)
        self.macro_button_reset.setFocusPolicy(QtCore.Qt.NoFocus)
        self.macro_button_reset.setObjectName("macro_button_reset")
        self.horizontalLayout.addWidget(self.macro_button_reset)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.macro_button_close = QtGui.QPushButton(Dialog)
        self.macro_button_close.setFocusPolicy(QtCore.Qt.NoFocus)
        self.macro_button_close.setObjectName("macro_button_close")
        self.horizontalLayout.addWidget(self.macro_button_close)
        self.macro_button_add = QtGui.QPushButton(Dialog)
        self.macro_button_add.setFocusPolicy(QtCore.Qt.TabFocus)
        self.macro_button_add.setObjectName("macro_button_add")
        self.horizontalLayout.addWidget(self.macro_button_add)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.macro_button_reset, QtCore.SIGNAL("clicked()"), self.macro_input_position.clear)
        QtCore.QObject.connect(self.macro_button_reset, QtCore.SIGNAL("clicked()"), self.macro_value_from.clear)
        QtCore.QObject.connect(self.macro_button_reset, QtCore.SIGNAL("clicked()"), self.macro_value_to.clear)
        QtCore.QObject.connect(self.macro_button_reset, QtCore.SIGNAL("clicked()"), self.macro_value_step.clear)
        QtCore.QObject.connect(self.macro_button_reset, QtCore.SIGNAL("clicked()"), self.macro_input_filesafter.clear)
        QtCore.QObject.connect(self.macro_button_reset, QtCore.SIGNAL("clicked()"), self.macro_input_summed.clear)
        QtCore.QObject.connect(self.macro_button_reset, QtCore.SIGNAL("clicked()"), self.macro_input_sampleName.clear)
        QtCore.QObject.connect(self.macro_button_close, QtCore.SIGNAL("clicked()"), Dialog.close)
        QtCore.QObject.connect(self.macro_button_add, QtCore.SIGNAL("clicked()"), Dialog.action_add_macro)
        QtCore.QObject.connect(self.macro_select_discrete, QtCore.SIGNAL("clicked(bool)"), Dialog.action_select_discrete)
        QtCore.QObject.connect(self.macro_select_interval, QtCore.SIGNAL("clicked(bool)"), Dialog.action_select_interval)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.macro_button_select_motor, self.macro_button_add)
        Dialog.setTabOrder(self.macro_button_add, self.macro_input_motor)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Add macro step", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Detector settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Sample name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Summed", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Post trigger", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "User comment", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Motor settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Motor position", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_select_discrete.setText(QtGui.QApplication.translate("Dialog", "Discrete value", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_select_interval.setText(QtGui.QApplication.translate("Dialog", "Interval (from, to, step)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Motor", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_button_select_motor.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Dialog", "Macro settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog", "Wait after shot (sec)", None, QtGui.QApplication.UnicodeUTF8))
        self.check_take_dark.setText(QtGui.QApplication.translate("Dialog", "Take dark before macro step", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Dialog", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_button_reset.setText(QtGui.QApplication.translate("Dialog", "Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_button_close.setText(QtGui.QApplication.translate("Dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_button_add.setText(QtGui.QApplication.translate("Dialog", "Add macro step", None, QtGui.QApplication.UnicodeUTF8))

