"""
Dialogs used in widgets
"""

# import from global packages 
from PyQt4 import QtGui, Qt
from PyQt4.QtGui import QMessageBox
import sys
import logging
import math
from PyQt4.QtGui import QInputDialog, QDialog, QGridLayout, QPushButton
from taurus import Device

# Import from local packages
from UI import add_macro_dialog, select_device_dialog, add_temperature_macro_dialog
from Revolver.macro.UI import layout_settings, layout_sardana_motro_macro
from Revolver.classes import devices, config, signals, macro, widget_plot
from PyTango._PyTango import DevState
from guiqwt.styles import CurveParam
from guiqwt.curve import CurveItem
from guiqwt.builder import make
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.resource.taurus_resource_utils import __init

def getHSVcolors(N):
        """
        Get color range from HSV color space defined by N
        @type N: int
        """
        return [(x * 360 / N, 230, 230) for x in range(N)]

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

class AddSardanaMotorMacroDialog(QtGui.QDialog, layout_sardana_motro_macro.Ui_Dialog, TaurusWidget):
    """
    Macro step dialog, emit signal 
    """
    def __init__(self, motor, parent=None):
        """
        Class constructor
        @type parent: DefaultWidget
        @param motor: devices.Motor
        """
        super(AddSardanaMotorMacroDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.motorDevice = motor
        
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        """
        Initialize dialog variables
        """
        self.door = devices.TangoDevice(config.BL_DEFAULT_DOOR)
        self.qDoor = Device(config.BL_DEFAULT_DOOR)
        self.scan_plot = widget_plot.Curve_plot(edit=False, toolbar=True,
                                                wintitle="All image and plot tools test", parent=self,
                                                options={"title":"Scan graph", "xlabel":"Motor position", "ylabel":"Avg"})
        
    def __init_signals(self):
        """
        Initialize dialog signals
        """
        Qt.QObject.connect(self, Qt.SIGNAL("showScan"), self.actionShowScanGraph)
        self.connect(self, Qt.SIGNAL("repaintCurve"), self.scan_plot.action_set_curve_data)
        self.connect(self.qDoor, Qt.SIGNAL("macroStatusUpdated"), self.stepper)
        
    def __main(self):
        """
        Set dialog properties
        """
        self.action_check_device_restrictions()
        #m = Device("motor/omvsme58_exp/1")
        #db = m.factory().getDatabase()
        #[logging.error(method) for method in dir(db) if callable(getattr(db, method))]
        try:
            alias = self.motorDevice.device.alias()
        except:
            self.motorDevice = devices.Motor(devices.SUB_MOTOR_DEVICES[self.motorDevice.devicePath.replace("tango://","")])
            alias = self.motorDevice.device.alias()
        #logging.error(alias)
        #logging.error(db.getElementFullName("exp_mot01"))
        #self.action_select_discrete(True)
        self.label_motor_name.setText(alias)
    
    def action_check_device_restrictions(self):
        attr = [self.macro_value_from, self.macro_value_to]
        self.parent.check_device_allowed_values(attr, self.motorDevice)
        
    def action_execute_macro(self):
        self.scan_plot.get_plot().del_all_items()
        self.scan_plot.get_plot().do_autoscale(True)   
        self.door.execute_command("RunMacro",['ascan',
                                      str(self.motorDevice.device.alias()),
                                      str(self.macro_value_from.value()),
                                      str(self.macro_value_to.value()),
                                      str(self.macro_steps.value()),
                                      str(self.macro_integration_time.value())
                                      ])
        
    def actionShowScanGraph(self):
        self.scan_plot.show()
   
    def stepper(self, data):
        macro = data[0]
        if macro is None: return        
        data = data[1][0]
        state, range, step, id = data["state"], data["range"], data["step"], data["id"]
        if id is None: return
        id = int(id)
        
        if state == "stop" or state == "finish":
            if id == self.taurusSequencerWidget.lastMacroId():
                self.scanStarted = False
        elif state == "start":
            if id == self.taurusSequencerWidget.firstMacroId():
                o = self.mainDoor.read_attribute("Output")
                devices = o.value[0].split()[2:-1]
                self.scanStarted = True
                
                HSV_tuples = getHSVcolors(len(devices))
                
                self.emit(Qt.SIGNAL("showScan"))
                self.scanOutput = []
                for index,dev in enumerate(devices):
                    colorHSV = HSV_tuples[index]
                    color = QtGui.QColor()
                    color.setHsv(colorHSV[0], colorHSV[1], colorHSV[2])
                    
                    param = CurveParam()
                    param.label = dev
                    curve = CurveItem(param)
                    curve = make.curve([], [], title=dev, color=color, marker=".", markerfacecolor=color, markeredgecolor=color)
                    curve.set_readonly(True)
                    self.scan_plot.plot.add_item(curve)
                    self.scanOutput.append( {"curve":curve, "X":[], "Y":[]} )
        elif state == "step":
            o = self.mainDoor.read_attribute("Output")
            values = o.value
            values = values[-1].split()[0:-1]
            x = values.pop(0)
            if x != "#Pt":
                for index, value in enumerate(values):
                    if( len(self.scanOutput[index]["X"]) > 0 ):
                        x = self.scanOutput[index]["X"][-1]+1
                    else:
                        x = 0
                    self.scanOutput[index]["X"].append(x)
                    self.scanOutput[index]["Y"].append(float(value))
                    self.emit(Qt.SIGNAL("repaintCurve"), self.scanOutput[index]["curve"], self.scanOutput[index]["X"], self.scanOutput[index]["Y"])

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
        try:
            motor = devices.Motor(str(devicePath))
            self.parent.check_device_allowed_values(attr, motor)
        except:
            logging.error("Default motor not initialized")
        
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
        except Exception, e:
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
    
    def __init__(self, parent=None, defaultDevice=config.DEVICE_HOTBLOWER, defaultPath=config.PATH_TEMPERATURE_DEVICE_FILTER):
        super(AddTemperatureMacroDialog, self).__init__(parent, setDefault=False)
        self.defaultPath = defaultPath
        self.defaultDevice = defaultDevice
        self.macro_input_motor.setText(defaultDevice)
      
    def action_select_device(self):
        SelectDeviceDialog(self, defaultPath=self.defaultPath).exec_()
    
    def action_check_device_restrictions(self, devicePath):
        try:
            device = devices.TemperatureDevice(str(devicePath))
            attr = [self.macro_value_from, self.macro_value_to, self.macro_input_position]
            self.parent.check_device_allowed_values(attr, device)
        except:
            logging.error("Device not connected") 
    
    def action_add_macro(self):
        """
        Signal handler:
        emit signal to parent widget and pass new macro step as parameter
        """
        sampleName = str(self.macro_input_sampleName.text())
        summed = int(self.macro_input_summed.text())
        filesafter = int(self.macro_input_filesafter.text())
        comment = str(self.macro_input_comment.text())
        position = self.macro_input_position.text()
        intervalFrom = float(self.macro_value_from.text().replace(',', '.'))
        intervalTo = float(self.macro_value_to.text().replace(',', '.'))
        intervalStep = float(self.macro_value_step.text().replace(',', '.'))
        wait_seconds = int(self.macro_wait_time.value())
        macro_wait_iterations = int(self.macro_wait_time_repeat.value())
        macro_wait_after = int(self.macro_wait_after.value())
        takeDark = self.check_take_dark.isChecked()
        
        device = devices.TemperatureDevice(str(self.macro_input_motor.text()))
                
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
        print defaultPath
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
        for path in self.defaultPath:
            self.taurusDevTree.setModel(path)
        nodes = self.taurusDevTree.getAllNodes()
        
        for nodeName, nodeWidget in nodes.iteritems():
            nodeNameLower = nodeName.lower().strip().split()[0]
            if devices.DEVICE_NAMES.has_key(nodeNameLower):
                self.exchange[devices.DEVICE_NAMES[nodeNameLower]] = nodeName;
                nodeWidget.setText(0, devices.DEVICE_NAMES[nodeNameLower])
            else:
                nodeWidget.setText(0, nodeNameLower)
        
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
            selectedMotor = str(config.DEVICE_SERVER + retDevice).strip()
            if self.defaultSignal == "changeDefaultMotor":
                config.DEVICE_MOTOR = selectedMotor
            self.parent.emit(Qt.SIGNAL(self.defaultSignal), selectedMotor)
            self.close()

class SettingsDialog(QtGui.QDialog, layout_settings.Ui_Dialog):
    
    dark_default = macro.MACRO_DARK_WAIT
    hbmin_default = config.SETTINGS_HOTBLOVER_TEMPERATURE_MIN
    hbmax_default = config.SETTINGS_HOTBLOVER_TEMPERATURE_MAX
    csmin_default = config.SETTINGS_CRYOSTREAMER_TEMPERATURE_MIN
    csmax_default = config.SETTINGS_CRYOSTREAMER_TEMPERATURE_MAX
    rampingThreshold_default = config.SETTINGS_RAMPING_ERROR_THRESHOLD
    stabmin_default = config.SETTINGS_STABILIZATION_TIME_MIN
    stabmax_default = config.SETTINGS_STABILIZATION_TIME_MAX
    rampingmax_default = config.SETTINGS_RAMPING_MAXIMUM_TIME
    
    def __init__(self, parent=None):
        """
        Class constructor
        @type parent: DefaultWidget
        """
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
            
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        """
        Initialize dialog variables
        """
        pass
    
    def __init_signals(self):
        """
        Initialize dialog signals
        """
        pass
        
    def __main(self):
        """
        Set dialog properties
        """
        pass
    
    def toggle_expert_mode_show(self, flag):
        self.expert_mode_panel.setVisible(flag)
        self.expert_settings.setVisible(flag)
        
    def toggle_elements_display(self, flag, elements):
        return
        for element in elements:
            element.setVisible(flag)
    
    def action_set_dark_timeout(self, value):
        macro.MACRO_DARK_WAIT = value
    
    def action_set_cryostreamer_min(self, value):
        config.SETTINGS_CRYOSTREAMER_TEMPERATURE_MIN = value
        
    def action_set_cryostreamer_max(self, value):
        config.SETTINGS_CRYOSTREAMER_TEMPERATURE_MAX = value
    
    def action_set_hotblower_min(self, value):
        config.SETTINGS_HOTBLOVER_TEMPERATURE_MIN = value
        
    def action_set_hotblower_max(self, value):
        config.SETTINGS_HOTBLOVER_TEMPERATURE_MAX = value
        
    def action_set_ramping_threshold(self, value):
        config.SETTINGS_RAMPING_ERROR_THRESHOLD = value
        
    def action_set_ramping_max(self, value):
        config.SETTINGS_RAMPING_MAXIMUM_TIME = value
        
    def action_set_tabilization_min(self, value):
        config.SETTINGS_STABILIZATION_TIME_MIN = value
        
    def action_set_stabilization_max(self, value):
        config.SETTINGS_STABILIZATION_TIME_MAX = value
    
    def action_reset_settings(self):
        self.option_dark_timeout.setValue(self.dark_default)
        self.hotblower_min.setValue(self.hbmin_default)
        self.hotblower_max.setValue(self.hbmax_default)
        self.cryostreamer_min.setValue(self.csmin_default)
        self.cryostreamer_max.setValue(self.csmax_default)
        
        self.ramping_threshold.setValue(self.rampingThreshold_default)
        self.ramping_time_max.setValue(self.rampingmax_default)
        self.stabilization_time_min.setValue(self.csmin_default)
        self.stabilization_time_max.setValue(self.csmax_default)
            
    def action_set_expert_mode(self, flag):
        """
        Set expert mode
        @type flag: bool
        """
        ok = False
        if flag:
            editPassword = Qt.QLineEdit(self)
            editPassword.setEchoMode(Qt.QLineEdit.Password)
            pin, ok = QInputDialog.getText(self, "Expert mode verification",
                                          "Please enter expert mode pin:", Qt.QLineEdit.Password,
                                          "");
        if ok:
            if pin != config.SETTINGS_EXPERT_MODE_PASSWORD:
                self.button_expert_mode.setChecked(False)
                self.emit(signals.SIG_SHOW_WARNING, "Export mode", "Wrong pin entered !")
                self.expert_settings.setEnabled(False)
                return False
            else:
                self.button_expert_mode.setChecked(True)
                self.expert_settings.setEnabled(True)
        else:
            self.button_expert_mode.setChecked(False)
            self.expert_settings.setEnabled(False)
            return False
        return True

"""
class AboutUI(QtGui.QDialog, aboutUI.Ui_Dialog):
    
    def __init__(self, parent=None):
        super(AboutUI, self).__init__(parent)
        self.setupUi(self)
        self.banner.setPixmap(QtGui.QPixmap(config.ICON_ABOUT))
        self.layout().setSizeConstraint(Qt.QLayout.SetFixedSize)
        self.parent = parent
"""

from taurus.qt.qtgui.panel import TaurusAttrForm
class DeviceAttributeDialog(QtGui.QDialog, TaurusWidget):
    
    def __init__(self, devicePath, parent=None, attributeFilter=None):
        self.devicePath = devicePath
        
        super(DeviceAttributeDialog, self).__init__()
        form = TaurusAttrForm(self)
        if attributeFilter:
            def displayFilter(attribute):
                if attribute.label in attributeFilter:
                    return True
            form.setViewFilters([displayFilter])
        
        form.setWindowTitle("Attributes for device @ %s" % devicePath)
        self.addChild(form)
        self.setFixedHeight(600)
        self.setFixedWidth(600)
        form.setFixedHeight(600)
        form.setFixedWidth(600)
        form.setModel(devicePath)
        
        self.mainForm = form
        

class MotorAttributeDialog(DeviceAttributeDialog):
    
    def __init__(self, devicePath, parent=None, attributeFilter=None):
        super(MotorAttributeDialog, self).__init__(devicePath, parent, attributeFilter)
        
        encoderButton = QPushButton("Encoder")
        self.connect(encoderButton, Qt.SIGNAL("clicked()"), self.openEncoderDialog)
        self.mainForm.children()[1].children()[2].addButton(encoderButton,0)
        
    def openEncoderDialog(self):
        attributes = ["Position","StepPositionController","StepPositionInternal","StepPosition","EncoderRawPosition",
                      "HomePosition","FlagHomed","EncoderConversion","EncoderRatio","FlagUseEncoderPosition",
                      "FlagClosedLoop","FlagInvertEncoderDirection","CorrectionGain","DeadBand",
                      "SlewRateCorrection","SlipTolerance","WriteRead","State"]
        encoderAttribute = DeviceAttributeDialog(self.devicePath, self.parent(), attributeFilter=attributes)
        encoderAttribute.exec_()

