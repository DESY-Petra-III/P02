#!/usr/bin/env python

# GPL v3 License applies
# coding: Konstantin Glazyrin (lorcat@gmail.com)

import sys 
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyQt4.QtNetwork import *

SIZEOF_UINT16 = 2

(NONE, CR, LF, CRLF) = ("None", "\\r", "\\n", "\\r\\n")

class TcpClientForm(QDialog):
    def __init__(self, parent=None):
        super(TcpClientForm, self).__init__(parent)

        self.initUI()
        self.initVars()
        self.initEvents()
        

    def initUI(self):
        self.resize(500, 400)
        self.setWindowTitle("Tcp Client for Debugging (Schott, etc.)")

        grid = QGridLayout(self)

        self.lecmd = QLineEdit("&m?")
        self.btnsend = QPushButton("Send")
        self.te = QTextEdit("")
        self.leip = QLineEdit("192.168.57.243")
        self.leport = QLineEdit("50811")
        self.leport.setValidator(QIntValidator(self.leport))
        self.leport.setMaximumWidth(50)

        # combobox for test of different line terminators
        self.cmblt = QComboBox()
        strl = QStringList()
        for v in (NONE, CR, LF, CRLF):
            strl.append(v)
        self.cmblt.addItems(strl)

        grid.addWidget(QLabel("IP:"), 0, 0)
        grid.addWidget(QLabel("Port:"), 0, 2)
        grid.addWidget(self.leip, 0, 1)
        grid.addWidget(self.leport, 0, 3)
        grid.addWidget(QLabel("Line Terminator:"), 0, 4)
        grid.addWidget(self.cmblt, 0, 5)
        grid.addWidget(QLabel("Command:"), 1, 0)
        grid.addWidget(self.lecmd, 1, 1, 1, 4)
        grid.addWidget(self.btnsend, 1, 5)
        grid.addWidget(self.te, 2, 0, 1, 6)

        grid.setColumnStretch(1, 50)
        return

    def initVars(self):
        self.socket = QTcpSocket()
        self.text = QString("")
        return

    def initEvents(self):
        self.connect(self.socket, SIGNAL("connected()"), self.connected)
        self.connect(self.socket, SIGNAL("readyRead()"), self.readResponse)
        self.connect(self.socket, SIGNAL("disconnected()"), self.disconnected)
        self.connect(self.socket, SIGNAL("error(QAbstractSocket::SocketError)"), self.reportError)

        self.connect(self.btnsend, SIGNAL("clicked()"), self.btnsend_clicked)

        return

    def reportError(self, msg):
        if(QAbstractSocket.RemoteHostClosedError==msg):
            msg = "<font color='red'>Error: host has closed connection</font>"
            self.te.append(msg)
            print(msg)

    def connected(self):
        self.te.append("<connected>")
        print("connected")

        # get command and line terminators
        text = str(self.lecmd.text())

        format = "%s"
        if(self.cmblt.currentText()==CR):
            format = "%s\r"
            print("CR")
        elif(self.cmblt.currentText()==LF):
            format = "%s\n"
            print("LF")
        if(self.cmblt.currentText()==CRLF):
            format = "%s\r\n"
            print("CRLF")

        text = format % text

        self.socket.write(text)

        self.te.append("&nbsp; &nbsp; command &gt;<font color='black'><b>%s</b></font>" % text)
        return

    def disconnected(self):
        print("disconnected")
        self.te.append("</disconnected>\n")
        self.socket.close()
        return

    def readResponse(self):
        print("reading")
        output = ""
        while(self.socket.bytesAvailable()):
            t = self.socket.readData(10)
            output += t

        self.te.append("&nbsp; &nbsp; response &lt; <font color='green'><b>%s</b></font>" % output)
        self.socket.close()
        return

    def btnsend_clicked(self):
        if(self.socket.isOpen()):
            self.socket.close()

        ip = self.leip.text()
        port = 50811
        try:
            port = int(self.leport.text())
        except ValueError:
            self.leport.setText(str(port))

        self.socket.connectToHost(ip, port)
        return

    def closeEvent(self, event):
        if(self.socket.isOpen()):
            self.socket.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = TcpClientForm()
    form.show()
    app.exec_()