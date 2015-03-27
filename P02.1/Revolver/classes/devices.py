"""
Device wrappers
"""

# import from global packages 
from PyTango import DeviceProxy, DevState, ConnectionFailed, DevFailed
from time import sleep
from sys import exc_info
import logging
import socket
import numpy
import collections
from threading import Thread
import ntpath
import time
from PyTango import DeviceProxy, Database

# Import from local packages
from Revolver.classes import threads, config, signals

# global variables definitions
stopDevices = False
runningDevices = set()
DEVICE_NAMES = dict((y, x) for x, y in config.DEVICE_NAMES.iteritems())

def getSubDevice(filter):
        exportedDevices = dict()
        db = Database()
        eDevices = db.get_device_exported(filter).value_string
        for eDevice in eDevices:
            sd = db.get_device_property(eDevice,"__SubDevices")["__SubDevices"]
            for s in sd:
                exportedDevices[s] = eDevice
        return exportedDevices
        
SUB_MOTOR_DEVICES = getSubDevice("*motor*")

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

def get_all_running_devices(devicePath):
    deviceList = []
    if runningDevices:
        for device in runningDevices:
            if device.devicePath == devicePath:
                deviceList.append(device)
    return deviceList

class TangoDevice(object):
    """
    Wrapper for basic Tango device.
    It provides registering device, halting device and executing commands
    """
    POLL_STATE_TIME = 0.5
    TEST_MODE = False
    
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
        self.deviceError = False
        self.defaultClass = self.__class__
        self.enableControls = True
        
        try:
            self.__device_init()
        except:
            logging.error(str("Device %s could not be connected" % self.devicePath))
            self.name = self.devicePath
            if config.DEVICE_ALLOW_RETRY:
                self._retry_device()
                #raise Exception(str("Device %s could not be connected" % self.devicePath))
                # logging.error(str("Device %s could not be connected" % self.devicePath))
                #else: 
                
                #raise Exception(str("Device %s could not be connected" % self.devicePath))

    def __postInit__(self):
        pass
    
    def __device_init(self):
        self.device = DeviceProxy(self.devicePath)
        info = self.device.import_info()
        self.name = info.name
        if(DEVICE_NAMES.has_key(self.name)):
            self.name = DEVICE_NAMES[self.name]
        self.deviceError = False
        self.__postInit__()
                
    def _retry_device(self, callback=None):
        self.deviceError = True
        thread = Thread(target=self.__retry_routine, args=([callback]))
        threads.add_thread(thread)
        thread.start()
        self.__class__ = DummyDevice
    
    def __retry_routine(self, callback):
        retrySleep = [True]
        while(retrySleep[0] and threads.THREAD_KEEP_ALIVE):
            try:
                DeviceProxy(self.devicePath).state()
                logging.error("Device online: %s" % (self.devicePath) )
                retrySleep = [False]
            except:
                logging.error("Device offline, retrying: %s" % (self.devicePath) )
            threads.thread_sleep(config.DEVICE_RETRY_INTERVAL, sleepFlags=retrySleep)
        if threads.THREAD_KEEP_ALIVE == True:
            self.__class__ = self.defaultClass
            self.__device_init()
            if callback: callback()
        return True        
    
    def isDeviceError(self):
        return self.deviceError
        
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
        global runningDevices
        runningDevices.add(self)
    
    def is_connected(self):
        """
        Return true if device is connected
        @rtype: bool
        """
        if self.device is None: return False
        else: return True
    
    def read_attributes(self, attributes):
        try:
            return self.device.read_attributes(attributes)
        except:
            logging.error("Device read attribute error: retrying device")
            if not config.DEVICE_ALLOW_RETRY: 
                raise Exception(str("Device %s could not be connected" % self.devicePath))
            else: 
                self._retry_device()
                return self.read_attributes(attributes)
    
    def read_attribute(self, attribute):
        try:
            return self.device.read_attribute(attribute)
        except:
            if not config.DEVICE_ALLOW_RETRY: 
                raise Exception(str("Device %s could not be connected" % self.devicePath))
            else: 
                self._retry_device()
                return self.read_attribute(attribute)
    
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
        try:
            if self.device:
                return self.device.command_inout(commandName, commandParam)
        except:
            if not config.DEVICE_ALLOW_RETRY: 
                raise Exception(str("Device %s could not be connected" % self.devicePath))
            else: 
                self._retry_device()
                return self.execute_command(commandName, commandParam)
            
        
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
        @type duration: float if not config.DEVICE_ALLOW_RETRY: 
                raise Exception(str("Device %s could not be connected" % self.devicePath))
            else: 
                self._retry_device()
                return self.execute_command(commandName, commandParam)
        """
        if self.device:
            sleep(duration)
    
    def poll(self, commandName, duration=0.1, commandResult = True, callback=None, commandParam=None):
        """
        Poll device with command
        @type commandName: String
        @type duration: float
        @type callback: fun
        @type commandParam: String  
        """
        while (self.execute_command(commandName, commandParam) == commandResult and threads.THREAD_KEEP_ALIVE):
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
        if self.profiling: return False
        self.profiling = True
        logging.info("Profiling of device %s started" % self.devicePath)
        return True
    
    def stop_profiling(self):
        self.profiling = False
    
    def current_value(self, value):
        return self.read_attribute(value).value
        
    def __profiling_routine(self):
        pass

class DummyDevice(object):
    """
    Wrapper for basic Tango device.
    It provides registering device, halting device and executing commands
    """
    
    TEST_MODE = False
    
    def __init__(self, devicePath):
        """
        Class constructor
        @type devicePath: String
        """
        return
    
    def __device_init(self):
        return False
                
    def _retry_device(self):
        return False
    
    def isDeviceError(self):
        return True    
        
    def halt(self, callBack=None):
        """
        Stop device
        """
        return False
    
    def running_remove(self, *args):
        """
        Remove device from all running devices set
        """
        return False
    
    def running_add(self):
        """
        Add device to all runing devices set
        """
        return False
    
    def is_connected(self):
        """
        Return true if device is connected
        @rtype: bool
        """
        return False
    
    def read_attributes(self, attributes):
        output = []
        for attribute in attributes:
            struct = collections.namedtuple(attribute, "value")
            struct.value = 0 
            output.append(struct)
        return output
    
    def read_attribute(self, attribute):
        struct = collections.namedtuple("struct", "value")
        struct.value = 0
        return struct
    
    def write_attributes(self, attributes):
        return False
    
    def write_attributes_async(self, attributes, callback=None):
        return False
        
    def execute_command(self, commandName, commandParam=None):
        return False
        
    def wait_for_state(self, state, callback=None):
        return False
    
    def wait_seconds(self, duration=1):
        return False
    
    def poll(self, commandName, duration=0.1, callback=None, commandParam=None):
        return False
        
    def check_idle(self):
        return False

    def is_idle(self):
        return False
    
    def start_profiling(self):
        return False
    
    def stop_profiling(self):
        return False
    
    def current_value(self, *args):
        return False
        
    def __profiling_routine(self):
        return False
    
    def get_value(self):
        return 0

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
        status = self.read_attribute("value").value
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
        status = self.read_attribute("value").value
        if status == 0:
            self.close()
            logging.warn("Shutter closed")
    
    def is_open(self):
        """
        Main shutter is opened when BS0OffenDisplayState and BSA1OffenDisplayState states are set to 0
        """
        states = self.read_attributes(("BS0OffenDisplayState","BSA1OffenDisplayState"))
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
            attr = devc.read_attribute("Counts")
            #  time.sleep(0.001)
            self.output["current"][0] = float(attr.value)
        logging.info("Profiling of device %s ended" % self.devicePath)
    
    def halt(self):
        """
        Reimplement TangoDevice.halt
        Close shutter
        """
        status = self.read_attribute("value").value
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
        """if self.profiling: return
        Close shutter
        """
        status = self.read_attribute("value").value
        if status == 1:
            self.put_out()
        
    def put_in(self):
        """
        Put laser in
        """
        self.write_attributes([('Valve6', 1)])
        self.running_add()
        logging.warn("Laser in")
    
    def put_out(self):
        """
        Put laser out
        """
        self.write_attributes([('Valve6', 0)])
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
        bits = [1,2,4,8,16,32,64,128,256,512,1024,2048]
        set_value = []
        for index,register in enumerate(self.registers):
            bitValue = 0
            if value & bits[index]: bitValue = 1
            set_value.append((register, bitValue))
        self.device.write_attributes(set_value)
    
    def get_value(self):
        """
        Get absorber value from Tango server
        Count value from defined registers
        int(bin(register1+register2+register3+register...))
        """
        states = self.read_attributes(tuple(reversed(self.registers)))
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
            if not config.DEVICE_ALLOW_RETRY: 
                raise Exception(str("Device %s could not be connected" % self.devicePath))
            else: 
                self._retry_device()
                return self.is_idle()
    
    def set_file_index(self, fileIndex=1):
        """
        Set file index, usually before new macro fires up
        """
        self.check_idle()
        self.write_attributes([("FileIndex", int(fileIndex))])
    
    def take_dark(self, Shutter, summed, filename=None):
        """
        Take dark shot
        @type Shutter: Shutter
        @type summed: int
        """
        self.check_idle()
        Shutter.close()
        self.wait_seconds(1)
        attributes = [("ExposureTime", 1.0), ("SummedDarkImages", int(summed))]
        if filename is not None:
            attributes.append(("FilePattern", str("%s" % filename)))
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
    
    def __postInit__(self):
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
    
    def take_filename(self):
        try:
            return ntpath.split(self.execute_command("WriteReadSocket", "processor.fileName"))[1]
        except:
            pass
    
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
        self.currentPostion = self.current_value()
        
    def __postInit__(self):
        self.maxValue = self.read_attribute("UnitLimitMax").value
        self.minValue = self.read_attribute("UnitLimitMin").value

    def __moved__(self):
        """
        This method is automatically called after motor stops
        """
        self.running_remove()
        position = self.read_attribute("Position").value
        logging.info("Motor: %s changed position to: %.5f", self.devicePath, position)
    
    def is_idle(self):
        try:
            cp = self.current_value()
            
            if self.device.state() == DevState.MOVING or self.currentPostion != cp:
                self.currentPostion = cp
                return False
            else:
                self.currentPostion = cp
                return True
        except:
            return None
    
    def check_idle(self):
        """
        Check if motor is not moving. 
        If it's moving raise exception.
        """
        if self.device.state() == DevState.MOVING:
            raise Exception("Motor is moving")
    
    def halt(self, callBack=None):
        """
        Reimplement TangoDevice.halt
        Stop all motor motions if motor is moving
        """
        if self.execute_command("CheckMove") == True:
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

class TemperatureDevice(TangoDevice):
    
    HOMING_POINTS = 10
        
    def __init__(self, devicePath, threshold=2, initSelf=True):
        """
        Class constructor
        @type devicePath: String
        """
        super(TemperatureDevice, self).__init__(devicePath)
        #self.waitForHoming = False
        self.rampingThreshold = config.SETTINGS_RAMPING_ERROR_THRESHOLD
        self.ramping = False
        self.waitForStabilization = None
        self.status = "Unknown"
        self.settings = config.TEMPERATURE_DEVICE_SETTINGS[devicePath]["settings"]
        
        if initSelf:
            self.maxValue = config.TEMPERATURE_DEVICE_SETTINGS[devicePath]["settings"]["MAX"]
            self.minValue = config.TEMPERATURE_DEVICE_SETTINGS[devicePath]["settings"]["MIN"]
            self.safeValue = config.TEMPERATURE_DEVICE_SETTINGS[devicePath]["settings"]["SAFE"]
            #self.waitForHoming = config.TEMPERATURE_DEVICE_SETTINGS[devicePath]["settings"]["HOMING"]
            
            self.threshold = threshold
            self.idle = True
            
            self.setpointValue = config.TEMPERATURE_DEVICE_SETTINGS[devicePath]["setpoint"]
            self.readoutValue = config.TEMPERATURE_DEVICE_SETTINGS[devicePath]["readout"]
            actualTemperature = self.read_attribute(self.readoutValue).value
            
            self.output["movingAverage"] = [actualTemperature]
            self.output["temperature"] = [actualTemperature]
            self.output["statusString"] = ["Idle"]
    
    def __stop_stabilization__(self):
        """
        Set flag to False and stop stabilization wait loop
        """
        self.waitForStabilization = False
    
    def __stop_homing__(self):
        self.settings["HOMING"] = False
    
    def __start_homing__(self):
        self.settings["HOMING"] = True
    
    def isHoming(self):
        return self.settings["HOMING"]
    
    def __set_idle(self, flag):
        """
        Set hotblower to idle position by flag
        @type flag: bool
        """
        if flag: self.running_remove()
        self.idle = flag
            
    def is_idle(self):
        """
        Return true if device is on stabilized temperature
        @rtype: bool
        """
        return self.idle
    
    def __postInit__(self):
        return
    
    def is_stabilized(self):
        """
        Is device stabilized on setpoint temperature?
        @rtype: bool 
        """
        actualTemperature = self.read_attribute(self.readoutValue).value
        actualSetpoint = self.read_attribute(self.setpointValue).value
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
    '''
    def halt(self, force=False, callBack=None):
        """
        Stop actual stabilization or ramping loop.
        Set new setpoint to minimum value, dont wait to stabilization. 
        @type force: bool
        @type callBack: function
        """
        if force or not self.is_idle():
            self.__stop_stabilization__()
            attributes = [(self.setpointValue, self.safeValue)]
            self.write_attributes(attributes)
            logging.info("Hotblower halted, setpoint set to temperature %.5f", self.safeValue)
        if callBack: callBack()
    '''
        
    def halt(self, force=False, callBack=None, homing=False):
        """
        Stop actual stabilization or ramping loop.
        Set new setpoint to minimum value, dont wait to stabilization. 
        @type force: bool
        @type callBack: function
        """
        if force or not self.is_idle():
            self.__stop_stabilization__()
            if homing and not self.isHoming():
                logging.info("%s halted, start homing to value %.5f" % (self.devicePath, self.safeValue))
                thread = threads.threading.Thread(target=self.__homing, args=([callBack]))
                threads.add_thread(thread)
                thread.start()
    
    def __homing(self, callBack):
        if self.isHoming(): return
        self.running_add()
        self.__start_homing__()
        setPoint = self.read_attribute(self.readoutValue).value
        steps = self.HOMING_POINTS
        oneHomingStep = (setPoint - self.safeValue) / self.HOMING_POINTS
        tempSteps = []
        while steps != 0:
            tempSteps.append(setPoint - (oneHomingStep * steps))
            steps -= 1
        tempSteps.reverse()
        
        for i in tempSteps:
            self.write_attributes([(self.setpointValue, i)])
            while True:
                actualTemperature = self.read_attribute(self.readoutValue).value
                if not self.isHoming() or not threads.THREAD_KEEP_ALIVE: return
                if i <= (actualTemperature + self.rampingThreshold) and i >= (actualTemperature - self.rampingThreshold): break
                sleep(self.POLL_STATE_TIME)
        
        self.__stop_homing__() 
        logging.info("Homing ended for device %s" % self.devicePath)
        if callBack: callBack()
        
    def start_profiling(self):
        """
        Start profiling of device
        """
        if TangoDevice.start_profiling(self):
            thread = threads.threading.Thread(target=self.__profiling_routine)
            threads.add_thread(thread)
            thread.start()
    
    def __profiling_routine(self):
        """
        Profiling routine
        put movingAverage and actual temperature into profiling output
        """
        #minStabilizeCount = config.SETTINGS_STABILIZATION_TIME_MIN / self.POLL_STATE_TIME
        measuredPoints = collections.deque(maxlen=60)
        
        while self.profiling and threads.THREAD_KEEP_ALIVE:
            actualTemperature = self.read_attribute(self.readoutValue).value
            actualSetpoint = self.read_attribute(self.setpointValue).value
            measuredPoints.append(actualTemperature)
            averageStabilization = reduce(lambda x, y: x + y, measuredPoints) / len(measuredPoints)
            self.output["movingAverage"][0] = averageStabilization
            self.output["temperature"][0] = actualTemperature
            '''if not self.waitForStabilization:
                self.output["statusString"][0] = "Ramping"
                if abs(abs(actualSetpoint) - abs(averageStabilization)) > config.SETTINGS_RAMPING_ERROR_THRESHOLD:
                    self.output["statusString"][0] = "Ramping"
                else:
                    if abs(actualSetpoint - averageStabilization) <= self.threshold:
                        self.output["statusString"][0] = "Stabilized"
                    else:
                        self.output["statusString"][0] = "Stabilizing"
            else:'''
            self.output["statusString"][0] = self.status
            sleep(self.POLL_STATE_TIME)
        logging.info("Profiling of device %s ended" % self.devicePath)
                
    def wait_temperature_stabilized(self):
        """
        Wait in loop until hotblower was stabilized.
        Stop stabilization routine with self.waitForStabilization flag
        Wait until ramping threshold was reached, than start stabilization loop
        @rtype: bool
        """
        self.idle = False
        self.waitForStabilization = True
        stabilizeCount = config.SETTINGS_STABILIZATION_TIME_MIN / self.POLL_STATE_TIME
        minStabilizeCount = config.SETTINGS_STABILIZATION_TIME_MIN / self.POLL_STATE_TIME
        maxStabilizeCount = config.SETTINGS_STABILIZATION_TIME_MAX / self.POLL_STATE_TIME
        maxRampingCount = config.SETTINGS_RAMPING_MAXIMUM_TIME / self.POLL_STATE_TIME
        count = 0
        actualSetpoint = self.read_attribute(self.setpointValue).value
        measuredPoints = collections.deque(maxlen=60)
        self.ramping = True
        self.status = "Ramping"
        
        while (self.ramping or (count < stabilizeCount and count < maxStabilizeCount) ) and threads.THREAD_KEEP_ALIVE and self.waitForStabilization:
            
            actualTemperature = self.read_attribute(self.readoutValue).value
            measuredPoints.append(actualTemperature)
            averageStabilization = reduce(lambda x, y: x + y, measuredPoints) / len(measuredPoints)
            
            if self.ramping and count >= maxRampingCount:
                return None
                self.waitForStabilization = False
                break
            if self.ramping:
                if abs(abs(actualSetpoint) - abs(averageStabilization)) <= config.SETTINGS_RAMPING_ERROR_THRESHOLD: 
                    logging.info("Ramping end")
                    count = 0
                    self.ramping = False
                    self.status = "Stabilizing"
            if not self.ramping and count >= minStabilizeCount - 1 and abs(actualSetpoint - averageStabilization) <= self.threshold:
                logging.info("%s stabilized on temperature: %.5fC", self.devicePath, actualSetpoint)
                self.idle = True
                self.status = "Stabilized"
                self.waitForStabilization = False
                return True
            else:
                stabilizeCount += 1
            sleep(self.POLL_STATE_TIME)
            count += 1
        
        if self.ramping == True:
            logging.info("Device %s could not be ramped to temperature: %.5fC", self.devicePath, actualSetpoint)
        if self.waitForStabilization:
            logging.info("Device %s could not be stabilized on temperature: %.5fC", self.devicePath, actualSetpoint)
        self.__set_idle(True)
        self.waitForStabilization = False
        return False
        
    def set_temperature(self, temperature, callback=None):
        """
        Set hotblower setpoint to new temperature
        @type temperature: float
        @type callback: fun
        """
        self.check_idle()
        self.__stop_homing__()
        attributes = [(self.setpointValue, temperature)]
        self.write_attributes(attributes)
        while self.read_attribute(self.setpointValue).value != temperature:
            sleep(0.1)
        self.running_add()
        return self.wait_temperature_stabilized()
        
    def current_value(self, value=None):
        """
        Return value defined in value parameter
        @rtype: mixed
        @type value: String
        """
        if not value: value = self.readoutValue
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
        self.deviceError = False
        self.defaultClass = self.__class__
        self.addToPosition = 0
        
    def isDeviceError(self):
        for device in self.devices:
            if device.isDeviceError():
                return True
        return False
        
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
        if self.deviceError == True:
            for device in self.devices:
                if device.deviceError:
                    return False
            self.deviceError = False
        else: 
            for device in self.devices:
                if device.deviceError:
                    self.deviceError = True
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
    
    def current_value(self, *args):
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
        leftMinimum = self.leftMotor.read_attribute("UnitLimitMin").value
        rightMinimum = self.rightMotor.read_attribute("UnitLimitMin").value
        leftMaximum = self.leftMotor.read_attribute("UnitLimitMax").value
        rightMaximum = self.rightMotor.read_attribute("UnitLimitMax").value
        
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
        half_position = (self.get_actual_position() - position) / 2
        leftMotorPosition = self.leftMotor.current_value() + half_position
        rightMotorPosition = self.rightMotor.current_value() + half_position
        
        leftMinimum = self.leftMotor.read_attribute("UnitLimitMin").value
        rightMinimum = self.rightMotor.read_attribute("UnitLimitMin").value
        leftMaximum = self.leftMotor.read_attribute("UnitLimitMax").value
        rightMaximum = self.rightMotor.read_attribute("UnitLimitMax").value
        
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
    
class VirtualMotorSum2D(VirtualMotorDistance2D):
    """
    Two virtually connected motors.
    It's position represent distance between this two motors.
    """
    
    def get_actual_position(self):
        """
        Get actual distance between left and right motor
        """
        leftMotorPosition = self.leftMotor.current_value()
        rightMotorPosition = self.rightMotor.current_value()
        if hasattr(self.addToPosition, '__call__'): add = self.addToPosition()
        else: add = self.addToPosition
        return leftMotorPosition + rightMotorPosition + add
        
    def move(self, position, callback=None, async=False):
        """
        Move left and right motor to opposite direction by specified distance
        """
        half_position = (self.get_actual_position() - position) / 2
        leftMotorPosition = self.leftMotor.current_value() + half_position
        rightMotorPosition = self.rightMotor.current_value() + half_position
        
        # check motor limits
        leftMinimum = self.leftMotor.read_attribute("UnitLimitMin").value
        rightMinimum = self.rightMotor.read_attribute("UnitLimitMin").value
        leftMaximum = self.leftMotor.read_attribute("UnitLimitMax").value
        rightMaximum = self.rightMotor.read_attribute("UnitLimitMax").value
        
        if(leftMotorPosition < leftMinimum or rightMotorPosition < rightMinimum):
            raise Exception("Minimum motor position was exceeded")
        if(leftMotorPosition > leftMaximum or rightMotorPosition > rightMaximum):
            raise Exception("Maximum motor position was exceeded")
        
        self.leftMotor.move(leftMotorPosition, async=True)
        self.rightMotor.move(rightMotorPosition, async=True)
    

class counter(TangoDevice):
    """
    Class that define Shutter device
    """
    
    def __init__(self, devicePath, timer):
        """
        Class constructor
        @type devicePath: String
        """
        super(counter, self).__init__(devicePath)
        self.timer = TangoDevice(timer)
    
    def get_counts(self, sampleTime):
        
        self.timer.device.SampleTime = sampleTime
        self.device.Reset()
        
        self.timer.Start()
        
        while self.timer.state() == DevState.MOVING:
            time.sleep(0.1)
            
        return self.device.Counts