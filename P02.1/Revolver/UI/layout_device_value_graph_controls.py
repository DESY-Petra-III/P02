# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpVus7iK.ui'
#
# Created: Tue Oct 22 17:02:20 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(620, 214)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.graph_layout = QtGui.QGridLayout()
        self.graph_layout.setObjectName("graph_layout")
        self.gridLayout.addLayout(self.graph_layout, 0, 0, 1, 1)
        self.controls = QtGui.QWidget(Form)
        self.controls.setObjectName("controls")
        self.gridLayout_3 = QtGui.QGridLayout(self.controls)
        self.gridLayout_3.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.gridLayout_3.setObjectName("gridLayout_3")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 0, 3, 1, 1)
        self.label_2 = QtGui.QLabel(self.controls)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 4, 1, 1)
        self.polling_controls = QtGui.QWidget(self.controls)
        self.polling_controls.setObjectName("polling_controls")
        self.gridLayout_2 = QtGui.QGridLayout(self.polling_controls)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.input_polling_time = QtGui.QDoubleSpinBox(self.polling_controls)
        self.input_polling_time.setDecimals(1)
        self.input_polling_time.setMinimum(0.1)
        self.input_polling_time.setMaximum(999999.0)
        self.input_polling_time.setSingleStep(0.5)
        self.input_polling_time.setProperty("value", 1.0)
        self.input_polling_time.setObjectName("input_polling_time")
        self.gridLayout_2.addWidget(self.input_polling_time, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.polling_controls)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.polling_controls, 0, 6, 1, 1)
        self.input_values_number = QtGui.QSpinBox(self.controls)
        self.input_values_number.setMinimum(1)
        self.input_values_number.setMaximum(9999)
        self.input_values_number.setProperty("value", 600)
        self.input_values_number.setObjectName("input_values_number")
        self.gridLayout_3.addWidget(self.input_values_number, 0, 5, 1, 1)
        self.pushButton_2 = QtGui.QPushButton(self.controls)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_3.addWidget(self.pushButton_2, 0, 1, 1, 1)
        self.pushButton = QtGui.QPushButton(self.controls)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_3.addWidget(self.pushButton, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.controls, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"), Form.action_save_ascii)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), Form.action_save_image)
        QtCore.QObject.connect(self.input_values_number, QtCore.SIGNAL("valueChanged(int)"), Form.action_check_settings)
        QtCore.QObject.connect(self.input_polling_time, QtCore.SIGNAL("editingFinished()"), Form.action_check_settings)
        QtCore.QObject.connect(self.input_polling_time, QtCore.SIGNAL("editingFinished()"), Form.action_polling_changed)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Trend control", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Show values", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Polling time (s)", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Form", "Export as ascii", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Form", "Export as image", None, QtGui.QApplication.UnicodeUTF8))

