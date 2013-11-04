# import global classes 
from PyQt4 import QtGui
import threading
import sys
import time
import signal
 
# Import local classes
from UI import layout_status_led
from gui_default_widget import DefaultWidget
from Revolver.classes import config, devices, threads, signals

class DeviceLedStatusWidget(layout_status_led.Ui_Form, DefaultWidget):
    
    # device status polling time
    POLLING_TIME = 0.1
    
    def __init__(self, device, parent=None):
        super(DeviceLedStatusWidget, self).__init__()
        self.device = device        
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        self.idle = True
        # state if device should be polled or no
        self.STOP = False
    
    def __init_signals(self):
        self.connect(self, signals._SIG_SET_LED_COLOR, lambda color: self.status_led.setLedColor(color))
        
    def __main(self):
        self.change_device(self.device)
    
    def __start_polling(self):
        """
        Start polling routine
        """
        self.STOP = False
        thread = threading.Thread(target=self.__poll_status, args=())
        threads.add_thread(thread, self.widget_id)
        thread.start()
        
    def __poll_status(self):
        """
        Polling routine
        """
        while threads.THREAD_KEEP_ALIVE and not self.STOP:
            try:
                idle = self.device.is_idle()
                if self.status_changed_check(idle):
                    if idle: 
                        self.emit(signals._SIG_SET_LED_COLOR, "green")
                        self.emit(signals.SIG_DEVICE_IDLE, True)
                    else: 
                        self.emit(signals._SIG_SET_LED_COLOR, "blue")
                        self.emit(signals.SIG_DEVICE_IDLE, False)
            except AttributeError:
                return
            except RuntimeError:
                return
            except:
                self.emit(signals._SIG_SET_LED_COLOR, "red")
                self.emit(signals.SIG_DEVICE_STATUS_ERROR)
            
            time.sleep(self.POLLING_TIME)
    
    def hideEvent(self, *args, **kwargs):
        """
        This event is called when widget was hide in the UI
        """
        self.STOP = True
        return DefaultWidget.hideEvent(self, *args, **kwargs)
    
    def showEvent(self, *args, **kwargs):
        """
        This event is called when widget was shown in the UI
        """
        self.__start_polling()
        self.emit(signals.SIG_DEVICE_STATUS_CHANGED, self.idle)
        return DefaultWidget.showEvent(self, *args, **kwargs)
        
    def status_changed_check(self, newStatus):
        """
        Check if device status changed
        """
        if self.idle == newStatus: return False
        else:
            self.idle = newStatus
            self.emit(signals.SIG_DEVICE_STATUS_CHANGED, newStatus)
            return True
               
    def change_device(self, device):
        """
        Change default device for this widget. 
        Set current name to device_name lable.
        """
        self.device = device
        self.device_name.setText(self.device.name)
    
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    motor = devices.Motor(config.DEVICE_MOTOR)
    widget = DeviceLedStatusWidget(device=motor)
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
