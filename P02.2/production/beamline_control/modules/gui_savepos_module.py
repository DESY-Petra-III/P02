#!/bin/env python
import ast
import copy
from PyQt4.QtCore import *
from PyQt4.QtGui import *

MANPOSITIONS = "Saved Positions"

MSAVEPOSAPP = "SaveMotorPositionsApp"
MSAVEPOSAPPDOMAIN = "desy.de"
MSAVEPOSAPPORG = "DESY"

MSAVEPOSAPPCONFIGFILE = "settings_positions.ini"

MSAVEPOSAPPVERSION = "0.2"

# widget settings
# label, date, motor positions, number (unique for separation), protected (protects from changes - expert mode)
MSAVEPOSAPPSET = {
        "PositionsApplication": {"Version": MSAVEPOSAPPVERSION, "Order":("Sample stage", "Pinhole stack")},
        "Order": {"Current": ["Sample stage", "Pinhole stack"]},
        "Sample stage":{
                 "Template":[ "Label", "","Date", "20130901","CenX", 0.,"CenY", 0.,"SamZ", 0., "Omega", 0.,  "Protected", False],
                 "Cross": [ "Label", "","Date", "20130901","CenX", 0.,"CenY", 0.,"SamZ", 0., "Omega", 0.,  "Protected", True]
                 },
        "Pinhole stack":{"Template":[ "Label", "","Date", "20130901","PinY", 0.,"PinZ", 0.,"Protected", False]}
}

# 
(MSAVEPOSIADD, MSAVEPOSIEDIT, MSAVEPOSIEXPORT) = ("beamline_images/add.png", "beamline_images/edit.png", "beamline_images/export.png")

# colors for cells
(MSAVEPOSCOLORPROTECT, MSAVEPOSCOLORODD, MSAVEPOSCOLOREVEN) = (QColor('red').light(), QColor('white'), QColor('grey').light())

# Export signal
SIGNALMSAVEPOSEXPORT = "exportPosition"


# Modal Dialog Window title
MANPOSITIONSDIALOG =  "Add or Change position"

