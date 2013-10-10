import PyTango
import pylab
import numpy
import p3cntr
reload(p3cntr)
import sys
from PyQt4 import QtGui,QtCore


cenxGP = p3cntr.Motor("CenX GP",
            "Center X",
            "haspp02oh1:10000/p02/motor/eh2b.43")
cenyGP = p3cntr.Motor("CenY GP",
            "Center Y",
            "haspp02oh1:10000/p02/motor/eh2b.42")
SamzGP = p3cntr.Motor("SamZ GP",
              "Sample Z GP",
              "haspp02oh1:10000/p02/motor/eh2b.37")
omegaGP = p3cntr.Motor("Omega GP",
           "Omega GP",
           "haspp02oh1:10000/p02/motor/eh2b.38")

print cenxGP,cenyGP,omegaGP,SamzGP

App = QtGui.QApplication(sys.argv)
stack_widget = p3cntr.ui.MotorWidget([cenxGP,cenyGP,SamzGP,omegaGP])
stack_widget.setWindowTitle('Sample stack GP')

stack_widget.setAutoFillBackground(True)
pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Window, QtGui.QColor('blue').light())
stack_widget.setPalette(pal)

stack_widget.show()
App.exec_()
