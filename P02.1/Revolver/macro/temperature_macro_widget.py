"""
Gui that represent widget to enter and run macro.
This widget can contain three types of macro: motor, widget and time macro
"""
from PyQt4 import QtGui, QtCore, Qt
import sys
import signal
import logging
import pickle
import threading
import time

from Revolver.classes import devices, macro, dialogs, threads, signals, config
from Revolver.macro import default_macro, gui_logging_widget
from Revolver.macro.UI import layout_temperature_macro
from Revolver import gui_default_widget
from copy import copy

class TemperatureMacro(layout_temperature_macro.Ui_Form, default_macro.MacroControls):
    
    def __init__(self, parent=None):
        super(TemperatureMacro, self).__init__(self)
        default_macro.MacroControls.__init__(self)
        self.macroType = default_macro.MACRO_TEMPERATURE
        self.parent = parent
        self.steps = []
        self.threshold = float(self.error_threshold.value())
        self.repeatSteps = 1
        
        self.connect(self.table, Qt.SIGNAL('highlight_row'), self.action_highlight_macro_position)
        
        self.table.horizontalHeader().resizeSection(0, 150)
        self.table.horizontalHeader().resizeSection(1, 150)
        self.table.horizontalHeader().resizeSection(10, 50)
        self.table.horizontalHeader().resizeSection(11, 110)
        self.table.horizontalHeader().setStretchLastSection(True);
        self.table.setColumnHidden(2, True)
        self.table.setColumnHidden(5, True)
        self.table.horizontalHeader().setResizeMode(9, Qt.QHeaderView.Fixed)
        self.table.verticalHeader().setResizeMode(Qt.QHeaderView.Fixed)
    
    def action_show_settings(self):
        """
        Set logifle
        """
        settings = dialogs.SettingsDialog(self)
        settings.toggle_elements_display(False, [settings.cryostreamer_label, settings.cryostreamer_settings])
        settings.option_dark_timeout.setValue(macro.MACRO_DARK_WAIT)
        settings.cryostreamer_min.setValue(config.SETTINGS_CRYOSTREAMER_TEMPERATURE_MIN)
        settings.cryostreamer_max.setValue(config.SETTINGS_CRYOSTREAMER_TEMPERATURE_MAX)
        settings.hotblower_min.setValue(config.SETTINGS_HOTBLOVER_TEMPERATURE_MIN)
        settings.hotblower_max.setValue(config.SETTINGS_HOTBLOVER_TEMPERATURE_MAX)
        settings.ramping_threshold.setValue(config.SETTINGS_RAMPING_ERROR_THRESHOLD)
        settings.ramping_time_max.setValue(config.SETTINGS_RAMPING_MAXIMUM_TIME)
        settings.stabilization_time_min.setValue(config.SETTINGS_STABILIZATION_TIME_MIN)
        settings.stabilization_time_max.setValue(config.SETTINGS_STABILIZATION_TIME_MAX)
        settings.exec_()
       
    def action_open_dialog_add_macro(self):
        dialogs.AddTemperatureMacroDialog(self).exec_()
    
    def action_reset_macro(self):
        """
        Signal handler:
        reset macro
        """
        self.repeatSteps = []
        self.steps = []
        self.removePositions = []
        self.repeat_macro.setValue(0)
        self.action_repaint_macros()    
          
    def action_start_macro(self):
        """
        Signal response:
        start all macros into new thread
        """
        steps = self.generate_macro_steps()
        if not steps:
            self.emit(signals.SIG_SHOW_WARNING, "Macro", "Please add at least one macro step !")
            return
        
        takeDark = self.action_check_dark_shot_taken(steps[0])
        self.emit(signals.SIG_SET_PROGRESSBAR, self.macro_progressbar, 0)
        thread = threading.Thread(target=self.execute_macro, args=([takeDark]))
            
        try:
            if self.macro_reset_fileindex.isChecked(): devices.Detector(config.DEVICE_DETECTOR).set_file_index(1)
            threads.add_thread(thread)
            thread.start()
        except:
            self.window().emit(signals.SIG_SHOW_ERROR, "Macro error", "Macro step could not be executed")
            self.emit(signals.SIG_ENABLE_CONTROLS)
            return
        self.emit(signals.SIG_DISABLE_CONTROLS)
        
    def action_add_macro(self, macro):
        """
        Signal handler:
        add macro into macro table
        """
        self.table.blockSignals(True)
        self.steps.append(macro)
        
        # self.action_repaint_macros()
        size = self.table.rowCount()
        self.table.setRowCount(size + 1)
        values = [macro.sampleName, macro.alias, macro.devicePath,
                  str(macro.temperature), str(macro.summed),
                  str(macro.filesafter), str(macro.holdingTime), str(macro.holdingCount), str(macro.wait), macro.comment]
        
        for index, value in enumerate(values):
            item = QtGui.QTableWidgetItem(value)
            if index == 1:
                item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(size, index, item)
        
        index = index + 1
        takeDark = QtGui.QCheckBox()
        takeDark.setStyleSheet("margin-left:15px")
        if macro.takeDark:
            takeDark.setChecked(True)
        self.table.setIndexWidget(self.table.model().index(size, index), takeDark)
        
        index = index + 1  
        removeButton = QtGui.QPushButton("Remove")
        self.removePositions.append(removeButton)
        self.connect(removeButton, Qt.SIGNAL('clicked()'), lambda: self.action_remove_macro(removeButton))
        self.table.setIndexWidget(self.table.model().index(size, index), removeButton)
        self.table.blockSignals(False)
    
    def action_repaint_macros(self):
        """
        Signal handler:
        repaint macro table
        """
        self.table.blockSignals(True)
        table = self.table
        table.setRowCount(0)
        
        for index, lMacro in enumerate(self.steps):
            size = table.rowCount()
            table.setRowCount(size + 1)
            values = [lMacro.sampleName, lMacro.alias, lMacro.devicePath,
                      str(lMacro.temperature), str(lMacro.summed),
                      str(lMacro.filesafter), str(lMacro.holdingTime), str(lMacro.holdingCount), str(lMacro.wait), str(lMacro.comment)]
            
            for index, value in enumerate(values):
                table.setItem(size, index, QtGui.QTableWidgetItem(value))
            
            index = index + 1
            takeDark = QtGui.QCheckBox()
            takeDark.setStyleSheet("margin-left:15px")
            if lMacro.takeDark:
                takeDark.setChecked(True)
            table.setIndexWidget(table.model().index(size, index), takeDark)
            
            index = index + 1  
            removeButton = QtGui.QPushButton("Remove")
            self.removePositions.append(removeButton)
            self.connect(removeButton, Qt.SIGNAL('clicked()'), lambda removeButton=removeButton: self.action_remove_macro(removeButton))
            table.setIndexWidget(table.model().index(size, index), removeButton)
        self.table.blockSignals(False)
    
    def generate_macro_steps(self, insertEmitHandler=True):
        """
        Prepare all macro steps
        """
        self.repeatSteps = int(self.repeat_macro.value())
        self.steps = []
        self.threshold = float(self.error_threshold.value())
        rows = self.table.rowCount()
        for i in range(0, rows):
            sampleName = self.table.item(i, 0).text()
            motorAlias = self.table.item(i, 1).text()
            motorDevice = self.table.item(i, 2).text()
            temperature = float(self.table.item(i, 3).text())
            summed = int(self.table.item(i, 4).text())
            filesafter = int(self.table.item(i, 5).text())
            holdingTime = int(self.table.item(i, 6).text())
            holdingCount = int(self.table.item(i, 7).text())
            wait = int(self.table.item(i, 8).text())
            comment = self.table.item(i, 9).text()
            takeDark = self.table.indexWidget(self.table.model().index(i, 10)).isChecked()
            
            newMacro = macro.TemperatureMacro(motorAlias, motorDevice, sampleName, summed, filesafter, temperature, holdingTime, holdingCount, wait, takeDark, comment)
            if insertEmitHandler: newMacro.emit = self.emit_handler
            self.steps.append(newMacro)
        return self.steps
    
    def action_load_macro(self, values=None):
        """
        Signal handler:
        load macro from input file
        """
        if not(values):
            filename = QtGui.QFileDialog.getOpenFileName(self, "Load macro", "", "*.macro")
            if filename:
                macroFile = open(filename, 'r')
                self.action_reset_macro()
                values = pickle.load(macroFile)
                macroFile.close()
            else:
                return
                
            if values["type"] != self.macroType:
                    self.emit(signals.SIG_LOAD_MACRO, values["type"], values)
                    return
            
        (self.steps, self.repeatSteps, self.threshold) = (values["steps"], values["repeatSteps"], values["threshold"])
        self.repeat_macro.setValue(self.repeatSteps)
        self.error_threshold.setValue(self.threshold)
        self.action_repaint_macros()
        
        logging.info("Macro was successfully loaded from file: %s", filename)
        # self.generate_macro_steps()
        # default_macro.MacroControls.action_load_macro(self)
        
    def action_save_macro(self):
        """
        Signal handler:
        save macro into file
        """
        
        self.generate_macro_steps(insertEmitHandler=False)        
            
        if(self.steps):
            filename = QtGui.QFileDialog.getSaveFileName(self, "Save macro", "newMacro.macro", "*.macro")
            if filename:
                macroFile = open(filename, 'w+')
                values = {"type":self.macroType, "steps":self.steps, "repeatSteps":self.repeatSteps, "threshold":self.threshold}
                pickle.dump(values, macroFile)
                macroFile.close()
                logging.info("Macro was successfully saved into file: %s", filename)
        else:
            QtGui.QMessageBox.question(self, 'Add macro warning', "No macro to save !", QtGui.QMessageBox.Ok)
        default_macro.MacroControls.action_save_macro(self)
    
    def action_start_logging(self, *args, **kwargs):
        device = args[0]
        device.start_profiling()
        
        if self.logWidget:
            self.logWidget.setFloating(True)
            self.logWidget.reset()
            deviceStatuses = []
            params = [{"device":device, "value":"temperature", "description":"Real temperature", "source":device.output},
                      {"device":device, "value":"movingAverage", "description":"Average temperature", "source":device.output},
                      {"device":device, "value":device.setpointValue, "description":"Setpoint temperature"}]
            
            deviceStatusesParams = [{"value":device.output["temperature"], "description":"Temperature:"},
                      {"value":device.output["movingAverage"], "description":"Moving average:"},
                      {"deviceValue":device.setpointValue, "description":"Setpoint:"},
                      {"value":device.output["statusString"], "description":"Status:"}]
            device_polling = copy(args[0])
            deviceStatuses.append({"device":device_polling, "params":deviceStatusesParams})
            
            graphOptions = {"title":"Hotblower temperature log", "xlabel":"Time [s]", "ylabel":"Temperature [C]"}
            logComment = "# Temperature device: %s" % (device.devicePath)
            logComment += "\n# Error threshold: %.3f" % (self.threshold)
            
            self.logWidget.start_log_polling(params, graphOptions, logComment=logComment, deviceStatuses=deviceStatuses)
            self.logWidget.set_kill_all_permissions(False)
            self.logWidget.show()
    
        if self.logWidget2:
            self.logWidget2.reset()
            detectorController = devices.DetectorController(config.DEVICE_DETECTOR_CONTROLLER)
            params = [{"device":device, "value":device.output["temperature"], "description":"Real temperature"},
                      {"device":device, "value":device.output["movingAverage"], "description":"Average temperature"},
                      {"device":device, "deviceValue":device.setpointValue, "description":"Setpoint temperature"},
                      {"device":detectorController, "method":"take_filename", "description":"Filename", "lock":self.threadLock, "noGraph":True}]
            logComment = "# Temperature device: %s" % (device.devicePath)
            logComment += "\n# Error threshold: %.3f" % (self.threshold)
            self.logWidget2.start_log_signals_no_graphics(self, signals.SIG_MACRO_STEP_COMPLETED, params, logComment=logComment)
            self.logWidget2.set_kill_all_permissions(False)
    
    def action_stop_logging(self, *args, **kwargs):
        if self.logWidget:
            device = args[0]
            device.stop_profiling()
            self.logWidget.stop()
        if self.logWidget2:
            self.logWidget2.stop()
    
    def execute_macro(self, takeDark=None):
        """
        Init macro and start main macro loop
        """
        self.generate_macro_steps()
        device = devices.TemperatureDevice(self.steps[0].devicePath)
        macro.STOP = False
        try:
            if takeDark: takeDark.run()
            if self.macro_steps():
                self.emit(signals.SIG_SHOW_INFO, "Macro", "Macro was successfully executed")
                if self.macro_return_to_ambient: device.halt(force=True)
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Macro error", "Macro was not executed correctly.", self.get_exception())
            device.halt(force=True)
        
        self.emit(signals.SIG_ENABLE_CONTROLS)
    
    def macro_steps(self, lastStepStart=None):
        """
        Routine that executes all macro steps defined in table
        """
        try:
            device = devices.TemperatureDevice(self.steps[0].devicePath)
            self.emit(signals._SIG_START_LOGGING, device)
            
            step = float(100 / float(len(self.steps)))
            for i in range(0, self.repeatSteps, 1):
                self.emit(signals.SIG_SET_PROGRESSBAR, self.macro_progressbar, 0)
                if not lastStepStart: lastStepStart = time.time()
                for index, current_macro in enumerate(self.steps):
                    if macro.STOP:
                        logging.warn("Next macro was canceled !")
                        break
                    self.table.emit(QtCore.SIGNAL("highlight_row"), int(index))
                    logging.warning("Starting macro " + str(index + 1))
                    current_macro.run(lastStepStart, threshold=self.threshold, device=device)
                    lastStepStart = time.time()
                    if macro.STOP == False:
                        logging.warning("Macro " + str(index + 1) + " execution completed")
                        self.emit(signals.SIG_MACRO_STEP_COMPLETED)
                    self.emit(signals.SIG_SET_PROGRESSBAR, self.macro_progressbar, step * (index + 1))
                    current_macro.wait_seconds()
                if macro.STOP == False:
                    logging.warn("All macro steps was executed")
                else:
                    logging.warn("Macro was canceled !")
                    self.emit(signals._SIG_STOP_LOGGING, device)
                    return False
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Macro error", "Macro was not executed correctly.", self.get_exception())
            self.emit(signals._SIG_STOP_LOGGING, device)
            return False
        self.emit(signals._SIG_STOP_LOGGING, device)
        return lastStepStart
    
    def action_macro_edited(self, item):
        """
        Signal handler:
        validate input if macro was changed in table
        """
        self.table.blockSignals(True)
        row = item.row()
        coll = item.column()
        value = item.text()
        collName = self.table.horizontalHeaderItem(coll).text()
        try:
            if(coll == 0): self.validate_input(collName, "String", value)
        except:
            item.setText("Sample name")
        try:
            if(coll in (4 , 5, 6, 7, 8)): 
                self.validate_input(collName, "int", value)
                item.setText(str(int(value)))
        except:
            item.setText("0")
        try:
            if(coll == 6): self.validate_input(collName, "float", value)
        except:
            item.setText("0")
        try:
            if(coll == 3): 
                value = self.validate_input(collName, "float", value)
                devicePath = str(self.table.item(row, 2).text())
                device = devices.TemperatureDevice(devicePath)
                self.validate_device_minmax_value(value, device)
        except:
            item.setText("0")
        self.table.blockSignals(False)
    
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    config.DEVICE_ALLOW_RETRY = False
    app = QtGui.QApplication(sys.argv)
    win = gui_default_widget.DefaultMainWindow()
    win.setMinimumSize(1100, 500)
    win.action_add_settings_menu()
    
    # init widget
    widget = TemperatureMacro()
    widget.connect(win, signals.SIG_SHOW_SETTINGS, widget.action_show_settings)
    widget.logWidget = gui_logging_widget.LoggingWidget(win)
    win.addDockWidget(QtCore.Qt.DockWidgetArea(4), widget.logWidget)
    widget.logWidget.hide()
    
    widget.logWidget2 = gui_logging_widget.LoggingWidget(win)
    win.addDockWidget(QtCore.Qt.DockWidgetArea(4), widget.logWidget2)
    widget.logWidget2.hide()
        
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
