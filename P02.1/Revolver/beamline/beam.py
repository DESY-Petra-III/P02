'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''
from PyQt4.QtGui import QApplication
import signal
import sys

# import global classes 
import default_beamline_device as default_device
from UI import beam
from Revolver.classes import signals

class Beamline_beam(beam.Ui_Form, default_device.Beamline_device):
    
    def __init__(self, parent=None):
        super(Beamline_beam, self).__init__(parent)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        pass
    
    def __init_signals(self):
        pass
    
    def __main(self):
        pass
    
    def action_device(self, state):
        self.emit(signals.SIG_SHOW_BEAMLINE_DEVICE_CONTROLS, self.controlIndex)
    
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QApplication(sys.argv)
    
    # init widget
    widget = Beamline_beam()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
    
