"""
Gui that represent widget to enter and run macro.
This widget can contain three types of macro: motor, widget and time macro
"""
from PyQt4 import QtGui, Qt
import logging

from Revolver.gui_default_widget import DefaultWidget
from Revolver.classes import config, devices, macro, dialogs, signals

# macro types
MACRO_SIMPLE = 0
MACRO_LOOP = 1
MACRO_TIME = 2
MACRO_TEMPERATURE = 3

class MacroControls(DefaultWidget):
    def __init__(self, parent=None, table=None):
        super(MacroControls, self).__init__(self)
        self.removePositions = []
        self.macroType = None
        self.logWidget = None
        self.macroDevices = set()
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        """
        Initialize all variables
        """
        pass
        
    def __init_signals(self):
        """
        Initialize all signals
        """
        self.connect(self, signals._SIG_ADD_MACRO, self.action_add_macro)
        self.connect(self, signals._SIG_START_LOGGING, self.action_start_logging)
        self.connect(self, signals._SIG_STOP_LOGGING, self.action_stop_logging)
                
    def __main(self):
        """
        Set widget properties
        """
        # set default motor model
        self.emit(Qt.SIGNAL("changeDefaultMotor"), config.DEVICE_MOTOR)
    
    def action_start_logging(self):
        pass
    
    def action_stop_logging(self):
        pass
    
    def action_disable_controls(self):
        """
        Disable controls
        """
        self.widget_select.setDisabled(True)
        self.macro_main_controls.hide()
        self.macro_steps_controls.show()
        self.emit(signals.SIG_MACRO_STARTED, self.macroType)
        
    def action_enable_controls(self):
        """
        Enable controls
        """
        self.widget_select.setEnabled(True)
        self.macro_steps_controls.hide()
        self.macro_main_controls.show()
        self.emit(signals.SIG_MACRO_ENDED, self.macroType)
    
    def action_open_dialog_add_macro(self):
        dialogs.AddMacroDialog(self).exec_()
    
    def action_reset_macro(self):
        """
        Signal handler:
        reset macro
        """
        pass
    
    def action_STOP(self):
        """
        Signal handler:
        stop macro
        """
        macro.STOP = True
    
    def action_halt_macro(self):
        """
        Signal handler:
        stop all motors, close shutter, stop macro
        """
        devices.halt_all_running_devices()
        macro.STOP = True
    
    def action_repaint_macros(self):
        """
        Signal handler:
        repaint macro table
        """
        table = self.table
        table.setRowCount(0)
        for index, lMacro in enumerate(self.steps):
            size = table.rowCount()
            table.setRowCount(size + 1)
            values = [lMacro.sampleName, lMacro.motorAlias, lMacro.motorDevice,
                      str(lMacro.position), str(lMacro.summed),
                      str(lMacro.filesafter), str(lMacro.wait), lMacro.comment]
            
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
    
    def action_load_macro(self):
        """
        Signal handler:
        load macro from input file
        """
        self.emit(Qt.SIGNAL("macroLoaded(int)"), self.macroType)
        
    def action_save_macro(self):
        """
        Signal handler:
        save macro into file
        """
        self.emit(Qt.SIGNAL("macroSaved(int)"), self.macroType)
    
    def action_start_macro(self):
        """
        Generate loop macro steps
        """
        try:
            mainShutter = devices.MainShutter(config.DEVICE_SHUTTER_MAIN)
            if not(mainShutter.is_open()):
                self.emit(signals.SIG_SHOW_WARNING, "Macro", "Please open main shutter !")
                return
            
            self.set_diode_laser_out()
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Macro", "Macro start error !") 
    
    def action_check_dark_shot_taken(self, firstMacroStep):
        """
        Check if dark shot is taken on the first macro step
        @type firstMacroStep: macro
        """
        if not firstMacroStep.takeDark:
            answer = dialogs.askWarnDialog(self, "Dark shot", "Do you want to take dark shot before macro start?")
            if answer:
                darkShotMacro = macro.DarkShotMacro(firstMacroStep.summed)
                darkShotMacro.emit = self.emit_handler
                return darkShotMacro
            else:
                return None
          
    def action_add_macro(self):
        pass
    
    def generate_macro_steps(self):
        pass
    
    def action_highlight_macro_position(self, position):
        self.table.selectRow(position)
    
    def action_macro_edited(self):
        pass
    
    def emit_handler(self, signal, *args, **kargs):
        """
        Override DefaultWidget.emit_handler
        @type signal: String
        @type args: list
        @type kargs: dict
        """
        if(signal == "showTimeProgress"): self.emit(Qt.SIGNAL("showElement"), self.macro_wait_controls, kargs.get("flag"))
        elif(signal == "macroOperation"): self.current_operation_status.setText(args[0])
        elif(signal == "setWaitProgress"): self.emit(signals.SIG_SET_PROGRESSBAR, self.macro_waiting_progressbar, args[0])
    
    def action_remove_macro(self, button):
        """
        Signal handler:
        remove macro from macro table
        """
        position = self.removePositions.index(button)
        self.table.removeRow(position)
        del self.removePositions[position]
        logging.info("Macro step %i removed from table", position + 1)
