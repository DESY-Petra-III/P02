"""
Device wrappers
"""

# import from global packages 
from PyTango import DeviceProxy, DevState
from time import sleep
from sys import exc_info
import logging
import socket
import numpy
import collections


# Import from local packages
from Revolver.classes import threads, config

# global variables definitions
stopDevices = False
runningDevices = set()
DEVICE_NAMES = dict((y, x) for x, y in config.DEVICE_NAMES.iteritems())

def halt_all_running_devices():
    """
    Halt all running devices from current widget / application
    """
    logging.warn("Stopping all running registered devices")
    global stopDevices
    global runningDevices
    stopDevices = True
    if runningDevices:
        for device in runningDevices:
            device.halt()
    stopDevices = False
    runningDevices = set()

def get_running_device(devicePath):
    global stopDevices
    if runningDevices:
        for device in runningDevices:
            if device.devicePath == devicePath:
                return device

class TangoDevice(object):
    """
    Wrapper for basic Tango device.
    It provides registering device, halting device and executing commands
    """
    POLL_STATE_TIME = 0.5
    
    def __init__(self, devicePath):
        """
        Class constructor
        @type devicePath: String
        """
        self.devicePath = devicePath
        self.maxValue = False
        self.minValue = False
        self.name = "Generic device"
        self.output = {}
        self.profiling = False
        
        try:
            self.device = DeviceProxy(self.devicePath)
            info = self.device.import_info()
            self.name = info.name
            if(DEVICE_NAMES.has_key(self.name)):
                self.name = DEVICE_NAMES[self.name]
            
        except:
            raise Exception(str("Device %s could not be connected" % self.devicePath))
    
    def halt(self, callBack=None):
        """
        Stop device
        """
        pass
    
    def running_remove(self, *args):
        """
        Remove device from all running devices set
        """
        try:
            if(not stopDevices):
                runningDevices.remove(self)
        except: pass
    
    def running_add(self):
        """
        Add device to all runing devices set
        """
        runningDevices.add(self)
    
    def is_connected(self):
        """
        Return true if device is connected
        @rtype: bool
        """
        if self.device is None: return False
        else: return True
    
    def write_attributes(self, attributes):
        """
        Write attribute to device
        @type attributes: list
        @rtype: String
        """
        if self.device:
            for attribute in attributes:
                logging.info("Attribute: %s wrote on device: %s", attribute[0], self.devicePath)    
            return self.device.write_attributes(attributes)
    
    def write_attributes_async(self, attributes, callback=None):
        if self.device:
            for attribute in attributes:
                logging.info("Attribute: %s wrote on device: %s", attribute[0], self.devicePath)
            return self.device.write_attributes_asynch(attributes, callback)
        
    def execute_command(self, commandName, commandParam=None):
        """
        Execute command on device
        @type commandName: String
        @type commandParam: String
        @rtype: String
        """
        if self.device:
            return self.device.command_inout(commandName, commandParam)
        
    def wait_for_state(self, state, callback=None):
        """
        Wait for state
        @type state: DevState.state
        """
        if self.device:
            while (self.device.state() == state): sleep (self.POLL_STATE_TIME)
            if not (callback is None): callback(self)
    
    def wait_seconds(self, duration=1):
        """
        Wait for a time duration
        @type duration: float
        """
        if self.device:
            sleep(duration)
    
    def poll(self, commandName, duration=0.1, callback=None, commandParam=None):
        """
        Poll device with command
        @type commandName: String
        @type duration: float
        @type callback: fun
        @type commandParam: String  
        """
        while (self.execute_command(commandName, commandParam) and threads.THREAD_KEEP_ALIVE):
            self.wait_seconds(duration)
        if not (callback is None): callback(self)
        
    def check_idle(self):
        """
        Check if device id idle
        """
        pass

    def is_idle(self):
        """
        Return True if is idle, False if not and None if unknown 
        """
        return None
    
    def start_profiling(self):
        self.profiling = True
        logging.info("Profiling of device %s started" % self.devicePath)
    
    def stop_profiling(self):
        self.profiling = False
    
    def current_value(self, value):
        return self.device.read_attribute(value).value
        
    def __profiling_routine(self):
        pass
    
