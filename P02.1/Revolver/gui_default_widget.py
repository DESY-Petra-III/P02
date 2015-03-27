"""
Default widget definition
All widget should be derived from DefaultWidget class
"""

# import global classes 
from PyQt4.QtGui import QMainWindow, QMessageBox, QApplication, QWidget
from PyQt4 import QtGui
from PyQt4.Qt import SIGNAL
import logging
import sys
import signal
from os import listdir
from os.path import isfile, join, splitext, basename, dirname
import re

# Import local classes
from Revolver.macro.UI import layout_settings
from Revolver.classes import devices, config, signals, threads, macro, dialogs
from string import replace

# Every widget derived from this widget will get internal identity number
GLOBAL_WIDGET_ID = 1

def enum(**enums):
    return type('Enum', (), enums)

class DefaultWidget(QWidget):
    """
    DefaultWidget class definition.
    It implements all basic methods for every widget.
    """
    EXPERT_SETTINGS_PIN = str(2501)
    
    def __init__(self, parent=False):
        """
        Class constructor
        @type parent: DefaultWidget
        """
        super(DefaultWidget, self).__init__()
        self.parent = parent
        self.setupUi(self)
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def setupUi(self, parent):
        """
        Metho to be override with GUI generated from Qt Designer
        """
        pass
    
    def __init_variables(self):
        """
        Initialize all variables
        defaulMotorDevice specified dafault motor which is used in some widgets
        widgets variable stored all widgets that are included in current widget
        """
        global GLOBAL_WIDGET_ID
        self.widget_id = GLOBAL_WIDGET_ID
        #self.defaultMotorDevice = devices.Motor(config.DEVICE_MOTOR)
        self.killall = True
        self.widgets = []
        GLOBAL_WIDGET_ID += 1
    
    def __init_signals(self):
        """
        Initialize all signals
        """
        self.connect(self, signals.SIG_SHOW_ERROR, self.action_show_error)
        self.connect(self, signals.SIG_SHOW_WARNING, self.action_show_warning)
        self.connect(self, signals.SIG_SET_PROGRESSBAR, self.action_set_progress)
        self.connect(self, signals.SIG_HALT_DEVICES, self.action_halt_all_devices)
        self.connect(self, signals.SIG_CHANGE_DEFAULT_MOTOR, self.action_change_default_motor)
        self.connect(self, signals.SIG_SHOW_ELEMENT, self.action_show_element)
        self.connect(self, signals.SIG_SHOW_INFO, self.action_show_info)
        self.connect(self, signals.SIG_DISABLE_CONTROLS, self.action_disable_controls)
        self.connect(self, signals.SIG_ENABLE_CONTROLS, self.action_enable_controls)
        self.connect(self, signals.SIG_SHOW_CONTROLS, self.action_show_controls)
        self.connect(self, signals.SIG_HIDE_CONTROLS, self.action_hide_controls)
    
    def __main(self):
        """
        Set widget properties
        """
        self.emit(SIGNAL("created()"))
        pass
    
    def hideEvent(self, *args, **kwargs):
        self.emit(signals.SIG_HIDDEN)
        return QWidget.hideEvent(self, *args, **kwargs)
    
    def showEvent(self, *args, **kwargs):
        self.emit(signals.SIG_SHOWN)
        return QWidget.showEvent(self, *args, **kwargs)
    
    def set_kill_all_permissions(self, permission):
        """
        Set killall permissions.
        If widget is about to close, dont stop other threads.
        """
        self.killall = permission
    
    def emit_handler(self, signal, *args, **kargs):
        """
        Default emit handler:
        @type signal: String
        """
        pass
    
    def action_show_element(self, element, show):
        """
        Signal handler:
        show element
        """
        element.setShown(show)
    
    def action_show_error(self, errorTitle, errorMessage, threadException=False):
        """
        Signal handler:
        show error message in dialog window
        @type errorTitle: String
        @type errorMessage: String
        @type threadException: bool
        """
        try:
            if threadException: errorMessage = str("%s\n%s" % (errorMessage, threadException))
            else: errorMessage = str("%s\n%s" % (errorMessage, self.get_exception()))
        except:
            pass
        logging.error(str("%s, %s" % (errorTitle, errorMessage)))
        QMessageBox.question(self, errorTitle, errorMessage, QMessageBox.Ok)
    
    def action_show_warning(self, warnTitle, warnMessage):
        """
        Signal handler:
        show warning message
        @type warnTitle: String
        @type warnMessage: String
        """
        logging.warn(str("%s, %s" % (warnTitle, warnMessage)))
        QMessageBox.question(self, warnTitle, warnMessage, QMessageBox.Ok)
    
    def action_show_info(self, title, message):
        """
        Signal handler:
        show warning message
        @type title: String
        @type message: String
        """
        QMessageBox.question(self, title, message, QMessageBox.Ok)
    
    def action_halt_all_devices(self):
        """
        Halt all running devices
        """
        devices.halt_all_running_devices()
    
    def action_halt_all_threads(self):
        """
        Halt all running threads
        """
        threads.stop_all_threads()
    
    def close_widget(self):
        """
        Close application
        """
        QApplication.quit()
        logging.info("Closing application")
        sys.exit()
     
    def closeEvent(self, event):
        """
        Override close application event
        @type event: QCloseEvent
        """
        if not self.killall:
            threads.stop_widget_threads(self.widget_id)
            event.accept()
            return
        
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.warning(self, 'Quit application',
                         quit_msg, QMessageBox.Yes, QMessageBox.No)
    
        if reply == QMessageBox.Yes:
            macro.STOP = True
            self.action_halt_all_devices()
            self.action_halt_all_threads()
            event.accept()
            macro.STOP = False
        else:
            event.ignore()
        
    def check_device_allowed_values(self, attr, device):
        """
        Signal handler:
        check minimum and maximum value for loop motor
        attr variable contain list of all Spinboxes, that should be limited by maximum and minimum
        motor position
        @type attr: list
        @type device: tangoDevice
        """
        for selector in attr:
            selector.setMaximum(device.maxValue)
            selector.setMinimum(device.minValue)
            selector.setValue(device.current_value())
    
    def get_exception(self):
        """
        Get exception from application environment
        """
        exception_info = sys.exc_info()
        if exception_info[0] is None: return "Unspecified exception"
        return str("Exception %s with message: %s" % (exception_info[0], exception_info[1]))
    
    def validate_input(self, name, inputType, value):
        """
        validate input from user and if not valid, show error message
        @type name: String
        @type inputType: String
        @type value: mixed 
        """
        try:
            if (value is None) or (value == ""): raise Exception("Input error")
            elif inputType == 'string': return str(value)
            elif inputType == 'int': return int(value)
            elif inputType == 'float': return float(value.replace(',', '.'))
        except:
            message = name + " value must be non empty " + inputType
            QMessageBox.question(self, 'Input error', message, QMessageBox.Ok)
            raise Exception(message)
    
    def validate_device_minmax_value(self, value, device=None):
        """
        Validate motor position against maximum and minimum values
        @type value: float
        @type device: tangoDevice
        """
        if device is None: device = self.defaultMotorDevice
        if device.minValue and ((value is None) or (value < device.minValue)):
            message = "Device value exceeded minimal alloved value " + str(device.minValue)
            QMessageBox.question(self, 'Input error', message, QMessageBox.Ok)
            raise Exception(message)
        elif device.maxValue and ((value is None) or (value > device.maxValue)):
            message = "Device value exceeded maximal alloved value " + str(device.maxValue)
            QMessageBox.question(self, 'Input error', message, QMessageBox.Ok)
            raise Exception(message)
    
    def action_set_progress(self, progressBar, value):
        """
        Signal handler:
        set value for progress bar. Value is defined in percentage.
        @type progressBar: QtGui.QProgressBar
        @type value: int
        """
        progressBar.setValue(value)
    
    def action_change_default_motor(self, motorPath):
        """
        Signal handler:
        set default motor model
        @type motorPath: String
        """
        try:
            self.defaultMotorDevice = devices.Motor(motorPath)
        except:
            pass
    
    def set_diode_laser_out(self):
        """
        Put laser and diode out
        """
        try:
            devices.Laser(config.DEVICE_SERVER+config.DEVICE_NAMES["LASER"]).put_out()
            devices.Diode(config.DEVICE_SERVER+config.DEVICE_NAMES["DIODE"]).put_out()
        except:
            self.emit(SIGNAL("showError"), "Diode and laser action", "Diode and laser could not be put out.")
    
    def insert_widget(self, widget, layout):
        """
        Insert widget into specified layout.
        @type widget: DefaultWidget
        @type layout: QtGui.QLayout  
        """
        self.register_widget(widget)
        layout.addWidget(widget)
        layout.update()
    
    def register_widget(self, widget):
        """
        Register widget into widgets
        @type widget: DefaultWidget
        """
        # if isinstance(widget, DefaultWidget):
        self.widgets.append(widget)
        # else:
        #    raise Exception("Widget is not of type DefaultWidget")
    
    def set_startup_logfile(self):
        """
        Set new logfile file, when file exists append .x (1,2,3,...) 
        and save new logfile
        """
        newLogNumber = 0
        currentFile =  splitext(config.DEFAULT_LOG_FILE)
        fileExtension = currentFile[1]
        
        filePath = dirname(config.DEFAULT_LOG_FILE)
        fileName = currentFile[0].replace(filePath+"/","").replace("\\","")
        
        regex = re.compile('^%s_(\d*)%s$'%(fileName,fileExtension))
        for f in listdir(filePath):
            fileName_actual = join(filePath,f)
            if isfile(fileName_actual):
                try:
                    logParsed = regex.findall(f)
                    logNumber = int(logParsed[0])
                    if logNumber > newLogNumber: 
                        newLogNumber = int(logNumber)
                        logPattern = str(logParsed[0])
                except:
                    pass
        newLogNumber += 1
        config.ACTUAL_LOG_FILE = filePath + "/%s_%05d%s" % (fileName, newLogNumber, fileExtension)
        return config.ACTUAL_LOG_FILE
    
    def action_disable_controls(self):
        """
        Disable controls
        """
        pass
    
    def action_enable_controls(self):
        """
        Enable controls
        """
        actualFile = config.DEFAULT_LOG_FILE
    
    def action_change_logfile(self):
        """
        Set logifle
        """
        actualFile = config.DEFAULT_LOG_FILE
        
        dialog = QtGui.QFileDialog()
        filename = str(dialog.getSaveFileName(self, "Logfile output", actualFile, "*.log"))
        if filename:
            logging.info("Logfile changed to: %s" % filename)
            config.DEFAULT_LOG_FILE = filename
            
    def action_show_controls(self):
        """
        Signal handler:
        Override this function to show widget controls
        """
        pass
    
    def action_hide_controls(self):
        """
        Signal handler:
        Override this function to hide widget controls
        """
        pass
    
    def action_add_settings_menu(self):
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.actionSettingsUser = QtGui.QAction(self)
        self.menuSettings.addAction(self.actionSettingsUser)
        self.menubar.addActions([self.menuFile.menuAction(), self.menuSettings.menuAction()])
        self.actionSettingsUser.triggered.connect(lambda:self.emit(signals.SIG_SHOW_SETTINGS))
        self.menuSettings.setTitle(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettingsUser.setText(QtGui.QApplication.translate("MainWindow", "User settings", None, QtGui.QApplication.UnicodeUTF8))

class DefaultMainWindow(QMainWindow, DefaultWidget):
    """
    Default window.
    Use this class to define a window with possibility to quit and set the log file.
    """
    
    def __init__(self, parent=None):
        super(DefaultMainWindow, self).__init__()
        
        self.menubar = QtGui.QMenuBar(self)
        self.setMenuBar(self.menubar)
        
        self.menuFile = QtGui.QMenu(self.menubar)
        
        self.actionSet_logfile = QtGui.QAction(self)
        self.actionQuit = QtGui.QAction(self)
        
        self.menuFile.addActions([self.actionSet_logfile, self.actionQuit])
        
        self.actionQuit.triggered.connect(self.close)
        self.actionSet_logfile.triggered.connect(self.action_change_logfile)
        
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSet_logfile.setText(QtGui.QApplication.translate("MainWindow", "Set logfile", None, QtGui.QApplication.UnicodeUTF8))

        
# MAIN PROGRAM #################################################################################
        
if __name__ == '__main__':
    
    # create main window
    app = QApplication(sys.argv)
    
    # init widget
    widget = DefaultWidget()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
    
