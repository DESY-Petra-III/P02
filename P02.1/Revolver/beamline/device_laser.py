'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''

# import global classes 
import default_beamline_device as default_device
from UI import laser
from Revolver.classes import devices, signals

class Beamline_laser(laser.Ui_Form, default_device.Beamline_device):
    
    STOP_BEAM_OFFSET = -25
    
    def __init__(self, parent=None, devicePath=None):
        super(Beamline_laser, self).__init__(parent)
        default_device.Beamline_device.__init__(self, devicePath=devicePath)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        self.device = self.laser = devices.Laser(self.devicePath)
    
    def __init_signals(self):
        pass
    
    def __main(self):
        pass
    
    def action_device(self, state):
        try:
            if state:
                self.laser.put_in()
            else:
                self.laser.put_out()
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Device error", "Laser state could not be changed")
            return
        
        self._is_block_state_changed(state)
        
    def check_state(self):
        state = self.laser.read_attribute("Valve6").value
        if self.check_device_error(): return state
        if not(self._is_block_state_changed(not(state))): return state
        
        self.device_button.blockSignals(True)
        if state == 0:
            self.device_button.setChecked(True)
        elif state == 1:
            self.device_button.setChecked(False)
        self.device_button.blockSignals(False)
        
        return state
    
