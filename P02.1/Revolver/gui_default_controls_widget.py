# import global classes 
from PyQt4 import QtCore, Qt
 
# Import local classes
from Revolver.classes import signals
from  gui_default_widget import DefaultWidget

class EventSpinboxFilter(Qt.QObject):
    """
    Event filter for spinbox
    Value is changed only when ENTER is pressed
    """
    
    def __init__(self):
        super(EventSpinboxFilter, self).__init__()
      
    def eventFilter(self, *args, **kwargs):
        event = args[1]
        eventType = args[1].type()
        if eventType == Qt.QEvent.KeyPress and (event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return):
            args[0].emit(Qt.SIGNAL("valueChanged()"))
        return False

class DefaultControls(DefaultWidget):
    """
    Default beamline device controls.
    Set this widget as super class for derived beamline controllers.
    """
    
    # polling time to check device status
    POLLING_TIME = 0.25
    
    def __init__(self, parent=None, devicePath=None):
        super(DefaultControls, self).__init__(parent=parent)
        self.device = devicePath
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        pass
    
    def __init_signals(self):
        if self.parent:
            self.connect(self.parent, signals.SIG_CHANGE_MODE, self.change_mode)
        self.connect(self, signals.SIG_SHOW, self.action_before_shown)
        self.connect(self, signals.SIG_HIDE, self.action_before_hide)
        
    def __main(self):
        pass
        
    def __poll_status(self):
        """
        Poll device status.
        Should be polled by POLLING_TIME constatnt
        """
        pass
    
    def setupUi(self):
        pass
    
    def change_mode(self, mode):
        """
        Change controller mode
        """
        pass
    
    def set_margin_to_zero(self):
        """
        Set widget margins to zero
        """
        self.layout().setSpacing(0)
        self.layout().setMargin(0)
        
    def action_before_shown(self):
        """
        Do some action before controls was shown
        """
        pass
        
    def action_before_hide(self):
        """
        Do some action before controls was hide
        """
        pass
