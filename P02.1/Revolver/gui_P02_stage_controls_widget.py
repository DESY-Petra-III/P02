"""
Motor widget.
Populate motor position to user, which can be changed.
User can also stop all movements of selected motor.
Motor status is signalized by diode.
"""

# import global classes 
from PyQt4 import QtGui
import sys
import signal
 
# Import local classes
from Revolver.classes import config, signals
import gui_default_controls_widget as default_gui
import gui_stacked_motors_controls_widget
from Revolver.UI import layout_P02_stage_controls
from Revolver.beamline import default_beamline

class controls(layout_P02_stage_controls.Ui_Form, default_gui.DefaultControls):
    
    def __init__(self, parent=None):
        super(controls, self).__init__()
        default_gui.DefaultControls.__init__(self, parent=parent)
        self.__init_variables()
        self.__init_signals()
        self.__main()

    def __init_variables(self):
        # gonio_motors = ["p02/motor/exp.04", "p02/motor/exp.04", "p02/motor/exp.04", "p02/motor/exp.04"]
        self.gonio_motors = [config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["SAMX"],
                        config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["SAMY"],
                        config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["SAMZ"],
                        config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["OM"],
                        config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["TTI"],
                        config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["TTO"],
                        config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["DIFFH"],
                        config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["DIFFV"],
                        ]
        self.stage_gonio = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=self.gonio_motors, title="HR GONIO motors")
        
        # hab_motors = ["p02/motor/exp.04", "p02/motor/exp.04", "p02/motor/exp.04"]
        self.hab_motors = [config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["HAB_X"],
                      config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["HAB_Y"],
                      config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["HAB_Z"]]
        self.stage_hab = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=self.hab_motors, title="Hab motors")
        
        # cryo_motors = ["p02/motor/exp.04", "p02/motor/exp.04", "p02/motor/exp.04", "p02/motor/exp.04"]
        self.cryo_motors = [config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["CRYO_X"],
                       config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["CRYO_Y"],
                       config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["CRYO_Z"]]
        self.stage_cryo = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=self.cryo_motors, title="Cryo motors")
        
        # misc_motors = ["p02/motor/exp.04", "p02/motor/exp.04", "p02/motor/exp.04", "p02/motor/exp.04"]
        self.misc_motors = [config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["STAGE_X"],
                       config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["STAGE_Y"],
                       config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["STAGE_Z"],
                       config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["BATTERY"],
                       config.DEVICE_SERVER_P02 + config.DEVICE_NAMES["TBLZ"]]
        self.stage_misc = gui_stacked_motors_controls_widget.StackedMotorControls(parent=self, motors=self.misc_motors, title="Misc motors")
        
    def __init_signals(self):
        self.stage_gonio.set_margin_to_zero()
        self.stage_1.layout().addWidget(self.stage_gonio)
        
        self.stage_hab.set_margin_to_zero()
        self.stage_cryo.set_margin_to_zero()
        self.stage_2.layout().addWidget(self.stage_hab)
        self.stage_2.layout().addWidget(self.stage_cryo)
        
        self.stage_misc.set_margin_to_zero()
        self.stage_3.layout().addWidget(self.stage_misc)
        
    def __main(self):
        pass 
    
    def change_mode(self, mode):
        
        expert_gonio = self.gonio_motors[4:]
        expert_misc = self.misc_motors[4]
        if mode == default_beamline.DEFAULT_MODE:
            for motor in expert_gonio:
                self.stage_gonio.set_motor_controls_enabled(motor, False)
            self.stage_misc.set_motor_controls_enabled(expert_misc, False)
            #for motor in expert_misc:
            #    self.stage_misc.set_motor_controls_enabled(motor, False)
        elif mode == default_beamline.EXPERT_MODE:
            for motor in expert_gonio:
                self.stage_gonio.set_motor_controls_enabled(motor, True)
            self.stage_misc.set_motor_controls_enabled(expert_misc, True)
            #for motor in expert_misc:
            #    self.stage_misc.set_motor_controls_enabled(motor, True)
        
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    widget = controls()
    
    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)

    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()
