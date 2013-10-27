"""
Dialogs used in widgets
"""

# import from global packages 
from PyQt4 import QtGui, Qt
from PyQt4.QtGui import QMessageBox
import sys
import logging
import math

# Import from local packages
from UI import add_macro_dialog, select_device_dialog, add_temperature_macro_dialog
from Revolver.classes import devices, config, signals, macro

def askWarnDialog(parent, title, message):
    reply = QMessageBox.warning(parent, title,
                     message, QMessageBox.Yes, QMessageBox.No)

    if reply == QMessageBox.Yes:
        return True
    else:
        return False

def showInfoDialog(parent, title, message):
    QMessageBox.information(parent, title,
                     message, QMessageBox.Close)

class AddMacroDialog(QtGui.QDialog, add_macro_dialog.Ui_Dialog):
    """
    Macro step dialog, emit signal 
    """
    def __init__(self, parent=None, setDefault=True):
        """
        Class constructor
        @type parent: DefaultWidget
        """
        super(AddMacroDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        if setDefault:
            self.macro_input_motor.setText(config.DEVICE_MOTOR)
            self.action_check_device_restrictions(config.DEVICE_MOTOR)
            
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        """
        Initialize dialog variables
        """
        self.selectedModel = None
        self.positionDiscreete = True
        
    def __init_signals(self):
        """
        Initialize dialog signals
        """
        self.connect(self.macro_input_motor, Qt.SIGNAL('textChanged(QString)'), self.action_check_device_restrictions)
        self.connect(self.macro_button_select_motor, Qt.SIGNAL('clicked()'), self.action_select_device)
        self.connect(self, Qt.SIGNAL('changeDefaultMotor'), self.set_device)
        
    def __main(self):
        """
        Set dialog properties
        """
        self.action_select_discrete(True)
    
    def action_check_device_restrictions(self, devicePath):
        attr = [self.macro_value_from, self.macro_value_to, self.macro_input_position]
        motor = devices.Motor(str(devicePath))
        self.parent.check_device_allowed_values(attr, motor)
        
    def action_select_device(self):
        SelectDeviceDialog(self).exec_()
    
    def action_select_discrete(self, flag):
        """
        Signal handler:
        select discrete motor position
        """
        self.macro_input_position.show()
        self.macro_interval_controls.hide()
        self.positionDiscreete = True
    
    def action_select_interval(self, flag):
        """
        Signal handler:
        select interval motor position
        """
        self.macro_input_position.hide()
        self.macro_interval_controls.show()
        self.positionDiscreete = False
    
    def set_device(self):
        """
        Change motor, emit signal to parent widget
        """
        self.macro_input_motor.setText(config.DEVICE_MOTOR)
        self.parent.emit(Qt.SIGNAL('changeDefaultMotor'), config.DEVICE_MOTOR)
    
    def action_add_macro(self):
        """
        Signal handler:
        emit signal to parent widget and pass new macro step as parameter
        """
        sampleName = self.macro_input_sampleName.text()
        summed = self.macro_input_summed.text()
        filesafter = self.macro_input_filesafter.text()
        comment = self.macro_input_comment.text()
        position = self.macro_input_position.text()
        intervalFrom = self.macro_value_from.text()
        intervalTo = self.macro_value_to.text()
        intervalStep = self.macro_value_step.text()
        macro_wait_secons = self.macro_wait_time.text()
        takeDark = self.check_take_dark.isChecked()
        devicePath = str(self.macro_input_motor.text())        
        
        try:
            sampleName = self.parent.validate_input("Sample name", "string", sampleName)
            if self.positionDiscreete:
                position = self.parent.validate_input("Position", "float", position)
                self.parent.validate_device_minmax_value(position)
            else:
                intervalFrom = self.parent.validate_input("Position", "float", intervalFrom)
                intervalTo = self.parent.validate_input("Position", "float", intervalTo)
                intervalStep = self.parent.validate_input("Position", "float", intervalStep)
                self.parent.validate_device_minmax_value(intervalFrom)
                self.parent.validate_device_minmax_value(intervalTo)
                if intervalStep > math.fabs(intervalFrom - intervalTo): 
                    self.parent.emit(signals.SIG_SHOW_WARNING, "Input error", "Step is bigger than maximum allowed step")
                if intervalStep == 0: 
                    self.parent.emit(signals.SIG_SHOW_WARNING, "Input error", "Step must be bigger than zero")
        except:
            return

        try:
            if self.positionDiscreete:
                newMacro = macro.MotorMacro(self.parent.defaultMotorDevice.name, devicePath,
                                            sampleName, summed,
                                            filesafter, position,
                                            macro_wait_secons, takeDark, comment)
                self.parent.emit(Qt.SIGNAL("addMacro(macro)"), newMacro)
            else:
                mrange = macro.macroRange(intervalFrom, intervalTo, intervalStep)
                for position in mrange:
                    newMacro = macro.MotorMacro(self.parent.defaultMotorDevice.name, devicePath,
                                                sampleName, summed,
                                                filesafter, position,
                                                macro_wait_secons, takeDark, comment)
                    self.parent.emit(Qt.SIGNAL("addMacro(macro)"), newMacro)
        except:
            logging.error("Macro was not added: %s", sys.exc_info()[0])

class AddTemperatureMacroDialog(add_temperature_macro_dialog.Ui_Dialog, AddMacroDialog):
    
    def __init__(self, parent=None):
        super(AddTemperatureMacroDialog, self).__init__(parent, setDefault=False)
        self.macro_input_motor.setText(config.DEVICE_HOTBLOWER)
      
    def action_select_device(self):
        SelectDeviceDialog(self, defaultPath=config.PATH_HOTBLOWER_FILTER).exec_()
    
    def action_check_device_restrictions(self, devicePath):
        device = devices.Hotblower(str(devicePath))
        attr = [self.macro_value_from, self.macro_value_to, self.macro_input_position]
        self.parent.check_device_allowed_values(attr, device) 
    
    def action_add_macro(self):
        """
        Signal handler:
        emit signal to parent widget and pass new macro step as parameter
        """
        sampleName = str(self.macro_input_sampleName.text())
        summed = int(self.macro_input_summed.text())
        filesafter = int(self.macro_input_filesafter.text())
        comment = str(self.macro_input_comment.text())
        position = float(self.macro_input_position.text())
        intervalFrom = float(self.macro_value_from.text())
        intervalTo = float(self.macro_value_to.text())
        intervalStep = float(self.macro_value_step.text())
        wait_seconds = int(self.macro_wait_time.value())
        macro_wait_iterations = int(self.macro_wait_time_repeat.value())
        macro_wait_after = int(self.macro_wait_after.value())
        takeDark = self.check_take_dark.isChecked()
        
        device = devices.Hotblower(str(self.macro_input_motor.text()))
                
        try:
            sampleName = self.parent.validate_input("Sample name", "string", sampleName)
            if self.positionDiscreete:
                position = self.parent.validate_input("Position", "float", position)
            else:
                if intervalStep > math.fabs(intervalFrom - intervalTo): 
                    self.parent.emit(signals.SIG_SHOW_WARNING, "Input error", "Step is bigger than maximum allowed step")
                if intervalStep == 0: 
                    self.parent.emit(signals.SIG_SHOW_WARNING, "Input error", "Step must be bigger than zero")
        except:
            return

        # try:
        if self.positionDiscreete:
            newMacro = macro.TemperatureMacro(device.name, device.devicePath,
                                        sampleName, summed,
                                        filesafter, position,
                                        wait_seconds, macro_wait_iterations, macro_wait_after, takeDark, comment)
            self.parent.emit(Qt.SIGNAL("addMacro(macro)"), newMacro)
        else:
            mrange = macro.macroRange(intervalFrom, intervalTo, intervalStep)
            for position in mrange:
                newMacro = macro.TemperatureMacro(device.name, device.devicePath,
                                            sampleName, summed,
                                            filesafter, position,
                                            wait_seconds, macro_wait_iterations, macro_wait_after, takeDark, comment)
                self.parent.emit(Qt.SIGNAL("addMacro(macro)"), newMacro)
        # except:
        #    logging.error("Temperature macro was not added: %s", sys.exc_info()[0])
    
class SelectDeviceDialog(QtGui.QDialog, select_device_dialog.Ui_Dialog):
    """
    Dialog that can select desired device from device list
    """
    
    def __init__(self, parent=None, defaultSignal="changeDefaultMotor", defaultPath=config.PATH_MOTOR_FILTER):
        """
        Class constructor:
        @type parent: DefaultWidget
        @type defaultSignal: String
        @type defaultPath: String
        """
        super(SelectDeviceDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.defaultPath = defaultPath
        self.defaultSignal = defaultSignal
        self.exchange = {}
        self.__main()
        
    def __main(self):
        """
        Set dialog properties
        initialize taurusDevTree with path
        """
        self.taurusDevTree.setModel(self.defaultPath)
        nodes = self.taurusDevTree.getAllNodes()
        
        for nodeName, nodeWidget in nodes.iteritems():
            nodeNameLower = nodeName.lower()
            if devices.DEVICE_NAMES.has_key(nodeNameLower):
                self.exchange[devices.DEVICE_NAMES[nodeNameLower]] = nodeName;
                nodeWidget.setText(0, devices.DEVICE_NAMES[nodeNameLower])
        
    def action_select_motor(self, model=None):
        """
        Signal handler:
        emit signal to parent widget with selected motor devicePath
        """
        selected = self.taurusDevTree.getSelectedNodes()
        
        if selected:
            retDevice = str(selected[0].text(0))
            if self.exchange.has_key(retDevice):
                retDevice = self.exchange[retDevice]
            selectedMotor = config.DEVICE_SERVER + retDevice
            if self.defaultSignal == "changeDefaultMotor":
                config.DEVICE_MOTOR = selectedMotor
            self.parent.emit(Qt.SIGNAL(self.defaultSignal), selectedMotor)
            self.close()

"""
class AboutUI(QtGui.QDialog, aboutUI.Ui_Dialog):
    
    def __init__(self, parent=None):
        super(AboutUI, self).__init__(parent)
        self.setupUi(self)
        self.banner.setPixmap(QtGui.QPixmap(config.ICON_ABOUT))
        self.layout().setSizeConstraint(Qt.QLayout.SetFixedSize)
        self.parent = parent
"""
