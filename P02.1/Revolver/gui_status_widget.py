# import global classes 
from PyQt4 import QtGui, QtCore
import threading
import sys
import time
import signal
 
# Import local classes
from  gui_default_widget import DefaultWidget
from Revolver.classes import devices, threads, signals
from UI import layout_status

class StatusWidget(layout_status.Ui_Form, DefaultWidget):
    
    WARNING_STYLE = "QLabel { background-color : orange; color:#fff; font-weight:bold }"
    ERROR_STYLE = "QLabel { background-color : red; color:#fff; font-weight:bold }"
    DEFAULT_STYLE = "QLabel { background-color : green; color:#fff; font-weight:bold }"
    REFRESH_TIME = 1
    
    def __init__(self, parent=None):
        """
        Class constructor
        """
        super(StatusWidget, self).__init__()
        self.__initVariables()
        self.__initSignals()
        self.__main()
        
    def __initVariables(self):
        self.STOP = False
        self.signalButtons = [self.label_5, self.label_6,
                              self.label_7, self.label_8]
        
        try:
            self.globalKeywords = devices.TangoDevice("haspp02oh1:10000/petra/globals/keyword")
            self.ionchamber = devices.TangoDevice('haspp02oh1:10000/p02/adc/eh1b.01')
            self.diode = devices.Diode("haspp02oh1:10000/p02/adc/eh1b.01")
            self.absorber = devices.Absorber("haspp02oh1:10000/p02/festocompairdistributor/eh1a.01")
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Monitor error", "Monitor could not be initialized")
    
    def __initSignals(self):
        for button in self.signalButtons:  
            QtCore.QObject.connect(button, QtCore.SIGNAL("set_style"), self.action_set_ui_style)
        
    def __main(self):
        pass
    
    def showEvent(self, *args, **kwargs):
        """
        Refresh status whne widget is visible
        """
        self.STOP = False
        self.thread = threading.Thread(target=self.__check_routine)
        threads.add_thread(self.thread, self.widget_id)
        self.thread.start()
        self.diode.start_profiling()
        return DefaultWidget.showEvent(self, *args, **kwargs)
    
    def hideEvent(self, *args, **kwargs):
        """
        Stop refreshing status whne widget was hidden
        """
        self.STOP = True
        self.diode.stop_profiling()
        return DefaultWidget.hideEvent(self, *args, **kwargs)
    
    def action_set_ui_style(self, obj, style):
        """
        Signal handler:
        set css style on Qobject
        """
        obj.setStyleSheet(style)
    
    def get_treshold_color(self, currentValue, warningTreshold, errorThreshold):
        if (currentValue is None) or (currentValue <= errorThreshold) : return self.ERROR_STYLE
        elif currentValue <= warningTreshold : return self.WARNING_STYLE
        else: return self.DEFAULT_STYLE
        
    def __check_routine(self):
        beamCurrentValue = None
        ionchamberValue = None
        diodeValue = None
        absorberValue = None
        
        while not(self.STOP) and threads.THREAD_KEEP_ALIVE:
            
            try:
                beamCurrentValue = float(self.globalKeywords.device.read_attribute("BeamCurrent").value)
                beamCurrentValue = round(beamCurrentValue, 3)
                self.label_5.setText(str(beamCurrentValue))
            except:    
                self.label_5.setText("ERROR")
                
            try:
                ionchamberValue = self.ionchamber.device.read_attribute("value").value
                ionchamberValue = round(ionchamberValue, 3)
                self.label_6.setText(str(ionchamberValue))
            except:    
                self.label_6.setText("ERROR")
            
            try:
                diodeValue = self.diode.output["current"][0]
                self.label_7.setText(str(diodeValue))
            except:
                self.label_7.setText("ERROR")
            
            try:     
                absorberValue = self.absorber.get_value()
                self.label_8.setText(str(absorberValue))
            except:
                self.label_8.setText("ERROR")
            
            
            self.label_5.emit(QtCore.SIGNAL("set_style"),
                                   self.label_5, self.get_treshold_color(beamCurrentValue, 50, 10))
            
            self.label_6.emit(QtCore.SIGNAL("set_style"),
                                   self.label_6, self.get_treshold_color(ionchamberValue, 0.8, 0.7))
            
            self.label_6.emit(QtCore.SIGNAL("set_style"),
                                   self.label_7, self.get_treshold_color(diodeValue, -1, -1))
            
            self.label_8.emit(QtCore.SIGNAL("set_style"),
                                   self.label_8, self.get_treshold_color(diodeValue, -1, -1))
            
            time.sleep(self.REFRESH_TIME)
    
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    widget = StatusWidget()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()    

