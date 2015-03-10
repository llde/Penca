import sys
sys.path.append("./libpnc/uipnc")
sys.path.append("./icn")  # Fa trovare i files anche nelle sottocartelle.
import os

from PyQt4 import QtCore, QtGui, uic  # Moduli PyQT purtroppo fermi a QT4, uic serve per non compilare le forms
# TODO PyQT5 e QT5!!!
# TODO Port a Python 3 :)

# Moduli delle risorse e libpnc, per generare tutto lo scibile
# Lo da come import inutilizzato ma senza 'sta merda compilata non vediamo le icone demmerda.

import resor
import libpnc
from libpnc import Document
from libpnc import windows

if __name__ == "__main__":

    app = QtGui.QApplication([])
    # Percorsi e inizializzazioni di libpnc

    # app.setStyle('GTK+')
    # Serve stile di sistema, se stiamo su QT serve lo stile di merda di KDE... Merda!

    path = os.path.expanduser('~/PencaProject')
    if not os.path.exists(path):
        os.mkdir(path)
    Base = libpnc.PencaBaseModule(path)
    Doc = Document.PencaDocument()
    Doc.fillprojectpath(Base)

    # Show windows
    pncmainwindow = windows.mainpenca(app, Base, Doc)
    pncstart = windows.openwindow(Base, Doc, pncmainwindow)

    retlist = Base.returnpncfilelist()
    for element in retlist:
        pncstart.openList.addItem(element)
    pncmainwindow.show()
    pncstart.exec_()

    sys.exit(app.exec_())

