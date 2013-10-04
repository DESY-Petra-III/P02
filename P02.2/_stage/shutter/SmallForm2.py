import sys
from PyQt4 import QtGui,QtCore
import PyTango
import matplotlib
import time

"""Defines a simple QT-widget showing attributes of a
number of tango-devices. Is e.g. used for ShutterControl2.py."""

def read_tangodevice(device,attributename):
    #print device
    #print attributename
    try:
        result=device.read_attribute(attributename)
##        print result
##        print
        result=result.value
    except PyTango.DevFailed:
        print time.ctime(),"Dev Failed for device: ",device,"\nwhile reading attribute: ",attributename
        return None
    return result


class SmallForm2(QtGui.QWidget):
    def __init__(self,device_list,variable_list,parent=None,interval=1000,label_list=None,
        value_dicts=None,print_device_labels=True):
        

        super(SmallForm2,self).__init__(parent)
##        QtGui.QWidget.setFont(QtGui.QFont("Arial",16))
        if len(device_list)!=len(variable_list):
            raise ValueError,"Length of device-list and value-list does not match"

        self.layout=QtGui.QGridLayout()

        self.device_list=device_list
        self.variable_list=variable_list
        self.label_list=label_list
        self.device_name=[]
        self.variable_name=[]
        self.variable_value=[]
        self.value_dicts=value_dicts
        
        row=0
        for dev_index in range(len(self.device_list)):
            if print_device_labels:
                self.device_name+=[QtGui.QLabel("<b>"+self.device_list[dev_index]+"</b>")]
                self.device_name[-1].setWindowFlags(QtCore.Qt.SplashScreen)
                self.layout.addWidget(self.device_name[-1],row,0)
            row+=1
            self.variable_name+=[[]]
            self.variable_value+=[[]]
            for var_index in range(len(self.variable_list[dev_index])):
                if label_list is None:
                    self.variable_name[-1]+=[QtGui.QLabel(self.variable_list[dev_index][var_index])]
                else:
                    self.variable_name[-1]+=[QtGui.QLabel(self.label_list[dev_index][var_index])]
                self.variable_name[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
                self.layout.addWidget(self.variable_name[-1][-1],row,0)
                self.variable_value[-1]+=[QtGui.QLabel("")]
                self.variable_value[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
                self.layout.addWidget(self.variable_value[-1][-1],row,1)
##                print row
                row+=1
                

        self.setLayout(self.layout)
        self.setWindowTitle("")

        self.timer=QtCore.QTimer()
        QtCore.QObject.connect(self.timer,QtCore.SIGNAL("timeout()"),self.updateUI)
        self.timer.start(interval)

    def updateUI(self):
        for dev_index in range(len(self.device_list)):
            for var_index in range(len(self.variable_list[dev_index])):
##                print 'Reading variable ',self.variable_list[dev_index][var_index],' from device ',self.device_list[dev_index].name()
                device_data=read_tangodevice(PyTango.DeviceProxy(self.device_list[dev_index]),self.variable_list[dev_index][var_index])
                if device_data is None:
##                    self.variable_value="None"
                    self.variable_value[dev_index][var_index].setText("Tango Failure")
                else:
#                    print self.value_dicts
#                    print self.value_dicts[dev_index][var_index]
#                    print self.value_dicts[dev_index][var_index][device_data]
#                    try:
#                    self.variable_value[dev_index][var_index].setText(self.value_dicts[dev_index][var_index][device_data])
#                    except KeyError:
                    self.variable_value[dev_index][var_index].setText(str(device_data))
##                if dev_index==0 and var_index==0:
##                    self.setWindowTitle("%3.2f A"%device_data.value)

