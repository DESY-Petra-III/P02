'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''
from PyQt4.QtGui import QIcon, QWidget
import logging

# import global classes 
from Revolver import gui_default_widget
from Revolver.classes import signals

class Beamline_device(gui_default_widget.DefaultWidget):
    """
    Default beamline device.
    Set this widget as super class for derived beamline devices
    """
    
    # offset in pixels from current middle of device button
    STOP_BEAM_OFFSET = 10
    
    def __init__(self, parent=None, devicePath=None):
        """
        Class constructor
        @type parent: DefaultWidget
        @type devicePath: String
        """
        super(Beamline_device, self).__init__(parent)
        self.devicePath = devicePath
        self.deviceError = False
        self.device = None
        
        self.controlIndex = -1
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        """
        Initialize all variables
        Specify if devices has rights to block beam and set _beamBlocked flag to false
        """
        self.allowBlockBeam = True
        self._beamBlocked = None
        self.highlighter = QWidget()
        self.highlightColor = "210,226,237"
        self.beamlineControls = None
    
    def __init_signals(self):
        """
        Initialize all signals
        Connect SIG_BUTTON_CHANGE_ICON to function, that will change its icon
        Specify icon path as a parameter
        """
        self.connect(self, signals.SIG_BUTTON_CHANGE_ICON, lambda path:self.device_button.setIcon(QIcon(path)))
        self.connect(self, signals.SIG_DEVICE_STATUS_OK, self.set_device_ok)
        self.connect(self, signals.SIG_DEVICE_STATUS_ERROR, self.set_device_error)
    
    def __main(self):
        """
        Set beamline device properties
        """
        self.highlighter.setAutoFillBackground(True)
        self.highlighter.setStyleSheet("background-color: rgba(210,226,237, 50%);")
        self.layout().addChildWidget(self.highlighter)
        self.highlighter.lower()
        self.highlighter.lower()
        self.highlighter.hide()
    
    def _is_block_state_changed(self, newBlockState):
        """
        Check if beam block state of the device was changed 
        @type newBlockState: bool
        """
        if self._beamBlocked != newBlockState:
            if self.allowBlockBeam:
                self.action_block_beam(newBlockState)
            return True
    
    def set_highlight_color(self, color, saveColor=True):
        if saveColor: self.highlightColor = color
        self.highlighter.setStyleSheet("background-color: rgba("+color+",50%)")
    
    def set_controls_index(self, index=0):
        """
        Set controls for current device. 
        Index represent which controls should be selected from beamline controls setup.
        @type index: int
        """
        self.controlIndex = index
    
    def is_beam_blocked(self):
        """
        Check if current device is blocking beam
        @rtype: bool
        """
        if self._beamBlocked: return True
        else: return False
    
    def set_highlight(self, flag):
        """
        Highlight device
        @type flag: bool
        """
        if flag:
            self.highlighter.show()
        else:
            if not self.deviceError:
                self.highlighter.hide()
        pass
    
    def action_block_beam(self, state):
        """
        Set blocking state
        @type state: bool
        """
        self._beamBlocked = state
        self.emit(signals.SIG_BLOCK_BEAM, state)
        
    def action_device(self, state=None):
        """
        Default device action onclick
        """
        self.emit(signals.SIG_SHOW_BEAMLINE_DEVICE_CONTROLS, self.controlIndex)
    
    def check_state(self):
        """
        Override this function.
        This routine should check device state.
        """
        pass
    
    def check_device_error(self):
        if self.device.deviceError and not self.deviceError: 
            self.emit(signals.SIG_DEVICE_STATUS_ERROR)
            self.deviceError = True
            return True
        elif not self.device.deviceError and self.deviceError:
            self.deviceError = False
            self.emit(signals.SIG_DEVICE_STATUS_OK)
            self.emit(signals.SIG_ENABLE_CONTROLS_INDEX, self.controlIndex,True)
            return False
        elif self.device.deviceError:
            if self.controlIndex != -1:
                self.emit(signals.SIG_ENABLE_CONTROLS_INDEX, self.controlIndex,False)
            return True
        else:
            return False
    
    def set_device_error(self):
        self.device_button.blockSignals(True)
        self.device_button.setDisabled(True)
        self.set_highlight_color("255,0,0", False)
        self.set_highlight(True)
    
    def set_device_ok(self):
        self.device_button.blockSignals(False)
        self.device_button.setDisabled(False)
        self.set_highlight_color(self.highlightColor, False)
        self.set_highlight(False)
    
    def set_beamline(self, beamline):
        self.beamline = beamline