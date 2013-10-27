"""
Defines all macro types, that can be executed or saved as macro step
"""

# import from global packages 
from numpy import arange
from time import sleep, time

from Revolver.classes import devices, config

# global flag: stop macro
STOP = False

# constant: wait at least MACRO_DARK_WAIT seconds, then take dark
MACRO_DARK_WAIT = 5

def macroRange(start, end, step):
    """
    Creates range from start to end, creates float range
    @type start: float
    @type end: float
    @type step: float
    @rtype: list
    """
    if start <= end:
        mrange = list(arange(start, end, step))
    else:
        mrange = list(reversed(arange(end, start, step)))
    if(mrange[-1] != end):
        mrange.append(end)
    if(mrange[0] != start):
        mrange.insert(0, start)
    return mrange
       
class Macro(object):
    """
    Default macro class, other macro is derived from this class
    """
    def __init__(self):
        self.emit = None
        
    def run(self):
        """
        Main macro execution rutine
        """
        pass
    
    def wait_seconds(self, seconds=None):
        """
        Wait for specified time.
        Break if stopMacro changes to True.
        """
        if not seconds: seconds = self.wait
        if seconds <= 0: return
        step = float(100 / float(seconds))
        self.emit("showTimeProgress", flag=True)
        self.emit("setWaitProgress", 0)
        self.emit("macroOperation", "Waiting %i seconds" % seconds)
        for i in range(seconds):
            if STOP == True: break
            sleep(1)
            self.emit("setWaitProgress", (i + 1) * step)   
        self.emit("showTimeProgress", flag=False)    

class DarkShotMacro(Macro):
    def __init__(self, summed):
        """
        Class constructor:
        @type summed: int
        """
        super(DarkShotMacro, self).__init__()
        self.summed = summed
        
    def run(self, substractTime=0):
        """
        Execute macro step
        """
        detector = devices.Detector(config.DEVICE_DETECTOR)
        shutter = devices.Shutter(config.DEVICE_SHUTTER)
        self.wait_seconds(MACRO_DARK_WAIT - substractTime)
        
        self.emit("macroOperation", "Taking dark")
        detector.take_dark(shutter, self.summed)
        
class MotorMacro(Macro):
    """
    Motor device macro.
    Move motor to defined position, take a shot, than wait for specified time and end.
    """
    def __init__(self, motorAlias, motorDevice, sampleName, summed, filesafter, position, wait, takeDark, comment=None):
        """
        Class constructor:
        @type motorAlias: String
        @type motorDevice: String
        @type sampleName: String
        @type summed: int
        @type filesafter: int
        @type position: float
        @type wait: int
        @type comment: String 
        """
        super(MotorMacro, self).__init__()
        self.motorDevice = motorDevice
        self.motorAlias = motorAlias
        self.sampleName = sampleName
        self.summed = summed
        self.filesafter = filesafter
        self.wait = wait
        self.comment = comment
        self.position = position
        self.takeDark = takeDark
    
    def run(self, lastStepStart=0):
        """
        Execute macro step
        """
        motor = devices.Motor(str(self.motorDevice))
        detector = devices.Detector(config.DEVICE_DETECTOR)
        shutter = devices.Shutter(config.DEVICE_SHUTTER)
        self.emit("macroOperation", "Moving motor: %s to position %f" % (motor.name, float(self.position)))
        motor.move(float(self.position))
        comment2 = "Motor position at: %.3f" % self.position
        
        lastStepTook = int(round(time() - lastStepStart))
        if self.takeDark:
            if lastStepTook < MACRO_DARK_WAIT:
                self.wait_seconds(MACRO_DARK_WAIT - lastStepTook)
            self.emit("macroOperation","Taking dark")
            detector.take_dark(shutter, self.summed)
        
        self.emit("macroOperation","Taking shot")
        detector.take_shot(shutter, int(self.summed), int(self.filesafter), self.sampleName, str(self.comment), comment2=comment2)

class TimeMacro(Macro):
    """
    Time macro.
    Take shot, wait for specified time and repeat
    """
    
    def __init__(self, sampleName, summed, filesafter, wait, repeat, takeDark, comment=None):
        """
        Class constructor:
        @type sampleName: String
        @type summed: int
        @type filesafter: int
        @type wait: int
        @type repeat: int
        @type comment: String 
        """
        super(TimeMacro, self).__init__()
        self.sampleName = sampleName
        self.summed = summed
        self.filesafter = filesafter
        self.wait = wait
        self.repeat = repeat
        self.comment = comment
        self.takeDark = takeDark
    
    def run(self, lastStepStart=0):
        """
        Execute macro step
        """
        detector = devices.Detector(config.DEVICE_DETECTOR)
        shutter = devices.Shutter(config.DEVICE_SHUTTER)
        lastStepTook = int(round(time() - lastStepStart))
        if self.takeDark:
            if lastStepTook < MACRO_DARK_WAIT:
                self.wait_seconds(MACRO_DARK_WAIT - lastStepTook)
            self.emit("macroOperation", "Taking dark")
            detector.take_dark(shutter, self.summed)
        self.emit("macroOperation", "Taking shot")
        detector.take_shot(shutter, int(self.summed), int(self.filesafter), self.sampleName, str(self.comment))

class TemperatureMacro(Macro):
    
    def __init__(self, deviceAlias, device, sampleName, summed,
                 filesafter, temperature, holdingTime, holdingCount, wait,
                 takeDark, comment=None):
        """
        Class constructor:
        @type deviceAlias: String
        @type device: String
        @type sampleName: String
        @type summed: int
        @type filesafter: int
        @type temperature: float
        @type wait: int
        @type comment: String 
        """
        super(TemperatureMacro, self).__init__()
        self.devicePath = str(device)
        self.alias = deviceAlias
        self.sampleName = sampleName
        self.summed = summed
        self.filesafter = filesafter
        self.wait = wait
        self.holdingCount = holdingCount
        self.holdingTime = holdingTime
        self.comment = comment
        self.temperature = temperature
        self.takeDark = takeDark
        
    def run(self, lastStepStart=0, threshold=2, device=None):
        """
        Execute macro step
        """
        if not device: device = devices.Hotblower(str(self.devicePath))
        device.threshold = threshold
        detector = devices.Detector(config.DEVICE_DETECTOR)
        shutter = devices.Shutter(config.DEVICE_SHUTTER)
        self.emit("macroOperation", "Setpoint changed to temperature %f (stabilizing)" % (float(self.temperature)))
        device.set_temperature(self.temperature)

        lastStepTook = int(round(time() - lastStepStart))
        if self.takeDark:
            if lastStepTook < MACRO_DARK_WAIT:
                self.wait_seconds(MACRO_DARK_WAIT - lastStepTook)
            self.emit("macroOperation","Taking dark")
            detector.take_dark(shutter, self.summed)
        
        self.emit("macroOperation","Taking shot")
        comment2 = "Hotblower T_avg.: %.3f" % device.output["movingAverage"][0]
        detector.take_shot(shutter, int(self.summed), int(self.filesafter), self.sampleName, str(self.comment), comment2=comment2)

        if self.holdingCount > 0:
            for i in range(0, self.holdingCount):
                self.emit("macroOperation", "Taking shot")
                comment2 = "Hotblower T_avg.: %.3f" % device.output["movingAverage"][0]
                detector.take_shot(shutter, int(self.summed), int(self.filesafter), self.sampleName, str(self.comment), comment2=comment2)
                self.wait_seconds(self.holdingTime)
                
                
