# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmpQ29y18.ui'
#
# Created: Wed Oct 16 11:30:57 2013
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 278)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.button_select_motor = QtGui.QPushButton(Dialog)
        self.button_select_motor.setObjectName("button_select_motor")
        self.horizontalLayout.addWidget(self.button_select_motor)
        self.button_close = QtGui.QPushButton(Dialog)
        self.button_close.setObjectName("button_close")
        self.horizontalLayout.addWidget(self.button_close)
        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.taurusDevTree = TaurusDevTree(Dialog)
        self.taurusDevTree.setDragEnabled(False)
        self.taurusDevTree.setUniformRowHeights(False)
        self.taurusDevTree.setHeaderHidden(True)
        self.taurusDevTree.setObjectName("taurusDevTree")
        self.taurusDevTree.headerItem().setText(0, "1")
        self.taurusDevTree.header().setVisible(False)
        self.gridLayout_2.addWidget(self.taurusDevTree, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.button_close, QtCore.SIGNAL("clicked()"), Dialog.close)
        QtCore.QObject.connect(self.button_select_motor, QtCore.SIGNAL("clicked()"), Dialog.action_select_motor)
        QtCore.QObject.connect(self.taurusDevTree, QtCore.SIGNAL("doubleClicked(QModelIndex)"), Dialog.action_select_motor)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Select device", None, QtGui.QApplication.UnicodeUTF8))
        self.button_select_motor.setText(QtGui.QApplication.translate("Dialog", "Select device", None, QtGui.QApplication.UnicodeUTF8))
        self.button_close.setText(QtGui.QApplication.translate("Dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

from taurus.qt.qtgui.tree import TaurusDevTree
