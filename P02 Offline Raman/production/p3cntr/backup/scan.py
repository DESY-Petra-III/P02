#define scan macros for HASYLAB control system
import PyTango
import time
import numpy

import environment as env

from abstract import *
from motor import *
from counter import *
from detector import *
from measurement_group import *

def ct(dtime,MG=None):

    if MG is None:
        MG = env.Default_Measurement_Group
        
    old_sampletime = MG.sampletime
    MG.sampletime = dtime
    print old_sampletime
    print MG.sampletime
    print MG.timer._proxy.read_attribute("SampleTime").value
    counter_data,detector_data=MG.acquire()
    MG.sampletime = old_sampletime
    print old_sampletime
    print MG.sampletime
    print MG.timer._proxy.read_attribute("SampleTime").value
    return counter_data,detector_data


def mv(*args,**kwargs):
    if "block" not in kwargs:
        block = False
    else:
        block = kwargs["block"]
    
    if len(args)%2!=0:
        print "wrong number of arguments!"
        return None

    n = len(args)
    for i in range(0,n,2):
        args[i].move(args[i+1],block=False)

    if block:
        _wait_until_motors_arrived(*args)
    else:
        print "Caution - Motor(s) is/are now moving - returning to CLI!"

def mvr(*args,**kwargs):
    
    if "block" not in kwargs:
        block = False
    else:
        block = kwargs["block"]
        
    if len(args)%2!=0:
        print "wrong number of arguments!"
        return None
    n = len(args)

    mv_args=list(args)
    for i in range(0,n,2):
        mv_args[i+1]+=args[i].pos

    mv_args=tuple(mv_args)
    mv(*mv_args,block=block)
        

def aNscan(*args,**kwargs):
    
    if len(args)%3!=2:
        print "wrong number of arguments!"
        return None


    if "MG" in kwargs:
        MG = kwargs["MG"]
    else:
        MG = env.Default_Measurement_Group

    
    steps=args[-2]
    itime=args[-1]

    n = len(args)-2  ## 3 args per motor, plus steps + integration time
    
    for i in range(0,n,3):
        if not isinstance(args[i],Motor):
            raise ValueError,"first argument must be a motor instance!"

        if not (isinstance(args[i+1],float) or isinstance(args[i+1],int)):
            raise ValueError,"start position must be float or int"
        
        if not (isinstance(args[i+2],float) or isinstance(args[i+2],int)):
            raise ValueError,"end position must be float or int"
        
    if not isinstance(steps,int):
        raise ValueError,"steps must be an int"
        
    if not (isinstance(itime,float) or isinstance(itime,int)):
        raise ValueError,"integration time must be float or int"

    pos=[]
    for i in range(0,n,3):
        dpos = (float(args[i+2])-float(args[i+1]))/float(steps)
        pos += [numpy.arange(float(args[i+1]),float(args[i+2])+dpos,dpos)]

        
    print "Starting to move!"
    print
    for i in range(0,n,3):
        print args[i].name,'\t',
    for i in range(len(MG.counters)):
        print MG.counters[i].name,'\t',
    print
    print

    MG.sampletime=itime
    all_counter_data = []
    all_detector_data = []

    for s in range(steps+1):
        mv_args = []
        for i in range(0,n,3):
            mv_args+=[args[i],pos[i/3][s]]
        
        mv_args = tuple(mv_args)
        mv(*mv_args,block=True)
        counter_data,detector_data = MG.acquire()
        
        for i in range(0,n,3):
            print args[i].pos,'\t',
        for i in range(len(MG.counters)):
            print counter_data[i],'\t',
        print

        # write counter and detector-data line by line either here
        all_counter_data += [counter_data]
        all_detector_data += [detector_data]
    # or write them here in total. Should depend on write-mode
    return all_counter_data,all_detector_data



def dNscan(*args,**kwargs):
    if len(args)%3!=2:
        print "wrong number of arguments!"
        return None  

    aNscan_args=list(args)
    print aNscan_args

    n = len(args)-2  ## 3 args per motor, plus steps + integration time
    
    for i in range(0,n,3):
        if not isinstance(args[i],Motor):
            raise ValueError,"first argument must be a motor instance!"

        if not (isinstance(args[i+1],float) or isinstance(args[i+1],int)):
            raise ValueError,"start position must be float or int"
        
        if not (isinstance(args[i+2],float) or isinstance(args[i+2],int)):
            raise ValueError,"end position must be float or int"

        aNscan_args[i+1]+=args[i].pos
        aNscan_args[i+2]+=args[i].pos
    aNscan_args=tuple(aNscan_args)
    aNscan(*aNscan_args,**kwargs)


