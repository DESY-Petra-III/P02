# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/tmp/tmp6dFcC6.ui'
#
# Created: Tue Jan 28 19:30:49 2014
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(561, 339)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.expert_mode_panel = QtGui.QWidget(Dialog)
        self.expert_mode_panel.setStyleSheet("#expert_mode_panel {\n"
"    background:#d9d9d9;\n"
"    border-bottom: 3px solid #cfcfcf;\n"
"}")
        self.expert_mode_panel.setObjectName("expert_mode_panel")
        self.gridLayout_9 = QtGui.QGridLayout(self.expert_mode_panel)
        self.gridLayout_9.setMargin(5)
        self.gridLayout_9.setHorizontalSpacing(0)
        self.gridLayout_9.setVerticalSpacing(5)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.button_expert_mode = QtGui.QPushButton(self.expert_mode_panel)
        self.button_expert_mode.setCursor(QtCore.Qt.PointingHandCursor)
        self.button_expert_mode.setFocusPolicy(QtCore.Qt.NoFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/icons/expert_mode.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_expert_mode.setIcon(icon)
        self.button_expert_mode.setCheckable(True)
        self.button_expert_mode.setChecked(False)
        self.button_expert_mode.setObjectName("button_expert_mode")
        self.gridLayout_9.addWidget(self.button_expert_mode, 0, 2, 1, 1)
        self.label_3 = QtGui.QLabel(self.expert_mode_panel)
        self.label_3.setObjectName("label_3")
        self.gridLayout_9.addWidget(self.label_3, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.expert_mode_panel, 0, 0, 1, 1)
        self.stackedWidget = QtGui.QStackedWidget(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setMinimumSize(QtCore.QSize(0, 60))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtGui.QWidget()
        self.page.setObjectName("page")
        self.gridLayout_2 = QtGui.QGridLayout(self.page)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtGui.QGroupBox(self.page)
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
        self.option_dark_timeout = QtGui.QSpinBox(self.groupBox)
        self.option_dark_timeout.setMinimum(0)
        self.option_dark_timeout.setMaximum(999999)
        self.option_dark_timeout.setObjectName("option_dark_timeout")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.option_dark_timeout)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 2)
        self.expert_settings = QtGui.QGroupBox(self.page)
        self.expert_settings.setEnabled(False)
        self.expert_settings.setStyleSheet("QGroupBox {\n"
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
        self.expert_settings.setObjectName("expert_settings")
        self.formLayout_2 = QtGui.QFormLayout(self.expert_settings)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName("formLayout_2")
        self.hotblower_label = QtGui.QLabel(self.expert_settings)
        self.hotblower_label.setObjectName("hotblower_label")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.hotblower_label)
        self.hotblower_settings = QtGui.QWidget(self.expert_settings)
        self.hotblower_settings.setObjectName("hotblower_settings")
        self.layout_5 = QtGui.QHBoxLayout(self.hotblower_settings)
        self.layout_5.setMargin(0)
        self.layout_5.setObjectName("layout_5")
        self.label_15 = QtGui.QLabel(self.hotblower_settings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy)
        self.label_15.setObjectName("label_15")
        self.layout_5.addWidget(self.label_15)
        self.hotblower_min = QtGui.QDoubleSpinBox(self.hotblower_settings)
        self.hotblower_min.setMinimum(-999999.0)
        self.hotblower_min.setMaximum(999999.0)
        self.hotblower_min.setObjectName("hotblower_min")
        self.layout_5.addWidget(self.hotblower_min)
        self.label_16 = QtGui.QLabel(self.hotblower_settings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)
        self.label_16.setObjectName("label_16")
        self.layout_5.addWidget(self.label_16)
        self.hotblower_max = QtGui.QDoubleSpinBox(self.hotblower_settings)
        self.hotblower_max.setMinimum(-999999.0)
        self.hotblower_max.setMaximum(999999.0)
        self.hotblower_max.setObjectName("hotblower_max")
        self.layout_5.addWidget(self.hotblower_max)
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.hotblower_settings)
        self.cryostreamer_label = QtGui.QLabel(self.expert_settings)
        self.cryostreamer_label.setObjectName("cryostreamer_label")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.cryostreamer_label)
        self.cryostreamer_settings = QtGui.QWidget(self.expert_settings)
        self.cryostreamer_settings.setObjectName("cryostreamer_settings")
        self.layout_2 = QtGui.QHBoxLayout(self.cryostreamer_settings)
        self.layout_2.setMargin(0)
        self.layout_2.setObjectName("layout_2")
        self.label_9 = QtGui.QLabel(self.cryostreamer_settings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setObjectName("label_9")
        self.layout_2.addWidget(self.label_9)
        self.cryostreamer_min = QtGui.QDoubleSpinBox(self.cryostreamer_settings)
        self.cryostreamer_min.setMinimum(-999999.0)
        self.cryostreamer_min.setMaximum(999999.0)
        self.cryostreamer_min.setObjectName("cryostreamer_min")
        self.layout_2.addWidget(self.cryostreamer_min)
        self.label_10 = QtGui.QLabel(self.cryostreamer_settings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setObjectName("label_10")
        self.layout_2.addWidget(self.label_10)
        self.cryostreamer_max = QtGui.QDoubleSpinBox(self.cryostreamer_settings)
        self.cryostreamer_max.setMinimum(-999999.0)
        self.cryostreamer_max.setMaximum(999999.0)
        self.cryostreamer_max.setObjectName("cryostreamer_max")
        self.layout_2.addWidget(self.cryostreamer_max)
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.cryostreamer_settings)
        self.label_2 = QtGui.QLabel(self.expert_settings)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_2)
        self.cryostreamer_settings_2 = QtGui.QWidget(self.expert_settings)
        self.cryostreamer_settings_2.setObjectName("cryostreamer_settings_2")
        self.layout_4 = QtGui.QHBoxLayout(self.cryostreamer_settings_2)
        self.layout_4.setMargin(0)
        self.layout_4.setObjectName("layout_4")
        self.label_13 = QtGui.QLabel(self.cryostreamer_settings_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy)
        self.label_13.setObjectName("label_13")
        self.layout_4.addWidget(self.label_13)
        self.stabilization_time_min = QtGui.QDoubleSpinBox(self.cryostreamer_settings_2)
        self.stabilization_time_min.setMinimum(0.0)
        self.stabilization_time_min.setMaximum(999999.0)
        self.stabilization_time_min.setObjectName("stabilization_time_min")
        self.layout_4.addWidget(self.stabilization_time_min)
        self.label_14 = QtGui.QLabel(self.cryostreamer_settings_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setObjectName("label_14")
        self.layout_4.addWidget(self.label_14)
        self.stabilization_time_max = QtGui.QDoubleSpinBox(self.cryostreamer_settings_2)
        self.stabilization_time_max.setMinimum(0.0)
        self.stabilization_time_max.setMaximum(999999.0)
        self.stabilization_time_max.setObjectName("stabilization_time_max")
        self.layout_4.addWidget(self.stabilization_time_max)
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.cryostreamer_settings_2)
        self.label_7 = QtGui.QLabel(self.expert_settings)
        self.label_7.setObjectName("label_7")
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_7)
        self.ramping_threshold = QtGui.QDoubleSpinBox(self.expert_settings)
        self.ramping_threshold.setMinimum(0.0)
        self.ramping_threshold.setMaximum(999999.0)
        self.ramping_threshold.setObjectName("ramping_threshold")
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.ramping_threshold)
        self.label_6 = QtGui.QLabel(self.expert_settings)
        self.label_6.setObjectName("label_6")
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_6)
        self.ramping_time_max = QtGui.QDoubleSpinBox(self.expert_settings)
        self.ramping_time_max.setMinimum(0.0)
        self.ramping_time_max.setMaximum(999999.0)
        self.ramping_time_max.setObjectName("ramping_time_max")
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.FieldRole, self.ramping_time_max)
        self.gridLayout_2.addWidget(self.expert_settings, 1, 0, 1, 2)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName("page_2")
        self.stackedWidget.addWidget(self.page_2)
        self.gridLayout.addWidget(self.stackedWidget, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(0, 9, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.macro_button_reset = QtGui.QPushButton(Dialog)
        self.macro_button_reset.setFocusPolicy(QtCore.Qt.NoFocus)
        self.macro_button_reset.setObjectName("macro_button_reset")
        self.horizontalLayout.addWidget(self.macro_button_reset)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.macro_button_close = QtGui.QPushButton(Dialog)
        self.macro_button_close.setFocusPolicy(QtCore.Qt.NoFocus)
        self.macro_button_close.setObjectName("macro_button_close")
        self.horizontalLayout.addWidget(self.macro_button_close)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.macro_button_close, QtCore.SIGNAL("clicked()"), Dialog.close)
        QtCore.QObject.connect(self.button_expert_mode, QtCore.SIGNAL("clicked(bool)"), Dialog.action_set_expert_mode)
        QtCore.QObject.connect(self.option_dark_timeout, QtCore.SIGNAL("valueChanged(int)"), Dialog.action_set_dark_timeout)
        QtCore.QObject.connect(self.cryostreamer_min, QtCore.SIGNAL("valueChanged(double)"), Dialog.action_set_cryostreamer_min)
        QtCore.QObject.connect(self.cryostreamer_max, QtCore.SIGNAL("valueChanged(double)"), Dialog.action_set_cryostreamer_max)
        QtCore.QObject.connect(self.macro_button_reset, QtCore.SIGNAL("clicked()"), Dialog.action_reset_settings)
        QtCore.QObject.connect(self.ramping_threshold, QtCore.SIGNAL("valueChanged(double)"), Dialog.action_set_ramping_threshold)
        QtCore.QObject.connect(self.stabilization_time_min, QtCore.SIGNAL("valueChanged(double)"), Dialog.action_set_tabilization_min)
        QtCore.QObject.connect(self.stabilization_time_max, QtCore.SIGNAL("valueChanged(double)"), Dialog.action_set_stabilization_max)
        QtCore.QObject.connect(self.ramping_time_max, QtCore.SIGNAL("valueChanged(double)"), Dialog.action_set_ramping_max)
        QtCore.QObject.connect(self.hotblower_min, QtCore.SIGNAL("valueChanged(double)"), Dialog.action_set_hotblower_min)
        QtCore.QObject.connect(self.hotblower_max, QtCore.SIGNAL("valueChanged(double)"), Dialog.action_set_hotblower_max)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Expert mode", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "User settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Take dark timeout (sec.):", None, QtGui.QApplication.UnicodeUTF8))
        self.expert_settings.setTitle(QtGui.QApplication.translate("Dialog", "Expert settings", None, QtGui.QApplication.UnicodeUTF8))
        self.hotblower_label.setText(QtGui.QApplication.translate("Dialog", "Hotblower temperature:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("Dialog", "Min", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setText(QtGui.QApplication.translate("Dialog", "Max", None, QtGui.QApplication.UnicodeUTF8))
        self.cryostreamer_label.setText(QtGui.QApplication.translate("Dialog", "Cryostreamer temperature:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Dialog", "Min", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Dialog", "Max", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Stabilization time (sec):", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("Dialog", "Min", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("Dialog", "Max", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog", "Ramping temperature error threshold:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Maximum ramping time  (sec):", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_button_reset.setText(QtGui.QApplication.translate("Dialog", "Reset settings", None, QtGui.QApplication.UnicodeUTF8))
        self.macro_button_close.setText(QtGui.QApplication.translate("Dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

import macro_resources_rc