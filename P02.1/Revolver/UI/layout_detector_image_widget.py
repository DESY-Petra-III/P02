# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpBRw38l.ui'
#
# Created: Fri Sep 27 13:37:58 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(809, 661)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.central = QtGui.QGridLayout()
        self.central.setObjectName("central")
        self.gridLayout.addLayout(self.central, 0, 0, 1, 1)
        self.taurusImageDialog = TaurusImageDialog(Form)
        self.taurusImageDialog.setObjectName("taurusImageDialog")
        self.gridLayout.addWidget(self.taurusImageDialog, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.extra_guiqwt import TaurusImageDialog
