"""
Motor widget.
Populate motor position to user, which can be changed.
User can also stop all movements of selected motor.
Motor status is signalized by diode.
"""

# import global classes 
from PyQt4 import QtGui
import sys
import signal
 
# Import local classes
from Revolver.classes import devices, signals
from UI import layout_absorber_controls
import gui_default_controls_widget as default_gui

class Controls(layout_absorber_controls.Ui_Form, default_gui.DefaultControls):
    
    POLLING_TIME = 0.25
    
    def __init__(self, parent=None, devicePath=None):
        super(Controls, self).__init__()
        default_gui.DefaultControls.__init__(self, parent=parent, devicePath=devicePath)
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        self.absorber = devices.Absorber(self.device)
    
    def __init_signals(self):
        pass
        
    def __main(self):
        pass
    
    def action_before_shown(self):
        currentValue = self.absorber.get_value()
        self.absorber_value.setValue(currentValue)
    
    def reset_absorber_value(self):
        self.absorber_value.setValue(0)
        self.absorber.set_value(0)
        
    def set_absorber_value(self, value=None):
        self.absorber.set_value(value)
        
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    widget = Controls()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
