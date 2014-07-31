from PyQt4 import QtGui, QtCore
import sys
import signal
import logging
import time
import datetime
import math

from Revolver.gui_default_widget import DefaultWidget, DefaultMainWindow
from Revolver.gui_default_widget import DefaultWidget
from Revolver.classes import config, signals, devices
from Revolver.macro.UI import layout_sardana_motro_macro

class SardanaMotorMacro(QtGui.QDialog, layout_sardana_motro_macro.Ui_Dialog):
    
    def __init__(self, parent=None):
        super(SardanaMotorMacro, self).__init__(parent=parent)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        pass
    
    def __init_signals(self):
        pass
        
    def __main(self):
        pass
        
# MAIN PROGRAM #################################################################################
if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    widget = SardanaMotorMacro()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()    