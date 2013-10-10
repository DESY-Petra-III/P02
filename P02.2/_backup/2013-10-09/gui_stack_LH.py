import PyTango
import pylab
import numpy
import p3cntr
reload(p3cntr)
import sys
from PyQt4 import QtGui,QtCore


cenx_LH = p3cntr.Motor("CenX LH",
            "Center X LH",
            "haspp02oh1:10000/p02/motor/eh2a.09")
ceny_LH = p3cntr.Motor("CenY LH",
            "Center Y LH",
            "haspp02oh1:10000/p02/motor/eh2a.10")
Samz_LH = p3cntr.Motor("SamZ LH",
              "Sample Z LH",
              "haspp02oh1:10000/p02/motor/eh2a.05")
omega_LH = p3cntr.Motor("Omega LH",
           "Omega LH",
           "haspp02oh1:10000/p02/motor/eh2a.06")

print cenx_LH,ceny_LH,omega_LH,Samz_LH

App = QtGui.QApplication(sys.argv)
stack_widget = p3cntr.ui.MotorWidget([cenx_LH,ceny_LH,Samz_LH,omega_LH])
stack_widget.setWindowTitle('Sample stack LH')

stack_widget.setAutoFillBackground(True)
pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Window, QtGui.QColor('orange').light())
stack_widget.setPalette(pal)

stack_widget.show()
App.exec_()
