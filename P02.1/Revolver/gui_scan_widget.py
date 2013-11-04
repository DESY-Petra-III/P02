# import global classes 
from PyQt4 import QtGui, Qt
import logging
import sys
import signal
import pickle
import guiqwt.tools as tools
from guiqwt.builder import make
from time import time
from datetime import datetime
from threading import Thread
import random
from guiqwt.styles import CurveParam
from guiqwt.curve import CurveItem
from math import fabs
 
# Import local classes
from gui_default_widget import DefaultWidget
from Revolver.classes import config, dialogs, macro, widget_plot, devices, threads, signals
from UI import layout_scan
import gui_motor_controls_widget
from classes.widget_plot import Image_plot

def getHSVcolors(N):
        """
        Get color range from HSV color space defined by N
        @type N: int
        """
        return [(x * 360 / N, 230, 230) for x in range(N)]

class spinboxTable(Qt.QSpinBox):
    
    def __init__(self):
        super(spinboxTable, self).__init__()
    
    def focusInEvent(self, *args, **kwargs):
        self.emit(Qt.SIGNAL("clicked()"))
        return Qt.QSpinBox.focusInEvent(self, *args, **kwargs)

class ScanWidget(layout_scan.Ui_Form, DefaultWidget):
    
    def __init__(self, parent=None):
        super(ScanWidget, self).__init__(parent)
        self.__init_variables()
        self.__init_signals()
        self.__main()
        
    def __init_signals(self):
        """
        Initialize all signals
        """
        self.connect(self.input_scan_select_motor, Qt.SIGNAL('clicked()'), lambda: dialogs.SelectDeviceDialog(self).exec_())
        self.connect(self, Qt.SIGNAL('changeDefaultMotor'), lambda : self.input_scan_motor.setText(config.DEVICE_MOTOR))
        self.connect(self, Qt.SIGNAL("addRegion"), self.action_add_region)
        self.connect(self, Qt.SIGNAL("RECT_SELECTION_END_REAL_VALUE"), self.action_select_region)
        self.connect(self, Qt.SIGNAL("scanStart()"), self.action_show_scan_graph)
        self.connect(self, Qt.SIGNAL("scanStop()"), self.action_scan_end)
        self.connect(self, Qt.SIGNAL("strobScanStart()"), self.action_show_strob_scan_graph)
        self.connect(self, Qt.SIGNAL("strobScanStop()"), self.action_scan_end)
        self.connect(self, Qt.SIGNAL("toggleScan()"), self.action_toggle_scan)
        self.connect(self, Qt.SIGNAL("repaintCurve"), self.scan_plot.action_set_curve_data)
        self.connect(self.detectorImageScan.plot, Qt.SIGNAL("rect_plot_end"), self.action_add_region)
        self.connect(self.detectorImageScan.plot, Qt.SIGNAL("rect_plot_resized"), self.action_item_moved)
        
        attr = [self.input_scan_start_position, self.input_scan_end_position]
        self.connect(self.input_scan_motor, Qt.SIGNAL('textChanged(QString)'), lambda inputQtObj: self.check_device_allowed_values(attr, devices.Motor(str(inputQtObj))))
        
    def __init_variables(self):
        """
        Initialize all variables
        """
        self.motorWidget = gui_motor_controls_widget.MotorWidget(self, config.DEVICE_MOTOR)
        self.insert_widget(self.motorWidget, self.stroboscope_controls)
        
        self.motorWidget.hide()
        self.controls = {0 : [self.label_step_size, self.label_motor_position,
                              self.input_scan_start_position, self.input_scan_end_position,
                              self.header_scan_settings, self.input_scan_motor_step,
                              self.scan_progressbar],
                         1 : [self.header_stroboscope_settings, self.motorWidget]}
        self.scanType = 0
        self.selectRectFilter = None
        self.regions = []
        self.removePositions = []
        self.selections = []
        self.spinBoxes = []
        self.detectorImageScan = Image_plot(edit=False, toolbar=True,
                                            wintitle="All image and plot tools test", parent=self,
                                            options={"title":"Image from detector", "xlabel":"Widht", "ylabel":"Height"})
        self.scan_plot = widget_plot.Curve_plot(edit=False, toolbar=True,
                                                wintitle="All image and plot tools test", parent=self,
                                                options={"title":"Scan graph", "xlabel":"Motor position", "ylabel":"Avg"})
        
        plot = self.detectorImageScan.plot
        plot.set_axis_direction("left", False)
        plot.set_axis_direction("bottom", False)
        plot.set_axis_limits("left", 0, 2048)
        plot.set_axis_limits("bottom", 0, 2048)
        
    def __main(self):
        """
        Set widget properties
        """
        self.emit(Qt.SIGNAL("changeDefaultMotor"), config.DEVICE_MOTOR)
        self.scanRegions.setSelectionBehavior(Qt.QAbstractItemView.SelectItems);
        self.scanRegions.setSelectionMode(Qt.QAbstractItemView.SingleSelection);
        self.scanRegions.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.scanRegions.horizontalHeader().resizeSection(0, 150);
        
        self.scan_plot_layout.addWidget(self.scan_plot)
        self.detector_scan_image.addWidget(self.detectorImageScan)
        self.__add_region()
    
    def __add_region(self, x0=0, y0=0, x1=2047, y1=2047, description=None):
        """
        Add new region from program runtime
        @type x0: int
        @type y0: int
        @type x1: int
        @type y1: int
        @type description: String
        """
        self.detectorImageScan.get_tool(tools.RectangleTool).add_shape_to_plot(self.detectorImageScan.plot, Qt.QPoint(x0, y0), Qt.QPoint(x1, y1))
        all_regions = self.detectorImageScan.get_all_rectangles()
        last_region = all_regions[-1]
        self.change_region(last_region, x0, y0, x1, y1)
        self.action_add_region(ignore=True, description=description)
        
    def __createSpinBox(self, value=None):
        """
        Create spinbox with selected value
        @type value: int
        """
        spinBox = spinboxTable()
        spinBox.setMinimum(0)
        spinBox.setMaximum(2048)
        if value: spinBox.setValue(value)
        return spinBox
    
    def resizeEvent(self, *args, **kwargs):
        """
        Overriding resizeEvent handler, autoscale detector image.
        """
        self.detectorImageScan.plot.do_autoscale()
        return DefaultWidget.resizeEvent(self, *args, **kwargs)
    
    def change_region(self, region, x0, y0, x1, y1):
        """
        Invoke this method after user change region size
        @type region: guiqwt.shapes.RectangleShape
        @type x0: int
        @type y0: int
        @type x1: int
        @type y1: int
        """
        rx0, ry0, rx1, ry1 = region.get_rect()
        if rx0 > rx1: x0, x1 = x1, x0
        if ry0 > ry1: y0, y1 = y1, y0
        
        region.set_rect(x0, y0, x1, y1)
        self.detectorImageScan.plot.replot()
    
    def action_refresh_detector_image(self):
        """
        Refresh image from perking elmer detector
        """
        self.detectorImageScan.loadImageFromDetector()
    
    def remove_region(self, button):
        """
        Remove region from the table
        @type button: Qpushbutton
        """
        if len(self.removePositions) == 1:
            self.emit(signals.SIG_SHOW_ERROR, "Remove selection", "At least one selection should be added.")
            return
        position = self.removePositions.index(button)
        
        self.detectorImageScan.plot.del_item(self.selections[position])
        del self.spinBoxes[position]
        del self.removePositions[position]
        del self.selections[position]
        self.scanRegions.removeRow(position)
        self.detectorImageScan.plot.replot()
    
    def calculate_limits(self, rect):
        """
        Calculate position and size limits for rectangle selection
        @type rect: list(x0,y0,x1,y1)
        """
        x0, y0, x1, y1 = rect
        if x0 > 2047: x0 = 2047
        elif x0 < 0: x0 = 0
        if y1 > 2047: y1 = 2047
        elif y1 < 0 : y1 = 0
        if x1 > 2047: x1 = 2047
        elif x1 < 0: x1 = 0
        if y0 > 2047: y0 = 2047
        elif y0 < 0 : y0 = 0
        return (x0, y0, x1, y1)
    
    def action_item_moved(self, selection, *args):
        """
        Invoke this method when user move rectangle selection
        """
        try:
            position = self.selections.index(selection)
            spinBoxes = self.spinBoxes[position]
            x0, y0, x1, y1 = self.calculate_limits(selection.get_rect())
            
            if x0 > x1: x0, x1 = x1, x0
            if y0 > y1: y0, y1 = y1, y0
            
            for spinbox in spinBoxes: spinBoxes[spinbox].blockSignals(True)
            
            spinBoxes["x0"].setValue(x0)
            spinBoxes["x1"].setValue(x1)
            spinBoxes["y0"].setValue(y0)
            spinBoxes["y1"].setValue(y1)
            
            for spinbox in spinBoxes: spinBoxes[spinbox].blockSignals(False)
                
            self.change_region(selection, x0, y0, x1, y1)
        except:
            return
     
    def action_add_region(self, ignore=False, description=None):
        """
        Add new region into table
        This method is invoked when user add new rectangle selection in detector image
        @type ignore: bool
        @type description: String
        """
        all_regions = self.detectorImageScan.get_all_rectangles()
        last_region = all_regions[-1]
        if not ignore and last_region in self.selections: return
        
        x0, y0, x1, y1 = self.calculate_limits(last_region.get_rect())
        
        last_region.set_rect(x0, y0, x1, y1)
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        
        table = self.scanRegions
        size = int(table.rowCount())
        table.setRowCount(size + 1)
        
        if not description:
            description = "Selection %i" % (size + 1)
        table.setItem(size, 0, QtGui.QTableWidgetItem(description))
        
        x0spinBox = self.__createSpinBox(x0)
        table.setIndexWidget(table.model().index(size, 1), x0spinBox)
        y0spinBox = self.__createSpinBox(y0)
        table.setIndexWidget(table.model().index(size, 2), y0spinBox)
        x1spinBox = self.__createSpinBox(x1)
        table.setIndexWidget(table.model().index(size, 3), x1spinBox)
        y1spinBox = self.__createSpinBox(y1)
        table.setIndexWidget(table.model().index(size, 4), y1spinBox)
        
        spinBoxes = {"x0":x0spinBox, "y0":y0spinBox, "x1":x1spinBox, "y1":y1spinBox }
        self.connect(x0spinBox, Qt.SIGNAL("valueChanged(int)"), lambda: self.setRect(spinBoxes))
        self.connect(y0spinBox, Qt.SIGNAL("valueChanged(int)"), lambda: self.setRect(spinBoxes))
        self.connect(x1spinBox, Qt.SIGNAL("valueChanged(int)"), lambda: self.setRect(spinBoxes))
        self.connect(y1spinBox, Qt.SIGNAL("valueChanged(int)"), lambda: self.setRect(spinBoxes))
        self.connect(x0spinBox, Qt.SIGNAL("clicked()"), lambda: self.setRect(spinBoxes))
        self.connect(y0spinBox, Qt.SIGNAL("clicked()"), lambda: self.setRect(spinBoxes))
        self.connect(x1spinBox, Qt.SIGNAL("clicked()"), lambda: self.setRect(spinBoxes))
        self.connect(y1spinBox, Qt.SIGNAL("clicked()"), lambda: self.setRect(spinBoxes))
        self.spinBoxes.append(spinBoxes)
          
        removeButton = QtGui.QPushButton("Remove")
        self.removePositions.append(removeButton)
        self.connect(removeButton, Qt.SIGNAL('clicked()'), lambda: self.remove_region(removeButton))
        table.setIndexWidget(table.model().index(size, 5), removeButton)
        
        self.detectorImageScan.plot.replot()
        self.selections.append(last_region)
    
    def setRect(self, spinBoxes):
        """
        Reflect changes from modified region from spinboxes onto detector image
        @type spinBoxes: list
        """
        try:
            position = self.spinBoxes.index(spinBoxes)
            selection = self.selections[position]
            self.detectorImageScan.plot.unselect_all()
            self.detectorImageScan.plot.select_item(selection)
            x0 = spinBoxes["x0"].value()
            y0 = spinBoxes["y0"].value()
            x1 = spinBoxes["x1"].value()
            y1 = spinBoxes["y1"].value()
            
            if x0 > x1: x0, x1 = x1, x0
            if y0 > y1: y0, y1 = y1, y0
            
            self.change_region(selection, x0, y0, x1, y1)
            
            for spinbox in spinBoxes: spinBoxes[spinbox].blockSignals(True)
            
            spinBoxes["x0"].setValue(x0)
            spinBoxes["x1"].setValue(x1)
            spinBoxes["y0"].setValue(y0)
            spinBoxes["y1"].setValue(y1)
            
            for spinbox in spinBoxes: spinBoxes[spinbox].blockSignals(False)
            
        except:
            return
    
    def action_select_region(self, x, y, width, height):
        """
        Highlight one specified region in detector image
        """
        position = self.selections.index(self.selectRectFilter.activeSelection)
        spinBoxes = self.spinBoxes[position]
        spinBoxes["x0"].setValue(x)
        spinBoxes["y0"].setValue(y)
        spinBoxes["x1"].setValue(width)
        spinBoxes["y1"].setValue(height)
    
    def get_regions(self):
        """
        Get all regions from detector image
        """
        regions = {"type":0, "items":[]}
        table = self.scanRegions
        rows = table.rowCount()
        for i in range(0, rows):
            description = str(table.item(i, 0).text())
            x0 = int(self.spinBoxes[i]["x0"].value())
            y0 = int(self.spinBoxes[i]["y0"].value())
            x1 = int(self.spinBoxes[i]["x1"].value())
            y1 = int(self.spinBoxes[i]["y1"].value())
            region = {"description": description, "x0":x0,
                      "y0":y0, "x1":x1, "y1":y1}
            regions["items"].append(region)
        
        return regions
    
    def action_save_scan_ascii(self):
        """
        Save scan as ascii in the output file
        """
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save scan data", "scanData.txt", "*.txt")
        if not filename: return
        
        openFile = open(filename, "w+")
        now = datetime.now()
        regions = self.get_regions()
        openFile.write("# Scan output from date: %s\n" % (now.strftime("%d.%m.%y %H:%M")))
        for region in regions["items"]:
            openFile.write("# %s:\t%i\t%i\t%i\t%i\n" % (region["description"], region["x0"], region["y0"], region["x1"], region["x1"]))
             
        openFile.write("# Used motor: %s\n" % (self.data[0]["motor"]))
        openFile.write("# %s" % (self.dataHeader))
        
        data = [self.data[0]['dataX']];
        for d in self.data:
            data.append(d["dataY"])
        for index in range(len(data[0])):
            row = "\n"
            for index2, d in enumerate(data):
                if index2 == 0: row = row + ("%.4f" % d[index])
                else: row = row + ("\t%.4f" % d[index])
            openFile.write(row)
        openFile.close()
        
    def action_save_scan_image(self):
        """
        Save scan as png image file
        """
        self.scan_plot.get_tool(tools.SaveAsTool).activate_command(self.scan_plot.plot, True)
        
    def action_save_regions(self):
        """
        Scan region table and prepare object to save to the output file
        """
        regions = self.get_regions()
        
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save regions selection", "regionsSelection.regions", "*.regions;; *.txt")
        if filename:
            fileSave = open(filename, 'w+')
            pickle.dump(regions, fileSave)
            fileSave.close()
            logging.info("Regions selection was succesfully saved into file: %s", filename)
        
    def action_load_regions(self):
        """
        Load regions from selected input file
        """
        filename = QtGui.QFileDialog.getOpenFileName(self, "Load regions selection", "regionsSelection.regions", "*.regions;; *.txt")
        if filename:
            try:
                fileLoad = open(filename, 'r')
                regions = pickle.load(fileLoad)
                fileLoad.close()
                self.action_reset_regions(False)
                for region in regions["items"]:
                    self.__add_region(int(region["x0"]), int(region["y0"]), int(region["x1"]), int(region["y1"]), region["description"])
                     
                logging.info("Regions selection was succesfully loaded from file: %s", filename)
            except KeyError:
                self.emit(signals.SIG_SHOW_ERROR, "Load error", "Uknown file format")
    
    def action_reset_regions(self, addDefaultSelection=True):
        """
        Reset all created regions in image from detector
        Add default region (whole image) if addDefaultSelection flag is True
        @type addDefaultSelection: bool
        """
        for selection in self.selections:
            self.detectorImageScan.plot.del_item(selection)
        
        self.removePositions = []
        self.selections = []
        self.spinBoxes = []
        self.regions = []
        
        self.detectorImageScan.plot.replot()
        self.scanRegions.setRowCount(0)
        if addDefaultSelection : self.__add_region()
    
    def action_toggle_scan(self):
        """
        Signal handler:
        toggle scan start / stop
        """
        if not(macro.STOP): 
            macro.STOP = True
            self.motorWidget.action_stop_motor()
            self.button_stop_scan.setText("Start scan")
        else: 
            self.action_start_scan()
            self.button_stop_scan.setText("Stop scan")
    
    def action_start_scan(self):
        """
        Signal handler:
        start scan
        """
        summed = int(self.input_scan_summed.text())
        
        self.set_diode_laser_out()
        if self.scanType == 0:
            motor_start_position = float(self.input_scan_start_position.text())
            motor_end_position = float(self.input_scan_end_position.text())
            motor_step = float(self.input_scan_motor_step.text())
            
            if motor_start_position == motor_end_position:
                QtGui.QMessageBox.question(self, 'Input error', "Motor start position and motor end position must be different ", QtGui.QMessageBox.Ok)
                return
            
            try:
                self.validate_device_minmax_value(motor_start_position)
                self.validate_device_minmax_value(motor_end_position)
            except:
                return
                
        self.emit(signals.SIG_SET_PROGRESSBAR, self.scan_progressbar, 0)
        
        answer = dialogs.askWarnDialog(self, "Dark shot", "Do you want to take dark shot before macro start?")
        try:
            regions = self.get_regions()
            if self.scanType == 0:
                self.start_scan_plot_routine(summed, motor_start_position, motor_end_position, motor_step, regions, takeDark=answer)
            elif self.scanType == 1:
                self.start_strob_plot_routine(summed, regions, takeDark=answer)
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Scan error", "Scan could not be completed")
    
    def start_scan_plot_routine(self, summed, motorStart, motorEnd, motor_step, regions, takeDark=None):
        """
        Start plotting basic scan.
        Prepare GUI, check all restrictions and start plot thread.
        @type summed: int
        @type motorStart: float
        @type motorEnd: float
        @type motor_step: float
        @type regions: dict
        """
        if motor_step > fabs(motorStart - motorEnd): raise Exception("Step is bigger than maximum allowed step")
        if motor_step == 0: raise Exception("Step size must be greater than zero !") 
        
        macro.STOP = False
        
        scannedRegions = []
        self.dataHeader = "%s" % "Motor position"
        self.scan_plot.get_plot().del_all_items()
        self.scan_plot.get_plot().do_autoscale(True)
        
        HSV_tuples = getHSVcolors(len(regions["items"]))
        for index, region in enumerate(regions["items"]):
            colorHSV = HSV_tuples[index]
            color = QtGui.QColor()
            color.setHsv(colorHSV[0], colorHSV[1], colorHSV[2])
            
            param = CurveParam()
            param.label = region["description"]
            
            curve = CurveItem(param)
            curve = make.curve([], [], title=region["description"], color=color, marker=".")
            curve.set_readonly(True)
            self.scan_plot.plot.add_item(curve)
            
            self.dataHeader = self.dataHeader + "\t%s" % region["description"]
            quadrant = {'curve':curve, 'x0':region["x0"], 'y0':region["y0"],
                        'x1':region["x1"], 'y1':region["y1"], 'dataX' : [], 'dataY': [],
                        "axisX": "Pos", "axisY": "Avg", "motor": self.defaultMotorDevice.name}
            scannedRegions.append(quadrant)
        
        scan_attributes = [summed, motorStart, motorEnd, motor_step, scannedRegions, takeDark]
        self.emit(Qt.SIGNAL("scanStart()"))
        self.scan_plot.zoom_enabled(False)
                
        # execute scan thread
        thread = Thread(target=self.__scan_plot_routine, args=(scan_attributes))
        
        threads.add_thread(thread, self.widget_id)
        thread.start()
    
    def __scan_plot_routine(self, summed, motorStart, motorEnd, step, scanAttr, takeDark):
        """
        Scan routine:
        count steps, move motor to one step position and take a shot
        @type summed: int
        @type motorStart: float
        @type motorEnd: float
        @type step: float
        @type scanAttr: list
        """
        self.data = scanAttr
        logging.info("Scan started")
        
        try:
            motor = self.defaultMotorDevice
            detector = devices.Detector(config.DEVICE_DETECTOR)
            shutter = devices.Shutter(config.DEVICE_SHUTTER)
            detectorController = devices.DetectorController(config.DEVICE_DETECTOR_CONTROLLER)
            
            # move motor to start position, then open shutter
            scanStart = time()
            motor.move(motorStart)
            scanEnd = time()
            
            if takeDark:
                self.scan_take_dark(summed, (scanEnd - scanStart))
            
            index = 0
            avgMax = 0
            
            shutter.open()
            mrange = macro.macroRange(motorStart, motorEnd, step)
            progress_step = float(100 / float(len(mrange)))
                
            for i in mrange:
                if macro.STOP or not threads.THREAD_KEEP_ALIVE:
                    logging.info("Scan was stopped")
                    shutter.close()
                    break
                motor.move(round(float(i), 4))
                detector.take_scan_shot(summed)
                for attr in scanAttr:
                    avg = float(detectorController.take_readout(attr['x0'], attr['y0'], attr['x1'], attr['y1']))
                    # avg = random.randint(1, 100)
                    if avgMax < avg: avgMax = avg
                    attr['dataX'].append(i)
                    attr['dataY'].append(avg)
                    
                    self.emit(Qt.SIGNAL("repaintCurve"), attr['curve'], attr['dataX'], attr['dataY'])
                
                index = index + 1
                self.emit(signals.SIG_SET_PROGRESSBAR, self.scan_progressbar, progress_step * index)
                
            if not(macro.STOP):
                self.emit(signals.SIG_SET_PROGRESSBAR, self.scan_progressbar, 100)
                logging.info("Scan succesfully ended")
            
            shutter.close()
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Scan error", "Scan could not be completed.", self.get_exception())
            self.button_new_scan.click()
        
        self.emit(Qt.SIGNAL("scanStop()"))
    
    def start_strob_plot_routine(self, summed, regions, takeDark=None):
        """
        Start plotting stroboscope scan.
        Prepare GUI, check all restrictions and start plot thread.
        @type summed: int
        @type regions: dict
        """
        
        try:
            self.motorWidget.action_change_motor(self.defaultMotorDevice.devicePath)
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Stroboscope error", "Stroboscope could not start.", self.get_exception())
            self.button_new_strob.click()
        
        macro.STOP = False
        
        scannedRegions = []
        self.dataHeader = "%s" % "Time"
        self.scan_plot.get_plot().del_all_items()
        self.scan_plot.get_plot().do_autoscale(True)
        
        HSV_tuples = getHSVcolors(len(regions["items"]))
        for index, region in enumerate(regions["items"]):
            colorHSV = HSV_tuples[index]
            color = QtGui.QColor()
            color.setHsv(colorHSV[0], colorHSV[1], colorHSV[2])
            
            param = CurveParam()
            param.label = region["description"]
            curve = CurveItem(param)
            curve = make.curve([], [], title=region["description"], color=color, marker=".")
            curve.set_readonly(True)
            self.scan_plot.plot.add_item(curve)

            self.dataHeader = self.dataHeader + "\t%s" % region["description"]
            quadrant = {'curve':curve, 'x0':region["x0"], 'y0':region["y0"],
                        'x1':region["x1"], 'y1':region["y1"], 'dataX' : [], 'dataY': [],
                        "axisX": "Pos", "axisY": "Avg", "motor": self.defaultMotorDevice.name}
            scannedRegions.append(quadrant)
        
        self.scan_plot.zoom_enabled(False)
        scan_attributes = [summed, scannedRegions, takeDark]
        self.emit(Qt.SIGNAL("strobScanStart()"))
                
        # execute scan thread
        thread = Thread(target=self.__strob_plot_routine, args=(scan_attributes))
        threads.add_thread(thread, self.widget_id)
        thread.start()
       
    def __strob_plot_routine(self, summed, scanAttr, takeDark):
        """
        Strob routine:
        Take shot every tick specified by frequency.
        User can move selected motor in MotorWidget.
        @type summed: int
        @type scanAttr: list
        """
        self.data = scanAttr
        logging.info("Stroboscope started")
        
        try:
            detector = devices.Detector(config.DEVICE_DETECTOR)
            detectorController = devices.DetectorController(config.DEVICE_DETECTOR_CONTROLLER)
            shutter = devices.Shutter(config.DEVICE_SHUTTER)
            startTime = time()
            
            if takeDark:
                self.scan_take_dark(summed)

            xTime = 0
            graphValues = 20
            motorPosition = []
            shutter.open()
            while not(macro.STOP) and threads.THREAD_KEEP_ALIVE:
                stepTime = time()
                xTime = stepTime - startTime
                detector.take_scan_shot(summed)
                motorPosition.append(self.defaultMotorDevice.device.read_attribute("Position").value)
                for attr in scanAttr:
                    yAvg = float(detectorController.take_readout(attr['x0'], attr['y0'], attr['x1'], attr['y1']))
                    yAvg = random.randint(1, 100)
                    
                    attr['dataX'].append(xTime)
                    attr['dataY'].append(yAvg)
                    self.emit(Qt.SIGNAL("repaintCurve"), attr['curve'], attr['dataX'][graphValues * -1:], attr['dataY'][graphValues * -1:])
                # sleep(0.5)
                
            self.dataHeader = self.dataHeader + "\tMotor position"
            quadrant = {'dataX' : scanAttr[0]['dataX'], 'dataY': motorPosition, "motor": self.defaultMotorDevice.name}
            self.data.append(quadrant)    
            shutter.close()
            
        except:
            self.emit(signals.SIG_SHOW_ERROR, "Stroboscope error", "Stroboscope could not start.", self.get_exception())
            self.emit(Qt.SIGNAL("toggleScan()"))
        
        self.emit(Qt.SIGNAL("strobScanStop()"))
   
    def scan_take_dark(self, summed, substractTime=0):
        """
        Take dark for scan
        @type summed: int
        @type substractTime: int
        """
        dmacro = macro.DarkShotMacro(summed)
        dmacro.emit = self.emit_handler
        dmacro.run(int(substractTime))
    
    def emit_handler(self, signal, *args, **kargs):
        """
        @type signal: String
        @type args: list
        @type kargs: dict
        """
        if(signal == "showTimeProgress"): self.emit(Qt.SIGNAL("showElement"), self.scan_waiting_progress, kargs.get("flag"))
        elif(signal == "setWaitProgress"): self.emit(signals.SIG_SET_PROGRESSBAR, self.scan_waiting_progress, args[0])
    
    def action_change_scan_type(self, scanType):
        """
        Change scan type. Go over self.controls list hide all previous controls and show all actual
        @type scanType: int
        """
        map(lambda item: item.hide(), self.controls[self.scanType])
        map(lambda item: item.show(), self.controls[int(scanType)])
        self.scanType = scanType
    
    def action_reset_scan(self):
        """
        Signal handler:
        stop scan
        """
        macro.STOP = True
        self.scan_save_controls_widget.show()
        self.scan_widget_select.setCurrentWidget(self.scan_controls_widget)
      
    def action_show_scan_graph(self):
        """
        Show GUI for scan
        """
        self.button_stop_scan.hide()
        self.button_new_scan.setText("Stop scan")
        self.scan_save_controls_widget.hide()
        self.scan_progressbar.show()
        self.scan_widget_select.setCurrentWidget(self.scan_graph_widget)
    
    def action_show_strob_scan_graph(self):
        """
        Show GUI for stroboscope
        """
        self.button_stop_scan.hide()
        self.button_new_scan.setText("Stop scan")
        self.scan_save_controls_widget.hide()
        self.scan_widget_select.setCurrentWidget(self.scan_graph_widget)
    
    def action_scan_end(self):
        """
        Show GUI after scan ended
        """
        macro.STOP = True
        self.button_stop_scan.show()
        self.button_new_scan.setText("Repeat scan")
        self.button_stop_scan.setText("New scan")
        self.scan_save_controls_widget.show()
        self.scan_progressbar.hide()
        self.scan_plot.zoom_enabled(True)
               
# MAIN PROGRAM #################################################################################

if __name__ == '__main__':
    
    # create main window
    app = QtGui.QApplication(sys.argv)
    
    # init widget
    widget = ScanWidget(app)

    # connect signal from window "x" button to close the application correctly
    app.connect(app, signals.SIG_ABOUT_QUIT, widget.close_widget)
    
    # connect signal from keyboard interruption (if widget is closed with ctrl+c from console)
    signal.signal(signal.SIGINT, lambda *args, **kwargs: widget.close())
    
    # show widget
    widget.show()
    
    # execute application
    app.exec_()    
