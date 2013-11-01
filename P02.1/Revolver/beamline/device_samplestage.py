'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''

# import global classes 
import default_beamline_device as default_device
from UI import samplestage
from Revolver.classes import signals

class Beamline_samplestage(samplestage.Ui_Form, default_device.Beamline_device):
    
    STOP_BEAM_OFFSET = 1
    
    def __init__(self, parent=None):
        super(Beamline_samplestage, self).__init__(parent)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        self._beamBlocked = False
    
    def __init_signals(self):
        pass
    
    def __main(self):
        pass
    
    def action_device(self, state):
        self.emit(signals.SIG_SHOW_BEAMLINE_DEVICE_CONTROLS, self.controlIndex)
    
