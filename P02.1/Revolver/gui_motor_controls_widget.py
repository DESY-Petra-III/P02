"""
Motor widget.
Populate motor position to user, which can be changed.
User can also stop all movements of selected motor.
Motor status is signalized by diode.
"""

# import global classes 
from PyQt4 import QtGui, Qt
import sys
import signal
 
# Import local classes
from UI import layout_motor_widget
import gui_default_controls_widget as default_gui
import gui_device_status_led_widget as led_widget
from Revolver.classes import devices, config, signals

class MotorWidget(layout_motor_widget.Ui_Form, default_gui.DefaultControls):
    """
    Basic control widget for motor device
    """
    
    def __init__(self, parent=None, devicePath=None, device=None):
        super(MotorWidget, self).__init__()
        default_gui.DefaultControls.__init__(self, parent=parent, devicePath=devicePath)
        
        if device:
            self.defaultMotorDevice = device
        else:
            if not devicePath: self.defaultMotorDevice = devices.Motor(config.DEVICE_MOTOR)
            else: self.defaultMotorDevice = devices.Motor(devicePath)
        
        self.action_change_motor(device)
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        self.ledStatus = led_widget.DeviceLedStatusWidget(self.defaultMotorDevice)
        
    def __init_signals(self):
        self.connect(self, Qt.SIGNAL("changeMotor(String)"), self.action_change_motor)
        self.connect(self.motor_position, Qt.SIGNAL("valueChanged()"), self.action_read_motor_position)
        self.connect(self.ledStatus, signals.SIG_DEVICE_STATUS_CHANGED, self.action_enable_controls)
        
    def __main(self):
        self.layout.insertWidget(0, self.ledStatus)
        self.spinboxFilter = default_gui.EventSpinboxFilter()
        self.motor_position.installEventFilter(self.spinboxFilter)
        
    def action_change_motor_position_plus_double(self):
        """
        Change position by clicking the right double arrow button
        Position = Position + StepSize * 10
        """
        step = float(self.step_size.value())
        position = self.motor_position.value()
        newPosition = position + step * 10
        self.action_set_motor_position(newPosition)
    
    def action_change_motor_position_plus(self):
        """
        Change position by clicking the right arrow button
        Position = Position + StepSize
        """
        step = float(self.step_size.value())
        position = self.motor_position.value()
        newPosition = position + step
        self.action_set_motor_position(newPosition)
        
    def action_change_motor_position_minus_double(self):
        """
        Change position by clicking the left double arrow button
        Position = Position - StepSize * 10
        """
        step = float(self.step_size.value())
        position = self.motor_position.value()
        newPosition = position - step * 10
        self.action_set_motor_position(newPosition)
        
    def action_change_motor_position_minus(self):
        """
        Change position by clicking the left arrow button
        Position = Position - StepSize
        """
        step = float(self.step_size.value())
        position = self.motor_position.value()
        newPosition = position - step
        self.action_set_motor_position(newPosition)
    
    def action_change_motor(self, motor):
        """
        Change actual motor
        """
        self.check_device_allowed_values([self.motor_position], self.defaultMotorDevice)
        actualPosition = float(self.defaultMotorDevice.execute_command("GetPosition"))
        self.motor_position.setValue(actualPosition)
    
    def action_enable_controls(self, flag=True):
        """
        Enable / disable controls
        """
        self.button_stop_all_moves.setEnabled(not(flag))
        self.motor_controls.setEnabled(flag)
        if flag:
            self.read_motor_position_and_set()
        
    def action_change_step(self, step):
        """
        Change current stepSize
        """
        self.motor_position.setSingleStep(step)
    
    def action_read_motor_position(self):
        """
        Read current motor position from spinbox and change motor position
        """
        position = self.motor_position.value()
        self.action_set_motor_position(position)
    
    def read_motor_position_and_set(self):
        """
        Get motor position and set the spinbox value
        """
        actualPosition = float(self.defaultMotorDevice.execute_command("GetPosition"))
        self.motor_position.setValue(actualPosition)
    
    def action_stop_motor(self):
        """
        Stop motor movement
        """
        self.defaultMotorDevice.halt()
        
    def action_set_motor_position(self, position):
        """
        Set motor position, check limitis before
        """
        try:
            self.validate_device_minmax_value(position, self.defaultMotorDevice)
            self.defaultMotorDevice.move(position, async=True)
            self.motor_position.setValue(position)
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Motor position", "Motor limits was exceeded")
            self.read_motor_position_and_set()
            return       
        
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    widget = MotorWidget()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
