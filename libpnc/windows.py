# -*- coding: utf-8 -*-

""" Penca software. The novel editor in python, rilasciato sotto licenza gpl. Potete dunque
farne il cavolo che vi pare, persino provarlo ;)
Ma se siete qui di sicuro è per il codice, sappiate che userò le docstrings e cercherò di
mantenere il codice più commentato possibile.

@ Dipendenze: PyQt4 e Qt4, libsoup è già nel package.
@ Crediti: Le icone usate sono un pack free, appena mi ricordo aggiungo il nome.
@ Autore: Manolo Lelli """

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------------------------------------------------

import sys
sys.path.append("./libpnc/uipnc")
sys.path.append("./icn")  # Fa trovare i files anche nelle sottocartelle.
import os
from PyQt4 import QtCore, QtGui, uic  # Moduli PyQT purtroppo fermi a QT4, uic serve per non compilare le forms
import resor  # Risorse compilate

# ----------------------------------------------------------------------------------------------------------------------

""" Quello che succede nel file che avete aperto è che, paradossale, è il fulcro del programma. Potremo persino fare una
marea di cose diverse, ma grossomodo ogni classe si importa le Gui di cui necessita. È un po' come se ampliassimo le
classi presenti dopo aver importato e lanciato un'istanza delle finestre stesse."""
# TODO python 3 e Qt5

# ----------------------------------------------------------------------------------------------------------------------
# FINESTRE DI BASE: Main, dialogo principale
# ----------------------------------------------------------------------------------------------------------------------


