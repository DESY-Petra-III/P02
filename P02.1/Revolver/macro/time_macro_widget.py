"""
Gui that represent widget to enter and run macro.
This widget can contain three types of macro: motor, widget and time macro
"""
from PyQt4 import QtGui
import sys
import signal
import logging
import pickle
import threading
import time

from Revolver.classes import macro, threads, signals, devices, config
from Revolver.macro import default_macro, gui_logging_widget
from Revolver.macro.UI import layout_time_macro


class TimeMacro(layout_time_macro.Ui_Form, default_macro.MacroControls):
    
    def __init__(self, parent=None):
        super(TimeMacro, self).__init__(self)
        default_macro.MacroControls.__init__(self)
        self.macroType = default_macro.MACRO_TIME
        self.parent = parent
        self.timeMacro = None
        
    def action_reset_macro(self):
        """
        Signal handler:
        reset macro
        """
        self.macro_input_sampleName.setText("")
        self.macro_input_summed.setValue(0)
        self.macro_input_filesafter.setValue(1)
        self.macro_input_comment.setText("")
        self.macro_input_repeat.setValue(1)
        self.macro_wait_time.setValue(1)
        self.check_take_dark.setChecked(False)
    
    def action_repaint_macros(self):
        self.macro_input_sampleName.setText(self.timeMacro.sampleName)
        self.macro_input_summed.setValue(int(self.timeMacro.summed))
        self.macro_input_filesafter.setValue(int(self.timeMacro.filesafter))
        self.macro_input_comment.setText(self.timeMacro.comment)
        self.macro_input_repeat.setValue(int(self.timeMacro.repeat))
        self.macro_wait_time.setValue(int(self.timeMacro.wait))
        self.check_take_dark.setChecked(self.timeMacro.takeDark)
    
    def action_start_logging(self, *args, **kwargs):
        self.logWidget.action_log_init("Step\tFilename","# Wait after shot: %d sec.\n# Number of iterations: %d" % (self.timeMacro.wait, self.timeMacro.repeat))
        
    def action_stop_logging(self, *args, **kwargs):
        self.logWidget.stop()
    
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
            
        (self.timeMacro) = (values["timeMacro"])
        
        self.action_repaint_macros()
        
        logging.info("Time macro was successfully loaded")
        self.generate_macro_steps()
        default_macro.MacroControls.action_load_macro(self)
        
    def action_save_macro(self):
        """
        Signal handler:
        save macro into file
        """
        self.generate_macro_steps(insertEmitHandler=False)        
            
        if(self.timeMacro):
            filename = QtGui.QFileDialog.getSaveFileName(self, "Save macro", "newMacro.macro", "*.macro")
            if filename:
                macroFile = open(filename, 'w+')
                values = {"type":self.macroType, "timeMacro":self.timeMacro}
                pickle.dump(values, macroFile)
                macroFile.close()
                logging.info("Loop macro was successfully saved into file: %s", filename)
        else:
            QtGui.QMessageBox.question(self, 'Add macro waringn', "No macro to save !", QtGui.QMessageBox.Ok)
        
    def generate_macro_steps(self, insertEmitHandler=True):
        """
        Prepare all macro steps
        """
        sampleName = str(self.macro_input_sampleName.text())
        summed = str(self.macro_input_summed.text())
        filesafter = str(self.macro_input_filesafter.text())
        comment = str(self.macro_input_comment.text())
        repeat = int(self.macro_input_repeat.text())
        wait = int(self.macro_wait_time.text())
        takeDark = self.check_take_dark.isChecked()
                
        try:
            sampleName = self.validate_input("Sample name", "string", sampleName)
        except:
            return False
        
        self.timeMacro = macro.TimeMacro(sampleName, summed, filesafter, wait, repeat, takeDark, comment)
        if insertEmitHandler: self.timeMacro.emit = self.emit_handler
        return self.timeMacro
        
    def action_start_macro(self):
        """
        Signal response:
        start all macros into new thread
        """
        # default_macro.MacroControls.action_start_macro(self)
        if not self.generate_macro_steps(): return 
        takeDark = self.action_check_dark_shot_taken(self.timeMacro)
            
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
        Execute loop macro
        """
        self.emit(signals._SIG_START_LOGGING)
        macro.STOP = False
        logging.info("Time macro started")
        self.emit(signals.SIG_SET_PROGRESSBAR, self.macro_progressbar, 0)
        startTimetamp = time.time()
        detectorController = devices.DetectorController(config.DEVICE_DETECTOR_CONTROLLER)
            
        try:
            if takeDark: takeDark.run()
            step = float(100 / float(self.timeMacro.repeat))
            lastStepStart = time.time()
            for index in range(0, int(self.timeMacro.repeat)):
                if not threads.THREAD_KEEP_ALIVE: return
                logging.info("Time macro step #%i executed" % (index + 1))
                self.timeMacro.run(lastStepStart)
                self.emit(signals.SIG_MACRO_STEP_COMPLETED)
                lastStepStart = time.time()
                self.timeMacro.wait_seconds()
                self.emit(signals.SIG_SET_PROGRESSBAR, self.macro_progressbar, step * (index + 1))
                
                self.logWidget.action_log_point_data(lastStepStart-startTimetamp,[index, detectorController.take_filename()])
                if macro.STOP == True:
                    break
            if macro.STOP == False:
                logging.warn("All macro steps was executed")
                self.emit(signals.SIG_SHOW_INFO, "Macro", "Macro was successfully executed")
            else:
                logging.warn("Macro was canceled !")
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Macro error", "Macro was not executed correctly.", self.get_exception())
        self.emit(signals.SIG_ENABLE_CONTROLS)
        self.emit(signals._SIG_STOP_LOGGING)
    
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    config.DEVICE_ALLOW_RETRY = False
    
    # create main window
    app = QtGui.QApplication(sys.argv)

    # init widget
    widget = TimeMacro()
    widget.logWidget = gui_logging_widget.LoggingWidget()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()

    # execute application
    app.exec_()
