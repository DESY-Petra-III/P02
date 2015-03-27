'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''

# import global classes 
import default_beamline_device as default_device
from UI import absorber
from Revolver.classes import devices, signals

class Beamline_absorber(absorber.Ui_Form, default_device.Beamline_device):
    
    STOP_BEAM_OFFSET = 1
    
    def __init__(self, parent=None, devicePath=None):
        super(Beamline_absorber, self).__init__(parent, devicePath=devicePath)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        self.allowBlockBeam = False
        self.device = self.absorber = devices.Absorber(self.devicePath)
    
    def __init_signals(self):
        pass
    
    def __main(self):
        self.state = self.absorber.get_value()
        self.device_button.setCheckable(False)
        self.onImage = ":/devices/icons/sps_closed.png"
        self.offImage = ":/devices/icons/sps_open.png"
    
    def check_state(self):
        state = self.absorber.get_value()
        if self.check_device_error(): return state
        
        if not(self._is_block_state_changed(state)): return state
        
        self.device_button.blockSignals(True)
        if state >= 1:
            self.emit(signals.SIG_BUTTON_CHANGE_ICON, self.onImage)
            # self.device_button.setChecked(True)
        elif state == 0:
            self.emit(signals.SIG_BUTTON_CHANGE_ICON, self.offImage)
            # self.device_button.setChecked(False)
        self.device_button.blockSignals(False)
        
        return state