class Shutter(TangoDevice):
    """
    Class that define Shutter device
    """
    
    def __init__(self, devicePath):
        """
        Class constructor
        @type devicePath: String
        """
        super(Shutter, self).__init__(devicePath)
    
    def halt(self):
        """
        Reimplement TangoDevice.halt
        Close shutter
        """
        status = self.device.read_attribute("value").value
        if status == 0:
            self.close()
            logging.warn("Shutter closed")
        
    def close(self):
        """
        Close the Shutter
        """
        self.write_attributes([('value', 1)])
        self.running_remove()
    
    def open(self):
        """Open the Shutter"""
        self.write_attributes([('value', 0)])
        self.running_add()

class MainShutter(TangoDevice):
    """
    Class that define Shutter device
    """
    
    def __init__(self, devicePath):
        """
        Class constructor
        @type devicePath: String
        """
        super(MainShutter, self).__init__(devicePath)
    
    def halt(self):
        """
        Reimplement TangoDevice.halt
        Close shutter
        """
        return
        status = self.device.read_attribute("value").value
        if status == 0:
            self.close()
            logging.warn("Shutter closed")
    
    def is_open(self):
        """
        Main shutter is opened when BS0OffenDisplayState and BSA1OffenDisplayState states are set to 0
        """
        states = self.device.read_attributes(("BS0OffenDisplayState","BSA1OffenDisplayState"))
        if states[0].value == 0 and states[1].value == 0:
            return True
        else:
            return False
        
    def close(self):
        """
        Close the Shutter
        """
        return
        self.write_attributes([('value', 1)])
        self.running_remove()
    
    def open(self):
        """Open the Shutter"""
        return
        self.write_attributes([('value', 0)])
        self.running_add()

class Diode(TangoDevice):
    """
    Class that define diode device
    """
    def __init__(self, devicePath):
        """
        Class constructor
        @type devicePath: String
        """
        super(Diode, self).__init__(devicePath)
        self.output["current"] = [0]
    
    def start_profiling(self, dt=0.1, namet="haspp02oh1:10000/p02/timer/eh1b.01", namec="haspp02oh1:10000/p02/vfc/eh1b.02"):
        TangoDevice.start_profiling(self)
        thread = threads.threading.Thread(target=self.__profiling_routine, args=([dt, namet, namec]))
        threads.add_thread(thread)
        thread.start()
    
    def __profiling_routine(self, dt, namet, namec):
        devt = TangoDevice(namet)
        devt.device.write_attribute("SampleTime", dt)
        while self.profiling and threads.THREAD_KEEP_ALIVE:
            devc = TangoDevice(namec)
            devc.device.command_inout("Reset")  # reset counter
            #  time.sleep(0.001)
            devt.device.command_inout("StartAndWaitForTimer")
            #  time.sleep(0.001)
            attr = devc.device.read_attribute("Counts")
            #  time.sleep(0.001)
            self.output["current"][0] = float(attr.value)
        logging.info("Profiling of device %s ended" % self.devicePath)
    
    def halt(self):
        """
        Reimplement TangoDevice.halt
        Close shutter
        """
        status = self.device.read_attribute("value").value
        if status == 1:
            self.put_out()
        
    def put_in(self):
        """
        Put diode in
        """
        self.write_attributes([('Valve1', 1)])
        self.running_add()
        logging.warn("Diode in")
    
    def put_out(self):
        """
        Put diode out
        """
        self.write_attributes([('Valve1', 0)])
        self.running_remove()
        logging.warn("Diode out")

class Laser(TangoDevice):
    """
    Class that define Shutter device
    """
    
    def __init__(self, devicePath):
        """
        Class constructor
        @type devicePath: String
        """
        super(Laser, self).__init__(devicePath)
    
    def halt(self):
        """
        Close shutter
        """
        status = self.device.read_attribute("value").value
        if status == 1:
            self.put_out()
        
    def put_in(self):
        """
        Put laser in
        """
        self.write_attributes([('Valve6', 0)])
        self.running_add()
        logging.warn("Laser in")
    
    def put_out(self):
        """
        Put laser out
        """
        self.write_attributes([('Valve6', 1)])
        self.running_remove()
        logging.warn("Laser out")

