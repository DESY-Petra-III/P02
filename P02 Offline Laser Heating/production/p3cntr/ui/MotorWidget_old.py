import sys
from PyQt4 import QtGui,QtCore
import PyTango
import matplotlib
import functools
import time


class My_QPushButton(QtGui.QPushButton):
    def sizeHint(self):
        return QtCore.QSize(30,24)
    

class MotorWidget(QtGui.QDialog):
    def __init__(self,device_list,parent=None,interval=200,
                 button_rel_actions=None,button_abs_actions=None):
    
        #add here a try statement to catch motors that do not posses a
        #UnitBacklash attribute
        if button_rel_actions is None:
            button_rel_actions = []
            for device in device_list:
                try:
                    #bl_value = device._proxy.read_attribute("UnitBacklash").value
                    ulim_min = device._proxy.read_attribute("UnitLimitMin").value
                    ulim_max = device._proxy.read_attribute("UnitLimitMax").value
                    delta_step = (ulim_max-ulim_min)/10000.
                except:
                    bl_value = -1.

                button_rel_actions.append([delta_step,10.*delta_step])
            #button_rel_actions = [[device._proxy.read_attribute("UnitBacklash").value,
            #           10.*device._proxy.read_attribute("UnitBacklash").value] for device in device_list]

        print button_rel_actions


        super(MotorWidget,self).__init__(parent)

        layout=QtGui.QGridLayout()
        
        self.device_list=device_list
        self.device_name=[]
        self.motordev_widget=[]
        self.wrappers=[]
        self.values=[None for i in range(len(self.device_list))]
        
        row=0
        for dev_index in range(len(self.device_list)):
            
            self.motordev_widget+=[[]]
            self.wrappers+=[[]]
            
            col=0
            
            self.device_name+=[QtGui.QLabel("<b>"+self.device_list[dev_index].name+"</b>")]
            self.device_name[-1].setWindowFlags(QtCore.Qt.SplashScreen)
            layout.addWidget(self.device_name[-1],row,col)
            col+=1

            self.motordev_widget[-1]+=[My_QPushButton("<<<")]
            self.motordev_widget[-1][-1].setAutoDefault(False)
            self.motordev_widget[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
            self.wrappers[-1]+= [functools.partial(self.limit_move,self.device_list[dev_index],-1.)]
            self.connect(self.motordev_widget[-1][-1],QtCore.SIGNAL("clicked()"),
                         self.wrappers[-1][-1])
            layout.addWidget(self.motordev_widget[-1][-1],row,col)
            col+=1
            
            self.motordev_widget[-1]+=[My_QPushButton("<<")]
            self.motordev_widget[-1][-1].setAutoDefault(False)
            self.motordev_widget[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
            self.wrappers[-1]+= [functools.partial(self.rel_move,self.device_list[dev_index],-1.,
                                                   button_rel_actions[dev_index][1])]
            self.connect(self.motordev_widget[-1][-1],QtCore.SIGNAL("clicked()"),
                         self.wrappers[-1][-1])
            layout.addWidget(self.motordev_widget[-1][-1],row,col)
            col+=1

            
            self.motordev_widget[-1]+=[My_QPushButton("<")]
            self.motordev_widget[-1][-1].setAutoDefault(False)
            self.motordev_widget[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
            self.wrappers[-1]+= [functools.partial(self.rel_move,self.device_list[dev_index],-1.,
                                                   button_rel_actions[dev_index][0])]
            self.connect(self.motordev_widget[-1][-1],QtCore.SIGNAL("clicked()"),
                         self.wrappers[-1][-1])
            layout.addWidget(self.motordev_widget[-1][-1],row,col)
            col+=1






            
            self.motordev_widget[-1]+=[QtGui.QLineEdit("")]
            self.motordev_widget[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
            self.wrappers[-1]+=[functools.partial(self.abs_move,
                                                         self.device_list[dev_index],
                                                         self.motordev_widget[-1][-1])]
            self.connect(self.motordev_widget[-1][-1],QtCore.SIGNAL("returnPressed()"),
                         self.wrappers[-1][-1])
            layout.addWidget(self.motordev_widget[-1][-1],row,col)
            col+=1






            

            self.motordev_widget[-1]+=[My_QPushButton(">")]
            self.motordev_widget[-1][-1].setAutoDefault(False)
            self.motordev_widget[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
            self.wrappers[-1]+= [functools.partial(self.rel_move,self.device_list[dev_index],1.,
                                                   button_rel_actions[dev_index][0])]
            self.connect(self.motordev_widget[-1][-1],QtCore.SIGNAL("clicked()"),
                         self.wrappers[-1][-1])
            layout.addWidget(self.motordev_widget[-1][-1],row,col)
            col+=1
            
            self.motordev_widget[-1]+=[My_QPushButton(">>")]
            self.motordev_widget[-1][-1].setAutoDefault(False)
            self.motordev_widget[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
            self.wrappers[-1]+= [functools.partial(self.rel_move,self.device_list[dev_index],1.,
                                                   button_rel_actions[dev_index][1])]
            self.connect(self.motordev_widget[-1][-1],QtCore.SIGNAL("clicked()"),
                         self.wrappers[-1][-1])
            layout.addWidget(self.motordev_widget[-1][-1],row,col)
            col+=1
            
            self.motordev_widget[-1]+=[My_QPushButton(">>>")]
            self.motordev_widget[-1][-1].setAutoDefault(False)
            self.motordev_widget[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
            self.wrappers[-1]+= [functools.partial(self.limit_move,self.device_list[dev_index],1.)]
            self.connect(self.motordev_widget[-1][-1],QtCore.SIGNAL("clicked()"),
                         self.wrappers[-1][-1])
            layout.addWidget(self.motordev_widget[-1][-1],row,col)
            col+=1         
            row+=1

        col=0

        

        self.motordev_widget[-1]+=[QtGui.QPushButton("&Exit")]
        self.motordev_widget[-1][-1].setAutoDefault(False)
        self.motordev_widget[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
        self.connect(self.motordev_widget[-1][-1],QtCore.SIGNAL("clicked()"),
                         self.close)
        layout.addWidget(self.motordev_widget[-1][-1],row,col)

          
        col=4        
      
        self.motordev_widget+=[[]]
        self.wrappers+=[[]]
        self.motordev_widget[-1]+=[QtGui.QPushButton("&Stop all moves")]
        self.motordev_widget[-1][-1].setAutoDefault(False)
        self.motordev_widget[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
        self.connect(self.motordev_widget[-1][-1],QtCore.SIGNAL("clicked()"),
                         self.stop_all_moves)
        layout.addWidget(self.motordev_widget[-1][-1],row,col)
        row+=1

        self.setLayout(layout)
        self.setWindowTitle("Motor Widget")

        self.timer=QtCore.QTimer()
        QtCore.QObject.connect(self.timer,QtCore.SIGNAL("timeout()"),self.updateUI)
        self.timer.start(interval)
        return

    def abs_move(self,device,widget):
##        print device,widget
        position=widget.text()
        position=float(position)
##        print "Now in abs-move, moving to ",position
##        time.sleep(2)
        device.move(position)
##        print "still in abs_move"
##        time.sleep(2)
        return
##
##    def small_move(self,device,direction):
##        print "small move",device,direction
##        device.move(device._proxy.read_attribute("Position").value+direction*device._proxy.read_attribute("UnitBacklash").value)
##        return
##    
##    def med_move(self,device,direction):
##        print "med move",device,direction
##        device.move(device._proxy.read_attribute("Position").value+10*direction*device._proxy.read_attribute("UnitBacklash").value)
##        return
##

    
    def rel_move(self,device,direction,step):
##        print "rel move",device,direction,step
        device.move(device._proxy.read_attribute("Position").value+direction*step)
        return
    
    def limit_move(self,device,direction):   
##        print "limit move",device,direction 
        if direction<0.:
            device.move(device._proxy.read_attribute("UnitLimitMin").value+abs(device._proxy.read_attribute("UnitBacklash").value))
        else:
            device.move(device._proxy.read_attribute("UnitLimitMax").value-abs(device._proxy.read_attribute("UnitBacklash").value))
        return

    def updateUI(self):
        for dev_index in range(len(self.device_list)):
            try:
                device_value=self.device_list[dev_index]._proxy.read_attribute("Position").value           
            except PyTango.DevFailed:
                device_value="Tango Failure"
            if self.values[dev_index]!=device_value:
                self.values[dev_index]=device_value
                self.motordev_widget[dev_index][3].setText(str(device_value))
        return


    def stop_all_moves(self):
        for device in self.device_list:
            device._proxy.StopMove()
        return