def ascan(mot,ipos,epos,steps,itime,**kwargs):
    args=(mot,ipos,epos,steps,itime)
    all_counter_data,all_detector_data = aNscan(*args,**kwargs)
    return all_counter_data,all_detector_data

    
def a2scan(mot1,ipos1,epos1,mot2,ipos2,epos2,steps,itime,**kwargs):
    args=(mot1,ipos1,epos1,mot2,ipos2,epos2,steps,itime)
    all_counter_data,all_detector_data = aNscan(*args,**kwargs)
    return all_counter_data,all_detector_data


def a3scan(mot1,ipos1,epos1,mot2,ipos2,epos2,
           mot3,ipos3,epos3,steps,itime,**kwargs):
    args=(mot1,ipos1,epos1,mot2,ipos2,epos2,
           mot3,ipos3,epos3,steps,itime)
    all_counter_data,all_detector_data = aNscan(*args,**kwargs)
    return all_counter_data,all_detector_data

def dscan(mot,ipos,epos,steps,itime,**kwargs):
    args=(mot,ipos,epos,steps,itime)
    all_counter_data,all_detector_data = dNscan(*args,**kwargs)
    return all_counter_data,all_detector_data

    
def d2scan(mot1,ipos1,epos1,mot2,ipos2,epos2,steps,itime,**kwargs):
    args=(mot1,ipos1,epos1,mot2,ipos2,epos2,steps,itime)
    all_counter_data,all_detector_data = dNscan(*args,**kwargs)
    return all_counter_data,all_detector_data


def d3scan(mot1,ipos1,epos1,mot2,ipos2,epos2,
           mot3,ipos3,epos3,steps,itime,**kwargs):
    args=(mot1,ipos1,epos1,mot2,ipos2,epos2,
           mot3,ipos3,epos3,steps,itime)
    all_counter_data,all_detector_data = dNscan(*args,**kwargs)
    return all_counter_data,all_detector_data


def mesh(mot1,ipos1,epos1,steps1,mot2,ipos2,epos2,steps2,itime,**kwargs):
    pass


def mesh3(mot1,ipos1,epos1,steps1,mot2,ipos2,epos2,steps2,
          mot3,ipos3,epos3,steps3,itime,**kwargs):
    pass


def _wait_until_motors_arrived(*args,**kwargs):
##    print "Waiting for motors to reach final position ...",
    if "dtime" not in kwargs:
        dtime = 0.2
    else:
        dtime = kwargs["dtime"]
    
##    print args
    motor_list=[]
    for arg in args:
##        print arg,isinstance(arg,Motor)
        if isinstance(arg,Motor):
            motor_list+=[arg]
##        print motor_list
##        print
##    print motor_list
##    raw_input()
    all_motors_have_arrived = False
    while not all_motors_have_arrived:
        all_motors_have_arrived = True
        for m in motor_list:
##            print m.name,m._proxy.state()
            if m._proxy.state()==PyTango.DevState.MOVING:
                all_motors_have_arrived = False
                break

##        print all_motors_have_arrived            
        if not all_motors_have_arrived:
            time.sleep(dtime)
##    print "they arrived!"

##m1 = Motor("Arsch","Scheissmotor","p06/motor/exp.01")
##m2 = Motor("Arsch2","Scheissmotor2","p06/motor/exp.02")
##
##print m1
##print m2

# TEST mvr
##mvr(m1,+5.555,m2,-2.222)
##
##print m1
##print m2

# TEST aNscan
##aNscan(m2,-0.5,0.5,m1,-1.5,-0.5,10,0.1)

## This fails because m1 is slower than m2,
## and is thus being tried to move before
## it reaches the initial position
##aNscan(m1,-0.5,0.5,m2,-1.5,-0.5,10,0.1)

# TEST ascan + a2scan via aNscan
##ascan(m2,-0.5,0.5,10,0.1,det=["MarCCD","Ionikammer","XMAP"])
##a2scan(m2,-0.5,0.5,m1,-10,10,10,0.1,det=["MarCCD","Ionikammer","XMAP"])


# Test dNscan via aNscan
##dNscan(m2,-0.5,0.5,m1,-1.5,-0.5,10,0.1)

