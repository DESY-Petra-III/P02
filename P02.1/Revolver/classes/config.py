"""
Configuration file
"""
import Revolver

# define passwords
SETTINGS_EXPERT_MODE_PASSWORD = str(2501)

# define expert settings
SETTINGS_HOTBLOVER_TEMPERATURE_MIN = 20
SETTINGS_HOTBLOVER_TEMPERATURE_MAX = 750 
SETTINGS_HOTBLOVER_TEMPERATURE_SAFE = 22
SETTINGS_CRYOSTREAMER_TEMPERATURE_MIN = 80
SETTINGS_CRYOSTREAMER_TEMPERATURE_MAX = 300
SETTINGS_CRYOSTREAMER_TEMPERATURE_SAFE = 295 
SETTINGS_RAMPING_MAXIMUM_TIME = 1800
SETTINGS_STABILIZATION_TIME_MIN = 60
SETTINGS_STABILIZATION_TIME_MAX = 300
SETTINGS_RAMPING_ERROR_THRESHOLD = 2
SETTINGS_TEST_MODE = False

# define server
DEVICE_SERVER = 'tango://haspp02oh1:10000/'
DEVICE_SERVER_P02 = 'tango://haspp02oh1:10000/'
#DEVICE_SERVER = 'tango://has6117b:10000/'
#DEVICE_MOTOR = DEVICE_SERVER + "p02/motor/exp.01"
DEVICE_DETECTOR_CONTROLLER = DEVICE_SERVER_P02 + 'p02/pectrl/xrd.01'

# define default devices
DEVICE_DETECTOR = DEVICE_SERVER + 'p02/pedetector/xrd.01'
#DEVICE_DETECTOR_CONTROLLER = DEVICE_SERVER + 'p02/pectrl/xrd.01'
DEVICE_SHUTTER = DEVICE_SERVER + 'p02/register/eh1a.out01'
DEVICE_SHUTTER_MAIN = DEVICE_SERVER + 'p02/shutter/1'
DEVICE_MOTOR = DEVICE_SERVER + "p02/motor/eh1a.14"

#DEVICE_HOTBLOWER = DEVICE_SERVER_P02 + "p02/eurotherm2408/ch1a.01"
DEVICE_HOTBLOWER = DEVICE_SERVER_P02 + "p02/eurotherm/exp.01"
DEVICE_CRYOSTREAMER = DEVICE_SERVER + "p02/cryocontempctrl/elab.01"

MACROSERVER = DEVICE_SERVER_P02+"p02/macroserver/haspp02ch1a.01"

TEMPERATURE_DEVICE_SETTINGS = {
                        DEVICE_HOTBLOWER : {
                                            "setpoint":"Setpoint", 
                                            "readout":"Temperature",
                                            "settings":{
                                                        "MIN":SETTINGS_HOTBLOVER_TEMPERATURE_MIN, 
                                                        "MAX":SETTINGS_HOTBLOVER_TEMPERATURE_MAX, 
                                                        "SAFE":SETTINGS_HOTBLOVER_TEMPERATURE_SAFE,
                                                        "HOMING":True,
                                                        }
                                            },
                        DEVICE_CRYOSTREAMER : {
                                            "setpoint":"SetTempLoop1", 
                                            "readout":"TempChannelA",
                                            "settings":{
                                                        "MIN":SETTINGS_CRYOSTREAMER_TEMPERATURE_MIN, 
                                                        "MAX":SETTINGS_CRYOSTREAMER_TEMPERATURE_MAX, 
                                                        "SAFE":SETTINGS_CRYOSTREAMER_TEMPERATURE_SAFE,
                                                        "HOMING":True,
                                                        }
                                            }
                     }