class Absorber(TangoDevice):
    """
    Class that define Shutter device
    """
    
    def __init__(self, devicePath, registers=("Valve2","Valve3","Valve4","Valve5")):
        """
        Class constructor
        @type devicePath: String
        """
        super(Absorber, self).__init__(devicePath)
        self.registers = registers
    
    def halt(self):
        """
        Set absorber to zero value
        """
        status = self.device.get_value()
        if status != 0:
            self.set_value(0)
    
    def set_value(self, value=None):
        """
        Set absorber value to Tango server
        for every specified register get bit value
        register1 & 1
        register2 & 2
        register3 & 4
        regitser4 & bits[n]
        """
        if not value: value = self.get_value()
        bits = [1,2,4,8,16,32,64,128,256,512,1024,2048]
        set_value = []
        for index,register in enumerate(self.registers):
            bitValue = 0
            if value & bits[index]: bitValue = 1
            set_value.append((register, bitValue))
        self.absorber.write_attributes(set_value)
    
    def get_value(self):
        """
        Get absorber value from Tango server
        Count value from defined registers
        int(bin(register1+register2+register3+register...))
        """
        states = self.device.read_attributes(self.registers)
        att_bin = ""
        for state in states:
            att_bin += str(state.value)
        att_dec = int(att_bin, 2)
        return att_dec
    
class Detector(TangoDevice):
    """
    Class that define PerkinElmer detector device
    """
    
    def __init__(self, devicePath):
        """
        Class constructor
        @type devicePath: String
        """
        super(Detector, self).__init__(devicePath)
    
    def halt(self):
        """
        Reimplement TangoDevice.halt
        Send acquisition.cancel() SIGNAL thru detector controller to stop acqusition
        """
        controller = DetectorController(config.DEVICE_DETECTOR_CONTROLLER)
        controller.execute_command("WriteReadSocket", "acquisition.cancel()")
    
    def check_idle(self):
        """
        Check if motor is not moving. 
        If it's moving raise exception.
        """
        if self.device.state() == DevState.MOVING:
            raise Exception("Detector is acquiring image.")
    
    def is_idle(self):
        try:
            if self.device.state() == DevState.MOVING:
                return False
            else:
                return True
        except:
            return None
    
    def take_dark(self, Shutter, summed):
        """
        Take dark shot
        @type Shutter: Shutter
        @type summed: int
        """
        self.check_idle()
        Shutter.close()
        self.wait_seconds(1)
        attributes = [("ExposureTime", 1.0), ("SummedDarkImages", int(summed))]
        self.write_attributes(attributes)
        self.execute_command("AcquireDarkImagesAndSave")
        self.running_add()
        self.wait_for_state(DevState.MOVING, self.running_remove)
    
    def take_shot(self, Shutter, summed, filesafter, filename, comment=None, comment2=None, comment3=None, comment4=None, exposureTime=1):
        """
        Take dark shot
        @type Shutter: Shutter
        @type summed: int
        @type filesafter: int
        @type filename: String
        @type comment: String
        """
        self.check_idle()
        attributes = [("ExposureTime", exposureTime), ("SummedSaveImages", int(summed)),
                      ("FilesAfterTrigger", int(filesafter)), ("FilePattern", str("%s" % filename)),
                      ('UserComment1', str("%s" % comment))]
        if(comment2):
            attributes.append(('UserComment2', str("%s" % comment2)))
        if(comment3):
            attributes.append(('UserComment3', str("%s" % comment3)))
        if(comment4):
            attributes.append(('UserComment4', str("%s" % comment3)))
                              
        self.write_attributes(attributes)
        Shutter.open()
        self.wait_seconds(1)
        self.execute_command("AcquireSubtractedImagesAndSave")
        self.running_add()
        self.wait_seconds(summed * filesafter)
        Shutter.close()
        self.wait_seconds(1)
        self.wait_for_state(DevState.MOVING, self.running_remove)
        
    def take_scan_shot(self, summed):
        """
        Take scan shot, no need to close and open shutter
        @type summed: int
        """
        self.check_idle()
        attributes = [("ExposureTime", 1.0), ("SummedSaveImages", int(summed)),
                      ("FilesAfterTrigger", 1)]
        self.write_attributes(attributes)
        self.execute_command("AcquireSubtractedImages")
        self.running_add()
        self.wait_for_state(DevState.MOVING, self.running_remove)

