import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *


def load_certs(cert_path):
    # cert_path is a string "/path/to/cert/files"
    ssl_config = QSslConfiguration.defaultConfiguration()
    print(ssl_config.localCertificate)
    
    ssl_config.setProtocol(QSsl.AnyProtocol)

    certs = ssl_config.caCertificates()

    for cert_filename in os.listdir(cert_path):
        if os.path.splitext(cert_filename)[1] in ('.cer', '.crt', '.pem'):
            cert_filepath = os.path.join(cert_path, cert_filename)
            print("Loading cert: %s"%cert_filepath)
            cert_file = QFile(cert_filepath)
            cert_file.open(QIODevice.ReadOnly)
            cert = QSslCertificate(cert_file)
            certs.append(cert)

    ssl_config.setCaCertificates(certs)
    QSslConfiguration.setDefaultConfiguration(ssl_config)

def errors(*tlist):
    t = type(tlist[0])
    if(t is list or t is tuple):
	tlist = tlist[0]
    for i,v in enumerate(tlist):
	socket.ignoreSslErrors()
	print(i,v.error(), v.errorString())


app = QApplication([])

#load_certs("./")

socket=QSslSocket()
socket.setProtocol(QSsl.AnyProtocol)

# socket.ignoreSslErrors(QSslError(QSslError.UnableToGetLocalIssuerCertificate))
# socket.ignoreSslErrors([QSslError(QSslError.UnableToGetLocalIssuerCertificate), QSslError(QSslError.CertificateUntrusted)])
# socket.addCaCertificates("./")
# socket.addCaCertificates("/etc/pki/CA")
# socket.setLocalCertificate("/etc/pki/tls/cert.pem")

socket.connectToHostEncrypted("ics.desy.de", 443 );

socket.connect(socket, SIGNAL("sslErrors (const QList<QSslError>&)"), errors)

if(not socket.waitForEncrypted()):
    print(socket.errorString())


socket.write( "GET / HTTP/1.1\r\n"+
              "Host: ics.desy.de\r\n"+
              "Connection: Close\r\n\r\n" );

while (socket.waitForReadyRead()):
     print(socket.readAll().data())