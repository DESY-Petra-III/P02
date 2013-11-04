# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpxQKMgg.ui'
#
# Created: Fri Oct 25 14:21:13 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(842, 172)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.stage = QtGui.QToolBox(Form)
        self.stage.setCursor(QtCore.Qt.ArrowCursor)
        self.stage.setStyleSheet("QToolBox::tab {\n"
"   background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,\n"
"                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);\n"
"  color: darkgray;\n"
"  font-weight:bold;\n"
"  border-bottom:1px solid #fff;\n"
"}\n"
" \n"
"QToolBox::tab:selected {\n"
"    color: black;\n"
"    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                stop: 0 #feccb1, stop: 0.4 #f17432,\n"
"                                stop: 0.5 #ea5507, stop: 1.0 #fb955e);\n"
"}")
        self.stage.setFrameShadow(QtGui.QFrame.Sunken)
        self.stage.setMidLineWidth(0)
        self.stage.setObjectName("stage")
        self.stage_1 = QtGui.QWidget()
        self.stage_1.setGeometry(QtCore.QRect(0, 0, 842, 79))
        self.stage_1.setObjectName("stage_1")
        self.formLayout = QtGui.QFormLayout(self.stage_1)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.stage.addItem(self.stage_1, "")
        self.stage_2 = QtGui.QWidget()
        self.stage_2.setGeometry(QtCore.QRect(0, 0, 842, 79))
        self.stage_2.setObjectName("stage_2")
        self.formLayout_2 = QtGui.QFormLayout(self.stage_2)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName("formLayout_2")
        self.stage.addItem(self.stage_2, "")
        self.stage_3 = QtGui.QWidget()
        self.stage_3.setGeometry(QtCore.QRect(0, 0, 842, 79))
        self.stage_3.setObjectName("stage_3")
        self.formLayout_3 = QtGui.QFormLayout(self.stage_3)
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_3.setObjectName("formLayout_3")
        self.stage.addItem(self.stage_3, "")
        self.gridLayout.addWidget(self.stage, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(Form)
        self.stage.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.stage.setItemText(self.stage.indexOf(self.stage_1), QtGui.QApplication.translate("Form", " # HR GONIO", None, QtGui.QApplication.UnicodeUTF8))
        self.stage.setItemText(self.stage.indexOf(self.stage_2), QtGui.QApplication.translate("Form", " # HAB and CRYO", None, QtGui.QApplication.UnicodeUTF8))
        self.stage.setItemText(self.stage.indexOf(self.stage_3), QtGui.QApplication.translate("Form", " # MISC", None, QtGui.QApplication.UnicodeUTF8))

