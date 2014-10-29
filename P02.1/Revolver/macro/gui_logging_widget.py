"""
Created on Oct 20, 2013

@author: Martin Domaracky

"""
from PyQt4 import QtGui, QtCore
import sys
import signal
import logging
import time
import datetime
import math

from Revolver.gui_default_widget import DefaultWidget
from Revolver.classes import config, signals, devices
from Revolver import gui_device_value_graph_controls_widget, gui_device_status_value_widget

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
        self.logfile = None
        self.deviceParams = None
        self.deviceStatuses = []
        
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
        self.logfile = self.set_startup_logfile()
        line = "############################ %s - Start ############################" % self.logTitle
        line += "\n# Log initialized at: %s" % time.strftime("%D %T")
        if(logComment):
            line += "\n%s" % logComment
        line += "\n%s\t%s\t%s\t%s" % ("Time", logDataHeader, "Timestamp", "Datetime")
        self.action_log_line(line, False)
    
    def action_log_line(self, line, leadingBreak=True):
        logFile = open(self.logfile, 'a+')
        logFile.write(("\n" if leadingBreak else "")+"%s" % line)
        logFile.close()
    
    def log_condition(self, value):
        try:
            return str("%.3f") % value
        except:
            return str(value)
    
    def action_log_point_data(self, xPoint, yValues):
        """
        @type xPoint: float
        @type yValues: list
        """
        timestamp_s = time.time()
        line = "%.3f\t" % xPoint 
        line += "\t".join([self.log_condition(y) for y in yValues])+"\t%s\t%s" % (timestamp_s, time.strftime("%D %T"))
        self.action_log_line(line)
    
    def start_log_polling(self, deviceParams, graphParams, pollingTime=1, logTitle="Log", logComment="", deviceStatuses=[]):
        """
        Start logging by polling
        """
        self.deviceStatuses = deviceStatuses
        self.logTitle = logTitle
        valuesHeader = ""
        for index, line in enumerate(deviceParams):
            if index != 0: valuesHeader += "\t"
            valuesHeader += line["description"]
        self.action_log_init(valuesHeader, logComment)
        
        if self.log_graph: self.log_output_profiling.removeWidget(self.log_graph)
        self.log_graph = gui_device_value_graph_controls_widget.Controls(deviceParams=deviceParams, graphOptions=graphParams)
        self.log_graph.input_values_number.setMaximum(1000000000)
        self.connect(self.log_graph, signals.SIG_LOG_POINT_DATA, self.action_log_point_data)
        
        self.log_output_profiling.addWidget(self.log_graph)
        self.log_graph.action_start_plot(mode=gui_device_value_graph_controls_widget.MODE_POLLING)
        self.add_device_status_controller()
                
    def start_log_signals(self, emiter, signal, deviceParams, graphParams, pollingTime=1, logTitle="Log", logComment="", deviceStatuses=[]):
        """
        Start logging by signal emit
        """
        self.deviceStatuses = deviceStatuses
        self.logTitle = logTitle
        valuesHeader = ""
        for index, line in enumerate(deviceParams):
            if index != 0: valuesHeader += "\t"
            valuesHeader += line["description"]
        self.action_log_init(valuesHeader, logComment)
        self.deviceParams = deviceParams
        
        if self.log_graph: self.log_output_profiling.removeWidget(self.log_graph)
        self.log_graph = gui_device_value_graph_controls_widget.Controls(deviceParams=deviceParams, graphOptions=graphParams)
        self.log_graph.input_values_number.setMaximum(1000000000)
        self.connect(self.log_graph, signals.SIG_LOG_POINT_DATA, self.action_log_point_data)
        
        self.log_output_profiling.addWidget(self.log_graph)
        self.log_graph.action_start_plot(mode=gui_device_value_graph_controls_widget.MODE_SIGNAL)
        self.log_graph.polling_controls.hide()
        
        self.connect(emiter, signal, self.log_graph, signals.SIG_PLOT_SIGNAL)
        #self.add_device_status_controller()
        
    def start_log_signals_values(self, emiter, signal, deviceParams, graphParams, pollingTime=1, logTitle="Log", logComment="", deviceStatuses=[]):
        """
        Start logging by signal emit
        """
        self.deviceStatuses = deviceStatuses
        self.logTitle = logTitle
        valuesHeader = ""
        for index, line in enumerate(deviceParams):
            if index != 0: valuesHeader += "\t"
            valuesHeader += line["description"]
        self.action_log_init(valuesHeader, logComment)
        self.deviceParams = deviceParams
        
        if self.log_graph: self.log_output_profiling.removeWidget(self.log_graph)
        self.log_graph = gui_device_value_graph_controls_widget.Controls(deviceParams=deviceParams, graphOptions=graphParams)
        self.log_graph.input_values_number.setMaximum(1000000000)
        self.connect(self.log_graph, signals.SIG_LOG_POINT_DATA, self.action_log_point_data)
        self.log_output_profiling.addWidget(self.log_graph)
        self.log_graph.action_start_plot(mode=gui_device_value_graph_controls_widget.MODE_SIGNAL)
        self.log_graph.polling_controls.hide()
        
        self.connect(emiter, signal, self.log_graph, signals.SIG_PLOT_SIGNAL)
        #self.add_device_status_controller()

    def start_log_signals_no_graphics(self, emiter, signal, deviceParams, pollingTime=1, logTitle="Log", logComment=""):
        """
        Start logging by signal no graphics
        """
        self.logTitle = logTitle
        valuesHeader = ""
        for index, line in enumerate(deviceParams):
            if index != 0: valuesHeader += "\t"
            valuesHeader += line["description"]
        self.action_log_init(valuesHeader, logComment)
        self.deviceParams = deviceParams
        
        self.connect(emiter, signal, self.log_no_graphics)
    
    def add_device_status_controller(self):
        for deviceStatus in self.deviceStatuses:
            params = deviceStatus["params"]
            deviceStatus["widget"] = gui_device_status_value_widget.DeviceValueStatusWidget(deviceStatus["device"], params)
            self.log_graph.device_controllers.addWidget(deviceStatus["widget"])
            self.log_graph.adjustSize()
        
    def log_no_graphics(self):
        try:
            self.xTime += 1
        except:
            self.xTime = 1
        dataY = []    
        for index, region in enumerate(self.deviceParams):
            if region.has_key("value"):
                yValue = region['value'][0]
            elif region.has_key("method"):
                yValue = getattr(region['device'], region['method'])()
            else:
                yValue = region['device'].read_attribute(region['deviceValue']).value
            dataY.append(yValue)
            if region['device'].deviceError: continue
            
        #self.emit(signals.SIG_LOG_POINT_DATA, self.xTime, dataY)
        self.action_log_point_data(self.xTime, dataY)
    
    def reset(self):
        try:
            if self.log_graph:
                self.log_graph.deleteLater()
                self.log_graph.destroy()
                for deviceStatus in self.deviceStatuses:
                    try:
                        deviceStatus["widget"].STOP = True
                    except:
                        pass
        except:
            logging.error("Graph could not be reset")
        
    def stop(self):
        """
        Stop logging
        """
        try:
            line = "\n# Log finished at: %s" % time.strftime("%D %T")
            line += "\n############################# %s - End #############################" % self.logTitle
            self.action_log_line(line)
            try:
                self.log_graph.emit(signals.SIG_STOP)
            except:
                pass
        except:
            logging.error("Log could not be ended")
        
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
