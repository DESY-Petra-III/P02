import PyTango
import p3cntr
import sys

from PyQt4 import QtGui, QtCore

WINDOWTITLE = "Offline Laser Heating"

###
## MOfflineLaserHeating - class for showing motor widgets
###
class MOfflineLaserHeating(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MOfflineLaserHeating, self).__init__(parent)

        self.initVars()
        self.initSelf()
        self.initEvents()

    # initialize variables if needed
    def initVars(self):
        return

    # initialize gui
    def initSelf(self):
        self.setWindowTitle(WINDOWTITLE)

        # adjust palette - color scheme
        self.setAutoFillBackground(True)
        pal = QtGui.QPalette(QtGui.QColor('red').light())
        self.setPalette(pal)

        # create icon
        self.createIcon()

        # create central widget from 
        self.createCentralWidget()

        # show window
        self.show()
        return

    # initialize events if needed
    def initEvents(self):
        return

    # create the main widget
    def createCentralWidget(self):
        wdgt = QtGui.QWidget(self)
        layout = QtGui.QGridLayout(wdgt)

        # implement motors
        cenx_LH = p3cntr.Motor("CenX LH",
            "Center X LH",
            "haspllabcl4:10000/p02/motor/ecsi.01")
        ceny_LH = p3cntr.Motor("CenY LH",
                    "Center Y LH",
                    "haspllabcl4:10000/p02/motor/ecsi.02")
        Samz_LH = p3cntr.Motor("SamZ LH",
                      "Sample Z LH",
                      "haspllabcl4:10000/p02/motor/ecsi.03")

        # put motors on a single widgets
        wmotors = p3cntr.ui.MotorWidgetAdvanced([cenx_LH,ceny_LH,Samz_LH])

        # add things to a layout
        layout.addWidget(wmotors, 1, 1)

        self.setCentralWidget(wdgt)
        return

    def createIcon(self):
        # icon 
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtGui.QColor(100,0,0))
        self.setWindowIcon(QtGui.QIcon(pixmap))
        return

    def closeEvent(self, event):
        event.accept()
        return
###
## MOfflineLaserHeating END
###

if(__name__ == '__main__'):
    app = QtGui.QApplication([])
    form = MOfflineLaserHeating()
    app.exec_()
