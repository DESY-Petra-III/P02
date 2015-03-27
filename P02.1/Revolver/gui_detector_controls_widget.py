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
import logging
 
# Import local classes
from Revolver.classes import devices, config, signals, threads
from UI import layout_detector_controls, layout_detector_controls_with_attributes
import gui_default_controls_widget as default_gui
import gui_stacked_motors_controls_widget
import gui_device_status_led_widget as led_widget
import threading
from taurus.qt.QtCore import Signal
from PyQt4.Qt import SIGNAL
import math
from classes.devices import Laser, Diode

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
        self.connect(self.detectorStatus, signals.SIG_DEVICE_STATUS_ERROR, self.action_enable_all_controls)
        self.connect(self.detectorStatus, signals.SIG_DEVICE_STATUS_OK, self.action_enable_controls)
        
    def __main(self):
        self.detector_motors_controls.set_margin_to_zero()
        self.insert_widget(self.detector_motors_controls, self.detector_motor_layout)
        self.detector_input_values.layout().addWidget(self.detectorStatus, 0, 1)
    
    def action_enable_controls(self, flag=True):
        if not self.detector.isDeviceError():
            self.button_take_dark.setEnabled(flag)
            self.button_take_shot.setEnabled(flag)
            self.button_stop_acquisition.setEnabled(not(flag))
            self.detector_input_values.setEnabled(flag)
    
    def action_enable_all_controls(self, flag=False):
        self.button_take_dark.setEnabled(flag)
        self.button_take_shot.setEnabled(flag)
        self.button_stop_acquisition.setEnabled(flag)
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
            self.set_diode_laser_out()
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
            self.set_diode_laser_out()
            thread = threading.Thread(target=self.detector.take_dark, args=([devices.Shutter(config.DEVICE_SHUTTER), summed]))
            threads.add_thread(thread, self.widget_id)
            thread.setDaemon(True)
            thread.start()
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Detector dark shot", "Dark shot could not be taken")
            
            
class DetectorControlsWithAttributes(layout_detector_controls_with_attributes.Ui_Form, DetectorControls):
    
    def __init__(self, detectorDevice, sddMotor, motorPaths=[], parent=None):
        motorPaths.append(sddMotor)
        DetectorControls.__init__(self, detectorDevice, motorPaths=motorPaths, parent=parent)
        self.sddMotor = sddMotor
        self.detector_motors_controls.setup[self.sddMotor.devicePath].setDisabled(True)
    
    def __init_variables(self):
        DetectorControls.__init_variables(self)
    
    def action_offset_changed(self, value):
        self.detector_motors_controls.setup[self.sddMotor.devicePath].read_motor_position_and_set()
        
    def set_attributes(self, r, lambdav, offset, psize, e):
        self.r_input.setValue(r)
        self.lambda_input.setValue(lambdav)
        self.offset_input.setValue(offset)
        self.pixelSize_input.setValue(psize)
        self.energy_input.setValue(e)
        self.count_attributes()
        
    def count_attributes(self):
        r = float(self.r_input.value())
        lambdav = float(self.lambda_input.value())
        offset = float(self.offset_input.value())
        pixelSize = float(self.pixelSize_input.value())
        e = float(self.energy_input.value())
        sdd = float(self.sddMotor.current_value("Position"))
        try:
            q = (4*math.pi/lambdav)*math.sin(0.5*math.atan(r*pixelSize/sdd))
            self.qmax_input.setValue(q)
        except:
            print "compute error"
        
    def count_energy(self, lambdav):
        if lambdav == 0: return
        self.energy_input.blockSignals(True)
        e = 12.3984/lambdav
        self.energy_input.setValue(e)
        self.energy_input.blockSignals(False)
        self.count_attributes()
        
    def count_lambda(self, energy):
        if energy == 0: return
        self.lambda_input.blockSignals(True)
        lambdav = 12.3984/energy
        self.lambda_input.setValue(lambdav)
        self.lambda_input.blockSignals(False)
        self.count_attributes()
        
    
# MAIN PROGRAM #################################################################################
from classes import devices, config
if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    P02_DEVICES = dict((x, config.DEVICE_SERVER_P02  + y) for x, y in config.DEVICE_NAMES.iteritems())
    detector = devices.Detector(P02_DEVICES["PE_DETECTOR"])
    SDD = devices.VirtualMotorSum2D([devices.Motor(P02_DEVICES["PEX_LARGE"]), devices.Motor(P02_DEVICES["PEX"])], "SDD")
    
    detectorMotors = [P02_DEVICES["PEX_LARGE"],
                   P02_DEVICES["PEX"],
                   P02_DEVICES["PEY"]]
    
    widget = DetectorControlsWithAttributes(detectorDevice=detector, sddMotor=SDD, motorPaths=detectorMotors, parent=app)
    SDD.addToPosition = lambda: float(widget.offset_input.value())
    widget.set_attributes(r=1024, lambdav=0.206, offset=1500, psize=0.2, e=60)
    
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
