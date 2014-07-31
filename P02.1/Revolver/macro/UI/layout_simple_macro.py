# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpwGjyZH.ui'
#
# Created: Thu Jan 23 15:09:09 2014
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(989, 700)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setMargin(5)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.macro_main_controls = QtGui.QWidget(Form)
        self.macro_main_controls.setObjectName("macro_main_controls")
        self.gridLayout_4 = QtGui.QGridLayout(self.macro_main_controls)
        self.gridLayout_4.setContentsMargins(0, 5, 0, 0)
        self.gridLayout_4.setHorizontalSpacing(5)
        self.gridLayout_4.setVerticalSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.button_save_macro = QtGui.QPushButton(self.macro_main_controls)
        self.button_save_macro.setObjectName("button_save_macro")
        self.gridLayout_4.addWidget(self.button_save_macro, 0, 1, 1, 1)
        self.button_load_macro = QtGui.QPushButton(self.macro_main_controls)
        self.button_load_macro.setObjectName("button_load_macro")
        self.gridLayout_4.addWidget(self.button_load_macro, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(255, 24, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 0, 3, 1, 1)
        self.button_add_macro = QtGui.QPushButton(self.macro_main_controls)
        self.button_add_macro.setStyleSheet("QPushButton{background:#80DFFF}\n"
"QPushButton:disabled{ background:silver;color:grey }")
        self.button_add_macro.setObjectName("button_add_macro")
        self.gridLayout_4.addWidget(self.button_add_macro, 0, 4, 1, 1)
        self.button_run_macros = QtGui.QPushButton(self.macro_main_controls)
        self.button_run_macros.setStyleSheet("QPushButton{background:#80FF9F}\n"
"QPushButton:disabled{ background:silver;color:grey }")
        self.button_run_macros.setObjectName("button_run_macros")
        self.gridLayout_4.addWidget(self.button_run_macros, 0, 5, 1, 1)
        self.button_macro_reset = QtGui.QPushButton(self.macro_main_controls)
        self.button_macro_reset.setObjectName("button_macro_reset")
        self.gridLayout_4.addWidget(self.button_macro_reset, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.macro_main_controls, 2, 0, 1, 1)
        self.macro_wait_controls = QtGui.QGroupBox(Form)
        self.macro_wait_controls.setStyleSheet("QGroupBox {\n"
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
        self.macro_wait_controls.setObjectName("macro_wait_controls")
        self.gridLayout_9 = QtGui.QGridLayout(self.macro_wait_controls)
        self.gridLayout_9.setSpacing(5)
        self.gridLayout_9.setContentsMargins(5, 10, 5, 5)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.macro_waiting_progressbar = QtGui.QProgressBar(self.macro_wait_controls)
        self.macro_waiting_progressbar.setProperty("value", 0)
        self.macro_waiting_progressbar.setObjectName("macro_waiting_progressbar")
        self.gridLayout_9.addWidget(self.macro_waiting_progressbar, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.macro_wait_controls, 3, 0, 1, 1)
        self.macro_steps_controls = QtGui.QGroupBox(Form)
        self.macro_steps_controls.setEnabled(True)
        self.macro_steps_controls.setStyleSheet("QGroupBox {\n"
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
        self.macro_steps_controls.setObjectName("macro_steps_controls")
        self.gridLayout_6 = QtGui.QGridLayout(self.macro_steps_controls)
        self.gridLayout_6.setSpacing(5)
        self.gridLayout_6.setContentsMargins(5, 10, 5, 5)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.current_operation_status = QtGui.QLabel(self.macro_steps_controls)
        self.current_operation_status.setStyleSheet("background:orange;padding:5")
        self.current_operation_status.setObjectName("current_operation_status")
        self.gridLayout_6.addWidget(self.current_operation_status, 0, 0, 1, 2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.macro_progressbar = QtGui.QProgressBar(self.macro_steps_controls)
        self.macro_progressbar.setProperty("value", 0)
        self.macro_progressbar.setObjectName("macro_progressbar")
        self.horizontalLayout_3.addWidget(self.macro_progressbar)
        self.input_macro_halt = QtGui.QPushButton(self.macro_steps_controls)
        self.input_macro_halt.setStyleSheet("QPushButton{background:purple;font-weight:bold;color:#fff;}\n"
"QPushButton:disabled{ background:silver;color:grey }")
        self.input_macro_halt.setObjectName("input_macro_halt")
        self.horizontalLayout_3.addWidget(self.input_macro_halt)
        self.gridLayout_6.addLayout(self.horizontalLayout_3, 1, 0, 1, 2)
        self.gridLayout.addWidget(self.macro_steps_controls, 4, 0, 1, 1)
        self.repaet_macro_layout = QtGui.QWidget(Form)
        self.repaet_macro_layout.setObjectName("repaet_macro_layout")
        self.gridLayout_8 = QtGui.QGridLayout(self.repaet_macro_layout)
        self.gridLayout_8.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.gridLayout_8.setContentsMargins(-1, 5, -1, -1)
        self.gridLayout_8.setObjectName("gridLayout_8")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_8.addItem(spacerItem1, 0, 1, 1, 1)
        self.label_8 = QtGui.QLabel(self.repaet_macro_layout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setObjectName("label_8")
        self.gridLayout_8.addWidget(self.label_8, 0, 3, 1, 1)
        self.repeat_macro = QtGui.QSpinBox(self.repaet_macro_layout)
        self.repeat_macro.setMinimum(1)
        self.repeat_macro.setMaximum(999999999)
        self.repeat_macro.setObjectName("repeat_macro")
        self.gridLayout_8.addWidget(self.repeat_macro, 0, 4, 1, 1)
        self.macro_reset_fileindex = QtGui.QCheckBox(self.repaet_macro_layout)
        self.macro_reset_fileindex.setChecked(True)
        self.macro_reset_fileindex.setObjectName("macro_reset_fileindex")
        self.gridLayout_8.addWidget(self.macro_reset_fileindex, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.repaet_macro_layout, 1, 0, 1, 1)
        self.widget_select = QtGui.QWidget(Form)
        self.widget_select.setObjectName("widget_select")
        self.gridLayout_2 = QtGui.QGridLayout(self.widget_select)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.macro_controls_loop = QtGui.QWidget(self.widget_select)
        self.macro_controls_loop.setEnabled(True)
        self.macro_controls_loop.setStyleSheet("b")
        self.macro_controls_loop.setObjectName("macro_controls_loop")
        self.loop_macro_controls = QtGui.QGridLayout(self.macro_controls_loop)
        self.loop_macro_controls.setMargin(0)
        self.loop_macro_controls.setHorizontalSpacing(0)
        self.loop_macro_controls.setObjectName("loop_macro_controls")
        self.gridLayout_2.addWidget(self.macro_controls_loop, 0, 0, 1, 1)
        self.table = QtGui.QTableWidget(self.widget_select)
        self.table.setEnabled(True)
        self.table.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
        self.table.setShowGrid(True)
        self.table.setGridStyle(QtCore.Qt.SolidLine)
        self.table.setObjectName("table")
        self.table.setColumnCount(10)
        self.table.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(9, item)
        self.table.horizontalHeader().setCascadingSectionResizes(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setCascadingSectionResizes(True)
        self.table.verticalHeader().setStretchLastSection(False)
        self.gridLayout_2.addWidget(self.table, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.widget_select, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.button_macro_reset, QtCore.SIGNAL("clicked()"), Form.action_reset_macro)
        QtCore.QObject.connect(self.button_save_macro, QtCore.SIGNAL("clicked()"), Form.action_save_macro)
        QtCore.QObject.connect(self.button_load_macro, QtCore.SIGNAL("clicked()"), Form.action_load_macro)
        QtCore.QObject.connect(Form, QtCore.SIGNAL("created()"), self.macro_steps_controls.hide)
        QtCore.QObject.connect(Form, QtCore.SIGNAL("created()"), self.macro_wait_controls.hide)
        QtCore.QObject.connect(self.input_macro_halt, QtCore.SIGNAL("clicked()"), Form.action_halt_macro)
        QtCore.QObject.connect(self.button_add_macro, QtCore.SIGNAL("clicked()"), Form.action_open_dialog_add_macro)
        QtCore.QObject.connect(self.button_run_macros, QtCore.SIGNAL("clicked()"), Form.action_start_macro)
        QtCore.QObject.connect(self.table, QtCore.SIGNAL("itemChanged(QTableWidgetItem*)"), Form.action_macro_edited)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Macro", None, QtGui.QApplication.UnicodeUTF8))
        self.button_save_macro.setText(QtGui.QApplication.translate("Form", "Save macro", None, QtGui.QApplication.UnicodeUTF8))
        self.button_load_macro.setText(QtGui.QApplication.translate("Form", "Load macro", None, QtGui.QApplication.UnicodeUTF8))
        self.button_add_macro.setText(QtGui.QApplication.translate("Form", "Add macro step", None, QtGui.QApplication.UnicodeUTF8))
        self.button_run_macros.setText(QtGui.QApplication.translate("Form", "Start macro", None, QtGui.QApplication.UnicodeUTF8))
        self.button_macro_reset.setText(QtGui.QApplication.translate("Form", "Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_wait_controls.setTitle(QtGui.QApplication.translate("Form", "Waiting", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_waiting_progressbar.setFormat(QtGui.QApplication.translate("Form", "Waiting progress: %p%", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_steps_controls.setTitle(QtGui.QApplication.translate("Form", "Macro progress and status", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_progressbar.setFormat(QtGui.QApplication.translate("Form", "Macro progress: %p%", None, QtGui.QApplication.UnicodeUTF8))
        self.input_macro_halt.setText(QtGui.QApplication.translate("Form", "Stop macro", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Form", "Execute macro steps", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_reset_fileindex.setText(QtGui.QApplication.translate("Form", "Reset detector fileindex", None, QtGui.QApplication.UnicodeUTF8))
        self.table.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("Form", "Sample name", None, QtGui.QApplication.UnicodeUTF8))
        self.table.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("Form", "Motor", None, QtGui.QApplication.UnicodeUTF8))
        self.table.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("Form", "Motor device", None, QtGui.QApplication.UnicodeUTF8))
        self.table.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("Form", "Position", None, QtGui.QApplication.UnicodeUTF8))
        self.table.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("Form", "Summed", None, QtGui.QApplication.UnicodeUTF8))
        self.table.horizontalHeaderItem(5).setText(QtGui.QApplication.translate("Form", "Post trigger", None, QtGui.QApplication.UnicodeUTF8))
        self.table.horizontalHeaderItem(6).setText(QtGui.QApplication.translate("Form", "Wait (sec)", None, QtGui.QApplication.UnicodeUTF8))
        self.table.horizontalHeaderItem(7).setText(QtGui.QApplication.translate("Form", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.table.horizontalHeaderItem(8).setText(QtGui.QApplication.translate("Form", "Dark", None, QtGui.QApplication.UnicodeUTF8))
        self.table.horizontalHeaderItem(9).setText(QtGui.QApplication.translate("Form", "Action", None, QtGui.QApplication.UnicodeUTF8))

