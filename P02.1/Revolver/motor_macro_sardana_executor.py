"""
Gui that represent widget to enter and run macro.
This widget can contain three types of macro: motor, widget and time macro
"""
from PyQt4 import QtGui,  Qt
import logging
from taurus import Device
from Revolver.classes import devices, signals, config, widget_plot, input_widgets
from Revolver.UI import layout_sardana_motor_macro_executor 
from Revolver.gui_default_widget import DefaultWidget
from PyTango._PyTango import DevState
from guiqwt.styles import CurveParam
from guiqwt.curve import CurveItem
from guiqwt.builder import make
from taurus.qt.qtgui.container import TaurusMainWindow, TaurusWidget
from taurus.qt.qtgui.extra_macroexecutor import dooroutput
from taurus.core.util.codecs import CodecFactory
from taurus.core.tango.sardana.macroserver import CHANGE_EVT_TYPES
from time import sleep


def getHSVcolors(N):
        """
        Get color range from HSV color space defined by N
        @type N: int
        """
        return [(x * 360 / N, 230, 230) for x in range(N)]

class motorMacroExecutor(layout_sardana_motor_macro_executor.Ui_Form, DefaultWidget, TaurusWidget):
    
    """
    Macro step dialog, emit signal 
    """
    def __init__(self, motor, parent=None):
        """
        Class constructor
        @type parent: DefaultWidget
        @param motor: devices.Motor
        """
        super(motorMacroExecutor, self).__init__(parent)
        TaurusWidget.__init__(self, parent, False)
        #self.setupUi(self)
        self.parent = parent
        self.motorDevice = motor
        
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        """
        Initialize dialog variables
        """
        self._running_macros = None
        self.door = devices.TangoDevice(config.BL_DEFAULT_DOOR)
        self.qDoor = Device(config.BL_DEFAULT_DOOR)
        self.qDoor.getAttribute('MacroStatus').addListener(self.macroStatusReceived)
        
        #Qt.QObject.connect(self.qDoor, Qt.SIGNAL("macroStatusUpdated"), self.stepper)
        self.scan_plot = widget_plot.Curve_plot(edit=False, toolbar=True,
                                                wintitle="All image and plot tools test", parent=self,
                                                options={"title":"Scan graph", "xlabel":"Motor position", "ylabel":"Avg"})
        
    def __init_signals(self):
        """
        Initialize dialog signals
        """
        Qt.QObject.connect(self, Qt.SIGNAL("showScan"), self.actionShowScanGraph)
        self.connect(self, Qt.SIGNAL("repaintCurve"), self.scan_plot.action_set_curve_data)
        #Qt.QObject.connect(self.qDoor, Qt.SIGNAL("macroStatusUpdated"), self.macroStatusReceived)
        
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
        self.motorSelect = input_widgets.MotorSelect(alias)
        self.gridLayout.addWidget(self.motorSelect, 1,1)
        self.connect(self.motorSelect, Qt.SIGNAL("currentIndexChanged(QString)"), self.actioDefaultMotorChanged)
        self.actioDefaultMotorChanged(alias)
        self.stop_button.hide()
    
    def actioDefaultMotorChanged(self, motorAlias):
        self.motorDevice = devices.Motor(devices.getSubDevice(str(motorAlias)).keys()[0])
        self.motorAlias = motorAlias
        self.motorParent = Device(devices.getSubDevice(str(motorAlias)).values()[0])
        self.action_check_device_restrictions()
    
    def action_reset_values(self):
        logging.error("clear")
    
    def action_disable_controls(self):
        self.controls_group.setDisabled(True)
        self.scan_type.setDisabled(True)
        self.motorSelect.setDisabled(True)
        self.macro_integration_time.setDisabled(True)
        self.execute_button.hide()
        self.stop_button.show()
        
    def action_enable_controls(self):
        self.controls_group.setEnabled(True)
        self.scan_type.setEnabled(True)
        self.motorSelect.setEnabled(True)
        self.macro_integration_time.setEnabled(True)
        self.stop_button.hide()
        self.execute_button.show()
        
    def action_check_device_restrictions(self):
        currentIndex = self.controls_group.currentIndex() 
        if currentIndex == 0:
            attr = [self.StartStopNp_start_value, self.StartStopNp_stop_value]
        elif currentIndex == 1:
            return    
        
        self.parent.check_device_allowed_values(attr, self.motorDevice)
    
    def action_change_type(self, index):
        self.controls_group.setCurrentIndex(index)
        self.action_check_device_restrictions()
    
    def action_stop_macro(self):
        self.door.execute_command("StopMacro")
        
    def action_execute_macro(self):
        #logging.error(self.motorParent.getAttribute("Position"))
        self.motorStartPosition = self.motorDevice.current_value()
        self._running_macros = True
        self.emit(signals.SIG_DISABLE_CONTROLS)
        self.scan_plot.get_plot().del_all_items()
        self.scan_plot.get_plot().do_autoscale(True)
        self.scan_plot.show()
        
        currentIndex = self.controls_group.currentIndex() 
        if currentIndex == 0:
            self.door.execute_command("RunMacro",['ascan',
                                          str(self.motorSelect.currentText()),
                                          str(self.StartStopNp_start_value.value()),
                                          str(self.StartStopNp_stop_value.value()),
                                          str(self.StartStopNp_np_value.value()),
                                          str(self.macro_integration_time.value())
                                          ])
        elif currentIndex == 1:
            rangeStep = self.RangeNp_range_value.value()
            start = self.motorStartPosition - rangeStep/2
            end = self.motorStartPosition + rangeStep/2
            self.door.execute_command("RunMacro",['ascan',
                                          str(self.motorSelect.currentText()),
                                          str(start),
                                          str(end),
                                          str(self.RangeNp_np_value.value()),
                                          str(self.macro_integration_time.value())
                                          ])
        
    def actionShowScanGraph(self):
        self.scan_plot.show()
   
    def macroStatusReceived(self, s, t, v):
        if v is None or self._running_macros is None:
            return
        if t not in CHANGE_EVT_TYPES: return

        # make sure we get it as string since PyTango 7.1.4 returns a buffer
        # object and json.loads doesn't support buffer objects (only str)
        v = map(str, v.value)
        if not len(v[1]):
            return
        format = v[0]
        codec = CodecFactory().getCodec(format)

        # make sure we get it as string since PyTango 7.1.4 returns a buffer
        # object and json.loads doesn't support buffer objects (only str)
        v[1] = str(v[1])
        fmt, data = codec.decode(v)
        
        macro = data[0]
        if macro is None: return     
        
        data = data[0]
        state, range, step, id = data["state"], data["range"], data["step"], data["id"]
        if id is None: return
        id = int(id)
        
        if state == "stop" or state == "finish":
            self.scanStarted = False
            self.motorDevice.move(self.motorStartPosition)
            self.emit(signals.SIG_ENABLE_CONTROLS)
        elif state == "start":
            sleep(0.2)
            o = self.qDoor.read_attribute("Output")
            devices = o.value[0].split()[3:-1]
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
            o = self.qDoor.read_attribute("Output")
            values = o.value
            values = values[-1].split()[0:-1]
            values.pop(0)
            x = values.pop(0)
            for index, value in enumerate(values):
                self.scanOutput[index]["X"].append(float(x))
                self.scanOutput[index]["Y"].append(float(value))
                self.emit(Qt.SIGNAL("repaintCurve"), self.scanOutput[index]["curve"], self.scanOutput[index]["X"], self.scanOutput[index]["Y"])
   
        
    
