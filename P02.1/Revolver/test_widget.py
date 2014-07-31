from PyQt4.QtGui import QMainWindow, QMessageBox, QApplication, QWidget
from PyQt4 import QtGui
from PyQt4.Qt import SIGNAL
import logging
import taurus
import sys
import taurustest



class DefaultTestWidget(taurustest.Ui_Form, QWidget):
        
    def __init__(self, parent=False):
        """
        Class constructor
        @type parent: DefaultWidget
        """
        super(DefaultTestWidget, self).__init__()
        self.parent = parent
        self.setupUi(self)
        #td = taurus.Device("tango://has6117b:10000/p02/motor/exp.04")
        
    
    

# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
      
    # create main window
    app = QtGui.QApplication(sys.argv)

    # init widget
    widget = DefaultTestWidget()
    
    #logging.error(widget.taurusMacroExecutorWidget.parent)
    #taurus.Database()
    widget.taurusMacroExecutorWidget.setModel("p02/door/has6117b")
    #widget.taurusMacroExecutorWidget.emit(SIGNAL('doorChanged'),"p02/door/has6117b")
    #widget.taurusMacroExecutorWidget.emit(SIGNAL('doorChanged'),"p02/macroserver/has6117b")
    
    
    # show widget
    widget.show()

    # execute application
    app.exec_()