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

from Revolver.classes import devices, macro, threads, signals, config
from Revolver.macro import default_macro, gui_logging_widget
from Revolver.macro.UI import layout_simple_macro
from Revolver import gui_default_widget


class SimpleMotorMacro(layout_simple_macro.Ui_Form, default_macro.MacroControls):
    
    def __init__(self, parent=None):
        super(SimpleMotorMacro, self).__init__(self)
        default_macro.MacroControls.__init__(self)
        self.macroType = default_macro.MACRO_SIMPLE
        self.parent = parent
        self.steps = []
        self.repeatSteps = 1
        self.connect(self.table, Qt.SIGNAL('highlight_row'), self.action_highlight_macro_position)
        
        self.table.horizontalHeader().resizeSection(0, 150)
        self.table.horizontalHeader().resizeSection(1, 150)
        self.table.horizontalHeader().resizeSection(8, 50)
        self.table.horizontalHeader().resizeSection(9, 110)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnHidden(2, True)
        self.table.setColumnHidden(5, True)
        self.table.horizontalHeader().setResizeMode(8, Qt.QHeaderView.Fixed)
        self.table.verticalHeader().setResizeMode(Qt.QHeaderView.Fixed)
        
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
                
                if values["type"] != self.macroType:
                    self.emit(signals.SIG_LOAD_MACRO, values["type"], values)
                    return
            else:
                return
            
        (self.steps, self.repeatSteps) = (values["steps"], values["repeatSteps"])
        self.repeat_macro.setValue(self.repeatSteps)
        self.action_repaint_macros()
        
        logging.info("Macro was successfully loaded")
        self.generate_macro_steps()
        default_macro.MacroControls.action_load_macro(self)
        
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
                values = {"type":self.macroType, "steps":self.steps, "repeatSteps":self.repeatSteps}
                pickle.dump(values, macroFile)
                macroFile.close()
                logging.info("Macro was successfully saved into file: %s", filename)
        else:
            QtGui.QMessageBox.question(self, 'Add macro warning', "No macro to save !", QtGui.QMessageBox.Ok)
        default_macro.MacroControls.action_save_macro(self)
    
    def action_start_logging(self, *args, **kwargs):
        
        if self.logWidget:
            self.logWidget.setFloating(True)
            self.logWidget.reset()
            params = []
            deviceStatuses = []
            detectorController = devices.DetectorController(config.DEVICE_DETECTOR_CONTROLLER)
            for devicePath in self.macroDevices:
                device = devices.Motor(str(devicePath))
                params.append({"device":device, "value":"Position", "description":"%s" % device.name, "lock":self.threadLock})
                params.append({"device":detectorController, "method":"take_filename", "description":"Filename", "lock":self.threadLock, "noGraph":True})
                deviceStatuses.append( {"device":device, "params":[{"deviceValue":"Position", "description":"position"}]})
            graphOptions = {"title":"Motor position log", "xlabel":"Macro step", "ylabel":"Motor position"}
            
            logComment = "# motor device: %s" % (device.devicePath)
            
            self.logWidget.start_log_signals(self, signals.SIG_MACRO_STEP_COMPLETED, params, graphOptions, logComment=logComment, deviceStatuses=deviceStatuses)
            self.logWidget.set_kill_all_permissions(False)
            self.logWidget.show()
            
    def action_stop_logging(self, *args, **kwargs):
        """
        Stop logging values
        """
        if self.logWidget:
            self.logWidget.stop()
        
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
    
    def execute_macro(self, takeDark=None):
        """
        Init macro and start main macro loop
        """
        self.generate_macro_steps()
        macro.STOP = False
        try:
            if takeDark: takeDark.run()
            self.emit(signals._SIG_START_LOGGING)
            if self.macro_steps():
                self.emit(signals.SIG_SHOW_INFO, "Macro", "Macro was successfully executed")
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Macro error", "Macro was not executed correctly.", self.get_exception())
        self.emit(signals._SIG_STOP_LOGGING)
        self.emit(signals.SIG_ENABLE_CONTROLS)
    
        
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
        values = [macro.sampleName, macro.motorAlias, macro.motorDevice,
                  str(macro.position), str(macro.summed),
                  str(macro.filesafter), str(macro.wait), macro.comment]
        
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
    
    def generate_macro_steps(self, insertEmitHandler=True):
        """
        Prepare all macro steps
        """
        self.macroDevices = set()
        self.repeatSteps = int(self.repeat_macro.value())
        self.steps = []
        rows = self.table.rowCount()
        for i in range(0, rows):
            sampleName = self.table.item(i, 0).text()
            motorAlias = self.table.item(i, 1).text()
            motorDevice = self.table.item(i, 2).text()
            motorPosition = float(self.table.item(i, 3).text())
            summed = int(self.table.item(i, 4).text())
            filesafter = int(self.table.item(i, 5).text())
            wait = int(self.table.item(i, 6).text())
            comment = self.table.item(i, 7).text()
            takeDark = self.table.indexWidget(self.table.model().index(i, 8)).isChecked()
            
            self.macroDevices.add(motorDevice)
            newMacro = macro.MotorMacro(motorAlias, motorDevice, sampleName, summed, filesafter, motorPosition, wait, takeDark, comment)
            if insertEmitHandler: newMacro.emit = self.emit_handler
            self.steps.append(newMacro)
        return self.steps
    
    def macro_steps(self, lastStepStart=None):
        """
        Routine that executes all macro steps defined in table
        """
        try:
            step = float(100 / float(len(self.steps)))
            
            for i in range(0, self.repeatSteps, 1):
                self.threadLock.acquire()
                self.emit(signals.SIG_SET_PROGRESSBAR, self.macro_progressbar, 0)
                if not lastStepStart: lastStepStart = time.time()
                for index, current_macro in enumerate(self.steps):
                    if macro.STOP:
                        logging.warn("Next macro was canceled !")
                        break
                    self.table.emit(QtCore.SIGNAL("highlight_row"), int(index))
                    logging.warning("Starting macro " + str(index + 1))
                    current_macro.run(lastStepStart)
                    lastStepStart = time.time()
                    if macro.STOP == False:
                        logging.warning("Macro " + str(index + 1) + " execution completed")
                        self.emit(signals.SIG_MACRO_STEP_COMPLETED)
                    self.wait_lock_release()
                    self.emit(signals.SIG_SET_PROGRESSBAR, self.macro_progressbar, step * (index + 1))
                    current_macro.wait_seconds()
                if macro.STOP == False:
                    logging.warn("All macro steps was executed")
                else:
                    logging.warn("Macro was canceled !")
                    return False
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Macro error", "Macro was not executed correctly.", self.get_exception())
            return False
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
            if(coll in (4 , 5, 6)): 
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
                device = devices.Motor(devicePath)
                self.validate_device_minmax_value(value, device)
        except:
            item.setText("0")
        self.table.blockSignals(False)
    
# MAIN PROGRAM #################################################################################
if __name__ == '__main__':
    
    config.DEVICE_ALLOW_RETRY = False
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    win = gui_default_widget.DefaultMainWindow()
    win.setMinimumSize(900, 500)

    # init widget
    widget = SimpleMotorMacro()
    widget.logWidget = gui_logging_widget.LoggingWidget(win)
    win.addDockWidget(QtCore.Qt.DockWidgetArea(4), widget.logWidget)
    widget.logWidget.hide()
    
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
