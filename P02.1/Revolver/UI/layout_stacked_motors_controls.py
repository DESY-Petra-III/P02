# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmp0qbqbY.ui'
#
# Created: Thu Oct 24 17:33:56 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(703, 55)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout.setObjectName("gridLayout")
        self.group = QtGui.QGroupBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.group.sizePolicy().hasHeightForWidth())
        self.group.setSizePolicy(sizePolicy)
        self.group.setStyleSheet("QGroupBox {\n"
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
        self.group.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.group.setFlat(False)
        self.group.setObjectName("group")
        self.gridLayout_2 = QtGui.QGridLayout(self.group)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.stage_motors_layout = QtGui.QGridLayout()
        self.stage_motors_layout.setObjectName("stage_motors_layout")
        self.gridLayout_2.addLayout(self.stage_motors_layout, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.group, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Stage controls", None, QtGui.QApplication.UnicodeUTF8))
        self.group.setTitle(QtGui.QApplication.translate("Form", "Stacked motors", None, QtGui.QApplication.UnicodeUTF8))

