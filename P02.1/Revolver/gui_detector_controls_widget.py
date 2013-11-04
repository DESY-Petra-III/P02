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
from Revolver.classes import devices, config, signals, threads
from UI import layout_detector_controls
import gui_default_controls_widget as default_gui
import gui_stacked_motors_controls_widget
import gui_device_status_led_widget as led_widget
import threading

class DetectorControls(layout_detector_controls.Ui_Form, default_gui.DefaultControls):
    
    def __init__(self, detectorDevice, motorPaths=[], parent=None):
        super(DetectorControls, self).__init__()
        default_gui.DefaultControls.__init__(self, parent=parent)
        self.detector = detectorDevice
        self.motorPaths = motorPaths
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        self.detector_motors_controls = gui_stacked_motors_controls_widget.StackedMotorControls(motors=self.motorPaths, title="Detecor motors")
        self.detectorStatus = led_widget.DeviceLedStatusWidget(self.detector)
    
    def __init_signals(self):
        self.connect(self.detectorStatus, signals.SIG_DEVICE_STATUS_CHANGED, self.action_enable_controls)
        
    def __main(self):
        self.detector_motors_controls.set_margin_to_zero()
        self.insert_widget(self.detector_motors_controls, self.detector_motor_layout)
        self.detector_input_values.layout().addWidget(self.detectorStatus, 0, 1)
    
    def action_enable_controls(self, flag=True):
        self.button_take_dark.setEnabled(flag)
        self.button_take_shot.setEnabled(flag)
        self.button_stop_acquisition.setEnabled(not(flag))
        self.detector_input_values.setEnabled(flag)
    
    def action_stop_acquisition(self):
        try:
            self.detector.halt()
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Detector controls", "Detector could not be halted")
        
    def action_take_shot(self):
        summed = int(self.summed.value())
        postTrigger = int(self.post_trigger.value())
        comment = str(self.comment.text())
        
        try:
            sampleName = self.validate_input("Sample name", "string", self.sample_name.text())
        except:
            return
                
        try:
            #self.detector.take_shot(devices.Shutter(config.DEVICE_SHUTTER), summed, postTrigger, sampleName, comment)
            thread = threading.Thread(target=self.detector.take_shot, args=([devices.Shutter(config.DEVICE_SHUTTER), summed, postTrigger, sampleName, comment]))
            threads.add_thread(thread, self.widget_id)
            thread.setDaemon(True)
            thread.start()
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Detector shot", "Shot could not be taken")
    
    def action_take_dark_shot(self):
        summed = int(self.summed.value())
        
        try:
            # self.detector.take_dark(devices.Shutter(config.DEVICE_SHUTTER), summed)
            thread = threading.Thread(target=self.detector.take_dark, args=([devices.Shutter(config.DEVICE_SHUTTER), summed]))
            threads.add_thread(thread, self.widget_id)
            thread.setDaemon(True)
            thread.start()
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Detector dark shot", "Dark shot could not be taken")
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    widget = DetectorControls()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
