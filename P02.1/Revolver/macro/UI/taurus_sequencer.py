# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpoobplo.ui'
#
# Created: Mon Jun 16 09:02:27 2014
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(472, 583)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.taurusSequencerWidget = TaurusSequencerWidget(Form)
        self.taurusSequencerWidget.setObjectName("taurusSequencerWidget")
        self.gridLayout.addWidget(self.taurusSequencerWidget, 0, 1, 1, 1)
        self.graph_layout = QtGui.QGridLayout()
        self.graph_layout.setObjectName("graph_layout")
        self.gridLayout.addLayout(self.graph_layout, 0, 2, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.extra_macroexecutor import TaurusSequencerWidget
