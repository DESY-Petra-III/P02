"""
Created on Oct 20, 2013

@author: Martin Domaracky

"""
from PyQt4 import QtGui, QtCore
import sys
import signal

from Revolver.gui_default_widget import DefaultWidget
from Revolver.classes import config, signals
from Revolver import gui_device_value_graph_controls_widget
import time

class LoggingWidget(QtGui.QDockWidget, DefaultWidget):
    def __init__(self, parent=None):
        super(LoggingWidget, self).__init__(self)
        
        self.setMinimumSize(QtCore.QSize(79, 41))
        self.setFloating(True)
        widget = QtGui.QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        self.log_output_profiling = QtGui.QGridLayout()
        self.log_output_profiling.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(self.log_output_profiling)
        self.setWidget(widget)
        
        self.__init_variables()
        self.__init_signals()
        self.__main()
            
    def __init_variables(self):
        """
        Initialize all variables
        """
        self.log_graph = None
        self.logTitle = "Log"
        
    def __init_signals(self):
        """
        Initialize all signals
        """
        self.connect(self, signals.SIG_LOG_INIT, self.action_log_init)
        self.connect(self, signals.SIG_LOG_LINE, self.action_log_line)
                
    def __main(self):
        """
        Set widget properties
        """
        pass
    
    def action_log_init(self, logDataHeader, logComment=None):
        line = "\n############################ %s - Start ############################" % self.logTitle
        line += "\n# Log initialized at: %s" % time.strftime("%D %T")
        if(logComment):
            line += "\n%s" % logComment
        line += "\n%s\t%s" % ("Time", logDataHeader)
        self.action_log_line(line)
    
    def action_log_line(self, line):
        logFile = open(config.DEFAULT_LOG_FILE, 'a+')
        logFile.write("\n%s" % line)
        logFile.close()
    
    def action_log_point_data(self, xPoint, yValues):
        """
        @type xPoint: float
        @type yValues: list
        """
        line = "%.3f\t" % xPoint 
        line += "\t".join([str("%.3f" % y) for y in yValues])
        self.action_log_line(line)
    
    def start_log_polling(self, deviceParams, graphParams, pollingTime=1, logTitle="Log", logComment=""):
        """
        Start logging
        """
        self.logTitle = logTitle
        valuesHeader = ""
        for index, line in enumerate(deviceParams):
            if index != 0: valuesHeader += "\t"
            valuesHeader += line["description"]
        self.action_log_init(valuesHeader, logComment)
        
        self.log_graph = gui_device_value_graph_controls_widget.Controls(deviceParams=deviceParams, graphOptions=graphParams)
        self.log_graph.input_values_number.setMaximum(1000000000)
        self.connect(self.log_graph, signals.SIG_LOG_POINT_DATA, self.action_log_point_data)
        self.log_output_profiling.addWidget(self.log_graph)
        self.log_graph.action_start_plot(mode=gui_device_value_graph_controls_widget.MODE_POLLING)
                
    def start_log_signals(self, emiter, signal, deviceParams, graphParams, pollingTime=1, logTitle="Log", logComment=""):
        """
        Start logging
        """
        self.logTitle = logTitle
        valuesHeader = ""
        for index, line in enumerate(deviceParams):
            if index != 0: valuesHeader += "\t"
            valuesHeader += line["description"]
        self.action_log_init(valuesHeader, logComment)
        
        self.log_graph = gui_device_value_graph_controls_widget.Controls(deviceParams=deviceParams, graphOptions=graphParams)
        self.log_graph.input_values_number.setMaximum(1000000000)
        self.connect(self.log_graph, signals.SIG_LOG_POINT_DATA, self.action_log_point_data)
        self.log_output_profiling.addWidget(self.log_graph)
        self.log_graph.action_start_plot(mode=gui_device_value_graph_controls_widget.MODE_SIGNAL)
        self.log_graph.polling_controls.hide()
        
        self.connect(emiter, signal, self.log_graph, signals.SIG_PLOT_SIGNAL)
    
    def reset(self):
        if self.log_graph:
            self.log_graph.deleteLater()
            self.log_graph.destroy()
        
    def stop(self):
        """
        Stop logging
        """
        line = "\n# Log finished at: %s" % time.strftime("%D %T")
        line += "\n############################ %s - End ############################" % self.logTitle
        self.action_log_line(line)
        self.log_graph.emit(signals.SIG_STOP)
        
    """
    def change_logfile(self):
       
        filename = QtGui.QFileDialog.getSaveFileName(self, "Logfile output", "newLogfile.log", "*.log")
        if filename:
            self.outputFile = filename
            self.logfileInput.setText(self.outputFile)
            logFile = open(self.outputFile, 'a+')
            logFile.close()
          
    def action_show_controls(self):
        self.controls.show()
        
    def action_hide_controls(self):
        self.controls.hide()
     """     
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)

    # init widget
    widget = LoggingWidget()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)
    
    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()

    # execute application
    app.exec_()