class DetectorController(TangoDevice):
    """
    Class that manage connection to detector thru socket
    """
    
    def __init__(self, devicePath):
        """
        Class constructor
        Get IP address and port number from actual detector controller
        @type devicePath: String
        """
        super(DetectorController, self).__init__(devicePath)
        device_property = self.device.get_property(["IpAddr", "PortNb"])
        self.address = str(device_property["IpAddr"][0])
        self.port = int(device_property["PortNb"][0])
        self.socket = None
  
    def halt(self):
        """
        Reimplement TangoDevice.halt
        Close socket to detector if its open
        """
        if self.socket:
            self.execute_command("Init")
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
    
    def get_last_shot(self):
        """
        Get last shot from detector.
        @rtype: dict
        """
        self.running_add()
        lineLast = ""
        rowData = []
        readData = []
        self.socket = socket.socket()
        self.socket.connect((self.address, self.port))
        
        # get image width / height / filename
        self.socket.send("data().width\n\r")
        dataWidth = int(self.socket.recv(256).strip())
        self.socket.send("data().height\n\r")
        dataHeight = int(self.socket.recv(256).strip())
        self.socket.send("processor.fileName\n\r")
        filename = self.socket.recv(1024).strip()
        
        # get whole image from detector
        self.socket.send("data().getImageData(0,0,%i,%i)\n\r" % (dataWidth - 1, dataHeight - 1))
        j = 0
        
        # read image from socket by 4000 bytes, read until end of buffer
        try:
            while True:
                line = self.socket.recv(4000)
                if line[0] == ",":
                    line = lineLast + line
                elif lineLast:
                    line = lineLast + line
                lineData = line.strip().split(",")
                lineLast = lineData.pop()
                actualRowLen = len(rowData)
                lineLen = len(lineData)
                missingLength = dataWidth - actualRowLen
                if lineLen >= missingLength:
                    rowData = rowData + lineData[:missingLength - 1]
                    readData.append(map(float, rowData))
                    rowData = lineData[missingLength - 1:]
                    j = j + 1
                else:
                    rowData = rowData + lineData
                if "\n" in line: 
                    break;
        except:
            print str("Exception %s with message: %s" % (exc_info()[0], exc_info()[1]))
        finally:
            self.halt()
            self.running_remove()
      
        return {"data": numpy.asarray(readData), "width":dataWidth, "height":dataHeight, "filename": filename}
    
    def take_readout(self, X0=0, Y0=0, X1=2047, Y1=2047):
        """
        Read average value of pixels from detector.
        Value is defined by square (Xst, Yst),(Xend, Yend)
        @type X0: int
        @type Y0: int
        @type X1: int
        @type Y1: int
        """
        cmd = self.execute_command("WriteReadSocket", "%s%s,%s,%s,%s%s" % ("processor.integrateRectangle(", X0, Y0, X1, Y1, ")"))
        val = cmd.split(",")
        return val[0]
        
