from PyQt4 import Qt
from PyTango import DeviceProxy, Database
import logging

class MotorSelect(Qt.QComboBox):
    
    def __init__(self, defaultMotor, *args, **kwargs):
        Qt.QComboBox.__init__(self, *args, **kwargs)
        self.defaultMotor = defaultMotor
        self.__populateSardanaMotors()
        self.setStyleSheet("combobox-popup: 0;");
        self.setMaxVisibleItems(15)
        
    def __populateSardanaMotors(self):
        exportedDevices = dict()
        db = Database()
        eDevices = db.get_device_alias_list("*mot*")
        self.addItems(eDevices)
        self.setCurrentIndex(self.findText(self.defaultMotor))
        
        