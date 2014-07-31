'''
Created on Oct 3, 2013

@author: Martin Domaracky
'''

from PyQt4 import Qt
from PyQt4.QtGui import QApplication,QInputDialog
import signal
from threading import Thread
from time import sleep
import logging
import sys
from taurus.qt.qtgui.extra_sardana import ExpDescriptionEditor

# import global classes 
from Revolver.classes import threads, signals, config
from Revolver.macro import taurus_sequencer
from Revolver import gui_default_widget
from UI import beamline_default

DEFAULT_MODE = 0
EXPERT_MODE = 1

class Beamline(beamline_default.Ui_Form, gui_default_widget.DefaultWidget):
    
    EXPERT_MODE_PIN = str(2501)
    BEAM_HEIGHT = 7 
    BEAM_TOP_OFFSET = 3
    BEAMLINE_TITLE = "Default beamline"
    DEVICE_POLLING_TIME = 0.5
    _STOP_POLLING_DEVICES = False
    
    def __init__(self, parent=None):
        super(Beamline, self).__init__(parent)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_variables(self):
        self.beam = Qt.QWidget()
        self.controls = []
        self.setup = []
        self.lastSelectedDevice = None
        self.previousMode = DEFAULT_MODE
        self.currentMode = DEFAULT_MODE
        self.currentControlsId = None
        self.mgrpEditor = ExpDescriptionEditor(door=config.BL_DEFAULT_DOOR)
        self.macroExecutor = taurus_sequencer.TaurusSequencer(doorName=config.BL_DEFAULT_DOOR)
        self.macroExecutor.set_kill_all_permissions(False)
    
    def __init_signals(self):
        self.connect(self, signals.SIG_CHECK_BEAM, self.action_check_beam)
    
    def __main(self):
        self.beam.setStyleSheet("background:red;")
        self.bemaline_setup.addChildWidget(self.beam)
        self.beam.lower()
        thread = Thread(target=self._device_polling_routine, args=())
        threads.add_thread(thread, self.widget_id)
        thread.start()
    
    def _device_polling_routine(self):
        """
        Poll all devices for current state
        """
        while not self._STOP_POLLING_DEVICES and threads.THREAD_KEEP_ALIVE:
            for setupItem in self.setup:
                setupItem.check_state()
            sleep(self.DEVICE_POLLING_TIME)
    
    def resizeEvent(self, *args, **kwargs):
        """
        Override resize event, emit signal that beam should change it's position in current beamline widget
        """
        self.emit(signals.SIG_CHECK_BEAM)
        return gui_default_widget.DefaultWidget.resizeEvent(self, *args, **kwargs)
    
    def action_check_beam(self):
        """
        This method checks if the beam is blocked or not and calculates it's position
        according to current setup.
        """
        try:
            (x, y, width, height) = self.bemaline_setup.geometry().getRect()
            (leftMargin, topMargin, rightMargin, bottomMargin) = self.bemaline_setup.getContentsMargins()
            self.beam.setGeometry(x, y + (height / 2) - topMargin - self.BEAM_TOP_OFFSET, width, self.BEAM_HEIGHT)
            
            for device in reversed(self.setup):
                if device.is_beam_blocked():
                    (dx, dy, dwidth, dheight) = device.geometry().getRect()
                    ndx = dx + (dwidth / 2) - device.STOP_BEAM_OFFSET
                    ndy = y + (height / 2)
                    ndwidth = width - ndx + x
                    ndheight = self.BEAM_HEIGHT
                    self.beam.setGeometry(ndx, ndy - topMargin - self.BEAM_TOP_OFFSET, ndwidth, ndheight)
                    break
        except:
            logging.error("Error", self.get_exception())
        
    def change_background(self, color):
        """
        Change background of current controls
        @type color: String
        """
        self.controls_frame.setStyleSheet("#controls_frame{background-color:rgba("+color+",100%);}")
    
    def action_open_sardana_macro(self):
        self.macroExecutor.show()
    
    def action_open_mgrp_editor(self):
        self.mgrpEditor.show()
    
    def action_controls_changed(self, controls_id):
        """
        Invoke this method when controls was changed
        @type controls_id: int
        """
        currentControls = self.controls[controls_id]
        
        if self.currentControlsId:
            self.controls[self.currentControlsId]["widget"].action_before_hide()            
        
        currentControls["widget"].action_before_shown()
        self.currentControlsId = controls_id
          
        if not currentControls.has_key("background"):
            self.change_background("210,226,237")
        else:
            newBg = currentControls["background"]
            self.change_background(newBg)
            
        if self.lastSelectedDevice:
            self.lastSelectedDevice.set_highlight(False)
        currentControls["device"].set_highlight(True)
        self.lastSelectedDevice = currentControls["device"]
    
    def set_current_controls(self, index):
        if self.beamline_device_controls.tabBar().isTabEnabled(index):
            self.beamline_device_controls.setCurrentIndex(index)
    
    def action_set_controls_enabled(self, controlsIndex, flag):
        self.beamline_device_controls.tabBar().setTabEnabled(controlsIndex,flag)
        
    def action_set_expert_mode(self, flag):
        """
        Set expert mode
        @type flag: bool
        """
        if flag:
            editPassword = Qt.QLineEdit(self)
            editPassword.setEchoMode(Qt.QLineEdit.Password)
            pin, ok = QInputDialog.getText(self, "Expert mode verification",
                                          "Please enter expert mode pin:", Qt.QLineEdit.Password,
                                          "");
            if ok:
                if pin == self.EXPERT_MODE_PIN:
                    self.previousMode = self.currentMode 
                    self.currentMode = EXPERT_MODE
                else:
                    self.button_expert_mode.setChecked(False)
                    self.emit(signals.SIG_SHOW_WARNING, "Export mode", "Wrong pin entered !")
                    return False
            else:
                self.button_expert_mode.setChecked(False)
                return False
        else:
            self.currentMode = self.previousMode
        return True
            
# MAIN PROGRAM #################################################################################
from taurus.qt.qtgui.application import TaurusApplication
if __name__ == '__main__':
    
    # create main window
    app = TaurusApplication(sys.argv)
    
    # init widget
    widget = Beamline()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
    
