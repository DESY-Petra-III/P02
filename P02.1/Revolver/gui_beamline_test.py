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

class Beamline_test(default_beamline.Beamline):
    
    # window title for current beamline
    BEAMLINE_TITLE = "Beamline P02"
    
    def __init__(self, parent=None):
        """
        Class constructor
        @type parent: DefaultWidget
        """
        super(Beamline_test, self).__init__(parent)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        """
        Initialize all variables
        Specify beamline setup and controllers
        """

        # define beamline devices
        self.slits1 = device_slits.Beamline_slits()
        self.slits2 = device_slits.Beamline_slits()
        self.beamX = beam.Beamline_beam()
        
        # put specified devices in beamline setup, they will appear left to right
        self.setup = [self.slits1, self.slits2,self.beamX]
        
        # define slits 1 controls
        s1_left = devices.Motor(config.DEVICE_SERVER + "p02/motor/exp.01")
        s2_left = devices.Motor(config.DEVICE_SERVER + "p02/motor/exp.02")
        
        self.slits1Motors = [
                        s1_left]
        self.slits1Controls = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=self.slits1Motors, title="Slits 1 motors")
        
        self.slits1Motors2 = [
                        s2_left]
        self.slits1Controls2 = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=self.slits1Motors2, title="Slits 2 motors")
        
        # define beam controls
        petraParams = [{"devicePath":config.DEVICE_SERVER_P02+"petra/globals/keyword", "value":"BeamCurrent", "description":"Petra current"}]
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
        self.controls = [
                        {"device":self.slits1, "widget":self.slits1Controls, "tabname":"Slits 1", "background":"237,219,133"},
                        {"device":self.slits2, "widget":self.slits1Controls2, "tabname":"Slits 2", "background":"207,219,133"},
                        {"device":self.beamX, "widget":self.petraStatus, "tabname":"Petra current", "background":"244,180,180"}
                         ]
        
    def __init_signals(self):
        """
        Initialize all signals
        connect signals.SIG_BLOCK_BEAM handler to every device widget
        if device blocked the beam action_check_beam routine will be called
        """
        for device in self.setup:
            self.connect(device, signals.SIG_BLOCK_BEAM, self.action_check_beam)
            device.set_beamline(self)
    
    def __main(self):
        """
        Set beamline properties
        Initialze beamline title, set beamline setup and controllers
        """
        self.setWindowTitle(self.BEAMLINE_TITLE)
        
        self.petraStatus.action_start_plot()
        
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
                      
        # emit signal that current beamline changed its mode successfully       
        self.emit(signals.SIG_CHANGE_MODE, self.currentMode)
        
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QApplication(sys.argv)
    
    # init widget
    widget = Beamline_test()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
    