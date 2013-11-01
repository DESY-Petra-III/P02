'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''
# import global classes 
import default_beamline_device
from UI import wall

class Beamline_wall(wall.Ui_Form, default_beamline_device.Beamline_device):
    
    STOP_BEAM_OFFSET = 10
    
    def __init__(self, parent=None):
        super(Beamline_wall, self).__init__(parent)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        pass
    
    def __init_signals(self):
        pass
    
    def __main(self):
        pass
    
    def action_device(self, state):
        pass
