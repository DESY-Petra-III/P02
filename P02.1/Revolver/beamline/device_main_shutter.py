'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''

from PyQt4 import QtCore
from PyQt4.Qt import QCursor

# import global classes 
import default_beamline_device as default_device
from UI import shutter
from Revolver.classes import devices, config, signals

class Beamline_shutter(shutter.Ui_Form, default_device.Beamline_device):
    
    STOP_BEAM_OFFSET = 1
    
    def __init__(self, parent=None, devicePath=config.DEVICE_SHUTTER_MAIN):
        super(Beamline_shutter, self).__init__(parent)
        default_device.Beamline_device.__init__(self, devicePath=devicePath)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        self.device = self.shutter = devices.MainShutter(self.devicePath)
        
    def __init_signals(self):
        pass
    
    def __main(self):
        self.device_button.setCheckable(False)
        self.onImage = ":/devices/icons/shutter_open.png"
        self.offImage = ":/devices/icons/shutter_closed.png"
        self.device_button.setCursor(QCursor(QtCore.Qt.ArrowCursor))
                
    def check_state(self):
        try:
            state = self.shutter.is_open()
        except:
            state = False
        if self.check_device_error(): return state
            
        if not(self._is_block_state_changed(not(state))): return state
        self.device_button.blockSignals(True)
        if state:
            self.emit(signals.SIG_BUTTON_CHANGE_ICON, self.onImage)
        else:
            self.emit(signals.SIG_BUTTON_CHANGE_ICON, self.offImage)
        self.device_button.blockSignals(False)
        return state
        
    
