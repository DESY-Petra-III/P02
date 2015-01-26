from guiqwt.plot import ImageDialog, CurveDialog
import guiqwt.tools as tools
from guiqwt.builder import make
from guiqwt.shapes import RectangleShape
from PyQt4 import Qt
# from libtiff import TIFF
from numpy import zeros
from guiqwt.fit import FitParam, guifit

from Revolver.classes import devices, config, signals
class plot_event_filter(Qt.QObject):
    """
    Event filter, that cathces events from guiqwt plot element.
    """
    
    def __init__(self, parent):
        """
        Class constructor:
        @type parent: Qt.QObject
        """
        super(Qt.QObject, self).__init__()
        self.parent = parent
        self.moving = False
    
    def eventFilter(self, *args, **kwargs):
        """
        Event filter defined for mouse button release and press, mouse move. 
        """
        plot = args[0]
        event = args[1]
        eventType = args[1].type()
        actualTool = self.parent.get_active_tool()
        
        if eventType == Qt.QEvent.MouseButtonRelease:
            if plot.filter.state == 57 and self.moving == True and event.button() == 1:
                if actualTool == self.parent.get_tool(tools.RectangleTool):
                    plot.emit(Qt.SIGNAL("rect_plot_end"))
            if actualTool == self.parent.get_tool(tools.SelectTool):
                    plot.emit(Qt.SIGNAL("rect_plot_resized"), plot.get_active_item())
            self.moving = False
        
        if eventType == Qt.QEvent.MouseMove:
            self.moving = True
        
        if eventType == Qt.QEvent.MouseButtonPress:
            self.startPoint = event.pos() 
            if event.button() == 2:
                plot.do_autoscale()
                self.parent.activate_default_tool()
                actualTool.activate()
                return True
            if event.button() == 4:
                actualTool.activate()
                return False
        return False

class Widget_plot():
    """
    Main plot class for every plot dialog object.
    """
    
    def __init__(self):
        """
        Class constructor
        """
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        """
        Initialize all variables
        """
        self.plot = self.get_active_plot()
        for x in (4, 5, 11, 12, 18, 19, 7, 13, 14, 20, 21): 
            self.plot.filter.states[x] = {}
        self.plotFilter = plot_event_filter(self)
        self.plot.installEventFilter(self.plotFilter)
        
    def __init_signals(self):
        """
        Initialize all signals
        """
        pass
                
    def __main(self):
        """
        Set properties
        """
        pass
    
    def get_all_rectangles(self, typeFilter=RectangleShape):
        """
        Get all rectangles defined in current plot.
        @type typeFilter: Type
        @rtype: list
        """
        rectangles = []
        all_items = self.plot.get_items()
        for item in all_items:
            if isinstance(item, typeFilter):
                rectangles.append(item)
        return rectangles
    
    def zoom_enabled(self, flag):
        """
        Set true/false if zoom tool should be enabled
        @type flag: Bool
        """
        self.get_toolbar().children()[4].setEnabled(flag)
    
class Curve_plot(CurveDialog, Widget_plot):
    """
    Curve plot dialog
    """
    
    def __init__(self, wintitle='guiqwt plot', icon='guiqwt.svg', edit=True, toolbar=False, options=None, parent=None, panels=None):
        """
        Class constructor:
        @type wintitle: String
        @type icon: String
        @type edit: bool
        @type toolbar: bool
        @type options: diciotnary
        @type parent: mixed
        @type panels: list
        """
        super(Curve_plot, self).__init__(wintitle=wintitle, icon=icon, edit=edit, toolbar=toolbar, options=options, parent=parent, panels=panels)
        Widget_plot.__init__(self)
        self.__main()
    
    def __main(self):
        """
        Set properties
        """
        self.get_itemlist_panel().show()
    
    def action_set_curve_data(self, curve, x, y):
        """
        Signal handler:
        set data to desired curve in graph
        @type curve: Qwt5.QwtPlotCurve
        @type x: list
        @type y: list
        """
        if x[0] is not None and y[0] is not None:
            curve.set_data(x, y)
            if isinstance(self.get_active_tool(), tools.SelectTool):
                self.plot.do_autoscale()        
        
class Image_plot(ImageDialog, Widget_plot):
    
    def __init__(self, wintitle='guiqwt plot', icon='guiqwt.svg', edit=False, toolbar=False, options=None, parent=None, panels=None):
        """
        Class constructor:
        @type wintitle: String
        @type icon: String
        @type edit: bool
        @type toolbar: bool
        @type options: diciotnary
        @type parent: mixed
        @type panels: list
        """
        super(Image_plot, self).__init__(wintitle=wintitle, icon=icon, edit=edit, toolbar=toolbar, options=options, parent=parent, panels=panels)
        self.add_tool(tools.RectangleTool)
        Widget_plot.__init__(self)
        self.__init_variables()
        self.__init_signals()
        self.__main()
    
    def __init_variables(self):
        """
        Initialize all variables
        """
        self.image = make.image(zeros(shape=(2047, 2047)), colormap="binary")
        
    def __init_signals(self):
        """
        Initialize all signals
        """
        pass
    
    def __main(self):
        """
        Set properties
        """
        self.get_contrast_panel().show()
        self.image.set_movable(False)
        self.image.set_resizable(False)
        self.image.set_readonly(True)
        self.plot.add_item(self.image)
        self.plot.select_item(self.image)
        self.get_contrast_panel().set_range(0, 1700)
        try: self.button_box.hide() 
        except: pass
        
    def loadImageFromDetector(self):
        """
        Load image directly from Perkin Elmer detector.        
        """
        try:
            detectorController = devices.DetectorController(config.DEVICE_DETECTOR_CONTROLLER)
            dataObj = detectorController.get_last_shot()
        except:
            self.window().emit(signals.SIG_SHOW_ERROR, "Plot error", "Detector controller could not be initialized")
            return
        
        try:
            self.image.set_data(dataObj["data"])
            self.plot.set_title(dataObj["filename"])
            self.get_contrast_panel().set_range(0, 1700)
            self.plot.do_autoscale()
        except:
            self.window().emit(signals.SIG_SHOW_ERROR, "Plot error", "Image from detector could not be taken")
            return
            
    def loadImage(self, imgPath):
        """
        Load image from PNG file
        @type imgPath: string
        """
        return
        """
        self.imageLoad = imgPath
        img = TIFF.open(self.imageLoad, mode="r")
        return img.read_image(img)
        """
