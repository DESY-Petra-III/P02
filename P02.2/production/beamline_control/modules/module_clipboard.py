#!/bin/env python

# License GPL v.3 
# Coding Konstantin Glazyrin lorcat at gmail.com
# Simple module to allow beamline scripts to communicate within one system session without getting stupid Tango servers in between
# 
# The communication is done through the system clipboard using special mime type MCLIPBOARDTRACKERFORMAT
#
# The messages format is (for simplicity):
# <read><from>FROM</from><to>TO</to><value>VALUE</value></read>
# FROM - cannot be empty
# TO - can be regexp expression, all (all MClipboardTracker instances will see it), explicit file name - for specific script (will read and remove this message from the clipboard)
#
# There should be no '<>' symbols inside the FROM, TO, VALUE fields'

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Clipboard mime type
MCLIPBOARDTRACKERFORMAT = "application/x-qt-windows-mime;value=\"Petra-3-Clipboard\""

# Clipboard signal intended for testing the MClipboardTest
MCLIPBOARDTRACKERSIGNALDEBUG = "debug(const QString&)"
MCLIPBOARDTRACKERSIGNALUPDATE = "clipboardUpdated"

# template for read messages
MCLIPBOARDTRACKERREADTEMPLATE = "<read><from>%s</from><to>%s</to><value>%s</value></read>"

###
##    MClipboardTest - class to test system clipboard module
###
class MClipboardTest(QMainWindow):
    def __init__(self, app, parent=None):
        super(MClipboardTest, self).__init__(parent)

        self.initVars(app)
        self.initSelf()
        self.initEvents()

    def initVars(self, app):
        # application
        self._app = app

        # clipboard
        self._clip = app.clipboard()

        # clipboard tracker
        self._tracker = MClipboardTracker()
        return

    def initSelf(self):
        wdgt = QWidget()
        grid = QGridLayout(wdgt)

        self.teclip = QTextEdit()
        self.teclip.setText("<read><from>FROM</from><to>all</to><value>VALUE</value></read>")
        self.tefromclip = QTextEdit()
        self.btn = QPushButton("Move To Clipboard")
        grid.addWidget(QLabel("Clipboard:"), 0, 0)
        grid.addWidget(self.teclip, 1, 0)
        grid.addWidget(QLabel("From Clipboard:"), 2, 0)
        grid.addWidget(self.tefromclip, 3, 0)
        grid.addWidget(self.btn, 4, 0)


        self.setCentralWidget(wdgt)
        self.show()
        return

    def initEvents(self):
        self.connect(self._tracker, SIGNAL(MCLIPBOARDTRACKERSIGNALDEBUG), self.processTrackerMessage)
        self.connect(self.btn, SIGNAL("clicked()"), self.processNewClipboardValue)
        return

    def processTrackerMessage(self, string):
        self.tefromclip.setText(string)
        return

    def processNewClipboardValue(self):
        # get text from QTextEdit
        text = self.teclip.toPlainText()
        
        dataReadToClipboardFromString(text)
        return

    def close(self, event):
        event.accept()

###
##    MClipboardTest END
###