class mainpenca(QtGui.QMainWindow):

    """ Finestra principale di Penca. Viene richiamata dal file pnc.py.
    @ Parametri: app è l'applicazione Qt, base è il modulo base istanziato, idem per doc, parent è la finestra padre.
    Di default è None."""

    def __init__(self, app, base, doc, parent=None):

        QtGui.QMainWindow.__init__(self, parent)  # Init sempre necessario per definire una finestra in Qt

        self.App = app
        self.Base = base
        self.Doc = doc

        uic.loadUi('./libpnc/uipnc/pncmain.ui', self)  # Carico la GUI
        self.fullscreen = False
        self.environment = environment(self.Base, self.Doc, self)
        self.stat = staticwindow(self.Base, self.Doc, self)
        self.help = help(self)

        left_spacer = QtGui.QWidget()  # Widget della barra, per spaziare
        left_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        right_spacer = QtGui.QWidget()
        right_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.toolBar.insertWidget(self.actionChapters, left_spacer)  # Inserisce prima di tutto
        self.toolBar.addWidget(right_spacer)  # Inserisce dopo

        self.actionChapters.triggered.connect(lambda: self.main_shoenv())  # Callbacks della finestra. Lambda è lentissimo.
        self.actionSave.triggered.connect(lambda: self.main_save())
        self.actionFullscreen.triggered.connect(lambda: self.main_gofull())
        self.pagina.textChanged.connect(lambda: self.main_updatettext())

        QtGui.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Save), self, lambda: self.main_save())  # Shotcut salva
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F4), self, lambda: self.main_showstatics())
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F2), self, lambda: self.main_shoenv())
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F1), self, lambda: self.help.exec_())
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F11), self, lambda: self.main_gofull())

    def main_save(self):

        """ Routine che si occupa di salvare. Salviamo, creiamo il file pnc ed infine mostriamo un dialogo che ci avverte
        dell'avvenuto salvataggio."""

        self.Doc.save()  # Salvo
        self.Doc.makearchivepnc()  # Faccio archivio pnc

        vdialog = QtGui.QMessageBox(self)  # Dialogo
        vdialog.setWindowTitle('Penca Info')
        vdialog.setText('Project saved.')
        vdialog.setIcon(QtGui.QMessageBox.Information)
        vdialog.addButton(QtGui.QMessageBox.Close)
        vdialog.exec_()

    def main_gofull(self):
        if self.fullscreen is False:
            self.showFullScreen()
            self.toolBar.hide()
            # BHO self.toolBar.setStyleSheet('QToolBar{background-color: rgba(255, 255, 255, 0)};')
            self.fullscreen = True
        elif self.fullscreen is True:
            self.showNormal()
            self.toolBar.show()
            # BHO self.toolBar.setStyleSheet('')
            self.fullscreen = False

    def main_shoenv(self):  # Mostra ENV
        self.environment.updatechap()
        self.environment.updatechar()

        self.environment.docList.setItemSelected(self.environment.docList.item(self.environment.index), True)
        self.environment.docList.setCurrentRow(self.environment.docList.row(self.environment.docList.selectedItems()[0]))
        self.environment.index = self.environment.docList.currentRow()
        self.environment.updatebyindexchap(self.environment.index)

        self.environment.pgList.setItemSelected(self.environment.pgList.item(self.environment.pgList.index), True)
        self.environment.pgList.setCurrentRow(self.environment.pgList.row(self.environment.pgList.selectedItems()[0]))
        self.environment.pgList.index = self.environment.pgList.currentRow()
        self.environment.pgList.onceclicked(self.environment.pgList.index)
        self.environment.exec_()

    def main_showchaplist(self):  # Mostra capitoli
        self.chapwin.update() # BHO????
        self.chapwin.exec_()
        self.edit.updatebyindex(self.edit.index)

    def main_showstatics(self):  # Mostra statistiche e ne esegue, per l'aggiornamento.
        self.stat.static_updatewords()
        self.stat.static_updatechars()
        self.stat.static_updatemic()
        self.stat.exec_()

    def main_updatebyindex(self, index):

        """ Questa funzione, preso un indice, ritorna i testi ed il nome dell'elemento all'indice i nella lista dei
        capitoli dell'oggetto Doc.
        @ Parametri: index è un indice che va da 0 a n. È un intero."""

        for element in self.Doc.chapters:  # Per elemento nei capitoli...
            if element.id == index:
                self.pagina.setText(element.documentText)  # Documento
                self.label.setText(element.title)  # Titolo
                # self.sintextedit.setText(element.synopse)  # Sinossi

    def main_updatettext(self):

        """ Funzione assai semplice che setta, nell'oggetto Status del Documento istanziato una variabile True, questa fa si di
        segnalare una modifica che, in questo caso, avviene alla modifica stessa del testo.
        Il testo viene automaticamente aggiornato nell'elemento capitolo."""

        for element in self.Doc.chapters:
            if element.id == self.Doc.index:
                element.documentText = unicode(self.pagina.toPlainText())  # Testo sovrascritto nel capitolo.
        self.Doc.setStatus()

    def closeEvent(self, event):

        """ Sovrascrittura del metodo closeEvent del main, per far sì che chieda di salvare se Status, nell'oggetto Doc,
        è True.
        @ Parametri: event. """

        if self.Doc.status is True:  # Mostra il dialogo
            result = QtGui.QMessageBox.question(self, "Penca info", "Save before exit?", QtGui.QMessageBox.Yes |
                                                QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            event.ignore()

            if result == QtGui.QMessageBox.Yes:  # OK
                self.Doc.save()
                self.Doc.makearchivepnc()
                self.App.quit()
            elif result == QtGui.QMessageBox.No:  # NO
                self.App.quit()


class environment(QtGui.QDialog):

    def __init__(self, base, doc, parent=None):
        QtGui.QDialog.__init__(self, parent)
        uic.loadUi('./libpnc/uipnc/env.ui', self)
        self.Base = base
        self.Doc = doc
        self.parent = parent
        self.setter = setter(self.Base, self.Doc, self)

        # Inserimento della doclist personalizzata
        # self.verticalLayout.removeWidget(self.docList)
        self.docList.close()
        self.docList = docList(self.Base, self.Doc, self, parent)
        self.verticalLayout.addWidget(self.docList)
        self.verticalLayout.update()
        # PgList
        self.pgList.close()
        self.pgList = pgList(self.Base, self.Doc, self, parent)
        #self.pgList.onceclicked()
        self.verticalLayout_2.addWidget(self.pgList)
        self.verticalLayout_2.update()
        # Indicizzazione
        self.index = 0
        # Callbacks
        self.docList.itemClicked.connect(lambda: self.clickedelement())
        self.addButton.clicked.connect(lambda: self.docList.newchap())
        self.removeButton.clicked.connect(lambda: self.docList.removechoice(self.index))
        self.editButton.clicked.connect(lambda: self.docList.editchap())
        self.addPngButton.clicked.connect(lambda: self.pgList.newchar())
        self.removePngButton.clicked.connect(lambda: self.pgList.removechoice(self.pgList.index))
        self.editPngButton.clicked.connect(lambda: self.pgList.editchar())
        #self.setter.saveButton.clicked.connect(self.savedatachapter)

    def updatechap(self):
        self.docList.clear()
        docs = self.Doc.retchaplist()
        if docs:
            print 'doc'
            for element in docs:
                self.docList.addItem(element.title)
                print element.id, 'DOC'
        else:
            'no doc'

    def updatechar(self):
        self.pgList.clear()
        pgs = self.Doc.retcharlist(True)
        if pgs:
            print 'pg'
            for element in pgs:
                self.pgList.addItem(element.name)
                print element.name, 'pg'
        else:
            'no pg'

    def updatebyindexchap(self, index):

        """ Questa funzione, preso un indice, ritorna i testi ed il nome dell'elemento all'indice i nella lista dei
        capitoli dell'oggetto Doc.
        @ Parametri: index è un indice che va da 0 a n. È un intero."""

        for element in self.Doc.chapters:  # Per elemento nei capitoli...
            if element.id == index:
                self.sintextedit.setText(element.synopse)  # Sinossi

    def clickedelement(self):
        self.index = int(self.docList.currentRow())
        self.updatebyindexchap(self.index)
        print self.index, 'selected'

    def savedatachapter(self):
        for element in self.Doc.chapters:
            if element.id == self.index:
                element.title = unicode(self.setter.lineTitle.text())
                element.synopse = unicode(self.setter.textSino.toPlainText())
                if self.index == self.Doc.index:
                    self.mainwindow.main.label.setText(unicode(self.setter.lineTitle.text()))
        self.setterwindow.close()
        self.updatechap()
        self.Doc.setStatus()


class help(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        uic.loadUi('./libpnc/uipnc/help.ui', self)

class staticwindow(QtGui.QDialog):

    """ Classe della finestra delle statistiche, quella che gestisce i conteggi.
    @ Parametri: app è l'applicazione Qt, base è il modulo base istanziato, idem per doc, parent è la finestra padre.
    Di default è None."""

    def __init__(self, base, doc, parent=None):

        QtGui.QDialog.__init__(self, parent)
        self.Base = base
        self.Doc = doc
        self.father = parent

        uic.loadUi('./libpnc/uipnc/statics.ui', self)  # Carico la GUI

    def static_updatewords(self):

        """ Funzione che si occupa di stampare nel label della finestra il numero delle parole presenti nell'area
        di testo. Usa il metodo split(). """

        words = len(unicode(self.father.pagina.toPlainText()).split())
        self.wordslabel.setText(unicode(words))

    def static_updatechars(self):

        """ Funzione che si occupa di stampare nel label della finestra il numero dei caratteri presenti nell'area
        di testo. """

        words = len(unicode(self.father.pagina.toPlainText()))  # Lunghezza del testo
        self.charslabel.setText(unicode(words))

    def static_updatemic(self):

        """ Aggiorna il personaggio più influente, most influent character, calcolando anche un exequo
        nel caso ve ne fossero più di uno."""

        words = unicode(self.father.pagina.toPlainText()).lower().split()  # parole
        pg = None
        thiscnt = 0
        pgs = []
        for element in self.Doc.characters:  # Carico i personaggi papabili
            pgs.append(element.name.lower())
        for element in pgs:  # per ogni personaggio parto da zero a contare
            cnt = 0
            for elem in words:
                if elem == element:  # Se trovo il pg aumento il counter
                    cnt += 1
            if cnt > thiscnt:  # Se il counter è maggiore, aumento il massimo
                thiscnt = cnt
                pg = element
            elif cnt != 0 and cnt == thiscnt:  # Se invece è diverso da 0 AND uguale a thiscount
                pg = pg + ', ' + element
        if pg is None:  # Caso None
            self.charlabel.setText('No char.')
        elif pg is not None:  # caso non None
            self.charlabel.setText(pg)


class openwindow(QtGui.QDialog):

    def __init__(self, base, doc, parent=None):
        self.Base = base
        self.Doc = doc
        self.opened = False
        QtGui.QDialog.__init__(self, parent)
        uic.loadUi('./libpnc/uipnc/pncstart.ui', self)

        self.father = parent

        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, lambda: self.escapemsg())

        # Callbacks
        self.versionButton.clicked.connect(lambda: self.versioninfo())
        self.openList.currentIndexChanged.connect(lambda: self.giveopendata(self.Doc))
        self.openButton.clicked.connect(lambda: self.openfile(self.Doc))
        self.newButton.clicked.connect(lambda: self.newfile())
        self.removeButton.clicked.connect(lambda: self.removechoice())
        self.quitButton.clicked.connect(lambda: sys.exit(self.father.App))

    def versioninfo(self):
        vdialog = QtGui.QMessageBox(self)
        vdialog.setWindowTitle('Penca Info')
        vdialog.setText('Penca is in alpha.<br>Version 0.30 <br>Codename: "Pierrot"')
        vdialog.setIcon(QtGui.QMessageBox.Information)
        vdialog.addButton(QtGui.QMessageBox.Close)
        vdialog.exec_()

    def closeEvent(self, event):

        if self.opened is False:
            event.ignore()
            vdialog = QtGui.QMessageBox(self)
            vdialog.setWindowTitle('Penca Info')
            vdialog.setText('Please, start creating a project <br>'
                            'or opening one, if not, <br>'
                            'Penca will crash.')
            vdialog.setIcon(QtGui.QMessageBox.Warning)
            vdialog.addButton(QtGui.QMessageBox.Close)
            vdialog.exec_()
        else:
            event.accept()
            self.close()


    def giveopendata(self, pncDoc):
        if not unicode(self.openList.currentText()):
            return
        data = pncDoc.openpncfile(unicode(self.openList.currentText()), True)
        print data
        title, author, about = data
        self.titleLabel.setText(title)
        if author == 'none':
            self.authorLabel.setText('No Author available.')
        else:
            self.authorLabel.setText(author)
        if about == 'none':
            self.aboutTextEdit.setText('No description available.')
        else:
            self.aboutTextEdit.setText(about)

        self.removeButton.setEnabled(True)
        self.openButton.setEnabled(True)

    def openfile(self, pncDoc, title=None):
        if not unicode(self.openList.currentText()):
            return
        if title is None:
            pncDoc.openpncfile(unicode(self.openList.currentText()))
        elif title is not None:
            pncDoc.openpncfile(unicode(title))
        self.opened = True
        vdialog = QtGui.QMessageBox(self)
        vdialog.setWindowTitle('Penca Info')
        vdialog.setText('Project opened.')
        vdialog.setIcon(QtGui.QMessageBox.Information)
        vdialog.addButton(QtGui.QMessageBox.Close)
        vdialog.exec_()
        self.close()
        listdocs = self.Doc.retchaplist()
        if listdocs:
            self.father.label.setText(listdocs[0].title)
            self.father.pagina.setText(listdocs[0].documentText)
            self.father.environment.updatechap()
            self.father.main_updatettext()

        self.Doc.ordercharlist(True)  # Personaggi
        self.Doc.setStatus(True)

    def newfile(self):
        newpncwindow(self.Base, self.Doc, self).exec_()

    def removechoice(self):

        """ Simple dialog show function, it is for project deleting. """

        ask = QtGui.QMessageBox(self)
        ask.setWindowTitle('Delete')
        ask.setText("Delete the selected project? It's irreversible.")
        ask.setIcon(QtGui.QMessageBox.Warning)
        okbutton = ask.addButton("Ok", QtGui.QMessageBox.ActionRole)
        ask.addButton(QtGui.QMessageBox.Cancel)
        okbutton.clicked.connect(lambda: self.deleteproject())
        ask.exec_()

    def deleteproject(self):

        self.Base.deleteproject(unicode(self.openList.currentText()))
        self.openList.clear()
        self.removeButton.setEnabled(False)
        self.openButton.setEnabled(False)
        retlist = self.Base.returnpncfilelist()
        for element in retlist:
            self.openList.addItem(element)
        self.titleLabel.setText(unicode("Not selected."))
        self.authorLabel.setText(unicode("Not selected."))

    def escapemsg(self):

        if self.opened is False:
            vdialog = QtGui.QMessageBox(self)
            vdialog.setWindowTitle('Penca Info')
            vdialog.setText('Please, start creating a project <br>'
                            'or opening one, if not, <br>'
                            'Penca will crash.')
            vdialog.setIcon(QtGui.QMessageBox.Warning)
            vdialog.addButton(QtGui.QMessageBox.Close)
            vdialog.exec_()
        else:
            self.close()

# Windows class AVANZATE =============================================================

class newpncwindow(QtGui.QDialog):

    def __init__(self, base, doc,parent=None):
        super(newpncwindow, self).__init__(parent)

        self.Base = base
        self.Doc = doc
        uic.loadUi('./libpnc/uipnc/Newpnc.ui', self)

        self.father = parent
        self.createButton.clicked.connect(lambda: self.createnew())
        self.title = None

    def createnew(self):
        title = self.lineTitle.text()
        self.title = str(title)
        author = self.lineAuthor.text()
        about = self.textAbout.toPlainText()
        if not title:
            print 'No title, cannot create.'
            return False
        if not author:
            author = 'none'
        if not about:
            about = 'none'
        self.Base.createnewfile(title, author, about)
        retlist = self.Base.returnpncfilelist()
        for element in retlist:
            self.father.openList.addItem(element)
        self.father.openfile(self.Doc, self.title)
        self.close()

class setter(QtGui.QDialog):

    def __init__(self, base, doc, parent=None):
        super(setter, self).__init__(parent)

        self.parent = parent
        self.Base = base
        self.Doc = doc
        uic.loadUi('./libpnc/uipnc/settercap.ui', self)
        self.saveButton.clicked.connect(lambda: self.savedatachapter())

    def savedatachapter(self):
        for element in self.Doc.chapters:
            if element.id == self.parent.index:
                element.title = unicode(self.lineTitle.text())
                element.synopse = unicode(self.textSino.toPlainText())
                if self.parent.index == self.Doc.index:
                    self.parent.parent.label.setText(unicode(self.lineTitle.text()))
                    self.parent.parent.sintextedit.setText(unicode(self.textSino.toPlainText()))
        self.close()
        self.Doc.setStatus()
        self.parent.updatebyindexchap(self.parent.index)
        self.parent.updatechap()


class choicepgedit(QtGui.QDialog):  # FINESTRA PRINCIPALE MAINWINDOW

    def __init__(self, base, doc, parent=None):
        super(choicepgedit, self).__init__(parent)
        self.father = parent
        self.Base = base
        self.Doc = doc
        uic.loadUi('./libpnc/uipnc/choosepng.ui', self)  # Carico la GUI
        self.edit = None
        self.editclassicButton.clicked.connect(lambda: self.showclassic())
        self.editcreativeButton.clicked.connect(lambda: self.showguided())


    def showclassic(self):
        self.edit = editpng(self.Base, self.Doc, self)
        self.edit.editButton.clicked.connect(lambda: self.new())

        self.edit.comboGender.setCurrentIndex(0)  #Set zero
        self.edit.index = None
        self.edit.remphotocheck.setVisible(False)
        self.edit.clearedit()
        self.edit.exec_()

    def new(self):
        print "pressed"

        if not self.edit.linename.text():
            vdialog = QtGui.QMessageBox(self)
            vdialog.setWindowTitle('Penca Info')
            vdialog.setText('Please insert a name, is required.')
            vdialog.setIcon(QtGui.QMessageBox.Information)
            vdialog.addButton(QtGui.QMessageBox.Close)
            vdialog.exec_()
        else:

            index = self.edit.index
            name = unicode(self.edit.linename.text())  # Carico nome, età, gender e bio
            age = int(self.edit.spinage.value())
            gender = self.edit.comboGender.currentIndex()
            bio = unicode(self.edit.texteditBio.toPlainText())
            imagepath = None

            if index is not None:
                imagepath = self.Doc.characters[index].photoname
            else:
                imagepath = None  # Ho caricato la foto, ora, di logica devo lavorarmi il salvataggio

            if self.edit.image != None:  # se ho selezionato una foto
                if imagepath is None:
                    imagepath = self.edit.image
                else:  # Se non è none, devo prima eliminare la foto
                    path = self.Doc.projectdatapath + '/' + imagepath
                    os.remove(path)
                    imagepath = self.edit.image

                if not os.path.exists(self.Doc.projectdatapath):
                    os.mkdir(self.Doc.projectdatapath)
                import shutil
                # Adesso dobbiamo vedere se esiste l'immagine
                pathdest = self.Doc.projectdatapath + '/' + self.edit.image
                if os.path.exists(pathdest):
                    passa = False
                    print 'exist------>'
                    grand = -1
                    while passa is False:
                        print 'IM DO WHILE'
                        grand += 1
                        ext = self.edit.image[-4:]
                        print ext, 'extension'
                        newimagename = self.edit.image[:-4] + str(grand) + ext
                        pathdestnew = self.Doc.projectdatapath + '/' + newimagename
                        imagepath = newimagename  # Fill della variabile
                        if not os.path.exists(pathdestnew):
                            tmpathrename = self.Doc.tmpworkingpath + '/' + newimagename
                            shutil.copyfile(self.edit.completepathimage, self.Doc.tmpworkingpath + '/' + self.edit.image)
                            os.rename(self.Doc.tmpworkingpath + '/' + self.edit.image, tmpathrename)
                            shutil.copyfile(tmpathrename, pathdestnew)
                            os.remove(tmpathrename)
                            passa = True
                            print 'passa True'
                elif not os.path.exists(pathdest):
                    shutil.copyfile(self.edit.completepathimage, self.Doc.projectdatapath + '/' + self.edit.image)
            else:
                if imagepath is None:
                    imagepath = None

            if self.edit.remphotocheck.isChecked() is True:
                if self.Doc.characters[index].photoname is not None:
                    path = self.Doc.projectdatapath + '/' + self.Doc.characters[index].photoname
                    os.remove(path)
                    imagepath = None
                else:
                    imagepath = None

            if index is None:
                self.Doc.newpc(name, age, imagepath, gender, bio)
            elif index is not None:
                self.Doc.newpc(name, age, imagepath, gender, bio, index)

            self.Doc.ordercharlist(True)
            self.father.updatechar()
            a = self.Doc.retcharlist(True)
            print a
            for element in a:
                print element, element.name
            self.edit.image = None

            self.Doc.setStatus()
            if index is None:
                self.father.pgList.onceclicked()
            else:
                self.father.pgList.onceclicked(index)
            self.edit.close()
            self.close()
            self.father.updatechar()

            self.father.pgList.setItemSelected(self.father.pgList.item(self.father.pgList.index), True)
            self.father.pgList.setCurrentRow(self.father.pgList.row(self.father.pgList.selectedItems()[0]))
            self.father.pgList.index = self.father.pgList.currentRow()
            self.father.pgList.onceclicked(self.father.pgList.index)

            print self.Doc.characters

    def showguided(self):
        vdialog = QtGui.QMessageBox(self)
        vdialog.setWindowTitle('Penca Info')
        vdialog.setText('Not implemented yet.<br>Maybe in Penca 0.35 or 0.40.')
        vdialog.setIcon(QtGui.QMessageBox.Information)
        vdialog.addButton(QtGui.QMessageBox.Close)
        vdialog.exec_()


class editpng(QtGui.QDialog):  # FINESTRA PRINCIPALE MAINWINDOW

    def __init__(self, base, doc, parent=None):
        super(editpng, self).__init__(parent)
        self.father = parent
        self.Base = base
        self.Doc = doc
        self.image = None
        self.index = None
        self.completepathimage = None
        uic.loadUi('./libpnc/uipnc/editpng.ui', self)
        self.chooseimage.clicked.connect(lambda: self.showDialog())

    def showDialog(self):

        filters = ['.jpg', '.png']
        path = QtGui.QFileDialog.getOpenFileName(self, "Open File", os.getcwd())
        passtest = False

        for element in filters:
            if element  in path:
                passtest = True
                print 'yes'

        if passtest is False:
            vdialog = QtGui.QMessageBox(self)
            vdialog.setWindowTitle('Penca Info')
            vdialog.setText('Not a valid image file.<br>Please, use .jpg or .png files.')
            vdialog.setIcon(QtGui.QMessageBox.Information)
            vdialog.addButton(QtGui.QMessageBox.Close)
            vdialog.exec_()
            self.image = None
        elif passtest is True:
            self.pathimage.setText(os.path.basename(str(path)))
            self.completepathimage = path
            self.image = os.path.basename(str(path))

    def clearedit(self):
        self.linename.clear()
        self.spinage.setValue(0)
        self.comboGender.setCurrentIndex(0)  #Set zero
        self.pathimage.setText("No image")
        self.index = None
        self.texteditBio.clear()
        self.remphotocheck.setVisible(False)


# Widgets class AVANZATE =============================================================
# Del tipo 'Mortacci mia che sciccheria!'

class docList(QtGui.QListWidget):

    def __init__(self, base, doc, parent, mainwindow):
        super(docList, self).__init__(parent)

        self.Base = base
        self.Doc = doc
        self.father = parent
        self.mainwindow = mainwindow
        # Set della listwidget
        self.font = QtGui.QFont()
        self.font.setFamily('Calibri')
        self.setAlternatingRowColors(True)
        self.font.setPointSize(12)
        self.setFont(self.font)
        self.setWordWrap(True)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        # Callbacks
        self.itemDoubleClicked.connect(self.doubleselectchap)

    def dragEnterEvent(self, event):
        super(docList, self).dragEnterEvent(event)
        ele = self.selectedItems()
        if ele:
            self.father.index = int(self.currentRow())
            print self.father.index, 'selected'

    def dragMoveEvent(self, event):
        super(docList, self).dragMoveEvent(event)

    def dropEvent(self, event):
        super(docList, self).dropEvent(event)
        print self.father.index
        self.Doc.movechapter(self.father.index, self.currentRow())
        prev = self.father.index
        next = self.currentRow()
        self.father.index = int(self.currentRow())
        self.father.updatechap()
        if prev == self.Doc.index:
            print 'preso'
            self.Doc.index = int(next)
        elif next == self.Doc.index:
            print 'preso'
            self.Doc.index = int(next)
        self.setCurrentRow(self.Doc.index)
        self.Doc.setStatus()
        print 'moved', prev, 'in', next, 'selected', self.Doc.index

    def doubleselectchap(self):
        self.Doc.index = int(self.currentRow())
        self.mainwindow.main_updatebyindex(int(self.currentRow()))
        self.father.close()

    def newchap(self):
        self.Doc.newchapter()
        self.father.updatechap()
        self.Doc.setStatus()

    def editchap(self):
        data = None
        for element in self.Doc.chapters:
            if element.id == self.father.index:
                data = element
        self.father.setter.lineTitle.setText(data.title)
        self.father.setter.textSino.setText(data.synopse)
        self.father.setter.exec_()

    def removechoice(self, index):

        """ Simple dialog show function, it is for project deleting. """

        ask = QtGui.QMessageBox(self)
        ask.setWindowTitle('Delete')
        ask.setText("Delete the selected chapter? It's irreversible.")
        ask.setIcon(QtGui.QMessageBox.Warning)
        okbutton = ask.addButton("Ok", QtGui.QMessageBox.ActionRole)
        ask.addButton(QtGui.QMessageBox.Cancel)
        okbutton.clicked.connect(lambda: self.delete(index))
        ask.exec_()

    def delete(self, index):
        print index
        self.Doc.delchapter(index)
        self.father.updatechap()
        docs = self.selectedItems()
        if docs:
            self.father.updatebyindexchap(int(self.currentRow()))
        elif not docs:
            self.Doc.index = None
            self.mainwindow.label.clear()
            self.mainwindow.pagina.clear()
        self.Doc.setStatus()


class pgList(QtGui.QListWidget):

    def __init__(self, base, doc, parent, mainwindow):
        super(pgList, self).__init__(parent)

        self.Base = base
        self.Doc = doc
        self.index = 0
        self.father = parent
        self.mainwindow = mainwindow
        # Set della listwidget
        self.font = QtGui.QFont()
        self.font.setFamily('Calibri')
        self.setAlternatingRowColors(True)
        self.font.setPointSize(12)
        self.setFont(self.font)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setWordWrap(True)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.newpng = choicepgedit(base, doc, self.father)
        # Callbacks
        self.itemClicked.connect(lambda: self.onceclicked())

    def newchar(self):
        self.newpng.exec_()

    def editchar(self):
        index = self.Doc.index = int(self.currentRow())
        self.newpng.edit = editpng(self.Base, self.Doc, self.father)
        self.newpng.edit.editButton.clicked.connect(lambda: self.newpng.new())
        self.newpng.edit.clearedit()
        self.newpng.edit.linename.setText(self.Doc.characters[index].name)
        self.newpng.edit.spinage.setValue(self.Doc.characters[index].age)
        if self.Doc.characters[index].photoname is not None:
            self.newpng.edit.pathimage.setText(self.Doc.characters[index].photoname)
        self.newpng.edit.comboGender.setCurrentIndex(self.Doc.characters[index].gender)
        self.newpng.edit.texteditBio.setText(self.Doc.characters[index].bio)
        self.newpng.edit.index = index  # Indice per la modifica
        self.newpng.edit.comboGender.setCurrentIndex(0)  #Set zero se no ERRORE
        self.newpng.edit.remphotocheck.setVisible(True)
        self.newpng.edit.exec_()

    def doubleselectchap(self):
        self.Doc.index = int(self.currentRow())
        self.mainwindow.updatebyindex(int(self.currentRow()))

    def onceclicked(self, index=None):
        if self.selectedItems():

            if index is None:
                self.index = self.row(self.selectedItems()[0])
            elif index is not None:
                self.index = index

            print self.index
            self.father.labelname.setText(self.Doc.characters[self.index].name)
            self.father.labelage.setText(str(self.Doc.characters[self.index].age))
            gender = self.Doc.characters[self.index].gender
            if gender is 0:
                gender = 'Male'
            elif gender is 1:
                gender = 'Female'
            elif gender is 2:
                gender = 'Unknow'
            self.father.labelgender.setText(gender)
            self.father.aboutarea.setText(self.Doc.characters[self.index].bio)
            if self.Doc.characters[self.index].photoname is not None:
                print "Will load the photo of the pg"
                image = QtGui.QImage()
                # Qui sotto preso da internet, il size del background non è supportato da QT 4.7
                # http://qt-project.org/forums/viewthread/41303
                self.father.photon.setStyleSheet('QWidget#photon{border-image: url(' + self.Doc.projectdatapath + "/" + self.Doc.characters[self.index].photoname + ') 0 0 0 0 stretch stretch;}')
            else:
                image = QtGui.QImage()
                self.father.photon.setStyleSheet('')

    def removechoice(self, index):

        """ Simple dialog show function, it is for project deleting. """

        ask = QtGui.QMessageBox(self)
        ask.setWindowTitle('Delete')
        ask.setText("Delete the selected character? It's irreversible.")
        ask.setIcon(QtGui.QMessageBox.Warning)
        okbutton = ask.addButton("Ok", QtGui.QMessageBox.ActionRole)
        ask.addButton(QtGui.QMessageBox.Cancel)
        okbutton.clicked.connect(lambda: self.delete(index))
        ask.exec_()

    def delete(self, index):
        print len(self.Doc.characters)
        print self.index
        self.Doc.delpc(self.index)
        print len(self.Doc.characters)
        self.clear()
        self.update()
        self.Doc.setStatus()

    def update(self):
        for element in self.Doc.characters:
            self.addItem(element.name)