# class for saving and recalling important positions
class MSavePos(QWidget):
    def __init__(self, app, savefile, parent=None):
        super(MSavePos, self).__init__(parent)

        self.initVars(app, savefile)
        self.initSelf()
        self.initEvents()

    # init variables and settings
    def initVars(self, app, savefile):
        # application
        self._app = app

        # data template
        self._data = copy.deepcopy(MSAVEPOSAPPSET)

        # mode - normal, expert
        self._bexpert = False

        # settings
        self._settings = QSettings(savefile, QSettings.IniFormat)

        # read settings
        self.readSettings()
        return

    # init gui
    def initSelf(self):
        grid = QGridLayout(self)

        self.setWindowTitle(MSAVEPOSAPP)

        label = QLabel("Saved Classes:")
        self.cmbclass = QComboBox(self)
        self.tbpositions = QTableWidget(self)
        self.initTable(self.tbpositions)

        # image buttons
        self.btnaddposition = QToolButton()
        self.btneditposition = QToolButton()
        self.btnexportposition = QToolButton()

        # apply images to the buttons
        self.btnaddposition.setIcon(QIcon(MSAVEPOSIADD))
        self.btneditposition.setIcon(QIcon(MSAVEPOSIEDIT))
        self.btnexportposition.setIcon(QIcon(MSAVEPOSIEXPORT))

        # initialize combobox from self._data, use order entry to control order of cmb entries
        v = self._data["PositionsApplication"]["Order"]
        t = type(v)
        if(t is str):
            v = ast.literal_eval(v)
        for k in v:
            self.cmbclass.addItem(k)

        self.cmbclass.setCurrentIndex(0)
        self.processTableRedraw()

        # setting tooltips
        self.setWidgetsToolTips(self.btnaddposition, "Add or refresh a position", self.btneditposition, "Edit the selected position", self.btnexportposition, "Export the selected position",
                                self.cmbclass, "Select position class")

        # place widgets to their places
        self.setWidgetsCertainLayout(grid, label, (0, 0), 
                                            self.cmbclass, (0, 1),
                                            self.btnaddposition, (0, 2),
                                            self.btneditposition, (0, 3),
                                            self.btnexportposition, (0, 4),
                                            self.tbpositions, (1, 0, 1, 5))

        grid.setColumnStretch(1, 50)

        self.setMinimumHeight(180)
        self.setMinimumWidth(400)

        self.tbpositions.adjustSize()
        self.adjustSize()
        self.show()
        return

    def initEvents(self):
        # selection change in table to rows
        self.connect(self.tbpositions, SIGNAL("itemSelectionChanged()"), self.processTableSelection)

        # combobox item changed
        self.connect(self.cmbclass, SIGNAL("currentIndexChanged(const QString&)"), self.processTableRedraw)

        # update data as soon as the data is changed
        self.connect(self.tbpositions, SIGNAL("cellChanged(int,int)"), self.processTableItem)

        # process buttons controlling data
        self.connect(self.btnaddposition, SIGNAL("clicked()"), self.processPositionAdd)
        func_callback = lambda bedit=True: self.processPositionAdd(bedit)
        self.connect(self.btneditposition, SIGNAL("clicked()"), func_callback)
        self.connect(self.btnexportposition, SIGNAL("clicked()"), self.processPositionExport)

        # remove entry buttons are initialized in TableRedraw - dynamic nature
        return

    # init table view
    def initTable(self, table):
        self.refreshTable(table)
        return

    # refresh table size
    def refreshTable(self, table):
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

    # event on exit
    def closeEvent(self, event):
        self.writeSettings()
        event.accept()

    # read settings upon widget start
    def readSettings(self):
        # create new config with dummy entries
        setting = self._settings

        # check if config file exists
        bexist = False
        setting.beginGroup("PositionsApplication")
        if(setting.contains("Version")):
            bexist = True
        setting.endGroup()

        # create and fill new config file if needed
        if(not bexist):
            self.writeSettings()

        # reading settings
            # fill self._data slowly
        groups = setting.childGroups()
        for group in groups:
            group = str(group)
            setting.beginGroup(group)
            child = setting.allKeys()
            for k in child:
                k = str(k)
                # discriminating different classes
                value = str(setting.value(k).toString())
                if(group=="Sample stage"):
                    value = ast.literal_eval(value)
                elif(group=="Pinhole stack"):
                    value = ast.literal_eval(value)
                
                self._data[group][k] = value
            setting.endGroup()
        return

    # save settings - positions
    def writeSettings(self):
        setting = self._settings
        for k in self._data:
                group = self._data[k]
                setting.beginGroup(k)
                for gk in group:
                    setting.setValue(gk, str(group[gk]))
                setting.endGroup()
        return

    # fast gui layout creation
    def setWidgetsCertainLayout(self, grid, *tlist):
        for i in range(len(tlist)/2):
            (wdgt, pos) = (tlist[2*i], tlist[2*i+1])

            # template to accomodate for widgets spanning more than 1 row/column
            template = [0,0,1,1]
            for j in range(len(pos)):
                template[j] = pos[j]

            grid.addWidget(wdgt, template[0], template[1], template[2], template[3])

    # fast tooltips assignment
    def setWidgetsToolTips(self, *tlist):
        for i in range(len(tlist)/2):
            (wdgt, tooltip) = (tlist[2*i], tlist[2*i+1])
            wdgt.setToolTip(tooltip)

    # process table selection, make row selections only
    def processTableSelection(self):
        model = self.tbpositions.selectionModel()
        index = model.currentIndex()
        model.setCurrentIndex(index, QItemSelectionModel.Rows|QItemSelectionModel.SelectCurrent)

        # we cannot deselect row, so enable widgets any time theris a tableselection change
        self.setWidgetsDisabled(False, self.btneditposition, self.btnexportposition)
        return

    # process table redraw on change of item selections
    def processTableRedraw(self, bresetselection=True):
        # see group
        group = str(self.cmbclass.currentText())

        # disable edit and export widgets
        self.setWidgetsDisabled(True, self.btneditposition, self.btnexportposition)
        # reset selection 
        if(bresetselection):
            self.tbpositions.selectionModel().reset()
        
        # temp container with all data for specific group
        temp = self._data[group]

        # clear current table values
        self.tbpositions.clear()

        (rows, cols) = (0, 0)

        # set row count - remember about template
        rows = len(temp.keys())-1

        # set column count and prep strings for the headers
        items = []
        strlist = QStringList()
        items = self._data[group]["Template"]
        cols = int(len(items)/2)                           
        for i in range(cols):
                string = items[2*i]
                if(string=="Protected"):      # skip protected 
                    continue
                strlist.append(items[2*i])
            # set column count
        self.tbpositions.setColumnCount(cols-1) # count -1 for protected
            # set column headers
        self.tbpositions.setHorizontalHeaderLabels(strlist)

        # add final column for remove buttons
        self.tbpositions.setColumnCount(self.tbpositions.columnCount()+1)
        self.tbpositions.setHorizontalHeaderItem(self.tbpositions.columnCount()-1, QTableWidgetItem(""))

        # set row count
        self.tbpositions.setRowCount(rows)

        # prepare data representation   

        sortedkeys = sorted(self._data[group], key=lambda key: self.makeSorted(self._data[group][key]), reverse=True)
        # fill table
        for i, label in enumerate(sortedkeys):   # enumerate through idividual positions
            # make a copy of label for future use
            labcopy = label
            # prepare list of items to fill table row
            items = self._data[group][label]

            # check mode for each row
            bprotected = False

            # skip template member
            if(labcopy=="Template"):
                continue

            for j in range(cols):                               # enumerate through of fields - columns
                wdgt = MTableWidgetItem()

                # format label for specific cell and style
                (templab, tempdat, format) = (items[2*j], items[2*j+1], "%s")
                # reference value to judge about the format
                refvalue = self._data[group]["Template"][2*j+1]

                if(templab=="Protected"):           # skip protected column, but spot the mode
                    bprotected = tempdat
                    continue
                if(templab!="Label"):
                    
                    t = type(refvalue)
                        # preformat float
                    if(t is float):
                        format = "%.04f"
                        # preformat integer
                    elif(t is int):
                        format = "%i"
                    # default format - string
                    label = format % tempdat
                else:
                    label = labcopy

                # adjusting style
                color = MSAVEPOSCOLORODD
                if(items[-1]):
                    color = MSAVEPOSCOLORPROTECT
                elif(i%2):
                    color = MSAVEPOSCOLOREVEN

                # adjusting ability to edit item
                wdgtflags = Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
                if(items[-1] and not self._bexpert or templab=="Date"  or templab=="Label"):
                     wdgtflags = wdgtflags ^ Qt.ItemIsEditable

                # attach data to the widget, so that it would be easier to track its change
                wdgt.storage = labcopy

                # add widget to the table
                wdgt.setBackgroundColor(color)
                wdgt.setText(label)
                wdgt.setFlags(wdgtflags)
                self.tbpositions.setItem(i,j, wdgt)
            
            # attach remove button to each row
            btn = QPushButton("Remove")
            self.tbpositions.setCellWidget(i, self.tbpositions.columnCount()-1, btn)

            # initilize buttons events
            self.initRemoveBtnEvents(btn, group, labcopy)

            # enable or disable mode depending on the protection mode
            if(bprotected and not self._bexpert):
                btn.setDisabled(bprotected)

        # resize table to fit
        self.refreshTable(self.tbpositions)
        return

    # init remove buttons events
    def initRemoveBtnEvents(self, btn, group, key):
        func_callback = lambda grp=group, k=key: self.processPositionDeleteSpecific(grp, k)
        self.connect(btn, SIGNAL("clicked()"), func_callback)
        return

    # sets expert mode
    def setExpertMode(self, value=False):
        self._bexpert = value
        self.processTableRedraw(False)

    # synchronize table and self._data entries
    def processTableItem(self, row, col):
        # check class of saved parameters
        string = str(self.cmbclass.currentText())

        # get changed item
        tbitem = self.tbpositions.currentItem()
        # check for table redraw from scratch
        if(tbitem is None):
            return
        tbtext = str(tbitem.text())
        
        # need to find label for current setup
        label = tbitem.storage

        temp = self._data[string][label][col*2+1]

        # check type for conversion from table to data
        func = str
        if(type(temp) is float):
            func = float
        elif(type(temp) is int):
            func = int

        # convert, forcely correct user if he made a stupid mistake and provided wrong values
        conv = 0
        try:
            conv = func(tbtext)
        except ValueError:
            format = "%s"
            if(type(temp) is float):
                conv = 0.0
                format = "%.04f"
            elif(type(temp) is int):
                conv = 0
                format = "%i"
            elif(type(temp) is str):
                conv = ""
            tbitem.setText(format%conv)
        
        # apply conversion to the data
        self._data[string][label][2*col+1] = conv
        # save settings file
        self.writeSettings()
        return

    # to form sorted list of positions (protected - first, everything else - later)
    def makeSorted(self, tlist):
        (date, protected) = (0, False)
        for i, v in enumerate(tlist):
            if(v == "Date"):
                date = int(tlist[i+1])
            if(v == "Protected"):
                protected = tlist[i+1]

        param = 0
        if(protected):
            param = 100000000
        res = param + date
        return res

    # add position or edit currently selected
    def processPositionAdd(self, bedit=False):
        # check class of saved position parameters
        group = str(self.cmbclass.currentText())

        # test if position is new or has been selected
        bnew = False
        index = self.tbpositions.currentIndex()
        if(not index.isValid()):
            bnew = True

        # initialize label of current item
        label = None

        # if some position is selected - show it
        if(not bnew):
            item = self.tbpositions.currentItem()
            label = self.tbpositions.currentItem().storage

        # discriminate between editing and adding new
        if(not bedit):
            label = None

        # start the modal dialog, add the new data
        d = MPositionDialog(self._data, group, self._bexpert, label, self)
        d.exec_()

        # save selection if was present
        model = self.tbpositions.selectionModel()
        index = model.currentIndex()

        # redraw table, save current selection
        self.processTableRedraw(False)

        # restore selection
        model.setCurrentIndex(index, QItemSelectionModel.Rows|QItemSelectionModel.SelectCurrent)
        
        #save positions into file
        self.writeSettings()
        return
    
    # add external data to specific group - external data
    def addExternalData(self, group, extdata):
        d = MPositionDialog(self._data, group, self._bexpert, "New", self, extdata)
        d.exec_()

        # save selection if was present
        model = self.tbpositions.selectionModel()
        index = model.currentIndex()

        # redraw table, save current selection
        self.processTableRedraw(False)

        # restore selection
        model.setCurrentIndex(index, QItemSelectionModel.Rows|QItemSelectionModel.SelectCurrent)
        
        #save positions into file
        self.writeSettings()
        return

    # delete position
    def processPositionDelete(self):
        # check if any item is selected
        index = self.tbpositions.currentIndex()
        if(not index.isValid()):
            return

        # check class of saved position parameters
        string = str(self.cmbclass.currentText())

        # get label for the selected item
        row = index.row()
        item = self.tbpositions.currentItem()
        label = self.tbpositions.currentItem().storage

        # delete the entry from self._data
        self._data[string].pop(label)
            # update table without rebuilding it
        self.tbpositions.removeRow(row)
        
        # update session
        self.settingsRemoveKey(string, label)
        
        #save positions into file
        self.writeSettings()
        return

    # delete specific position from both - table and data (remove button event)
    def processPositionDeleteSpecific(self, group, label):
        # find the row by checking first member storage
        for i in range(self.tbpositions.rowCount()):
            item = self.tbpositions.item(i, 0)
            if(item is not None and item.storage==label):
                # remove row
                self.tbpositions.removeRow(i)
                # delete the entry from self._data
                self._data[group].pop(label)
                # remove key from session
                self.settingsRemoveKey(group, label)
                #save positions into file
                self.writeSettings()
                break
        return

    # export position - use class as the differentiator
    def processPositionExport(self):
        # check current index and see if any position is selected
        index = self.tbpositions.currentIndex()
        if(not index.isValid()):
            return

        # check class of saved position parameters
        group = str(self.cmbclass.currentText())

        # get label for the selected item
        label = self.tbpositions.currentItem().storage

        self.emit(SIGNAL(SIGNALMSAVEPOSEXPORT), group, self._data[group][label])
        return

    # edit currently selected item
    def processPositionEdit(self):
        # check class of saved position parameters
        group = str(self.cmbclass.currentText())

        # test if position is new or has been selected
        bnew = False
        index = self.tbpositions.currentIndex()
        if(not index.isValid()):
            bnew = True

        label = None

        # if some position is selected - show it
        if(not bnew):
            item = self.tbpositions.currentItem()
            label = self.tbpositions.currentItem().storage

        d = MPositionDialog(self._data, group, self._bexpert, label, self)
        d.exec_()

        # save selection if was present
        model = self.tbpositions.selectionModel()
        index = model.currentIndex()

        # redraw table, save current selection
        self.processTableRedraw(False)

        # restore selection
        model.setCurrentIndex(index, QItemSelectionModel.Rows|QItemSelectionModel.SelectCurrent)
        
        #save positions into file
        self.writeSettings()
        return

    # remove specific key from settings
    def settingsRemoveKey(self, group, key):
        self._settings.beginGroup(group)
        self._settings.remove(key)
        self._settings.endGroup()
        return

    # set bunch of widgets to the disabled or enabled mode
    def setWidgetsDisabled(self, value, *tlist):
        t = type(tlist[0])
        if(t is tuple or t is list):
            tlist = tlist[0]

        for w in tlist:
            w.setDisabled(value)