###
##    MClipboardTracker - main class serving as a server for special clipboard messages
###
class MClipboardTracker(QObject):
    def __init__(self, parent=None):
        super(MClipboardTracker, self).__init__(parent)

        self.initVars()
        self.initEvents()    

    # initialize variables
    def initVars(self):
        # clipboard
        self._clip = QApplication.clipboard()

        # data to store values, we store as key-value
        self._data = {}
        return

    # initialize object events
    def initEvents(self):
        # track changes of the clipboard through signals a change of clipboard
        self.connect(self._clip, SIGNAL("dataChanged()"), self.processClipboardChange)
        return

    # do timer update
    def processClipboardChange(self):
        # check type of clipboard data - we need special formated text
        mimedata = self._clip.mimeData()

        if(MCLIPBOARDTRACKERFORMAT is not None and mimedata.hasFormat(MCLIPBOARDTRACKERFORMAT)):
            msg = str(mimedata.data(MCLIPBOARDTRACKERFORMAT))
            if(len(msg)>0):
                self.checkMessage(msg)
        return

    # process text, extract values, check if values are new and emit signal if value is new
    def checkMessage(self, msg):
        msg = QString(msg)
        # message may be multiline - check all entries, but one command - one line
        patt = QString("<read><from>([^<>]+)</from><to>([^<>]+)</to><value>([^<>]+)</value></read>")
        re = QRegExp(patt, Qt.CaseInsensitive)

        # script name - may be used for addressing
        scriptname = os.path.basename(__file__)

        pos = 0
        count = 0
        while(re.indexIn(msg, pos)>-1):
            (match, strfrom, strto, strwhat, length) = (re.cap(), str(re.cap(1)), str(re.cap(2)), str(re.cap(3)), re.matchedLength())

            pos = pos + length

            # flags controling how we proceed with the message
            (bour, bremove) = (False, False)
            # check if message is intended for this script, if so, remove message from clipboard queue
            reto = QRegExp(strto, Qt.CaseInsensitive)

            # message is intended for us
            if(QString(strto).toLower() == QString("all") or reto.indexIn(scriptname)>-1):
                bour = True

            # intended exactly for us, remove it
            if(scriptname==strto):
                bremove = True
            
            # save message to local _data
            if(bour and len(strfrom)>0):
                # create an empty entry
                if(not self._data.has_key(strfrom)):
                    self._data[strfrom] = ""

                # makle changes only if a change is detected
                if(self._data[strfrom]!=strwhat):
                    self._data[strfrom] = strwhat
                    count = count + 1

            # check if we need to remove data
            if(bremove):
                dataRemoveStringFromClipboard(match)

        # in case we have found something to report - something related to us
        if(count>0):
            # message for debugging
            msg = "Message: \r\n%s\r\n\r\nData:\r\n%s"%(msg, str(self._data))
            self.emit(SIGNAL(MCLIPBOARDTRACKERSIGNALDEBUG), msg)

            # report data - with new values
            self.emit(SIGNAL(MCLIPBOARDTRACKERSIGNALUPDATE), self._data.copy())
        return

###
##    MClipboardTracker END
###


###
##    Utility functions to add specific data for clipboard processing
###

# add data in form of from:to:value
def dataReadToClipboard(self, vfrom, vto, value):
    string = MCLIPBOARDTRACKERREADTEMPLATE%(str(vfrom), str(vto), str(value))
    self.dataReadToClipboardFromString(app, string)

# add data in form of a preapred string
def dataReadToClipboardFromString(string):
    #
    string = QString(string)
    #
    clipboard = QApplication.clipboard()
    # existing mimedata
    mimedata = clipboard.mimeData()

    # make a copy of existsing data, add our own values
    newdata = QMimeData()
    oldstring = QString("")
    for v in mimedata.formats():
        data = mimedata.data(v)
        newdata.setData(v, data)
        if(v==MCLIPBOARDTRACKERFORMAT):
            oldstring = QString(data)

    # current string has values - from:to:value
    # search and replace values for new ones if necessary
    # clipboard is made - one key (from) - one value 
    breplace = False
    re = QRegExp("<read><from>([^<>]+)</from><to>([^<>]+)</to><value>([^<>]+)</value></read>", Qt.CaseInsensitive)
    if(re.indexIn(string, 0)>-1):
        strfrom = re.cap(1)

        # check if this string exists already in our set, if we need to replace values
        patt = "<read><from>%s</from><to>([^<>]+)</to><value>([^<>]+)</value></read>" % (strfrom)
        re = QRegExp(patt, Qt.CaseInsensitive)
        # replace string if needed
        if(re.indexIn(oldstring)>-1):
            string = oldstring.replace(re, string)
            breplace = True

    # add new string if needed
    if(not breplace):
        string = QString("%s\r\n%s" % (oldstring, string))

    # set up mime data to pass it to the clipboard
    newdata.setData(MCLIPBOARDTRACKERFORMAT, QByteArray(string.toAscii()))

    # save mime data, save text
    clipboard.setMimeData(newdata)

# remove specific string from Clipboard
def dataRemoveStringFromClipboard(string):
    string = QString(string)

    clipboard = QApplication.clipboard()
    # existing mimedata
    mimedata = clipboard.mimeData()

    # make a copy of existsing data, add our own values
    newdata = QMimeData()
    oldstring = QString("")
    for v in mimedata.formats():
        data = mimedata.data(v)
        newdata.setData(v, data)
        if(v==MCLIPBOARDTRACKERFORMAT):
            oldstring = QString(data)

    # replace special ocurrencies
    string = oldstring.remove(string)

    # set up mime data to pass it to the clipboard
    newdata.setData(MCLIPBOARDTRACKERFORMAT, QByteArray(string.toAscii()))

    # save mime data, save text
    clipboard.setMimeData(newdata)

# debugging environment
if __name__ == '__main__':
    app = QApplication([])
    form = MClipboardTest(app)

    app.exec_()