class Motor(TangoDevice):
    """
    Class that define motor device
    """
    
    def __init__(self, devicePath):
        """
        Class constructor
        @type devicePath: String
        """
        super(Motor, self).__init__(devicePath)
        self.maxValue = self.device.read_attribute("UnitLimitMax").value
        self.minValue = self.device.read_attribute("UnitLimitMin").value
            
    def __moved__(self):
        """
        This method is automatically called after motor stops
        """
        self.running_remove()
        position = self.device.read_attribute("Position").value
        logging.info("Motor: %s changed position to: %.5f", self.devicePath, position)
    
    def is_idle(self):
        try:
            if self.execute_command("CheckMove"):
                return False
            else:
                return True
        except:
            return None
    
    def check_idle(self):
        """
        Check if motor is not moving. 
        If it's moving raise exception.
        """
        if self.execute_command("CheckMove"):
            raise Exception("Motor is moving")
    
    def halt(self, callBack=None):
        """
        Reimplement TangoDevice.halt
        Stop all motor motions if motor is moving
        """
        if self.execute_command("CheckMove"):
            self.execute_command("StopMove")
            logging.warn("Motor %s halted", self.devicePath)
        if callBack: callBack()
            
    def move(self, position, callback=None, async=False):
        """
        Move motor to specified position
        @type position: float
        @type callback: fun
        """
        self.check_idle()
        attributes = [("Position", position)]
        if not async:
            self.write_attributes(attributes)
            self.running_add()
            if callback:
                self.poll("CheckMove", callback=lambda positon: (self.__moved__(), callback()))
            else:
                self.poll("CheckMove", callback=lambda positon: (self.__moved__()))
        else:
            self.write_attributes_async(attributes, callback)
            self.running_add()
            
    def current_value(self, value="Position"):
        return TangoDevice.current_value(self, value)

class Hotblower(TangoDevice):
    """
    Class that define motor device
    """
    
    # Minimum waiting time in stabilization loop
    MIN_STABILIZATION_TIME = 30
    # Maximum waiting time in stabilization loop
    MAX_STABILIZATION_TIME = 120
        
    def __init__(self, devicePath, threshold=2):
        """
        Class constructor
        @type devicePath: String
        """
        super(Hotblower, self).__init__(devicePath)
        self.maxValue = 1000
        self.minValue = 20
        self.threshold = threshold
        self.rampingThreshold = 2
        self.__idle = True
        actualTemperature = self.device.read_attribute("Temperature").value
        self.output["movingAverage"] = [actualTemperature]
        self.output["temperature"] = [actualTemperature]
    
    def __stop_stabilization__(self):
        """
        Set flag to False and stop stabilization wait loop
        """
        self.waitForStabilization = False
    
    def __set_idle(self, flag):
        """
        Set hotblower to idle position by flag
        @type flag: bool
        """
        if flag: self.running_remove()
        self.__idle = flag
            
    def is_idle(self):
        """
        Return true if device is on stabilized temperature
        @rtype: bool
        """
        if self.__idle == True:
            return True
        else:
            return False
    
    def is_stabilized(self):
        """
        Is device stabilized on setpoint temperature?
        @rtype: bool 
        """
        actualTemperature = self.device.read_attribute("Temperature").value
        actualSetpoint = self.device.read_attribute("Setpoint").value
        diffTemperature = abs(actualSetpoint - actualTemperature)
        if diffTemperature <= self.threshold:
            return True
        else:
            return False
    
    def check_idle(self):
        """
        Check if hotblower is working. 
        If yes than raise exception.
        """
        if not(self.is_idle()):
            raise Exception("Hotblower is running on setpoint")
    
    def halt(self, force=False, callBack=None):
        """
        Stop actual stabilization or ramping loop.
        Set new setpoint to minimum value, dont wait to stabilization. 
        @type force: bool
        @type callBack: function
        """
        if force or not self.is_idle():
            self.__stop_stabilization__()
            attributes = [("Setpoint", self.minValue)]
            self.write_attributes(attributes)
            logging.info("Hotblower halted, setpoint set to temperature %.5f", self.minValue)
        if callBack: callBack()
    
    def start_profiling(self):
        """
        Start profiling of device
        """
        TangoDevice.start_profiling(self)
        thread = threads.threading.Thread(target=self.__profiling_routine, args=([]))
        threads.add_thread(thread)
        thread.start()
    
    def __profiling_routine(self):
        """
        Profiling routine
        put movingAverage and actual temperature into profiling output
        """
        minStabilizeCount = self.MIN_STABILIZATION_TIME / self.POLL_STATE_TIME
        measuredPoints = collections.deque(maxlen=minStabilizeCount)
        
        while self.profiling and threads.THREAD_KEEP_ALIVE:
            actualTemperature = self.device.read_attribute("Temperature").value
            measuredPoints.append(actualTemperature)
            averageStabilization = reduce(lambda x, y: x + y, measuredPoints) / len(measuredPoints)
            self.output["movingAverage"][0] = averageStabilization
            self.output["temperature"][0] = actualTemperature
            sleep(self.POLL_STATE_TIME)
        logging.info("Profiling of device %s ended" % self.devicePath)
                
    def wait_temperature_stabilized(self):
        """
        Wait in loop until hotblower was stabilized.
        Stop stabilization routine with self.waitForStabilization flag
        Wait until ramping threshold was reached, than start stabilization loop
        @rtype: bool
        """
        self.__set_idle(False)
        self.waitForStabilization = True
        stabilizeCount = self.MIN_STABILIZATION_TIME / self.POLL_STATE_TIME
        minStabilizeCount = self.MIN_STABILIZATION_TIME / self.POLL_STATE_TIME
        maxStabilizeCount = self.MAX_STABILIZATION_TIME / self.POLL_STATE_TIME
        count = 0
        
        actualSetpoint = self.device.read_attribute("Setpoint").value
        measuredPoints = collections.deque(maxlen=minStabilizeCount)
        ramping = True
        
        while (ramping or count != stabilizeCount and count < maxStabilizeCount and threads.THREAD_KEEP_ALIVE) and self.waitForStabilization:
            actualTemperature = self.device.read_attribute("Temperature").value
            measuredPoints.append(actualTemperature)
            averageStabilization = reduce(lambda x, y: x + y, measuredPoints) / len(measuredPoints)
            
            if ramping and abs(actualSetpoint - averageStabilization) <= self.rampingThreshold: 
                logging.info("Ramping end")
                count = 0
                ramping = False
            if not ramping and count >= minStabilizeCount - 1:
                if abs(actualSetpoint - averageStabilization) <= self.threshold:
                    logging.info("Hotblower: %s stabilized on temperature: %.5fC", self.devicePath, actualSetpoint)
                    self.__set_idle(True)
                    return True
                else:
                    stabilizeCount += 1
            sleep(self.POLL_STATE_TIME)
            count += 1
            
        if self.waitForStabilization:
            logging.info("Hotblower: %s could not be stabilized on temperature: %.5fC", self.devicePath, actualSetpoint)
        self.__set_idle(True)
        return False
        
    def set_temperature(self, temperature, callback=None):
        """
        Set hotblower setpoint to new temperature
        @type temperature: float
        @type callback: fun
        """
        self.check_idle()
        attributes = [("Setpoint", temperature)]
        self.write_attributes(attributes)
        self.running_add()
        self.wait_temperature_stabilized()
        
    def current_value(self, value="Temperature"):
        """
        Return value defined in value parameter
        @rtype: mixed
        @type value: String
        """
        return TangoDevice.current_value(self, value)

