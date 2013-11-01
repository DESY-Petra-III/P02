import sys

import PyTango
import p3cntr

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# constants for Rb signal measurement
RUBYREF = 694.31
(RUBYHYDRO, RUBYNONHYDRO) = ("hydrostatic", "non-hydrostatic")

###
## RubyWidget class - dedicated to the gui form shown on the screen
###
class RubyWidget(QMainWindow):
    def __init__(self, app, parent=None):
        super(RubyWidget, self).__init__(parent)
        
        # init variables 
        self.initVars(app)

        # init gui
        self.initSelf()
        
        # init events
        self.initEvents()

        # initialize settings
        self.readSettings()
        
    def initVars(self, app):
        # settings
        self._settings = QSettings(self)
        # application for clipboard access
        self.app = app
    
    def initSelf(self):
        self.setWindowTitle("Ruby system control")
        
        wdgt = QWidget()
        grid = QGridLayout(wdgt)
        
        pal = QPalette()
        color = QColor('blue').light()
        pal.setColor(QPalette.Window, color)
        self.setPalette(pal)
        wdgt.setPalette(pal)
        
        tab = QTabWidget()
        tab.setFont(QFont("Arial", 10))
        self.createStackTab(tab, pal)
        self.createRubySignalTab(tab, pal)
        self.createClipboardTab(tab, pal)
        grid.addWidget(tab, 0,0)
        
        self.setCentralWidget(wdgt)
        
        # icon
        pixmap = QPixmap(16,16)
        pixmap.fill(color)
        self.setWindowIcon(QIcon(pixmap))
        
        # status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
       
        self.show()
       
    def createStackTab(self, tab, pal):
        title = QString("Step 1: Sample alignment")
        
        wdgt = QWidget()
        grid = QGridLayout(wdgt)

        x_ruby = p3cntr.Motor("X ruby",
            "X ruby",
            "haspllabcl1:10000/llab/motor/mot.11")
        y_ruby = p3cntr.Motor("Y ruby (left / right)",
                    "Y ruby",
                    "haspllabcl1:10000/llab/motor/mot.12")
        z_ruby = p3cntr.Motor("Z ruby (up / down)",
                    "Z ruby",
                    "haspllabcl1:10000/llab/motor/mot.15")
        zoom_ruby = p3cntr.Motor("zoom ruby",
                    "zoom ruby",
                    "haspllabcl1:10000/llab/motor/mot.14")
        
        self.stack_widget = p3cntr.ui.MotorWidgetAdvanced([x_ruby,y_ruby,z_ruby,zoom_ruby])
        self.stack_widget.setWindowTitle('Sample stack ruby')

        self.stack_widget.setAutoFillBackground(True)
        self.stack_widget.setPalette(pal)
        grid.addWidget(self.stack_widget)
        
        tab.addTab(wdgt, title)
    
    def createRubySignalTab(self, tab, pal):
        title = QString("Step 2: Ruby measurement")
        
        wdgt = QWidget()
        grid = QGridLayout(wdgt)
        wdgt.setPalette(pal)
        
        label = QLabel("")
        label.setMinimumHeight(15)
        grid.addWidget(label, 0, 0)
        grid.setSpacing(10)
  
        
        (label1, label2, label3, label4) = (QLabel("Mode:"), QLabel("Ruby ref. signal:"), QLabel("Ruby signal:"), QLabel("Pressure:"))
        
        label5 = QLabel("Ruby calibration after:\n Mao H.K. ET AL. (1986) J. Geophys. Res. 91, 4673")
        label5.setAlignment(Qt.AlignTop)
        label5.setStyleSheet("background-color: #eee; padding: 10;")
        
        grid.addWidget(label1, 1, 1)
        self.cbmrbmode = QComboBox()
        self.cbmrbmode.addItem(RUBYHYDRO)
        self.cbmrbmode.addItem(RUBYNONHYDRO)
        grid.addWidget(self.cbmrbmode, 1, 2)
        grid.addWidget(label2, 2, 1)
        self.lerbref = QLineEdit("%.02f"%RUBYREF)
        self.lerbref.setValidator(QDoubleValidator(self.lerbref))
        grid.addWidget(self.lerbref, 2, 2)
        grid.addWidget(label3, 3, 1)
        self.lerbsign = QLineEdit("%.02f"%RUBYREF)
        self.lerbsign.setValidator(QDoubleValidator(self.lerbsign))
        grid.addWidget(self.lerbsign, 3, 2)
        grid.addWidget(label4, 4, 1)
        self.lbrbpress = QLabel("%.02f"%0)
        grid.addWidget(self.lbrbpress, 4, 2)
        self.btnrbcalc = QPushButton("Calculate")
        grid.addWidget(self.btnrbcalc, 5, 2)
        
        grid.addWidget(label5, 1, 3, 5, 1)
        
        grid.setRowStretch(6, 50)
        grid.setColumnStretch(3, 50)
        
        self.setRubyWidgetsFont(label1, label2, label3, label4, label5, self.cbmrbmode, self.lerbref, self.lerbsign, self.lbrbpress, self.btnrbcalc)
        self.lbrbpress.setStyleSheet("background-color: #eee; padding: 10; color: rgb(190, 0, 0); font-weight: bold;")
        
        self.connect(self.btnrbcalc, SIGNAL("clicked()"), self.calcRuby)
        self.connect(self.cbmrbmode, SIGNAL("currentIndexChanged(const QString&)"), self.calcRuby)
        self.connect(self.lerbref, SIGNAL("editingFinished()"), self.calcRuby)
        self.connect(self.lerbref, SIGNAL("returnPressed()"), self.calcRuby)
        self.connect(self.lerbsign, SIGNAL("editingFinished()"), self.calcRuby)
        self.connect(self.lerbsign, SIGNAL("returnPressed()"), self.calcRuby)
        
        tab.addTab(wdgt, title)
        self.calcRuby()
        return
        
    def createClipboardTab(self, tab, pal):
        title = QString("Step 3: Clipboard + InstantBird")
        wdgt = QWidget()
        wdgt.setFont(QFont("Arial", 12))
        wdgt.setMaximumWidth(520)
        grid = QGridLayout(wdgt)
        wdgt.setPalette(pal)
        
        # blank space
        grid.addWidget(QLabel(""), 0, 0)
        
        # user name
        grid.addWidget(QLabel("User Name: "), 1, 0)
        self.leusername = QLineEdit("")
        self.leusername.setToolTip("Give your group a name to use as a reference and pass to the clipboard")
        grid.addWidget(self.leusername, 1, 1)
        
        # cell name
        grid.addWidget(QLabel("Cell Name: "), 2, 0)
        self.lecellname = QLineEdit("")
        self.lecellname.setToolTip("Your cell reference name to pass to the clipboard")
        grid.addWidget(self.lecellname, 2, 1)
        
        # btn to copy values to the clipboard
        self.btncopy = QPushButton("Copy motor positions to clipboard")
        self.btncopy.setMinimumHeight(120)
        self.btncopy.setFont(QFont("Arial", 18))
        grid.addWidget(self.btncopy, 3, 1)
        
        grid.setRowStretch(4, 50)
        grid.setSpacing(15)
        
        tab.addTab(wdgt, title)

    # reading settings
    def readSettings(self):
        # check for Qt version
        if(PYQT_VERSION < 0x40a00):
            value = self._settings.value("Position").toPoint()
        else:
            value = self._settings.value("Position")
        if(value is not None):
            self.move(value)
        return

        # writing settings
    def writingSettings(self):
        self._settings.setValue("Position", self.pos())
        return
    
    # init events
    def initEvents(self):
        self.connect(self.btncopy, SIGNAL("clicked()"), self.btncopy_clicked)
    
    def btncopy_clicked(self):
        motors = self.stack_widget._motors
        motorsdict = self.stack_widget._motorsdict
        
        
        output = ""
        output_status = ""
        
        # user name and cell name
        (un, cn) = (self.leusername.text(), self.lecellname.text())
        
        if(un.length()>0):
            output += "User name: %s \n" % un
        
        if(cn.length()>0):
            output += "Cell name: %s \n\n" % cn
        
        # motor positions
        format = "%s: %.4f"
        for m in motors:
            (name, value) = (m.name, motorsdict[m.name]["Position"])

            value = (format%(name, value))
            output = output + value +"\n"
            output_status = output_status + value +";"
            
        # copy to the clipboard
        self.app.clipboard().setText(output)
        
        # show message in the status bar
        self.report("Copied to the clipboard: ("+output_status+")")
    
    def setRubyWidgetsFont(self, *tlist):
        font = QFont("Arial", 12)
        for w in tlist:
            w.setFont(font)
        
        tlist[-1].setMinimumHeight(40)
    
    def report(self, msg):
        self.status.showMessage(msg, 5000)
    
    # ruby calculation
    def calcRuby(self, *tlist):
        mode = self.cbmrbmode.currentText()
        
        (rbref, rbsign) = (0., 0.)
        try:
            (rbref, rbsign) = (
                float(str(self.lerbref.text())), 
                float(str(self.lerbsign.text()))    
                )
            self.lerbref.setText("%.02f"%rbref)
            self.lerbsign.setText("%.02f"%rbsign)
        except ValueError:
            self.report("Error: ValueError upon pressure calculation; please check the values")
            return
        
        (A, B) = (1904, 7.665)
        if(mode==RUBYNONHYDRO):
            B = 5.
        
        P = float(A/B*(pow((rbsign)/rbref, B)-1))
        
        self.lbrbpress.setText("%.3f GPa"%P)
        return

    # cleaning up 
    def closeEvent(self, event):
        self.writingSettings()
        event.accept()
###
## RubyWidget class end
###        

MAPPLICATION = "BeamlineStack"
MDOMAIN = "desy.de"
MORG = "DESY"

# main app call
if(__name__=="__main__"):
    app = QApplication(sys.argv)

    # initialize values for settings
    app.setOrganizationName(MORG)
    app.setOrganizationDomain(MDOMAIN)
    app.setApplicationName(MAPPLICATION)

    form = RubyWidget(app)
    app.exec_()
