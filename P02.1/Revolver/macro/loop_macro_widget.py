"""
Gui that represent widget to enter and run macro.
This widget can contain three types of macro: motor, widget and time macro
"""
from PyQt4 import QtGui, QtCore, Qt
import sys
import signal
import logging
import pickle
import time

from Revolver.gui_default_widget import DefaultMainWindow
from Revolver.classes import devices, macro, dialogs, threads, signals, config
from Revolver.macro import default_macro, simple_macro_widget, gui_logging_widget
from Revolver.macro.UI import layout_loop_macro


class LoopMotorMacro(layout_loop_macro.Ui_Form, simple_macro_widget.SimpleMotorMacro):
    
    def __init__(self, parent=None):
        super(LoopMotorMacro, self).__init__(self)
        simple_macro_widget.SimpleMotorMacro.__init__(self)
        self.macroType = default_macro.MACRO_LOOP
        self.parent = parent
        self.loop = {"motor":"", "from":"", "to":"", "step":""} 
        
        self.connect(self.macro_button_select_motor_loop, Qt.SIGNAL('clicked()'), lambda: dialogs.SelectDeviceDialog(self, "changeLoopingMotor").exec_())
        self.connect(self, Qt.SIGNAL('changeLoopingMotor'), lambda loopMotor: self.macro_input_motor_loop.setText(loopMotor))
        attr = [self.macro_loop_start, self.macro_loop_end]
        self.connect(self.macro_input_motor_loop, Qt.SIGNAL('textChanged(QString)'), lambda inputQtObject: self.check_device_allowed_values(attr, devices.Motor(str(inputQtObject))))
    
    def action_reset_macro(self):
        """
        Signal handler:
        reset macro
        """
        self.repeatSteps = []
        self.steps = []
        self.loop = {"motor":"", "from":"", "to":"", "step":""} 
        self.removePositions = []
        self.repeat_macro.setValue(0)
        self.macro_loop_start.setValue(0)
        self.macro_loop_end.setValue(0)
        self.macro_loop_step.setValue(0)
        
        self.macro_input_motor_loop.blockSignals(True)
        self.macro_input_motor_loop.setText("")
        self.macro_input_motor_loop.blockSignals(False)
        
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
            else:
                return
                
            if values["type"] != self.macroType:
                    self.emit(signals.SIG_LOAD_MACRO, values["type"], values)
                    return
            
        (self.steps, self.repeatSteps, self.loop) = (values["steps"], values["repeatSteps"], values["loop"])
        self.repeat_macro.setValue(self.repeatSteps)
        self.macro_loop_start.setValue(self.loop["from"])
        self.macro_loop_end.setValue(self.loop["to"])
        self.macro_loop_step.setValue(self.loop["step"])
        
        self.macro_input_motor_loop.blockSignals(True)
        self.macro_input_motor_loop.setText(self.loop["motor"])
        self.macro_input_motor_loop.blockSignals(False)
        
        self.action_repaint_macros()
        
        logging.info("Loop macro was successfully loaded")
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
                values = {"type":self.macroType, "steps":self.steps, "repeatSteps":self.repeatSteps, "loop":self.loop}
                pickle.dump(values, macroFile)
                macroFile.close()
                logging.info("Loop macro was successfully saved into file: %s", filename)
        else:
            QtGui.QMessageBox.question(self, 'Add macro waringn', "No macro to save !", QtGui.QMessageBox.Ok)
        
    def generate_macro_steps(self, insertEmitHandler=True):
        """
        Prepare all macro steps
        """
        self.loop = {"motor":str(self.macro_input_motor_loop.text()),
                     "from":float(self.macro_loop_start.value()),
                     "to":float(self.macro_loop_end.value()),
                     "step":float(self.macro_loop_step.value())} 
        simple_macro_widget.SimpleMotorMacro.generate_macro_steps(self, insertEmitHandler=insertEmitHandler)
        self.macroDevices.add(str(self.macro_input_motor_loop.text()))
        return self.steps
    
    def action_start_logging(self, *args, **kwargs):
        if self.logWidget:
            self.logWidget.setFloating(True)
            self.logWidget.reset()
            params = []
            deviceStatuses = []
            for index,devicePath in enumerate(self.macroDevices):
                device = devices.Motor(str(devicePath))
                if index == 0:
                    logComment = "# Inner loop motor device: %s" % (device.name)
                else:
                    logComment += "\n# Outer loop motor device: %s" % (device.name)
                params.append({"device":device, "value":"Position", "description":"%s" % device.name, "lock":self.threadLock}) 
                deviceStatuses.append( {"device":device, "params":[{"deviceValue":"Position", "description":"position"}]})
            graphOptions = {"title":"Motor position log", "xlabel":"Macro step", "ylabel":"Motor position"}
            detectorController = devices.DetectorController(config.DEVICE_DETECTOR_CONTROLLER)
            params.append({"device":detectorController, "method":"take_filename", "description":"Filename", "lock":self.threadLock, "noGraph":True})
            #logComment = "# Outer loop motor device: %s" % (self.macroDevices[1])
            #logComment += "\n# Inner loop motor device: %s" % (self.macroDevices[0])
            self.logWidget.start_log_signals(self, signals.SIG_MACRO_STEP_COMPLETED,
                                             params, graphOptions, logComment=logComment, deviceStatuses=deviceStatuses)
            self.logWidget.set_kill_all_permissions(False)
            self.logWidget.show()
    
    def action_stop_logging(self, *args, **kwargs):
        if self.logWidget:
            self.logWidget.stop()
    
    def action_start_macro(self):
        toPosition = float(self.macro_loop_end.value())
        step = float(self.macro_loop_step.value())
        
        if(len(self.macro_input_motor_loop.text()) == 0):
            self.emit(signals.SIG_SHOW_WARNING, "Macro", "Please choose loop motor !")
            return
        if step > toPosition:
            self.emit(signals.SIG_SHOW_WARNING, "Macro", "Step is bigger than ending motor position")
            return
        if step == 0:
            self.emit(signals.SIG_SHOW_WARNING, "Macro", "Step must be bigger than zero")
            return
        
        return simple_macro_widget.SimpleMotorMacro.action_start_macro(self)
     
    def macro_steps(self, lastStepStart=None):
        """
        Execute loop macro
        """
        logging.info("Looped macro started")
        
        motor = devices.Motor(self.loop["motor"])
        loopRange = macro.macroRange(self.loop["from"], self.loop["to"], self.loop["step"])
        
        try:
            index = 0
            step = float(100 / float(len(loopRange)))
            lastStepStart = time.time()
            self.emit(signals.SIG_SET_PROGRESSBAR, self.loop_macro_progressbar, 0)
            for position in loopRange:
                logging.warn("Executing step %i, looping motor moving to position: %.5f", index, position)
                if macro.STOP or not threads.THREAD_KEEP_ALIVE:
                    logging.warn("Loop macro was canceled !")
                    break
                self.emit(signals.SIG_SET_PROGRESSBAR, self.macro_progressbar, 0)
                self.emit_handler("macroOperation", "Moving looping motor: %s to position %f" % (motor.name, position))
                motor.move(position)
                # run all macro steps and return time, when last m,acro was executed
                lastStepStart = simple_macro_widget.SimpleMotorMacro.macro_steps(self, lastStepStart=lastStepStart)
                index = index + 1
                self.emit(signals.SIG_SET_PROGRESSBAR, self.loop_macro_progressbar, step * (index))
            if macro.STOP == False:
                self.emit(signals.SIG_SHOW_INFO, "Macro", "Macro was successfully executed")
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Macro error", "Macro was not executed correctly.", self.get_exception())
        
        self.emit(signals.SIG_ENABLE_CONTROLS)
        # simple_macro_widget.SimpleMotorMacro.macro_steps(self, lastStepStart=lastStepStart)
    
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    config.DEVICE_ALLOW_RETRY = False
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    win = DefaultMainWindow()
    win.setMinimumSize(900, 600)

    # init widget
    widget = LoopMotorMacro()
    
    
    
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
