'''
Created on Oct 21, 2013

@author: Martin Domaracky
'''
from PyQt4.Qt import SIGNAL

##############################################
# Generic public signals                     #
##############################################
SIG_ENABLE_CONTROLS = SIGNAL("enableControls()")
SIG_DISABLE_CONTROLS = SIGNAL("disableControls()")
SIG_SHOW_CONTROLS = SIGNAL("enableControls()")
SIG_HIDE_CONTROLS = SIGNAL("disableControls()")
SIG_SHOW_ERROR = SIGNAL("showError")
SIG_SHOW_WARNING = SIGNAL("showWarning(QString, QString)")
SIG_SHOW_INFO = SIGNAL("showInfo(QString, QString)")
SIG_SET_PROGRESSBAR = SIGNAL("changeProgress(QProgressBar*, int)")
SIG_HALT_DEVICES = SIGNAL("haltDevices()")
SIG_ABOUT_QUIT = SIGNAL("aboutToQuit()")
SIG_STOP = SIGNAL("stop()")
SIG_START = SIGNAL("start()")
SIG_PLOT_SIGNAL = SIGNAL("plotSignal()")
SIG_SHOWN = SIGNAL("shown()")
SIG_HIDDEN = SIGNAL("hidden()")
SIG_CHANGE_DEFAULT_MOTOR = SIGNAL('changeDefaultMotor')
SIG_SHOW_ELEMENT = SIGNAL('showElement')

##############################################
# Macro signals                              #
##############################################
# emit signal when macro started
# int - macroType
SIG_MACRO_STARTED = SIGNAL("macroStarted(int)")
# emit signal when macro ended
# int - macroType
SIG_MACRO_ENDED = SIGNAL("macroEnded(int)")
# emit signal when want to load macro
# int - macroType
# value - unpickled data
SIG_LOAD_MACRO = SIGNAL("loadMacro(int, value)")
SIG_MACRO_STEP_COMPLETED = SIGNAL("stepCompleted()")
# emit private signal when add macro step
# macro - classes.macro.*
_SIG_ADD_MACRO = SIGNAL("addMacro(macro)")
_SIG_START_LOGGING = SIGNAL("startLogging")
_SIG_STOP_LOGGING = SIGNAL("stopLogging")

##############################################
# Status signals                             #
##############################################
SIG_DEVICE_WORKING = SIGNAL("deviceWorking()")
SIG_DEVICE_IDLE = SIGNAL("deviceIdle(bool)")
SIG_DEVICE_STATUS_CHANGED = SIGNAL("deviceStatusChanged(bool)")
SIG_DEVICE_STATUS_ERROR = SIGNAL("deviceStatusError()")
_SIG_SET_LED_COLOR = SIGNAL("setLedColor")

##############################################
# Logging signals                            #
##############################################
SIG_LOG_INIT = SIGNAL("logInit(String, String)")
SIG_LOG_LINE = SIGNAL("logLine(String)")
SIG_LOG_DEVICE_PROFILING = SIGNAL("logProfiling")
SIG_LOG_POINT_DATA = SIGNAL("logPointData")

##############################################
# Beamline signals                           #
##############################################
SIG_BLOCK_BEAM = SIGNAL("action_block_beam(bool)")
SIG_SHOW_BEAMLINE_DEVICE_CONTROLS = SIGNAL("action_show_controls(int)")
# emit this signal if beam blocking should be checked
SIG_CHECK_BEAM = SIGNAL("action_check_beam()")
SIG_BUTTON_CHANGE_ICON = SIGNAL("changeIcon")
SIG_CHANGE_MODE = SIGNAL("change_mode(int)")
SIG_SHOW = SIGNAL("show()")
SIG_HIDE = SIGNAL("hide()")