###
##  End Of MSavePos class
###

###
##  MTableWidgetItem class - to override limited storage of the QTableWidgetItem, to add some additional info there, storage used for data synchronization
###

class MTableWidgetItem(QTableWidgetItem):
    def __init__(self,  type=QTableWidgetItem.Type):
        super(MTableWidgetItem, self).__init__(type)

        # additional storage for QTableWidgetItem
        self._storage = None

    # property storage linked to self._storage
    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, value):
        self._storage = value
        return self._storage

###
##  End Of MTableWidgetItem class 
###

###
##  MPositionDialog - dailog class to create new positions
### 

class MPositionDialog(QDialog):
    def __init__(self, data, strclass, expertmode, strlabel=None, parent=None, extdata=None):
        super(MPositionDialog, self).__init__(parent)
        
        self.initVars(data, strclass, strlabel, expertmode, extdata)
        self.initSelf()
        self.initEvents()
        return


    def initVars(self, data, strclass, strlabel, expertmode, extdata):
        # copy of data
        self._data = data
        # copy of class entry being edited
        self._class = strclass
        # copy of current item label
        self._label = strlabel
        # mode
        self._bexpert = expertmode

        # widgets for future data collection
        self._widgets = []
        # widget to track label names 
        self._wlabel = None
        
        # template
        self._template = None
        
        # external data
        self._extdata = extdata

        # buttons to cancel or save data
        self.btnCancel = None
        self.btnSave = None
        
        return

    #
    def initSelf(self):
        self.setModal(True)

        # sets template, try basic error handling
        # each class should have its own position template attached
        # template must be defined and present
        template = None
        try:
            template = self._data[self._class]["Template"]
        except KeyError:
            pass

        # exit if template is unknown
        if(template is None):
            return

        # set template to the active position if this position is selected
        if(self._label is not None):
            try:
                template = self._data[self._class][self._label]
            except KeyError:
                # means that template is for none existing thing - new, external one
                pass
        
        self._template = template
        # set widget
        wdgt = QWidget()
        grid = QGridLayout(wdgt)

        # fill layout, check if expert mode is on
        bexpertitem = False
        lastrow = 0
        for i in range(len(template)/2):
            caption = template[2*i]
            value = template[2*i+1]

            # add caption
            format = "%s :"
            grid.addWidget(QLabel(format % caption), i, 0)

            # QlineEdit widget 
            w = QLineEdit()

            # will track label values as a function of user rights - save reference to the widget
            if(caption=="Label"):
                self._wlabel = w
            # disable certain widgets, adjust values
            if(caption=="Label" and self._label is not None):
                value = self._label
                # track label widget - to check if we can edit certain position

            elif(caption=="Date"):
                w.setDisabled(True)
                value = str(QDate().currentDate().toString("yyyyMMdd"))
            elif(caption=="Protected" and not self._bexpert):
                bexpertitem = value
                w.setDisabled(True)

            # in case we have external data - update value
            if(self._extdata is not None):
                for j in range(len(self._extdata)/2):
                    (ref, refdata) = (self._extdata[2*j], self._extdata[2*j+1])
                    if(ref.find(caption)>-1):
                        value = refdata
            
            format = "%s"
            t = type(value)
            if(t is float):
                format = "%.04f"
                w.setValidator(QDoubleValidator(w))
            elif(t is int or type(value) is bool):
                format = "%i"
                w.setValidator(QIntValidator(w))

            w.setText(format%value)
            self._widgets.append(w)

            grid.addWidget(w, i, 1)

            lastrow = i

        # adding buttons - Save and cancel
        self.btnCancel = QPushButton("&Cancel")
        self.btnCancel.setDefault(True)
        self.btnSave = QPushButton("&Save")

        grid.setRowMinimumHeight(lastrow+1, 10)
        grid.addWidget(self.btnCancel, lastrow+2, 0)
        grid.addWidget(self.btnSave, lastrow+2, 1)

        # disable editing of widget in a case of low priveleges
        if(bexpertitem and not self._bexpert):
            self.btnSave.setDisabled(True)
            self.btnSave.setToolTip("No saving possible for protected items")

        # adjust layout
        layout = QGridLayout(self)
        layout.addWidget(wdgt, 0, 0)

        # adjust window
        self.setWindowTitle(MANPOSITIONSDIALOG)
        self.adjustSize()
        return

    # init events
    def initEvents(self):
        # cancel button closes dialog
        self.connect(self.btnCancel, SIGNAL("clicked()"), self.close)
        # save button saves if enabled
        self.connect(self.btnSave, SIGNAL("clicked()"), self.processPosSave)
        # check if user is allowed to change or edit a certain position
        self.connect(self._wlabel, SIGNAL("textChanged(const QString&)"), self.processLabelChange)
        
        # check label provided to the dialog for user rights
        self.processLabelChange(self._wlabel.text())
        return

    # process saving, for both expert and 
    def processPosSave(self):
        # enumerate through widgets, modify self._data
        temp = []
        label = ""
        for i,w in enumerate(self._widgets):
            value = str(w.text())
            caption = self._data[self._class]["Template"][2*i]      # take captions from template
            refvalue = self._data[self._class]["Template"][2*i+1]     # take reference value from template to determine format

            # check label
            if(caption=="Label"):       # this is label - individual for each cell
                # check if label has length
                if(len(value)==0):
                    QMessageBox.critical(self, "Error:", "Label cannot be empty")
                    return
                label = value
                value = ""
            elif(caption=="Protected"):     # this one is protected, need to check which flag is there
                value = int(value)
                if(value>0):
                    value = True
                else:
                    value = False
            else:
                # transform data based on reference template values for a given field
                t = type(refvalue)
                if(t is float):
                    value = float(value)
                elif(t is int):
                    value = int(value)
                elif(t is str):
                    value = str(value)
            
            temp.append(caption)
            temp.append(value)

        # final check - how empty is the thing
        if(len(temp)==0):
            return    

        # saving new or modified data
        self._data[self._class][label] = temp
        self.close()
        return
    
    # process label change - check if entry exists and if user is allowed to change it
    def processLabelChange(self, label):
        # walk through different positions
        for k in self._data[self._class].keys():
            # if user sets position label equal to the existing one - check rights
            if(str(k)==str(label)):
                pos = self._data[self._class][k]
                for i in range(len(pos)/2):
                    # check protected property
                    (tlabel, tvalue) = (pos[2*i], pos[2*i+1])
                    # if field exists and is protected but expert mode is off 
                    if(pos[2*i]=="Protected" and tvalue and not self._bexpert):
                         self.setWindowTitle("%s - %s" % (MANPOSITIONSDIALOG, "Protected"))
                         self.btnSave.setDisabled(True)
                         return
                self.setWindowTitle("%s - %s" % (MANPOSITIONSDIALOG, "Exists"))
                break
        # if labels coincide, but there is not issue with user rights
        
        # nothing found - ok, no changes necessary - user is allowed to change position values
        if(not self.btnSave.isEnabled()):
            self.btnSave.setDisabled(False)
            self.setWindowTitle(MANPOSITIONSDIALOG)
        return
        

    # close event
    def closeEvent(self, event):
        event.accept()

###
##  End Of MPositionDialog 
### 

if __name__ == '__main__':
    app = QApplication([])
    # set ini file configuration as needed for settings
    app.setOrganizationName(MSAVEPOSAPPORG);
    app.setOrganizationDomain(MSAVEPOSAPPDOMAIN);
    app.setApplicationName(MSAVEPOSAPP);

    form = MSavePos(app, MSAVEPOSAPPCONFIGFILE)
    app.exec_()



