"""
Gui that represent widget to enter and run macro.
This widget can contain three types of macro: motor, widget and time macro
"""
from PyQt4 import QtGui,  Qt
import logging
from taurus import Device
from Revolver.classes import devices, signals, config, widget_plot
from Revolver.macro.UI import taurus_sequencer
from Revolver.gui_default_widget import DefaultWidget
from PyTango._PyTango import DevState
from guiqwt.styles import CurveParam
from guiqwt.curve import CurveItem
from guiqwt.builder import make

def getHSVcolors(N):
        """
        Get color range from HSV color space defined by N
        @type N: int
        """
        return [(x * 360 / N, 230, 230) for x in range(N)]

class TaurusSequencer(taurus_sequencer.Ui_Form, DefaultWidget, QtGui.QApplication):
    
    def __init__(self, parent=None, doorName=None):
        super(TaurusSequencer, self).__init__(self)
        self.doorName = doorName
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_signals(self):
        Qt.QObject.connect(self.taurusSequencerWidget, Qt.SIGNAL("doorChanged"), self.taurusSequencerWidget.onDoorChanged)
        Qt.QObject.connect(self.qDoor, Qt.SIGNAL("macroStatusUpdated"), self.taurusSequencerWidget.onMacroStatusUpdated)
        Qt.QObject.connect(self, Qt.SIGNAL("showScan"), self.actionShowScanGraph)
        self.connect(self, Qt.SIGNAL("repaintCurve"), self.scan_plot.action_set_curve_data)
        Qt.QObject.connect(self.qDoor, Qt.SIGNAL("macroStatusUpdated"), self.stepper)
        Qt.QObject.connect(self.taurusSequencerWidget, Qt.SIGNAL("doorChanged"), self.onDoorChanged)
        self.connect(self.taurusSequencerWidget.playSequenceAction, Qt.SIGNAL("triggered()"), self.action_macroStart)
            
    def __init_variables(self):
        
        #pd.get_object
        self.scanStarted = False
        self.logSubscribed = False
        self.scanOutput = []
        self.qDoor = Device(self.doorName)
        self.scan_plot = widget_plot.Curve_plot(edit=False, toolbar=True,
                                                wintitle="All image and plot tools test", parent=self,
                                                options={"title":"Scan graph", "xlabel":"Motor position", "ylabel":"Avg"})
        
    def __main(self):
        self.mainDoor = devices.TangoDevice(self.doorName)
        self.taurusSequencerWidget.setModel("tango://has6117b:10000/p02/macroserver/has6117b")
        self.taurusSequencerWidget.emit(Qt.SIGNAL('doorChanged'),self.doorName)
        self.graph_layout.addWidget(self.scan_plot)
    
    def onDoorChanged(self):
        pass
    
    def actionShowScanGraph(self):
        self.scan_plot.show()
   
    def action_macroStart(self):
        self.scan_plot.get_plot().del_all_items()
        self.scan_plot.get_plot().do_autoscale(True)   
    
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
                super(TaurusSequencer, self).__init__(self)
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
                       
    
if __name__ == "__main__":
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.container import TaurusWidget
    from taurus.qt.qtgui.extra_macroexecutor import TaurusSequencerWidget
    import sys
    
    app = TaurusApplication(sys.argv)
    widget = TaurusSequencer(doorName=config.BL_DEFAULT_DOOR)
    
    widget.show()
    sys.exit(app.exec_())