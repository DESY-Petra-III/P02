import sys
from PyQt4 import Qt,QtGui,QtCore
import PyTango
import matplotlib
import SmallForm2
reload(SmallForm2)
import os
import pyglet
import time
import urllib2
import functools
import numpy

"""Defines a small GUI showing a couple of crucial parameters, including
the beam current, the status of the fast orbit feedback, the TopUp-mode
and the status of the frontend. In addition, a feedback is available,
which can act e.g. on the pitch and roll of the second crystal in order
to achieve stable beam position over longer time periods (hours to days).

It is currently utilizing the Quad BeamPositionMonitors present in the
mono and the microprobe hutches.

If you know what you are doing: Feel free to change! But if you are a non-
expert when it comes to feedbacks/Python/Tango/QT, it is better if you
restrain yourself to only modify the __init__-function just below, in which
a lot of variables are initialized to meaningful values, and the very end of
the script, which actually executes it, starting in line 734 at "button_labels=[[...",
which also contains a lot of initialization. When in doubt, ask me
(Gerd.Wellenreuther@desy.de)!"""



class CurrentSmallForm(SmallForm2.SmallForm2):
    def __init__(self,device_list,
        variable_list,
        parent=None,
        interval=1000,
        label_list=None,
        value_dicts=None,
        print_device_labels=False,
        ics_url=None,
        BS_list=None,
        BS_attrib_list=None):
        
        super(CurrentSmallForm,self).__init__(device_list,variable_list,parent=parent,
        interval=interval,label_list=label_list,value_dicts=value_dicts,
        print_device_labels=print_device_labels)
        self.current=None
        self.TopUp=None
        self.TopUp_str=None
        self.FOFB=None
        self.FOFB_str=None
        
        self.busy=False
        self.permit_experiment=None
        self.n_rows=0

        for i in range(len(device_list)):
            self.n_rows+=1
            for j in range(len(variable_list[i])):
                self.n_rows+=1
                
        self.ics_url=ics_url
        
        self.BS_open=[None for i in range(len(BS_list))]
        self.beam_in_hutch=[None for i in range(len(BS_list))]
        self.keep_BS_open=[None for i in range(len(BS_list))]
        self.hutch_modification=["" for i in range(len(BS_list))]

        self.BS_list=BS_list
        self.BS_attrib_list=BS_attrib_list

        self.QBPM_device_list=["P02/I404/mono.01","P02/I404/micro.01"]
#        self.QBPM_device_list=["P02/I404/mono.01"]
        self.QBPM_feedback_status=0 # 0 not running, 1 initializing sets, 2 mono feedback running, 3 micro feedback running

        self.QBPM_n_averages=10
        
        #self.QBPM_P=[[None,-0.2E-2,None],[None,-0.2E-2,None]]
        #self.QBPM_n_averages=4
        
        #self.QBPM_P=[[None,-0.2E-2,None],[None,-0.2E-2,None]]
        #self.QBPM_P=[[None,-0.7E-2,None],[None,-0.7E-2,None]]
        #self.QBPM_n_averages=1        
        
        self.QBPM_values=numpy.zeros((len(self.QBPM_device_list),3,self.QBPM_n_averages),dtype=numpy.float)
        self.QBPM_means=numpy.zeros((len(self.QBPM_device_list),3),dtype=numpy.float)
        self.QBPM_stddevs=numpy.zeros((len(self.QBPM_device_list),3),dtype=numpy.float)
        
        self.QBPM_sets=numpy.zeros((len(self.QBPM_device_list),3),dtype=numpy.float)
        self.QBPM_sets_stddevs=numpy.zeros((len(self.QBPM_device_list),3),dtype=numpy.float)
        self.QBPM_average_index=numpy.zeros((len(self.QBPM_device_list)),dtype=numpy.int)
        self.QBPM_index=0
        self.QBPM_label_widgets=[]
        self.QBPM_value_widgets=[]
        
        ## taking into account y-z-swap in Micro-QBPM
        #self.QBPM_fb_device_list=[[None,"P02/motor/mono.01",None],["P02/motor/mono.01",None,None]]
        #self.QBPM_labels=[["QBPM Mono Y","QBPM Mono Z","QBPM Mono I_avg"],["QBPM Micro Z","QBPM Micro Y","QBPM Micro I_avg"]]
        #self.QBPM_fb_margins=[[None,[0.035,0.085],None],[[0.035,0.085],None,None]]
        #self.QBPM_P=[[None,-0.7E-1,None],[-0.7E-2,None,None]]
	
	
        # for right QBPM cabeling
        self.QBPM_fb_device_list=[["P02/motor/mono.02","P02/motor/mono.01",None],["P02/motor/mono.02","P02/motor/mono.01",None]]
        self.QBPM_labels=[["QBPM Mono Y","QBPM Mono Z","QBPM Mono I_avg"],["QBPM Micro Y","QBPM Micro Z","QBPM Micro I_avg"]]
        self.QBPM_fb_margins=[[[-0.2,-0.00],[-0.14,-0.00],None],[[-0.2,-0.00],[-0.14,-0.00],None]]
        self.QBPM_P=[[0.2E-1,0.6E-2,None],[0.2E-1,0.6E-2,None]]



