'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''
import logging
# import global classes 
import default_beamline_device as default_device
from UI import shutter
from Revolver.classes import devices, config, signals

class Beamline_shutter(shutter.Ui_Form, default_device.Beamline_device):
    
    STOP_BEAM_OFFSET = 1
    
    def __init__(self, parent=None, devicePath=config.DEVICE_SHUTTER):
        super(Beamline_shutter, self).__init__(parent)
        default_device.Beamline_device.__init__(self, devicePath=devicePath)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        self.device = self.shutter = devices.Shutter(self.devicePath)
    
    def __init_signals(self):
        pass
    
    def __main(self):
        pass
    
    def action_device(self, state):
        try:
            if state:
                self.shutter.close()
            else:
                self.shutter.open()
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Shutter error", "Shutter state could not be changed")
            return
        
        self._is_block_state_changed(state)
        
    def check_state(self):
        state = self.shutter.read_attribute("value").value
        if self.check_device_error(): return state
        if not(self._is_block_state_changed(state)): return state
        
        self.device_button.blockSignals(True)
        if state == 1:
            self.device_button.setChecked(True)
        elif state == 0:
            self.device_button.setChecked(False)
        self.device_button.blockSignals(False)
        
        return state