# define device human names
DEVICE_NAMES = {
                
                'DIODE':'p02/festocompairdistributor/eh1a.01',
                'LASER':'p02/festocompairdistributor/eh1a.01',
                'ABSORBER':'p02/festocompairdistributor/eh1a.01',
                'PEX': 'p02/motor/eh1b.15',
                'PEY': 'p02/motor/eh1b.16',
                'S1_LEFT': 'p02/motor/eh1a.01',
                'HAB_Y': 'p02/motor/eh1a.21',
                'HAB_X': 'p02/motor/eh1a.20',
                'CRYO_Z': 'p02/motor/eh1a.19',
                'HAB_Z': 'p02/motor/eh1a.22',
                'L2ROLL': 'p02/motor/eh1b.25',
                'MAIN_SHUTTER': 'p02/shutter/1',
                'BSTY': 'p02/motor/eh1b.13',
                'BSTZ': 'p02/motor/eh1b.06',
                'PETRA_CURRENT': 'petra/globals/keyword',
                'PH2Y': 'p02/motor/eh1a.11',
                'L2PITCH': 'p02/motor/eh1b.29',
                'HOTBLOWER': 'p02/eurotherm2408/ch1a.01',
                'PEX_LARGE': 'p02/motor/eh1b.14',
                'S2_TOP': 'p02/motor/eh1a.07',
                'S1_TOP': 'p02/motor/eh1a.03',
                'L1PITCH': 'p02/motor/eh1b.26',
                'TTI': 'p02/motor/eh1b.04',
                'MAD_ROT': 'p02/motor/eh1b.11',
                'TTO': 'p02/motor/eh1b.07',
                'L1KAPPA': 'p02/motor/eh1b.17',
                'S2_BOTTOM': 'p02/motor/eh1a.08',
                'TBLZ': 'p02/motor/eh1a.23',
                'S2_RIGHT': 'p02/motor/eh1a.06',
                'CRYO_X': 'p02/motor/eh1a.17',
                'DIFFV': 'p02/motor/eh1b.02',
                'L2H': 'p02/motor/eh1b.22',
                'S2_LEFT': 'p02/motor/eh1a.05',
                'STAGE_X': 'p02/motor/eh1a.13',
                'STAGE_Y': 'p02/motor/eh1a.14',
                'STAGE_Z': 'p02/motor/eh1a.15',
                'S1_RIGHT': 'p02/motor/eh1a.02',
                'SPINNER': 'p02/motor/eh1a.16',
                'S1_TT': 'p02/motor/eh1b.12',
                'PH1Z': 'p02/motor/eh1a.10',
                'PH1Y': 'p02/motor/eh1a.09',
                'L2V': 'p02/motor/eh1b.23',
                'DIFFH': 'p02/motor/eh1b.01',
                'PH2Z': 'p02/motor/eh1a.12',
                'OM': 'p02/motor/eh1b.03',
                'CRYO_Y': 'p02/motor/eh1a.18',
                'BATTERY': 'p02/motor/eh1a.32',
                'IONCHAMBER': 'p02/adc/eh1b.01',
                'SMALL_SHUTTER': 'p02/register/eh1a.out01',
                'SAMZ': 'p02/motor/eh1b.10',
                'SAMY': 'p02/motor/eh1b.09',
                'SAMX': 'p02/motor/eh1b.08',
                'L1H': 'p02/motor/eh1b.18',
                'L1ROLL': 'p02/motor/eh1b.21',
                'S1_BOTTOM': 'p02/motor/eh1a.04',
                'PE_DETECTOR': 'p02/pedetector/xrd.01',
                'L1V': 'p02/motor/eh1b.19'}

# define default paths
PATH_MOTOR_FILTER = ["p02/motor/"]
PATH_HOTBLOWER_FILTER = ["p02/eurotherm/","p02/eurotherm2408/"]
PATH_CRYOSTREAMER_FILTER = ["p02/cryocontempctrl/"]
PATH_TEMPERATURE_DEVICE_FILTER = ["p02/eurotherm/","p02/eurotherm2408/","p02/cryocontempctrl/"]

# define log
PATH_LOG_FOLDER = Revolver.__path__[0] + "/log"
DEFAULT_LOG_FILE = PATH_LOG_FOLDER + "/logfile.log"
# actual file, where logdata is written
ACTUAL_LOG_FILE = DEFAULT_LOG_FILE

# define icons path
ICON_MAIN = "./icons/main.png"
ICON_MENU_QUIT = "./icons/exit.png"
ICON_ABOUT = "./icons/banner.jpg"
ICON_MENU_ABOUT = "./icons/about.png"

# define retry time in case of device error
DEVICE_RETRY_INTERVAL = 5
# define flag which set if system should retry for disconnected device
DEVICE_ALLOW_RETRY = True

BL_DEFAULT_DOOR = "tango://haspp02oh1:10000/p02/door/haspp02ch1a.01"
