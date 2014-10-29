# import global classes 
from PyQt4 import QtGui, Qt
import threading
import sys
import time
import signal
 
# Import local classes
from UI import layout_status_label
from gui_device_status_led_widget import DeviceLedStatusWidget
from Revolver.classes import config, devices, threads, signals

class DeviceValueStatusWidget(layout_status_label.Ui_Form, DeviceLedStatusWidget):
    
    POLLING_TIME = 0.25
    
    def __init__(self, device, params, parent=None):
        super(DeviceValueStatusWidget, self).__init__(device, parent)
        self.params = params
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        self.idleColor = "#00ff00"
        self.nonIdleColor = "#0000ff"
        self.nonEqualColor = "#ffa200"
        self.errorColor = "#ff0000"
        self.statusPollingTime = 1
        self.idle = True
        self.STOP_STATUS_CHECK = False
        self.sets = [self.set_1, self.set_2, self.set_3, self.set_4, self.set_5]
        self.labels = [self.label_s1, self.label_s2, self.label_s3, self.label_s4, self.label_s5]
        self.values = [self.value_s1, self.value_s2, self.value_s3, self.value_s4, self.value_s5]
        
    def __init_signals(self):
        self.connect(self, signals._SIG_SET_LED_COLOR, self.set_status_color)
        self.connect(self, signals.SIG_DEVICE_STATUS_ERROR, self.set_status_error)
        self.connect(self, signals.SIG_DEVICE_STATUS_OK, self.status_poll_routine_start)
        self.connect(self, Qt.SIGNAL("setStatusValue"), self.action_set_status_values)
        
    def __main(self):
        for index,param in enumerate(self.params):
            self.labels[index].setText(param["description"])
            self.sets[index].show()
        self.status_poll_routine_start()
            
    def set_status_color(self, color):
        colors = {"green":"#66FF33", "blue":"#33CCFF", "red":"#FF3366"}
        [i.setStyleSheet("background-color:" + colors[color]) for i in self.sets]
        
    def set_status_error(self):
        [i.setText("Error") for i in self.values]
        self.STOP_STATUS_CHECK = True
    
    def status_poll_routine_start(self):
        """
        Start polling routine
        """
        try:
            self.device.start_profiling()
        except:
            pass
        self.STOP_STATUS_CHECK = False
        thread = threading.Thread(target=self.__poll_status_check, args=())
        threads.add_thread(thread, self.widget_id)
        thread.start()
    
    def action_set_status_values(self,input,value):
        input.setText(value)
        
    def __poll_status_check(self):
        while threads.THREAD_KEEP_ALIVE and not self.STOP_STATUS_CHECK and not self.STOP:
            for index,param in enumerate(self.params):
                if param.has_key("value"):
                    try:
                        yValue = str("%.2f") % param['value'][0]
                    except TypeError:
                        yValue = str("%s") % param['value'][0]
                elif param.has_key("method"):
                    try:
                        yValue = getattr(param['device'], param['method'])()
                    except:
                        yValue = "ERROR"
                else:
                    yValue = self.device.read_attribute(param['deviceValue']).value
                self.emit(Qt.SIGNAL("setStatusValue"), self.values[index], str(yValue))
            time.sleep(self.statusPollingTime)
        
        
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    
    device = devices.TemperatureDevice(config.DEVICE_HOTBLOWER)
    params = [{"value":device.output["temperature"], "description":"Temperature:"},
              {"value":device.output["movingAverage"], "description":"Moving average:"},
              {"deviceValue":device.setpointValue, "description":"Setpoint:"},
              {"value":device.output["statusString"], "description":"Status:"},
              ]
    '''
    device = devices.Motor(config.DEVICE_MOTOR)
    params = [{"deviceValue":"Position", "description":"Setpoint:"}]
    '''
    widget = DeviceValueStatusWidget(device=device, params=params)
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
