# import global classes 
from PyQt4 import QtGui, QtCore
import sys
import signal
 
# Import local classes
from  gui_default_widget import DefaultWidget
from Revolver.classes import config, signals, dialogs, macro
from UI import layout_revolver
import gui_macro_widget
import gui_scan_widget
import gui_status_widget
from Revolver.macro import gui_logging_widget

class revolver(layout_revolver.Ui_MainWindow, QtGui.QMainWindow, DefaultWidget):
    
    def __init__(self, parent=None):
        super(revolver, self).__init__()
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_signals(self):
        self.actionQuit.triggered.connect(self.close)
        self.actionSet_logfile.triggered.connect(self.action_change_logfile)
    
    def __init_variables(self):
        self.macroWidget = gui_macro_widget.MacroWidget()
        self.scanWidget = gui_scan_widget.ScanWidget()
        self.statusWidget = gui_status_widget.StatusWidget()
        
    def __main(self):
        
        # set menu icons
        self.actionQuit.setIcon(QtGui.QIcon(config.ICON_MENU_QUIT))
        
        self.insert_widget(self.macroWidget, self.macro_layout)
        self.insert_widget(self.scanWidget, self.scan_layout)
        self.dockWidget.setWidget(self.statusWidget)
        self.action_tab_changed(self.macroWidget)
        
        logWidget = gui_logging_widget.LoggingWidget(self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(4), logWidget)
        logWidget.hide()
        self.macroWidget.set_log_widget(logWidget)
    
    def action_show_settings(self):
        """
        Set logifle
        """
        settings = dialogs.SettingsDialog(self)
        settings.toggle_expert_mode_show(False)
        settings.option_dark_timeout.setValue(macro.MACRO_DARK_WAIT)
        settings.exec_()
        
    def action_tab_changed(self, widget):
        size = widget.sizeHint()
        self.resize(size.width() + 150, size.height())
        
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    #config.DEVICE_ALLOW_RETRY = False
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(sys.argv)
    #app = QtGui.QApplication(sys.argv)
    
    # init widget
    widget = revolver()
    widget.connect(widget, signals.SIG_SHOW_SETTINGS, widget.action_show_settings)
    widget.action_add_settings_menu()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)
    
    # set window icon
    app.setWindowIcon(QtGui.QIcon(config.ICON_MAIN))
    
    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()    

