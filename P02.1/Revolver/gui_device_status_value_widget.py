# import global classes 
from PyQt4 import QtGui, Qt
import threading
import sys
import time
import signal
 
# Import local classes
from UI import layout_status_label
from gui_default_widget import DefaultWidget
from Revolver.classes import config, devices, threads, signals

class DeviceValueStatusWidget(layout_status_label.Ui_Form, DefaultWidget):
    
    POLLING_TIME = 0.25
    
    def __init__(self, device, checkValue, parent=None):
        super(DeviceValueStatusWidget, self).__init__()
        self.device = device        
        self.idle = None
        self.checkValue = checkValue
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        self.idleColor = "#00ff00"
        self.nonIdleColor = "#0000ff"
        self.nonEqualColor = "#ffa200"
        self.errorColor = "#ff0000"
    
    def __init_signals(self):
        self.connect(self, Qt.SIGNAL("setValueColor"), lambda color: self.value.setStyleSheet("background-color:" + color))
        
    def __main(self):
        self.change_device(self.device)
        thread = threading.Thread(target=self.__poll_status, args=())
        threads.add_thread(thread, self.widget_id)
        thread.start()
        
    def __poll_status(self):
        while threads.THREAD_KEEP_ALIVE:
            try:
                idle = self.device.is_idle()
                self.value.setText(str(self.device.device.read_attribute(self.checkValue).value))
                if idle:
                    self.emit(signals._SIG_SET_LED_COLOR, self.idleColor)
                    self.emit(signals.SIG_DEVICE_IDLE, True)
                else: 
                    self.emit(signals._SIG_SET_LED_COLOR, self.nonIdleColor)
                    self.emit(signals.SIG_DEVICE_IDLE, False)
                self.status_changed_check(idle)
            except AttributeError:
                return
            except RuntimeError:
                return
            except:
                self.emit(signals._SIG_SET_LED_COLOR, self.errorColor)
                self.emit(signals.SIG_DEVICE_STATUS_ERROR)
            
            time.sleep(self.POLLING_TIME)
    
    def status_changed_check(self, newStatus):
        if self.idle == newStatus: return
        else:
            self.idle = newStatus
            self.emit(signals.SIG_DEVICE_STATUS_CHANGED, newStatus)
             
    
    def change_device(self, device):
        self.device = device
        self.device_name.setText(self.device.name)
    
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    motor = devices.Hotblower(config.DEVICE_HOTBLOWER)
    widget = DeviceValueStatusWidget(device=motor, checkValue="Temperature")
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
