from __future__ import division
import sys
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyTango import *


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        
        self.initUi()
        
        self.updateUi()
        
#-----------

    def initUi(self):

        pal = QPalette()
        self.setAutoFillBackground(True)
        pal.setColor(QPalette.Window, QColor('orange').light())
        self.setPalette(pal)

        self.devKeithley3706  = DeviceProxy("tango://haspp02oh1:10000/p02/keithley3706/eh2b.01")
        self.devKeithleyCh1_value  = self.devKeithley3706.read_attribute("ValueCh1").value
        self.devKeithleyCh2_value  = self.devKeithley3706.read_attribute("ValueCh2").value
        self.devKeithleyCh3_value  = self.devKeithley3706.read_attribute("ValueCh3").value
        self.devKeithleyCh4_value  = self.devKeithley3706.read_attribute("ValueCh4").value

        self.valueCh1Label = QLabel("start")
        self.valueCh2Label = QLabel("start")
        self.valueCh3Label = QLabel("start")
        self.valueCh4Label = QLabel("start")

        self.Ch1Label = QLabel("Channel 1")
        self.Ch2Label = QLabel("Channel 2")
        self.Ch3Label = QLabel("Channel 3")
        self.Ch4Label = QLabel("Channel 4")

        self.messageLabel = QLabel("updates as fast as Keithley3706 permits!")
        
        self.exitButton   = QPushButton("Exit")
        
        grid = QGridLayout()

        grid.addWidget(self.Ch1Label, 0, 0)
        grid.addWidget(self.Ch2Label, 1, 0)
        grid.addWidget(self.Ch3Label, 2, 0)
        grid.addWidget(self.Ch4Label, 3, 0)

        grid.addWidget(self.valueCh1Label, 0, 1)
        grid.addWidget(self.valueCh2Label, 1, 1)
        grid.addWidget(self.valueCh3Label, 2, 1)
        grid.addWidget(self.valueCh4Label, 3, 1)
        grid.addWidget(self.messageLabel,    4, 0)
        grid.addWidget(self.exitButton,    5, 0)

        self.setLayout(grid)

        self.connect(self.exitButton, SIGNAL("clicked()"), self.exitFunction)

        self.setWindowTitle("Keithley3706")

        interval = 500
        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL("timeout()"), self.updateUi)
        self.timer.start(interval)

#------------------


    def updateUi(self):

        self.devKeithley3706.command_inout("StartMeasurement")
        
        state = self.devKeithley3706.state()
        while (state == DevState.MOVING):
            time.sleep(0.4)
            state = self.devKeithley3706.state()
        
        self.devKeithleyCh1_value  = self.devKeithley3706.read_attribute("ValueCh1").value
        self.valueCh1Label.setText(str(self.devKeithleyCh1_value))
#        time.sleep(0.2)
        
        self.devKeithleyCh2_value  = self.devKeithley3706.read_attribute("ValueCh2").value
        self.valueCh2Label.setText(str(self.devKeithleyCh2_value))
#        time.sleep(0.2)

        self.devKeithleyCh3_value  = self.devKeithley3706.read_attribute("ValueCh3").value
        self.valueCh3Label.setText(str(self.devKeithleyCh3_value))
#        time.sleep(0.2)
        
        self.devKeithleyCh4_value  = self.devKeithley3706.read_attribute("ValueCh4").value
        self.valueCh4Label.setText(str(self.devKeithleyCh4_value))

    def exitFunction(self):
        QApplication.quit()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()