class VirtualDevice(object):
    """
    Class that defines Virtual device
    Similar to TangoDevice, but did not use Tango server
    Good to implement devices that are somehow connected
    """
    
    def __init__(self, devices, name="VIRTUAL_DEVICE"):
        self.maxValue = False
        self.minValue = False
        self.name = name
        self.devicePath = "/virtual/%s" % name
        self.output = {}
        self.profiling = False
        self.devices = devices
                
    def halt(self, callBack=None):
        """
        Halt connected devices
        @type callBack: fun
        """
        for device in self.devices:
            device.halt()
        if callBack: callBack()
        
    def is_idle(self):
        """
        Chcek if all connected devices are idle
        @rtype: bool
        """
        for device in self.devices:
            if not device.is_idle(): return False
        return True
    
    def check_idle(self):
        """
        Check if device is idle. 
        If not than raise exception.
        """
        for device in self.devices:
            device.check_idle()
    
    def start_profiling(self):
        self.profiling = True
        logging.info("Profiling of device %s started" % self.name)
    
    def stop_profiling(self):
        self.profiling = False
    
    def current_value(self, value):
        """
        Imitate tango request to get current value
        """
        return 0
    
    def execute_command(self, commandName, commandParam=None):
        """
        Imitate tango request to get execute command on device
        """
        return 0
        
