#! /usr/bin/python2.6
'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''
from PyQt4.QtGui import QApplication
import sys
import signal

# import global classes 
from Revolver.classes import config, devices, signals
from beamline import (default_beamline, device_diode, device_shutter, device_ionchamber, device_pinhole,
                      device_absorber, device_detectorPE, device_samplestage, device_laser, wall, beam, device_slits,
                      device_beamstop)
import gui_detector_controls_widget
import gui_stacked_motors_controls_widget, gui_device_value_graph_controls_widget
import gui_P02_stage_controls_widget
from beamline import device_main_shutter
from Revolver import gui_absorber_controls_widget

"""
concat P02_DEVICES with DEVICE_SERVER_P02, produces 
real tango server paths to devices.
config.DEVICE_SERVER_P02 + config.DEVICE_NAME = "tango://server_path/device_path"
"""
P02_DEVICES = dict((x, config.DEVICE_SERVER_P02 + y) for x, y in config.DEVICE_NAMES.iteritems())

class Beamline_P02(default_beamline.Beamline):
    
    # window title for current beamline
    BEAMLINE_TITLE = "Beamline P02.1"
    
    def __init__(self, parent=None):
        """
        Class constructor
        @type parent: DefaultWidget
        """
        super(Beamline_P02, self).__init__(parent)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        """
        Initialize all variables
        Specify beamline setup and controllers
        """

        # define beamline devices
        self.mainShutter = device_main_shutter.Beamline_shutter(devicePath=P02_DEVICES["MAIN_SHUTTER"])
        self.smallShutter = device_shutter.Beamline_shutter(devicePath=P02_DEVICES["SMALL_SHUTTER"])
        self.diode = device_diode.Beamline_diode(devicePath=P02_DEVICES["DIODE"])
        self.pinhole = device_pinhole.Beamline_pinhole()
        self.pinhole2 = device_pinhole.Beamline_pinhole()
        self.ionchamber = device_ionchamber.Beamline_ionchamber()
        self.diodeADC = device_diode.Beamline_diode(devicePath=P02_DEVICES["DIODE"])
        self.absorber = device_absorber.Beamline_absorber(devicePath=P02_DEVICES["ABSORBER"])
        self.detectorPE = device_detectorPE.Beamline_detectorPE()
        self.samplestage = device_samplestage.Beamline_samplestage()
        self.laser = device_laser.Beamline_laser(devicePath=P02_DEVICES["LASER"])
        self.slits1 = device_slits.Beamline_slits()
        self.slits2 = device_slits.Beamline_slits()
        self.wall = wall.Beamline_wall()
        self.beamX = beam.Beamline_beam()
        self.beamstop = device_beamstop.Beamline_beamstop()
        
        # put specified devices in beamline setup, they will appear left to right
        self.setup = [self.detectorPE, self.beamstop, self.diode, self.diodeADC, self.samplestage,
                      self.pinhole2, self.pinhole, self.slits2, self.absorber, self.laser,
                      self.smallShutter, self.slits1, self.ionchamber,
                      self.wall, self.mainShutter, self.beamX]
        
        # define PE Detector controls
        detector = devices.Detector(P02_DEVICES["PE_DETECTOR"])
        SDD = devices.VirtualMotorSum2D([devices.Motor(P02_DEVICES["PEX_LARGE"]), devices.Motor(P02_DEVICES["PEX"])], "SDD")
        
        detectorMotors = [P02_DEVICES["PEX_LARGE"],
                       P02_DEVICES["PEX"],
                       P02_DEVICES["PEY"]]
        self.detectorControls = gui_detector_controls_widget.DetectorControlsWithAttributes(detectorDevice=detector, sddMotor=SDD, motorPaths=detectorMotors, parent=self)
        SDD.addToPosition = lambda: float(self.detectorControls.offset_input.value())
        self.detectorControls.set_attributes(r=1024, lambdav=0.206, offset=1500, psize=0.2, e=60)
        
        # define beamstop controls
        self.beamstopMotors = [P02_DEVICES["BSTY"],
                       P02_DEVICES["BSTZ"]]
        self.beamstopControls = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=self.beamstopMotors, title="Beamstop motors")
        
        # define absorber controls
        self.absorberControls = gui_absorber_controls_widget.Controls(parent=self, devicePath=P02_DEVICES["ABSORBER"])
        
        # define stage controls
        self.stageControls = gui_P02_stage_controls_widget.controls(parent=self)
        
        # define pinhole 1 controls
        pinhole1Motors = [P02_DEVICES["PH1Y"],
                       P02_DEVICES["PH1Z"]]
        self.pinhole1Controls = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=pinhole1Motors, title="Pinhole 1 motors")
        
        # define pinhole 2 controls
        pinhole2Motors = [P02_DEVICES["PH2Y"],
                       P02_DEVICES["PH2Z"]]
        self.pinhole2Controls = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=pinhole2Motors, title="Pinhole 2 motors")
        
        # define slits 1 controls
        s1_left = devices.Motor(P02_DEVICES["S1_LEFT"])
        s1_right = devices.Motor(P02_DEVICES["S1_RIGHT"])
        s1_top = devices.Motor(P02_DEVICES["S1_TOP"])
        s1_bottom = devices.Motor(P02_DEVICES["S1_BOTTOM"])
        s1_Cx = devices.VirtualMotorCenter2D([s1_left, s1_right], "S1_CX")
        s1_Cy = devices.VirtualMotorCenter2D([s1_top, s1_bottom], "S1_CY")
        s1_Dx = devices.VirtualMotorDistance2D([s1_left, s1_right], "S1_DX")
        s1_Dy = devices.VirtualMotorDistance2D([s1_top, s1_bottom], "S1_DY")
        self.slits1Motors = [s1_Dx, s1_Dy,
                        s1_Cx, s1_Cy,
                        s1_left, s1_right,
                       s1_top, s1_bottom]
        self.slits1Controls = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=self.slits1Motors, title="Slits 1 motors")
        
        # define slits 2 controls
        s2_left = devices.Motor(P02_DEVICES["S2_LEFT"])
        s2_right = devices.Motor(P02_DEVICES["S2_RIGHT"])
        s2_top = devices.Motor(P02_DEVICES["S2_TOP"])
        s2_bottom = devices.Motor(P02_DEVICES["S2_BOTTOM"])
        s2_Cx = devices.VirtualMotorCenter2D([s2_left, s2_right], "S2_CX")
        s2_Cy = devices.VirtualMotorCenter2D([s2_top, s2_bottom], "S2_CY")
        s2_Dx = devices.VirtualMotorDistance2D([s2_left, s2_right], "S2_DX")
        s2_Dy = devices.VirtualMotorDistance2D([s2_top, s2_bottom], "S2_DY")
        self.slits2Motors = [s2_Dx, s2_Dy,
                            s2_Cx, s2_Cy,
                            s2_left, s2_right,
                            s2_top, s2_bottom]
        self.slits2Controls = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=self.slits2Motors, title="Slits 2 motors")
        
        # define diode controls
        diode = devices.Diode(P02_DEVICES["DIODE"])
        diode.start_profiling()
        diodeParams = [{"device":diode, "value":"current", "description":"Diode current [VFC]", "source": diode.output}]
        graphOptions = {"title":"Diode value", "xlabel":"Time", "ylabel":"Status"}
        self.diodeControls = gui_device_value_graph_controls_widget.Controls(parent=self, title="Diode status", deviceParams=diodeParams, graphOptions=graphOptions)
        
        # define ionchamber controls
        ionChamberParams = [{"devicePath":P02_DEVICES["IONCHAMBER"], "value":"Value", "description":"Ion chamber value"}]
        graphOptions = {"title":"Ion chamber status", "xlabel":"Time", "ylabel":"Status"}
        self.ionChamberControls = gui_device_value_graph_controls_widget.Controls(parent=self, title="Ion chamber status", deviceParams=ionChamberParams, graphOptions=graphOptions)
        
        # define ionchamber controls
        diodeADC = [{"devicePath":P02_DEVICES["DIODE_ADC"], "value":"Value", "description":"Diode current [ADC]"}]
        graphOptions = {"title":"Diode [ADC]", "xlabel":"Time", "ylabel":"Status"}
        self.diodeADCControls = gui_device_value_graph_controls_widget.Controls(parent=self, title="Ion chamber status", deviceParams=diodeADC, graphOptions=graphOptions)
        
        
        # define beam controls
        petraParams = [{"devicePath":P02_DEVICES["PETRA_CURRENT"], "value":"BeamCurrent", "description":"Petra current"}]
        graphOptions = {"title":"Petra current", "xlabel":"Time", "ylabel":"Current"}
        self.petraStatus = gui_device_value_graph_controls_widget.Controls(parent=self, title="Petra status", deviceParams=petraParams, graphOptions=graphOptions)

        """ 
        define controls, that will appear in controls widget
        {
            (required)
                "device": defined beamline device widget (default_beamline_device.Beamline_device object)
                "widget": defined controls widget
                "tabname": name of the controls
            (optional)
                 "background": color of the controls background (r,g,b)
        }
        """
        self.controls = [{"device":self.detectorPE, "widget":self.detectorControls, "tabname":"Detector stage", "background":"186,224,155"},
                         {"device":self.beamstop, "widget":self.beamstopControls, "tabname":"Beamstop", "background":"155,224,176"},
                         {"device":self.diode, "widget":self.diodeControls, "tabname":"Diode [VFC]", "background":"155,224,223"},
                         {"device":self.diodeADC, "widget":self.diodeADCControls, "tabname":"Diode [ADC]", "background":"155,224,223"},
                         {"device":self.samplestage, "widget":self.stageControls, "tabname":"Sample stage", "background":"133,133,237"},
                         {"device":self.pinhole2, "widget":self.pinhole2Controls, "tabname":"Pinhole 2", "background":"237,187,133"},
                         {"device":self.pinhole, "widget":self.pinhole1Controls, "tabname":"Pinhole 1", "background":"237,187,133"},
                         {"device":self.slits2, "widget":self.slits2Controls, "tabname":"Slits 2", "background":"237,219,133"},
                         {"device":self.absorber, "widget":self.absorberControls, "tabname":"Absorber", "background":"171,155,224"},
                         {"device":self.slits1, "widget":self.slits1Controls, "tabname":"Slits 1", "background":"237,219,133"},
                         {"device":self.ionchamber, "widget":self.ionChamberControls, "tabname":"Ion chamber", "background":"133,133,237"},
                         {"device":self.beamX, "widget":self.petraStatus, "tabname":"Petra current", "background":"244,180,180"}]
        
    def __init_signals(self):
        """
        Initialize all signals
        connect signals.SIG_BLOCK_BEAM handler to every device widget
        if device blocked the beam action_check_beam routine will be called
        """
        for device in self.setup:
            self.connect(device, signals.SIG_BLOCK_BEAM, self.action_check_beam)
            self.connect(device, signals.SIG_ENABLE_CONTROLS_INDEX, self.action_set_controls_enabled)
            device.set_beamline(self)
    
    def __main(self):
        """
        Set beamline properties
        Initialze beamline title, set beamline setup and controllers
        """
        self.setWindowTitle(self.BEAMLINE_TITLE)
        
        self.petraStatus.action_start_plot()
        self.ionChamberControls.action_start_plot()
        self.diodeControls.action_start_plot()
        self.diodeADCControls.action_start_plot()
                
        for device in self.setup:
            self.bemaline_setup.addWidget(device)
        
        for controls in self.controls:
            index = self.beamline_device_controls.addTab(controls["widget"], controls["tabname"])
            controls["device"].set_controls_index(index)
            if controls.has_key("background"):
                controls["device"].set_highlight_color(controls["background"])
            self.connect(controls["device"], signals.SIG_SHOW_BEAMLINE_DEVICE_CONTROLS, self.set_current_controls)
        self.beamline_device_controls.setCurrentIndex(index)
        self.action_set_expert_mode(False)
      
    def action_set_expert_mode(self, flag):
        """
        Set expert mode for beamline P02
        First invoke default_beamline method: default_beamline.Beamline.action_set_expert_mode(self, flag)
        If return value from this function is True, than expert mode could be changed (user entered correct pin, clicked OK)
        Than proceed with expert mode settings for current beamline
        """
        if not default_beamline.Beamline.action_set_expert_mode(self, flag): return
        
        # define expert modes motors
        slits1_expert_mode = self.slits1Motors[2:]
        slits2_expert_mode = self.slits2Motors[2:]
        
        # enable / disable tab index from the beamline controllers tab
        self.action_set_controls_enabled(1, flag)
        
        # disable / enable expert mode motors depending on flag state (True / False)
        for hideMotor in slits1_expert_mode:
                self.slits1Controls.set_motor_controls_enabled(hideMotor.devicePath, flag)
        for hideMotor in slits2_expert_mode:
                self.slits2Controls.set_motor_controls_enabled(hideMotor.devicePath, flag)
        
        # emit signal that current beamline changed its mode successfully       
        self.emit(signals.SIG_CHANGE_MODE, self.currentMode)
        
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    from taurus.qt.qtgui.application import TaurusApplication
    # create main window
    app = TaurusApplication(sys.argv)
    
    # init widget
    widget = Beamline_P02()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
    
