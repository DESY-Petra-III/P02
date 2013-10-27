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
from Revolver.classes import devices, config, signals
from UI import layout_stacked_motors_controls
from Revolver import gui_default_widget
import gui_default_controls_widget as default_gui
import gui_motor_controls_widget

class StackedMotorControls(layout_stacked_motors_controls.Ui_Form, default_gui.DefaultControls):
    
    def __init__(self, parent=None, motors=None, title=None):
        super(StackedMotorControls, self).__init__()
        default_gui.DefaultControls.__init__(self, parent=parent)
        self.motors = motors
        self.title = title
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        self.setup = {}
    
    def __init_signals(self):
        pass
        
    def __main(self):
        if self.title:
            self.group.setTitle(self.title) 
        if self.motors:
            for motor in self.motors:
                if isinstance(motor, str):
                    motor_controls = gui_motor_controls_widget.MotorWidget(devicePath=motor)
                    self.setup[motor] = motor_controls
                else:
                    motor_controls = gui_motor_controls_widget.MotorWidget(device=motor)
                    self.setup[motor.devicePath] = motor_controls
                self.insert_widget(motor_controls, self.stage_motors_layout)
    
    def set_controls_title(self, title):
        self.group.setTitle(title)
        
    def set_motor_controls_enabled(self, motorPath, flag=True):
        try:
            self.setup[motorPath].setEnabled(flag)
        except:
            self.emit(signals.SIG_SHOW_ERROR,"Controller error", "Controller does not exists")
    
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    left = devices.Motor(config.DEVICE_SERVER + "p02/motor/exp.04")
    right = devices.Motor(config.DEVICE_SERVER + "p02/motor/exp.05")
    virtualMotor1 = devices.VirtualMotorDistance2D([left, right], "Dx")
    virtualMotor2 = devices.VirtualMotorCenter2D([left, right], "Cx")
    
    widget = StackedMotorControls(motors=[virtualMotor1, virtualMotor2, left, right])
    widget2 = StackedMotorControls(motors=[virtualMotor1, virtualMotor2, left, right])
    
    widget3 = gui_default_widget.DefaultWidget()
    widget3.setLayout(QtGui.QGridLayout())
    widget3.layout().addWidget(widget)
    widget3.layout().addWidget(widget2)
    
    win = gui_default_widget.DefaultMainWindow()
    win.setCentralWidget(widget3)
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    win.show()
    
    # execute application
    app.exec_()
