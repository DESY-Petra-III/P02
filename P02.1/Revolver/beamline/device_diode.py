'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''

# import global classes 
from Revolver.classes import devices, signals
import default_beamline_device as default_device
from UI import diode

class Beamline_diode(diode.Ui_Form, default_device.Beamline_device):
    
    STOP_BEAM_OFFSET = 10
    
    def __init__(self, parent=None, devicePath=None):
        super(Beamline_diode, self).__init__(parent)
        default_device.Beamline_device.__init__(self, devicePath=devicePath)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        self.device = self.diode = devices.Diode(self.devicePath)
    
    def __init_signals(self):
        pass
    
    def __main(self):
        pass
    
    def action_device(self, state):
        try:
            if state:
                self.diode.put_in()
            else:
                self.diode.put_out()
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Device error", "Diode state could not be changed")
            return
        
        self._is_block_state_changed(state)
        self.emit(signals.SIG_SHOW_BEAMLINE_DEVICE_CONTROLS, self.controlIndex)
        
    def check_state(self):
        state = self.diode.read_attribute("Valve1").value
        if self.check_device_error(): return state
        if not(self._is_block_state_changed(state)): return state
        
        self.device_button.blockSignals(True)
        if state == 0:
            self.device_button.setChecked(False)
        elif state == 1:
            self.device_button.setChecked(True)
        self.device_button.blockSignals(False)
    
