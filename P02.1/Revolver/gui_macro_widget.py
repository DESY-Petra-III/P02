# import from global packages
from PyQt4 import QtGui, QtCore
import sys
import signal

from Revolver.macro import default_macro, gui_logging_widget
from Revolver.UI import layout_macro
from Revolver.classes import signals
from Revolver.gui_default_widget import DefaultWidget, DefaultMainWindow
from Revolver.macro import loop_macro_widget, simple_macro_widget, time_macro_widget

class MacroWidget(layout_macro.Ui_Form, DefaultWidget):
    
    def __init__(self, parent=None):
        super(MacroWidget, self).__init__(parent=parent)
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        self.simpleMacroWidget = simple_macro_widget.SimpleMotorMacro(parent=self)
        self.loopMacroWidget = loop_macro_widget.LoopMotorMacro(parent=self)
        self.timeMacroWidget = time_macro_widget.TimeMacro(parent=self)
        self.layotuSetup = [self.simple_macro_layout, self.loop_macro_layout, self.time_macro_layout]
        self.widgetSetup = [self.simpleMacroWidget, self.loopMacroWidget, self.timeMacroWidget]
    
    def __init_signals(self):
        for widget in self.widgetSetup:
            self.connect(widget, signals.SIG_LOAD_MACRO, self.action_load_macro)
            self.connect(widget, signals.SIG_MACRO_STARTED, self.action_disable_controls)
            self.connect(widget, signals.SIG_MACRO_ENDED, self.action_enable_controls)
        
    def __main(self):
        self.simple_macro_layout.layout().addWidget(self.simpleMacroWidget)
        self.loop_macro_layout.layout().addWidget(self.loopMacroWidget)
        self.time_macro_layout.layout().addWidget(self.timeMacroWidget)
    
    def set_log_widget(self, logWidget):
        self.logWidget = logWidget
        for wm in self.widgetSetup:
            wm.logWidget = logWidget
    
    def action_load_macro(self, macroType, loadData):
        if macroType == default_macro.MACRO_LOOP:
            self.set_macro_type.setCurrentIndex(self.layotuSetup.index(self.loop_macro_layout))
            self.loopMacroWidget.action_load_macro(loadData)
        elif macroType == default_macro.MACRO_SIMPLE:
            self.set_macro_type.setCurrentIndex(self.layotuSetup.index(self.simple_macro_layout))
            self.simpleMacroWidget.action_load_macro(loadData)
        elif macroType == default_macro.MACRO_TIME: 
            self.set_macro_type.setCurrentIndex(self.layotuSetup.index(self.time_macro_layout))
            self.timeMacroWidget.action_load_macro(loadData)
        else:
            self.emit(signals.SIG_SHOW_WARNING, "Macro loading", "Macro could not be loaded")
        
    def action_macro_type_changed(self, pageIndex):
        self.macro_select.setCurrentWidget(self.layotuSetup[pageIndex])
        
    def action_disable_controls(self):
        self.set_macro_type.setDisabled(True)
        if self.parent:
            self.parent.emit(signals.SIG_DISABLE_CONTROLS)
    
    def action_enable_controls(self):
        self.set_macro_type.setEnabled(True)
        if self.parent:
            self.parent.emit(signals.SIG_ENABLE_CONTROLS)
        
# MAIN PROGRAM #################################################################################
if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    win = DefaultMainWindow()
    win.setMinimumSize(900, 600)

    # init widget
    widget = MacroWidget()
    logWidget = gui_logging_widget.LoggingWidget(win)
    win.addDockWidget(QtCore.Qt.DockWidgetArea(4), logWidget)
    logWidget.hide()
    widget.set_log_widget(logWidget)
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, win.close_widget)
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    win.setCentralWidget(widget)
    win.show()
    # execute application
    app.exec_()