class VirtualMotorDistance2D(VirtualDevice):
    """
    Two virtually connected motors.
    It's position represent distance between this two motors.
    """
    
    def __init__(self, devices, name):
        """
        devices parameter should contain list of two Motor objects
        name parameter is used to identify motor by its name
        @type devices: list
        @type name: String
        """
        super(VirtualMotorDistance2D, self).__init__(devices, name=name)
        self.leftMotor = devices[0]
        self.rightMotor = devices[1]
        self.minValue = -99999
        self.maxValue = 99999
    
    def get_actual_position(self):
        """
        Get actual distance between left and right motor
        """
        leftMotorPosition = self.leftMotor.current_value()
        rightMotorPosition = self.rightMotor.current_value()
        return leftMotorPosition - rightMotorPosition
        
    def move(self, position, callback=None, async=False):
        """
        Move left and right motor to opposite direction by specified distance
        """
        half_position = (self.get_actual_position() - position) / 2
        leftMotorPosition = self.leftMotor.current_value() - half_position
        rightMotorPosition = self.rightMotor.current_value() + half_position
        
        # check motor limits
        leftMinimum = self.leftMotor.device.read_attribute("UnitLimitMin").value
        rightMinimum = self.rightMotor.device.read_attribute("UnitLimitMin").value
        leftMaximum = self.leftMotor.device.read_attribute("UnitLimitMax").value
        rightMaximum = self.rightMotor.device.read_attribute("UnitLimitMax").value
        
        if(leftMotorPosition < leftMinimum or rightMotorPosition < rightMinimum):
            raise Exception("Minimum motor position was exceeded")
        if(leftMotorPosition > leftMaximum or rightMotorPosition > rightMaximum):
            raise Exception("Maximum motor position was exceeded")
        
        self.leftMotor.move(leftMotorPosition, async=True)
        self.rightMotor.move(rightMotorPosition, async=True)
    
    def current_value(self, value="Position"):
        if value=="Position": return self.get_actual_position()
        return 0
    
    def execute_command(self, commandName, commandParam=None):
        if commandName == "GetPosition": return self.get_actual_position()
        return 0
    
class VirtualMotorCenter2D(VirtualDevice):
    """
    Two virtually connected motors.
    It's position represent center created by this two motors.
    """
    
    def __init__(self, devices, name):
        super(VirtualMotorCenter2D, self).__init__(devices, name=name)
        self.leftMotor = devices[0]
        self.rightMotor = devices[1]
        self.minValue = -99999
        self.maxValue = 99999
    
    def get_actual_position(self):
        """
        Get actual center between left and right motor
        actualCenter = mean(leftPosition, rightMotorPosition)
        """
        leftMotorPosition = self.leftMotor.current_value()
        rightMotorPosition = self.rightMotor.current_value()
        return numpy.mean([leftMotorPosition, rightMotorPosition])
        
    def move(self, position, callback=None, async=False):
        """
        Increase both motors by one value
        """
        center_position = position - self.get_actual_position()
        leftMotorPosition = self.leftMotor.current_value() + center_position
        rightMotorPosition = self.rightMotor.current_value() + center_position
        
        leftMinimum = self.leftMotor.device.read_attribute("UnitLimitMin").value
        rightMinimum = self.rightMotor.device.read_attribute("UnitLimitMin").value
        leftMaximum = self.leftMotor.device.read_attribute("UnitLimitMax").value
        rightMaximum = self.rightMotor.device.read_attribute("UnitLimitMax").value
        
        if(leftMotorPosition < leftMinimum or rightMotorPosition < rightMinimum):
            raise Exception("Minimum motor position was exceeded")
        if(leftMotorPosition > leftMaximum or rightMotorPosition > rightMaximum):
            raise Exception("Maximum motor position was exceeded")
            
        self.leftMotor.move(leftMotorPosition, async=True)
        self.rightMotor.move(rightMotorPosition, async=True)
    
    def current_value(self, value="Position"):
        if value=="Position": return self.get_actual_position()
        return 0
    
    def execute_command(self, commandName, commandParam=None):
        if commandName == "GetPosition": return self.get_actual_position()
        return 0