#        self.QBPM_fb_minimum_change=[[None,4.E-5,None],[None,4.E-5,None]] #     this corresponds to a single full step of monoth2 - seems not to be sufficient
        self.QBPM_fb_minimum_change=[[2.E-6,2.E-6,None],[2.E-6,2.E-6,None]] # 	values lower than this do not make sense, this is 1/20 step!
        self.QBPM_fb_minimum_change=[[4.E-5,2.E-6,None],[4.E-5,2.E-6,None]] # 	1/20 step fpr mth2, fullstep for mchi2


        self.QBPM_fb_active=[[False,False,False],[False,True,False]] # only vertical feedback
        self.QBPM_fb_active=[[False,False,False],[True,True,False]] # vertical+horizontal feedback

        self.QBPM_minimum_current=[1E-9,1E-9]

        self.add_QBPM_to_layout()
        
                       
    def add_QBPM_to_layout(self):
         for dev_index in range(len(self.QBPM_device_list)):
             self.QBPM_label_widgets+=[[]]
             self.QBPM_value_widgets+=[[]]
             for index in range(3):
                 self.QBPM_label_widgets[-1]+=[QtGui.QLabel(self.QBPM_labels[dev_index][index])]
                 self.QBPM_label_widgets[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
                 self.layout.addWidget(self.QBPM_label_widgets[-1][-1],self.n_rows,0)
                 self.QBPM_value_widgets[-1]+=[QtGui.QLabel("")]
                 self.QBPM_value_widgets[-1][-1].setWindowFlags(QtCore.Qt.SplashScreen)
                 self.layout.addWidget(self.QBPM_value_widgets[-1][-1],self.n_rows,1)
                 self.n_rows+=1


    def updateUI(self):
        try:
##            print "In UpdateUI",self.QBPM_feedback_status
            while True:
#                print self.busy,
                if not self.busy:
                    self.busy=True
#                    print
                    break
                time.sleep(0.01)
                
                
            for dev_index in range(len(self.device_list)):
                for var_index in range(len(self.variable_list[dev_index])):
                    device_data=SmallForm2.read_tangodevice(PyTango.DeviceProxy(self.device_list[dev_index]),self.variable_list[dev_index][var_index])
                    try:
                        self.variable_value[dev_index][var_index].setText(self.value_dicts[dev_index][var_index][device_data])
                            
                    except KeyError:
                        write_logfile(time.ctime()+" KeyError, showing raw Tango data"+str(dev_index)+" "+str(self.device_list[dev_index])+" "+str(var_index)+" "+str(device_data)+"\n")
                        print "KeyError, showing raw Tango data",dev_index,self.device_list[dev_index],var_index,device_data
                        self.variable_value[dev_index][var_index].setText(str(device_data))
                    except TypeError:
                        #write_logfile(time.ctime()+"TypeError, showing raw Tango data"+str(dev_index)+" "+str(self.device_list[dev_index])+" "+str(var_index)+" "+str(device_data)+"\n")
                        #print "TypeError, showing raw Tango data",dev_index,self.device_list[dev_index],var_index,device_data
                        self.variable_value[dev_index][var_index].setText(str(device_data))
                                                            
                    if dev_index==0 and var_index==0:
                        if device_data is None:
                            self.setWindowTitle("No current readable!")
                        else:
                            self.setWindowTitle("%3.2f A"%device_data)
            
            # feedback 
            """
            switch_feedback_on=False
            for dev_index in range(len(self.QBPM_device_list)):
                while self.QBPM_average_index[dev_index]<self.QBPM_n_averages:
                    QBPM=PyTango.DeviceProxy(self.QBPM_device_list[dev_index])
                    results=SmallForm2.read_tangodevice(QBPM,"PosAndAvgCurr")
##                    print self.QBPM_average_index[dev_index],results
                    if not results is None:
                        for value_index in range(3):
##                            print self.QBPM_values.shape,numpy.array(results).shape
##                            print dev_index,value_index,self.QBPM_average_index[dev_index]
                            try:
                                self.QBPM_values[dev_index][value_index][self.QBPM_average_index[dev_index]]=results[value_index]
                            except IndexError:
                                print "Index-Error, self.QBPM_average_index overflow?"
                                print dev_index,value_index,self.QBPM_average_index[dev_index]#,self.QBPM_values,results
                                write_logfile(time.ctime()+" Index-Error, self.QBPM_average_index overflow?\n")
                                #write_logfile(time.ctime()+" "+str(dev_index)+" "+str(value_index)+" "+ str(self.QBPM_average_index[dev_index])+" "+str(self.QBPM_values)+" "+str(results)+"\n")
                                write_logfile(time.ctime()+" "+str(dev_index)+" "+str(value_index)+" "+ str(self.QBPM_average_index[dev_index])+"\n")
                        self.QBPM_average_index[dev_index]+=1
                        if not True in self.QBPM_fb_active[dev_index]:
                            break
                    else:
                        print "Error reading QBPM?"
                        write_logfile(time.ctime()+" Error reading QBPM?\n")
                        break
                    
                    
                    
                    
                if self.QBPM_average_index[dev_index]>=self.QBPM_n_averages:
                    if self.QBPM_feedback_status in [0,2,3]:
                        for value_index in range(3):
##                            print dev_index,value_index,self.QBPM_values[dev_index][value_index]
                            self.QBPM_means[dev_index][value_index]=numpy.mean(self.QBPM_values[dev_index][value_index])
                            self.QBPM_stddevs[dev_index][value_index]=numpy.std(self.QBPM_values[dev_index][value_index])

                    elif self.QBPM_feedback_status==1:
                        for value_index in range(3):
                            self.QBPM_sets[dev_index][value_index]=numpy.mean(self.QBPM_values[dev_index][value_index])
                            self.QBPM_sets_stddevs[dev_index][value_index]=numpy.std(self.QBPM_values[dev_index][value_index])
                            
                        print "Initialized "+str(self.QBPM_device_list[dev_index])+" with "+\
                              str(self.QBPM_sets[dev_index])+" +- "+str(self.QBPM_sets_stddevs[dev_index])
                        write_logfile(time.ctime()+" Initialized "+str(self.QBPM_device_list[dev_index])+\
                                      " with "+str(self.QBPM_sets[dev_index])+" +- "+str(self.QBPM_sets_stddevs[dev_index])+"\n")


                        switch_feedback_on=True

                    for value_index in range(3):                           
                        if self.QBPM_feedback_status==1:
                            print self.QBPM_device_list[dev_index],self.QBPM_labels[dev_index][value_index],
                            write_logfile(time.ctime()+" "+self.QBPM_device_list[dev_index]+" "+self.QBPM_labels[dev_index][value_index])
                            if not self.QBPM_fb_active[dev_index][value_index]:
                                print ": feedback is off"
                                write_logfile(": feedback is off\n")
                            else:
                                print ": is coupled to",self.QBPM_fb_device_list[dev_index][value_index],"by",self.QBPM_P[dev_index][value_index],"between the limits",self.QBPM_fb_margins[dev_index][value_index]
                                dev=PyTango.DeviceProxy(self.QBPM_fb_device_list[dev_index][value_index])
                                pos=SmallForm2.read_tangodevice(dev,"Position")
                                backlash=SmallForm2.read_tangodevice(dev,"UnitBacklash")
                                write_logfile(": is coupled to "+self.QBPM_fb_device_list[dev_index][value_index]+" by "+str(self.QBPM_P[dev_index][value_index])+" between the limits "+str(self.QBPM_fb_margins[dev_index][value_index])+"\n")
                                print "Position of",self.QBPM_fb_device_list[dev_index][value_index],"is",pos,", backlash is",backlash
                                write_logfile(time.ctime()+" Position of "+self.QBPM_fb_device_list[dev_index][value_index]+" is "+str(pos)+", backlash is"+str(backlash)+"\n")

                                    
                #if self.QBPM_average_index[dev_index]%self.QBPM_n_averages<self.QBPM_n_averages/2:
                if True:      
                    for value_index in range(3):    
                        self.QBPM_value_widgets[dev_index][value_index].setText("%1.3e / %1.3e"%(self.QBPM_means[dev_index][value_index],self.QBPM_sets[dev_index][value_index]))
                        
                    write_logfile(time.ctime()+" QBPM "+str(dev_index+1)+" updated to "+str(self.QBPM_means[dev_index])+"\n")
                else:
                    for value_index in range(3):    
                        self.QBPM_value_widgets[dev_index][value_index].setText("+-%1.1e / +-%1.1e"%(self.QBPM_stddevs[dev_index][value_index],self.QBPM_sets_stddevs[dev_index][value_index]))
     
                    
                        
            if switch_feedback_on:
                #print "Feedback is now active!"
                #write_logfile(time.ctime()+" Feedback is now active!\n")
                print "Feedback has now been initialized!"
                write_logfile(time.ctime()+" Feedback has now been initialized!\n")
                self.QBPM_feedback_status=0        
            """
                        
            check_beamline_status(self)
        except:
            print time.ctime(), " Exception in UpdateUI"
            write_logfile(time.ctime()+" Exception in UpdateUI\n")
            raise
        finally:
            self.busy=False    

    def play_message(self,level):
#        self.raise_()
#        self.activateWindow()
        self.show()
#        self.setFocus()
        if level==1:
            play("message1.wav")
#            play("Sequenz02_laut.wav")
        elif level==2:
            play("beamloss1.wav")
#            play("Sequenz01_laut.wav")

def fetch_url(url,timeout=1.5,retries=5):
    print("Fetching URL: %s" % url)
    try:
        result=urllib2.urlopen(url,None,timeout).readlines()
##        print "Fetch_URL:",url,"->",result
#        if not result==[" \n","LCL: success"]:
        if not result==[" \n","RMT: success"]:
            print "Result from ICS-Server is not what was expected!"
#            print [" \n","LCL: success"],"is not",result
            print [" \n","RMT: success"],"is not",result
            print "Calling again!"
            
            write_logfile(time.ctime()+" Result from ICS-Server is not what was expected!")
#            write_logfile(time.ctime()+" "+str([" \n","LCL: success"])+"is not"+str(result))
            write_logfile(time.ctime()+" "+str([" \n","RMT: success"])+"is not"+str(result))
            write_logfile(time.ctime()+" Calling again!")
            fetch_url(url,timeout=timeout)
    except:
        print "Exception while trying to fetch", url
        print "Calling again, retry ",retries,"!"
        write_logfile(time.ctime()+" Exception will trying to fetch "+str(url)+"\n")
        write_logfile(time.ctime()+" Calling again, retry "+str(retries)+"!")
        if retries>0:
            result=fetch_url(url,timeout=timeout,retries=retries-1)
        else:
            return None
            
    return result

# cxheck beamline status
def check_beamline_status(self,dev_threshold=0.05,minimum_current=10.,acctr_targetpath=""):
    BS_devlist=[]
    for BS_index in range(len(self.BS_list)):
        BS_devlist+=[[]]
        #print self.BS_list[BS_index]
        for BS in self.BS_list[BS_index]:
            #print BS,BS_devlist,PyTango.DeviceProxy(BS),BS_devlist[-1]
            BS_devlist[-1]+=[PyTango.DeviceProxy(BS)]
#    print BS_devlist
#    print "In check_beamline_status",self.busy
##    PETRAIII= PyTango.DeviceProxy("petra/globals/keyword")
    P3=PyTango.DeviceProxy(PETRAIII)

    current=SmallForm2.read_tangodevice(P3,"BeamCurrent")
    if self.current is None and current>minimum_current:
        self.current=current
    
    # check for beamlossby tracking deviation
    if not current is None and current>minimum_current:
        deviation=(self.current-current)/self.current
    else:
        deviation=0.
    if deviation>dev_threshold and self.current>minimum_current:
        print time.ctime(), " Warning! Deviation of current too large! Probable loss of beam!"
        write_logfile(time.ctime()+" Warning! Deviation of current too large! Probable loss of beam!\n")
        self.play_message(2)

    # check TopUp
    TopUp=SmallForm2.read_tangodevice(P3,"TopUpStatus")
    if self.TopUp is None:
        self.TopUp=TopUp
        self.TopUp_str=SmallForm2.read_tangodevice(P3,"TopUpStatusText")
        if self.TopUp_str is None:
            self.TopUp_str="None"
            
    new_TopUp_str=SmallForm2.read_tangodevice(P3,"TopUpStatusText")
    if new_TopUp_str is None:
        new_TopUp_str="None"
    else:
        new_TopUp_str=str(new_TopUp_str)            
    if self.current>minimum_current and not TopUp is None and self.TopUp!=TopUp:
        print time.ctime(), " Warning! Top Up mode has changed from ",self.TopUp_str," to ",new_TopUp_str
        write_logfile(time.ctime()+" Warning! Top Up mode has changed from "+self.TopUp_str+" to "+new_TopUp_str+"\n")

    # check orbit status
    FOFB=SmallForm2.read_tangodevice(P3,"FastOrbitFBStatus")
    if self.FOFB is None:
        self.FOFB=FOFB
        self.FOFB_str=SmallForm2.read_tangodevice(P3,"FastOrbitFBStatusText")        
    if self.current>minimum_current and not FOFB is None and self.FOFB!=FOFB:
        print time.ctime(), " Warning! Fast Orbit Feedback mode has changed from ",self.FOFB_str," to ",SmallForm2.read_tangodevice(P3,"FastOrbitFBStatusText")
        write_logfile(time.ctime()+" Warning! Fast Orbit Feedback mode has changed from "+self.FOFB_str+" to "+str(SmallForm2.read_tangodevice(P3,"FastOrbitFBStatusText"))+"\n")
   
    # something else - BS - shutters?
    BS_open=[]
    for BS_index in range(len(self.BS_list)):
#        print BS_devlist[BS_index][0]
#        print self.BS_attrib_list[BS_index]
        BS_open+=[SmallForm2.read_tangodevice(BS_devlist[BS_index][0],self.BS_attrib_list[BS_index])]
        if self.BS_open[BS_index] is None:
            self.BS_open[BS_index]=BS_open[BS_index]
        if self.beam_in_hutch[BS_index] is None:
            if BS_open[BS_index]==0:
                self.beam_in_hutch[BS_index]=True
                self.keep_BS_open[BS_index]=True
            else:
                self.beam_in_hutch[BS_index]=False
                self.keep_BS_open[BS_index]=False
        update_buttons()

            
        if self.current>minimum_current and not BS_open[BS_index] is None and self.BS_open[BS_index]!=BS_open[BS_index]:
            if BS_open[BS_index]==0:
                print time.ctime(), " P02 beamshutter BS"+str(BS_index)+" has been opened."
                write_logfile(time.ctime()+" P02 beamshutter BS"+str(BS_index)+" has been opened.\n")
            else:
                print time.ctime(), " Warning! P02 beamshutter BS"+str(BS_index)+" has been closed!"
                write_logfile(time.ctime()+" Warning! P02 beamshutter BS"+str(BS_index)+" has been closed!\n")
                
                print "Stopping experiment now!"
                write_logfile(time.ctime()+" Stopping experiment now!\n")
                os.system('scp %s %s:%s' % ("stop.txt", "haspP02nc1", "breakScan.brk"))
                self.play_message(1)
        update_buttons()

#    print self.BS_open,BS_open
    permit_experiment=FOFB==1 and current>minimum_current and BS_open==[0,0,0]
    if self.permit_experiment!=permit_experiment:
        if permit_experiment:
            print "Permitting experiment now!"
##            print 'scp %s %s:%s' % ("permit.txt", "haspP02nc1", "breakScan.brk.test")
            write_logfile(time.ctime()+" Permitting experiment now!\n")
##            write_logfile(time.ctime()+" scp "%s" "%s:%s"" % ("permit.txt", "haspP02nc1", "breakScan.brk.test")+"\n")
            os.system('scp %s %s:%s' % ("permit.txt", "haspP02nc1", "breakScan.brk"))
        else:
            print "Stopping experiment now!"
##            print 'scp %s %s:%s' % ("stop.txt", "haspP02nc1", "breakScan.brk.test")
            write_logfile(time.ctime()+" Stopping experiment now!\n")
##            write_logfile(time.ctime()+' scp "%s" "%s:%s"' % ("stop.txt", "haspP02nc1", "breakScan.brk.test")+"\n")
            os.system('scp %s %s:%s' % ("stop.txt", "haspP02nc1", "breakScan.brk"))
                

        
##    print self.current,self.TopUp,self.TopUp_str,self.FOFB,self.FOFB_str,deviation
    if not current is None:
        self.current=current
    if not TopUp is None:
        self.TopUp=TopUp  
    if not current is None:
        self.TopUp_str=new_TopUp_str
    if not FOFB is None:
        self.FOFB=FOFB
    FOFB_str=SmallForm2.read_tangodevice(P3,"FastOrbitFBStatusText")
    if not FOFB_str is None:
        self.FOFB_str=FOFB_str
    for BS_index in range(len(self.BS_list)):
        if not BS_open[BS_index] is None:
            self.BS_open[BS_index]=BS_open[BS_index]
    if not permit_experiment is None:
        self.permit_experiment=permit_experiment


    for BS_index in range(len(self.BS_list)):
        if self.hutch_modification[BS_index]=="Enable beam operation":
            print "Will now start to try to keep BS"+str(BS_index)+" open."
            write_logfile(time.ctime()+" Will now start to try to keep BS"+str(BS_index)+" open.\n")            
            self.keep_BS_open[BS_index]=True
            self.beam_in_hutch[BS_index]=True
        elif self.hutch_modification[BS_index]=="Stop beam operation":
            self.keep_BS_open[BS_index]=False
            self.beam_in_hutch[BS_index]=False
            
            # feedback
            """if self.QBPM_feedback_status == 1:
                initialize_feedback() # will actually stop it
            elif self.QBPM_feedback_status == 2 and BS_index==0:
                start_mono_feedback() # will actually stop it
            elif self.QBPM_feedback_status == 3 and BS_index!=2:
                start_micro_feedback() # will actually stop it"""
                
                
            print "Closing BS"+str(BS_index)+" now!"
            write_logfile(time.ctime()+" Closing BS"+str(BS_index)+" now!\n")
            update_buttons()
            fetch_url(self.ics_url+"action=closebs&shutter=06_"+str(BS_index))          # url to close
            while True:     
                BS_closed=SmallForm2.read_tangodevice(PyTango.DeviceProxy(self.BS_list[BS_index][1]),self.BS_attrib_list[BS_index])
                print "BS_closed:",BS_closed
                if BS_closed==3:
                    break
                print "Closing BS"+str(BS_index)+" now!"
                write_logfile(time.ctime()+" Closing BS"+str(BS_index)+" now!\n")            
                fetch_url(self.ics_url+"action=closebs&shutter=06_"+str(BS_index))      # url to close
                time.sleep(0.5)
            
            if BS_index==0:
                print "BS"+str(BS_index)+" should be closed now."
                write_logfile(time.ctime()+" BS"+str(BS_index)+" should be closed now.\n")
                print "Not breaking the area, because two hutches are attached to BS0."
                write_logfile(time.ctime()+" Not breaking the area, because two hutches are attached to BS0.\n")
            else:
                print "BS"+str(BS_index)+" should be closed now - breaking the interlock of the area!"
                write_logfile(time.ctime()+" BS"+str(BS_index)+" should be closed now - breaking the interlock of the area!\n")
                
                fetch_url(self.ics_url+"action=breakinterlock&area=06_"+str(BS_index+1))    # break interlock
                time.sleep(2.5)
                fetch_url(self.ics_url+"action=breakinterlock&area=06_"+str(BS_index+1))
                time.sleep(2.5)
                fetch_url(self.ics_url+"action=breakinterlock&area=06_"+str(BS_index+1))
                time.sleep(5.)
                fetch_url(self.ics_url+"action=breakinterlock&area=06_"+str(BS_index+1))
                 
##                PyTango.DeviceProxy("P02/ics/1").BreakInterlock(BS_index+1)
        self.hutch_modification[BS_index]=""
        update_buttons()


        if self.keep_BS_open[BS_index] and self.BS_open[BS_index]!=0:
            print "Trying to open BS"+str(BS_index)+"."
    ##        print "before ICS-call",self.ics_url+"action=openbs&shutter=06_2"
            fetch_url(self.ics_url+"action=openbs&shutter=06_"+str(BS_index))           # open interlock
    ##        print "after ICS-call"
            write_logfile(time.ctime()+" Shutter BS"+str(BS_index)+" is not open!\n")               
            write_logfile(time.ctime()+" Trying to open BS"+str(BS_index)+".\n")
            update_buttons()
            #time.sleep(3)
    #    print "Params:",self.beam_in_OH,self.keep_BS0_open,self.beam_in_EH1,self.keep_BS1_open,self.beam_in_EH2,self.keep_BS2_open,self.permit_experiment
        update_buttons()
    
    #feedback
    """
    for dev_index in range(len(self.QBPM_device_list)):
        if self.QBPM_feedback_status in [2,3] and self.QBPM_average_index[dev_index]>=self.QBPM_n_averages and current>minimum_current:        
            for value_index in range(3):
                if self.QBPM_means[dev_index][2]<self.QBPM_minimum_current[dev_index]:
                    print "Current in QBPM too small, not moving!",self.QBPM_means[dev_index][2],self.QBPM_minimum_current[dev_index]
                    write_logfile(time.ctime()+" Current in QBPM too small, not moving!" +str(self.QBPM_means[dev_index][2])+" "+str(self.QBPM_minimum_current[dev_index])+"\n")
                elif self.QBPM_fb_active[dev_index][value_index]:
                    fb_device=PyTango.DeviceProxy(self.QBPM_fb_device_list[dev_index][value_index])
                    #print dev_index,value_index,self.QBPM_P[dev_index][value_index],
                    deviation=(self.QBPM_sets[dev_index][value_index]-self.QBPM_means[dev_index][value_index])
                    #print deviation,
                    fb_device_pos=SmallForm2.read_tangodevice(fb_device,"Position")
                    #print fb_device_pos,
                    change=self.QBPM_P[dev_index][value_index]*deviation*fb_device_pos
                    #print change,change+fb_device_pos#,self.QBPM_fb_margins[dev_index][value_index],
                    #print self.QBPM_fb_margins[dev_index][value_index][0]<change+fb_device_pos<self.QBPM_fb_margins[dev_index][value_index][1]
                    if not self.QBPM_fb_margins[dev_index][value_index][0]<change+fb_device_pos<self.QBPM_fb_margins[dev_index][value_index][1]:
                        print "Movement would be too large, not moving!"
                        write_logfile(time.ctime()+" Movement would be too large, not moving!\n")
                    elif abs(change)<self.QBPM_fb_minimum_change[dev_index][value_index]:
                        print "Movement too small, not moving!", change,self.QBPM_fb_minimum_change[dev_index][value_index]
                        write_logfile(time.ctime()+" Movement too small, not moving!" +str(change)+" "+str(self.QBPM_fb_minimum_change[dev_index][value_index])+"\n")
                    else:
                        move_wo_backlash(fb_device,change+fb_device_pos)
        if self.QBPM_average_index[dev_index]>=self.QBPM_n_averages:
            self.QBPM_average_index[dev_index]=0"""

# stupid thins - modifies buttons?
def modify_area(area):
    if form.beam_in_hutch[area]:
        form.hutch_modification[area]="Stop beam operation"
    else:
        form.hutch_modification[area]="Enable beam operation"
    update_buttons()
            
# initialize feedback
def initialize_feedback():
##    print "In modify feedback"
##    print form.QBPM_feedback_status,"==>",
    if form.QBPM_feedback_status in [0,2,3]:
        form.QBPM_feedback_status=1
        print
        print "Will now initialize both QBPM-feedbacks."
        print "Could typically take up to 10 seconds ..."
        print
        write_logfile(time.ctime()+"Will now initialize both QBPM-feedbacks.\n")
        write_logfile(time.ctime()+"Could typically take up to 10 seconds ...\n")
##    print form.QBPM_feedback_status
    else:
        form.QBPM_feedback_status=0
        print
        print "Stopping QBPM-feedback initialization!"
        print 
        write_logfile(time.ctime()+"Stopping QBPM-feedback initialization!\n")
    update_buttons()
        

# mono feedback
def start_mono_feedback():
##    print "In modify feedback"
##    print form.QBPM_feedback_status,"==>",
    if form.QBPM_feedback_status in [2]:
        form.QBPM_feedback_status=0
        print
        print "Stopping Mono-QBPM-feedback!"
        print 
        write_logfile(time.ctime()+"Stopping Mono-QBPM-feedback!\n")
    else:
        form.QBPM_feedback_status=2        
        form.QBPM_fb_active=[[False,True,False],[False,False,False]] # only vertical feedback
	form.QBPM_fb_active=[[True,True,False],[False,False,False]] # vertical+horizontal feedback
	
        print
        print "Will now start Mono-QBPM-feedback."
        print "Could typically take up to "+str(form.QBPM_n_averages)+" seconds ..."
        print
        write_logfile(time.ctime()+"Will now start Mono-QBPM-feedback.\n")
        write_logfile(time.ctime()+"Could typically take up to "+str(form.QBPM_n_averages)+" seconds ...\n")
##    print form.QBPM_feedback_status
    update_buttons()


# micro feedback
def start_micro_feedback():
##    print "In modify feedback"
##    print form.QBPM_feedback_status,"==>",
    if form.QBPM_feedback_status in [3]:
        form.QBPM_feedback_status=0
        print
        print "Stopping Micro-QBPM-feedback!"
        print 
        write_logfile(time.ctime()+"Stopping Micro-QBPM-feedback!\n")
    else:
        form.QBPM_feedback_status=3
        form.QBPM_fb_active=[[False,False,False],[False,True,False]]   # for right QBMP-Micro cabeling, only vertical
        #form.QBPM_fb_active=[[False,False,False],[True,False,False]]   # taking into account y-z-swap in Micro-QBPM      
	form.QBPM_fb_active=[[False,False,False],[True,True,False]] # vertical+horizontal feedback	
        print
        print "Will now start Micro-QBPM-feedback."
        print "Could typically take up to "+str(form.QBPM_n_averages)+" seconds ..."
        print
        write_logfile(time.ctime()+"Will now start Micro-QBPM-feedback.\n")
        write_logfile(time.ctime()+"Could typically take up to "+str(form.QBPM_n_averages)+" seconds ...\n")
##    print form.QBPM_feedback_status
    update_buttons()

# moving without backlash? probably for feedback
def move_wo_backlash(device,pos):
    try:
        old_backlash=SmallForm2.read_tangodevice(device,"UnitBacklash")
##        print "Old Backlash:",old_backlash
        while SmallForm2.read_tangodevice(device,"UnitBacklash")!=0.:
##            print "Still not 0"
            while not device.state()==PyTango.DevState.ON:
                time.sleep(0.01)
            device.write_attribute("UnitBacklash",0.)
##        print "Not actually moving!"
##        print "Would move to ",pos
        print "QBPM-feedback moving",device.name(),"to",pos #,". QBPM positions: ",str(self.QBPM_means),str(self.QBPM_stddevs)
        write_logfile(time.ctime()+" QBPM-feedback moving "+device.name()+" to "+str(pos)+"\n") #. QBPM positions: "+str(self.QBPM_means)+str(self.QBPM_stddevs)+"
        while not device.state()==PyTango.DevState.ON:
            time.sleep(0.01)            
        device.write_attribute("Position",pos)
    except:                  
        print "Exception in move_wo_backlash!"
        print device,pos                 
        write_logfile(time.ctime()+"Exception in move_wo_backlash!\n")
        write_logfile(time.ctime()+str(device)+" "+str(pos)+"\n")
    finally:
        while not device.state()==PyTango.DevState.ON:
            time.sleep(0.01)
        device.write_attribute("UnitBacklash",old_backlash)
                      


                
def myexit(expired_time):
    pyglet.app.exit() 


def play(filename,delaytime=4):
        print "Sound disabled!"
        return
##    try:
        sound = pyglet.media.load(filename, streaming=False)
        sound.play()
        pyglet.clock.schedule_once(myexit, delaytime)
        pyglet.app.run()
##        time.sleep(delaytime)
##    except WindowsError:
##        pass


def write_logfile(message):
    logfile=open(logfile_name,"a")
    logfile.writelines([message])
    logfile.close()
    

def update_buttons():

    buttons=[form.pb10,form.pb20,form.pb30, form.pb40]
    
    for BS_index in range(len(form.BS_list)):
        buttons[BS_index].setAutoFillBackground(True)
        buttons[BS_index].setAutoDefault(False)
        if form.beam_in_hutch[BS_index]: 
            buttons[BS_index].setText(button_labels[BS_index][0])
            if form.BS_open[BS_index]==3:
            #if form.BS_open[BS_index]==1:
##                print "Setting button ",BS_index," to yellow!"
               buttons[BS_index].setStyleSheet("background-color: rgb(255, 240, 0); color: rgb(0, 0, 0)");
            elif form.BS_open[BS_index]==0:
##                print "Setting button ",BS_index," to red!"
                buttons[BS_index].setStyleSheet("background-color: rgb(255, 0, 0); color: rgb(255, 255, 255)");
        else:
            buttons[BS_index].setText(button_labels[BS_index][1])
##            print "Setting button ",BS_index," to green!"
            buttons[BS_index].setStyleSheet("background-color: rgb(0, 200, 0); color: rgb(0, 0, 0)");

    # feedback
    """form.pbqbpm.setAutoFillBackground(True)
    form.pbqbpm.setAutoDefault(False)
    if form.QBPM_feedback_status==1:
        form.pbqbpm.setText("Stop initialization")
        form.pbqbpm.setStyleSheet("background-color: rgb(255, 240, 0); color: rgb(0, 0, 0)");
    elif form.QBPM_feedback_status in [0,2,3]:
        form.pbqbpm.setText("Initialize QBPM-feedback ")
        form.pbqbpm.setStyleSheet("background-color: rgb(0, 200, 0); color: rgb(0, 0, 0)");
    else:
        raise ValueError
    
    form.pbqbpm2.setAutoFillBackground(True)
    form.pbqbpm2.setAutoDefault(False)            
    if form.QBPM_feedback_status ==2:
        form.pbqbpm2.setText("Stop Mono-QBPM-feedback")
        form.pbqbpm2.setStyleSheet("background-color: rgb(255, 0, 0); color: rgb(255, 255, 255)");
    elif form.QBPM_feedback_status in [0,1,3]:
        form.pbqbpm2.setText("Start Mono-QBPM-feedback")
        form.pbqbpm2.setStyleSheet("background-color: rgb(0, 200, 0); color: rgb(0, 0, 0)");
    else:
        raise ValueError
    
    form.pbqbpm3.setAutoFillBackground(True)
    form.pbqbpm3.setAutoDefault(False)            
    if form.QBPM_feedback_status==3:
        form.pbqbpm3.setText("Stop Micro-QBPM-feedback")
        form.pbqbpm3.setStyleSheet("background-color: rgb(255, 0, 0); color: rgb(255, 255, 255)");
    elif form.QBPM_feedback_status in [0,1,2]:
        form.pbqbpm3.setText("Start Micro-QBPM-feedback")
        form.pbqbpm3.setStyleSheet("background-color: rgb(0, 200, 0); color: rgb(0, 0, 0)");
    else:
        raise ValueError"""


    form.show()
    form.repaint()
    form.update()
    form.repaint()
    form.show()
        

def add_beam_control_buttons(self):

    self.pb10=QtGui.QPushButton("")
    self.pb10.setAutoDefault(False)
    self.pb10.setWindowFlags(QtCore.Qt.SplashScreen)
    self.pb10_wrapper=functools.partial(modify_area,0)
    self.connect(self.pb10,QtCore.SIGNAL("clicked()"),self.pb10_wrapper)
  
    self.pb20=QtGui.QPushButton("")
    self.pb20.setAutoDefault(False)
    self.pb20.setWindowFlags(QtCore.Qt.SplashScreen)
    self.pb20_wrapper=functools.partial(modify_area,1)
    self.connect(self.pb20,QtCore.SIGNAL("clicked()"),self.pb20_wrapper)
    
    self.pb30=QtGui.QPushButton("")
    self.pb30.setAutoDefault(False)
    self.pb30.setWindowFlags(QtCore.Qt.SplashScreen)
    self.pb30_wrapper=functools.partial(modify_area,2)
    self.connect(self.pb30,QtCore.SIGNAL("clicked()"),self.pb30_wrapper)
    
    self.pb40=QtGui.QPushButton("")
    self.pb40.setAutoDefault(False)
    self.pb40.setWindowFlags(QtCore.Qt.SplashScreen)
    self.pb40_wrapper=functools.partial(modify_area,3)
    self.connect(self.pb40,QtCore.SIGNAL("clicked()"),self.pb40_wrapper)
    
    # feedback
    """self.pbqbpm=QtGui.QPushButton("")
    self.pbqbpm.setAutoDefault(False)
    self.pbqbpm.setWindowFlags(QtCore.Qt.SplashScreen)
    self.pbqbpm_wrapper=functools.partial(initialize_feedback)
    self.connect(self.pbqbpm,QtCore.SIGNAL("clicked()"),self.pbqbpm_wrapper)
    
    self.pbqbpm2=QtGui.QPushButton("")
    self.pbqbpm2.setAutoDefault(False)
    self.pbqbpm2.setWindowFlags(QtCore.Qt.SplashScreen)
    self.pbqbpm2_wrapper=functools.partial(start_mono_feedback)
    self.connect(self.pbqbpm2,QtCore.SIGNAL("clicked()"),self.pbqbpm2_wrapper)
    
    self.pbqbpm3=QtGui.QPushButton("")
    self.pbqbpm3.setAutoDefault(False)
    self.pbqbpm3.setWindowFlags(QtCore.Qt.SplashScreen)
    self.pbqbpm3_wrapper=functools.partial(start_micro_feedback)
    self.connect(self.pbqbpm3,QtCore.SIGNAL("clicked()"),self.pbqbpm3_wrapper)"""

    self.layout.addWidget(self.pb10,self.n_rows+1,0)
    self.layout.addWidget(self.pb20,self.n_rows+2,0)
    self.layout.addWidget(self.pb30,self.n_rows+3,0)
    self.layout.addWidget(self.pb40,self.n_rows+4,0)
    
    # feedback
    """self.layout.addWidget(self.pbqbpm,self.n_rows+4,0)
    self.layout.addWidget(self.pbqbpm2,self.n_rows+5,0)
    self.layout.addWidget(self.pbqbpm3,self.n_rows+6,0)"""
    
    self.setLayout(self.layout)
    self.n_rows+=6


button_labels=[["Close frontend","Open frontend + keep frontend open"],
               ["Close BS1 + break EH1 interlock","Open BS1 + keep BS1 open"],
               ["Close BS2 + break EH2 interlock","Open BS2 + keep BS2 open"],
               ["Close BS2 + break EH2 interlock","Open BS2 + keep BS2 open"]]

       
                    
PETRAIII="petra/globals/keyword"
PETRAIII_UndBPos="petra/UndBPos/Zelle3"
VacuumInterlock="hasylab/vac.intlk/P02"
#BS0="hasylab/piconditions/bs06_0_offen"
#BS1="hasylab/piconditions/bs06_1_offen"
#BS2="hasylab/piconditions/bs06_2_offen"
BS0="P02/shutter/1"
BS1="P02/shutter/1"
BS2="P02/shutter/1"
BS3="P02/shutter/1"
QBPM="P02/i404/exp.01"
undulator="P02/undulator/1"
mono="P02/dcmener/oh.01"

App = QtGui.QApplication(sys.argv)
App.setFont(QtGui.QFont("Helvetica",16))


form = CurrentSmallForm(
            [PETRAIII,undulator,mono,VacuumInterlock,BS0,BS1,BS2,BS3], # device_list
               [["BeamCurrent","DeclaredState","MessageText","FastOrbitFBStatusText","TopUpStatusText"], # variable_list - for each device
	       ["Gap","Position"],
      	       ["Position"],
               ["FRONTEND_OFFEN"],
               ["ABS0OffenDisplayState"],
               ["BS0OffenDisplayState"],
               ["BSA1OffenDisplayState"],
               ["BSB1OffenDisplayState"]],
                
                # Defaults
                # parent=None,
                # interval=1000,
               
                label_list=[["beam current [mA]","PETRA state","BKR message","fast orbit feedback","top-up mode"], # label_list
                ["gap [mm]","gap [eV]"],
                ["mono energy [eV]"],
                ["frontend"],
                ["beamshutter 0"],
                ["beamshutter 1"],
                ["beamshutter 2"],
                ["beamshutter 3"]
                 ],
                
                value_dicts=[[None,None,None,{"Ein": "on","Aus":"off",None:"undefined","Unbestimmt":"undefined"},None], # value_dicts
                [None,None],[None],
                [{0:"closed",1:"open"}],
                [{3:"closed",0:"open",2:"fault2",5:"fault5",1:"countdown"}],
                [{3:"closed",0:"open",2:"fault2",5:"fault5",1:"countdown"}],
                [{3:"closed",0:"open",2:"fault2",5:"fault5",1:"countdown"}],
                [{3:"closed",0:"open",2:"fault2",5:"fault5",1:"countdown"}]],
                
                print_device_labels=False,  # print_device_labels
                
                ics_url="",    # ics_url
                
                BS_list=[["P02/shutter/1","P02/shutter/1"], # BS_list
                         ["P02/shutter/1","P02/shutter/1"],
                         ["P02/shutter/1","P02/shutter/1"],
                         ["P02/shutter/1","P02/shutter/1"]],
                         
                         
                BS_attrib_list=["ABS0OffenDisplayState","BS0OffenDisplayState","BSA1OffenDisplayState", "BSB1OffenDisplayState"]   # BS_attrib_list
                )


if os.name=='posix':
    path="./Log_ShutterControl/"
elif os.name=='nt':
    path="V:\\P02user\\Log_ShutterControl\\"
   

now_string = time.strftime("%Y-%m-%d %H-%M")
logfile_name=path+"ShutterControl_Log_"+now_string+".txt"
print time.ctime(), " Starting up ..."
write_logfile(time.ctime()+" Starting up ...\n")


add_beam_control_buttons(form)

form.show()
buttons=[form.pb10,form.pb20,form.pb30]
App.exec_()

