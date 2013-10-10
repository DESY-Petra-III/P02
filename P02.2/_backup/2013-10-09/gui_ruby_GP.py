import PyTango
import pylab
import numpy
import p3cntr
reload(p3cntr)
import sys
from PyQt4 import QtGui,QtCore


rubyX_GP = p3cntr.Motor("Ruby X GP",
            "Ruby X GP",
            "haspp02oh1:10000/p02/motor/eh2b.46")
rubyY_GP = p3cntr.Motor("Ruby Y GP >make sure the diode is out!<",
            "Ruby Y GP",
            "haspp02oh1:10000/p02/motor/eh2b.47")
rubyZ_GP = p3cntr.Motor("Ruby Z GP",
            "Ruby Z GP",
            "haspp02oh1:10000/p02/motor/eh2b.48")

print rubyX_GP, rubyY_GP, rubyZ_GP

App = QtGui.QApplication(sys.argv)
ruby_widget = p3cntr.ui.MotorWidget([rubyX_GP, rubyY_GP, rubyZ_GP])
ruby_widget.setWindowTitle('Ruby GP')

ruby_widget.setAutoFillBackground(True)
pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Window, QtGui.QColor('blue').light())
ruby_widget.setPalette(pal)

ruby_widget.show()
App.exec_()
