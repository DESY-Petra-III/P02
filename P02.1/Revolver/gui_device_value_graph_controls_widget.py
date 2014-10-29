"""
Create graph from device parameters
"""

# import global classes 
from PyQt4 import QtGui, Qt
import sys
import logging
from time import time
from Revolver.classes import config
import signal
from threading import Thread
from guiqwt.styles import CurveParam
from guiqwt.curve import CurveItem
from guiqwt.builder import make
import guiqwt.tools as tools
from PyTango import DeviceProxy
 
# Import local classes
from Revolver.classes import devices, signals, widget_plot, threads
from UI import layout_device_value_graph_controls
import gui_default_controls_widget as default_gui
from gui_scan_widget import getHSVcolors

MODE_POLLING = 1
MODE_SIGNAL = 2

class Controls(layout_device_value_graph_controls.Ui_Form, default_gui.DefaultControls):
    
    def __init__(self, deviceParams=[], parent=None, title=None, graphOptions=None):
        super(Controls, self).__init__()
        default_gui.DefaultControls.__init__(self, parent=parent)
        self.title = title
        self.graphOptions = graphOptions
        self.deviceParams = deviceParams
        self.SLEEP = [True]
        self.data = []
        self.signalCount = 0
        self.startPlottingMode = MODE_POLLING
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        self.graph = widget_plot.Curve_plot(wintitle="Device status", options=self.graphOptions)
        self.valuesNumber = 20
        self.pollingTime = 1
        self.maxSaveValues = int(self.input_values_number.maximum()) + 1
        self.STOP_PLOT = False
    
    def __init_signals(self):
        self.connect(self, Qt.SIGNAL("repaintCurve"), self.graph.action_set_curve_data)
        self.connect(self, signals.SIG_STOP, self.action_stop_plot)
        self.connect(self, signals.SIG_START, self.action_start_plot)
        self.connect(self, signals.SIG_START_MODE, self.action_start_plot)
        self.connect(self, signals.SIG_PLOT_SIGNAL, self.__graph_signal_routine)
        
    def __main(self):
        self.action_check_settings()
        self.graph.button_box.hide()
        self.graph_layout.addWidget(self.graph)
    
    def action_start_plot(self, mode=MODE_POLLING):
        self.STOP_PLOT = False
        self.signalCount = 0
        self.startPlottingMode = mode
        self.start_graph_plot_routine(mode)
    
    def action_stop_plot(self):
        self.STOP_PLOT = True
    
    def start_graph_plot_routine(self, mode):
        """
        """
        graphAttribute = []
        self.dataHeader = "%s" % "Time"
        self.graph.get_plot().del_all_items()
        self.graph.get_plot().do_autoscale(True)
        HSV_tuples = getHSVcolors(len(self.deviceParams))
        for index, region in enumerate(self.deviceParams):
            colorHSV = HSV_tuples[index]
            color = QtGui.QColor()
            color.setHsv(colorHSV[0], colorHSV[1], colorHSV[2])
            param = CurveParam()
            param.label = region["description"]
            curve = CurveItem(param)
            marker = "."
            if region.has_key("marker"):
                marker = region["marker"]
            curve = make.curve([], [], title=region["description"], color=color, marker=marker, markerfacecolor=color, markeredgecolor=color)
            curve.set_readonly(True)
            self.graph.plot.add_item(curve)
            self.dataHeader += "\t%s" % (region["description"])
            if region.has_key("device"):
                deviceInitialized = region["device"]
            else:
                deviceInitialized = devices.TangoDevice(region["devicePath"])
                
            if region.has_key("source"):
                quadrant = {'device':deviceInitialized, 'curve':curve, 'dataX' : [], 'dataY': [], 'value': deviceInitialized.output[region["value"]]}
            elif region.has_key("method"):
                quadrant = {'device':deviceInitialized, 'curve':curve, 'dataX' : [], 'dataY': [], 'method': region["method"]}
            else:
                quadrant = {'device':deviceInitialized, 'curve':curve, 'dataX' : [], 'dataY': [], 'deviceValue': region["value"]}
            if region.has_key("noGraph"):
                quadrant["noGraph"] = True
            if region.has_key("lock"):
                quadrant["lock"] = region["lock"]
            graphAttribute.append(quadrant)
        
        self.graph.zoom_enabled(False)
        
        # execute plot thread
        self.startTime = time()
        self.data = graphAttribute
        if mode == MODE_POLLING:
            thread = Thread(target=self.__graph_routine, args=([]))
            threads.add_thread(thread, self.widget_id)
            thread.start()
    
    def __graph_routine(self):
        """
        
        """
        try:
            xTime = 0
            while threads.THREAD_KEEP_ALIVE and not(self.STOP_PLOT):
                stepTime = time()
                xTime = stepTime - self.startTime
                dataY = []
                for attr in self.data:
                    if attr.has_key("value"):
                        yValue = attr['value'][0]
                    elif attr.has_key("method"):
                        yValue = getattr(attr['device'], attr['method'])()
                    else:
                        yValue = attr['device'].read_attribute(attr['deviceValue']).value
                    if attr['device'].deviceError: continue
                    dataY.append(yValue)
                    if attr.has_key("noGraph"): continue
                        
                    attr['dataX'].append(xTime)
                    attr['dataY'].append(yValue)
                    attr['dataX'] = attr['dataX'][self.maxSaveValues * -1:]
                    attr['dataY'] = attr['dataY'][self.maxSaveValues * -1:]
                    self.emit(Qt.SIGNAL("repaintCurve"), attr['curve'], attr['dataX'][self.valuesNumber * -1:], attr['dataY'][self.valuesNumber * -1:])
                self.emit(signals.SIG_LOG_POINT_DATA, xTime, dataY)
                try: 
                    attr['lock'].release() 
                except: 
                    pass
                threads.thread_sleep(self.pollingTime, sleepFlags=self.SLEEP)
                self.SLEEP[0] = True
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Graph error", "Graph routine could not start.", self.get_exception())
            # self._retry()
    
    def __grap_signal_routine_threaded(self):
        thread = Thread(target=self.__graph_signal_routine, args=([]))
        threads.add_thread(thread)
        thread.start()
    
    def __graph_signal_routine(self):
        """
        """
        try:
            self.signalCount += 1
            stepTime = time()
            xTime = stepTime - self.startTime
            if threads.THREAD_KEEP_ALIVE and not(self.STOP_PLOT):
                dataY = []
                for attr in self.data:
                    if attr.has_key("value"):
                        yValue = attr['value'][0]
                    elif attr.has_key("method"):
                        try:
                            yValue = getattr(attr['device'], attr['method'])()
                        except:
                            yValue = "ERROR"
                    else:
                        yValue = attr['device'].read_attribute(attr['deviceValue']).value
                    if attr['device'].deviceError: continue
                    
                    dataY.append(yValue)
                    if attr.has_key("noGraph"): continue
                    
                    attr['dataX'].append(self.signalCount)
                    attr['dataY'].append(yValue)
                    attr['dataX'] = attr['dataX'][self.maxSaveValues * -1:]
                    attr['dataY'] = attr['dataY'][self.maxSaveValues * -1:]
                    self.emit(Qt.SIGNAL("repaintCurve"), attr['curve'], attr['dataX'][self.valuesNumber * -1:], attr['dataY'][self.valuesNumber * -1:])
                self.emit(signals.SIG_LOG_POINT_DATA, xTime, dataY)
                try: 
                    attr['lock'].release() 
                except: 
                    pass
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Graph error", "Graph routine could not start.", self.get_exception())
    
    def _retry(self):
        """
        Retry device connection, only repaint when all devices all fully online
        """
        retrySleep = [True]
        while(retrySleep[0]):
            for attr in self.deviceParams:
                try:
                    DeviceProxy(attr["devicePath"]).state()
                    logging.error("Device online: %s" % (attr["devicePath"]) )
                    retrySleep = [False]
                except:
                    logging.error("Device not online, retrying: %s" % (attr["devicePath"]) )
            threads.thread_sleep(2, sleepFlags=retrySleep)
        
        # when device is online start plotting again
        self.emit(signals.SIG_START_MODE, self.startPlottingMode)
        
    def action_save_image(self):
        """
        Save scan as png image file
        """
        try:
            self.graph.get_tool(tools.SaveAsTool).activate_command(self.graph.plot, True)
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Graph save", "Graph could not be saved.")        
        
    def action_save_ascii(self):
        """
        Save scan as ascii file
        """
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save graph data", "scanData.txt", "*.txt")
        if not filename: return
        
        openFile = open(filename, "w+")
        openFile.write("# %s graph data export\n" % (self.title))
        openFile.write("# %s" % (self.dataHeader))
        
        data = [self.data[0]['dataX']];
        for d in self.data:
            data.append(d["dataY"])
        for index in range(len(data[0])):
            row = "\n"
            for index2, d in enumerate(data):
                if index2 == 0: row = row + ("%.4f" % d[index])
                else: row = row + ("\t%.4f" % d[index])
            openFile.write(row)
        openFile.close()
    
    def action_check_settings(self):
        self.valuesNumber = int(self.input_values_number.value())
        self.pollingTime = float(self.input_polling_time.value())
        
        for attr in self.data:
            self.emit(Qt.SIGNAL("repaintCurve"), attr['curve'], attr['dataX'][self.valuesNumber * -1:], attr['dataY'][self.valuesNumber * -1:])
    
    def action_polling_changed(self):
        self.SLEEP[0] = False
        
    def action_hide_controls(self):
        self.controls.hide()
        
    def action_show_controls(self):
        self.controls.hide()
    
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    petraParams = [{"devicePath":config.DEVICE_SERVER + "p02/adc/exp.01", "value":"Value", "description":"Petra current"}]
    graphOptions = {"title":"Petra current", "xlabel":"Time", "ylabel":"Current"}
    # petraStatus = gui_device_value_graph_controls_widget.Controls(parent=self, title="Petra status", deviceParams=petraParams, graphOptions=graphOptions)
    widget = Controls(parent=app, title="Petra status", deviceParams=petraParams, graphOptions=graphOptions)
    widget.action_start_plot()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
