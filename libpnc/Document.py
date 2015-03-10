# -*- coding: utf-8 -*-

import os
import shutil
import codecs
import zipfile
from bs4 import BeautifulSoup


class PencaDocument(object):

    """ The class represent the Penca document, first to use any module open a file and fill the
    projecttmpWorkingpath variable, use returnbasepath from basemodule."""

    def __init__(self):
        self.pnctitle = None
        self.pncauthor = None
        self.pncabout = None

        # Lista dei capitoli e personaggi (oggetti)
        self.chapters = []
        self.characters = []

        self.projecttmpworkingpath = None
        self.projectdatapath = None
        self.workingpath = None
        self.tmpworkingpath = None
        self.index = 0
        self.status = False

    def setStatus(self, clear=False):
        if clear is True:
            self.status = False
        elif clear is False:
            if self.status is True:
                return
            else:
                self.status = True

    def makearchivepnc(self):
        creationpath = self.tmpworkingpath + '/' + unicode(self.pnctitle)
        shutil.make_archive(self.workingpath + '/' + unicode(self.pnctitle), 'zip', creationpath)
        os.rename(self.workingpath + '/' + unicode(self.pnctitle) + '.zip', self.workingpath + '/' + unicode(self.pnctitle) + '.pnc')
        print 'All is go ok? Return True'
        return True

    def retchaplist(self):
        self.chapters.sort(key=lambda x: x.id)
        return self.chapters

    def orderchaplist(self):
        self.chapters.sort(key=lambda x: x.id)

    def retcharlist(self, byname):
        if byname is True:
            self.characters.sort(key=lambda x: x.name)
            return self.characters

    def ordercharlist(self, byname):
        if byname is True:
            self.characters.sort(key=lambda x: x.name)

    def movechapter(self, startind, endind):
        prevdoc = None
        enddoc = None

        if startind == endind:
            return

        for element in self.chapters:
            if element.id is startind:
                prevdoc = element
            if element.id is endind:
                enddoc = element

        print prevdoc, enddoc
        prevdoc.id, enddoc.id = enddoc.id, prevdoc.id


    def delchapter(self, index):
        a = False
        try:
            a = self.chapters.pop(index)
        except():
            print 'No doc index'
            return
        for element in self.chapters:
            if element.id > index:
                element.id -= 1

    def fillprojectpath(self, basemodule, overwrite=False):

        """ Fill the variable from a Base instance. """

        if self.projecttmpworkingpath in [None, '', ' ']:

            # Prendo i dati da istanza di Base
            paths = basemodule.returnbasepaths()

            if paths:

                # Provo ad inserire, se ecceziono, ritorno
                try:
                    self.workingpath = paths[0]
                    self.tmpworkingpath = paths[1]
                    self.projecttmpworkingpath = paths[2]
                except():
                    print 'Not possible to set projectpath'
                    return

    def newchapter(self):

        doclist = self.retchaplist()
        index = 0
        if not doclist:
            index = 0
        elif doclist:
            index = len(doclist)
        print 'created doc', index
        item = PencaChapter(index, 'New Title', 'New Synopse', 'New Document')
        self.chapters.append(item)

    def shrink(self, string):

        if string in [' ', '', '\n', '\r', None, True, False]:
            return False
        string = unicode(string)
        while string[0] in [' ', '\n', '\r']:
            string = string[1:]
        while string[-1] in [' ', '\n', '\r']:
            string = string[:-1]
        return string

    def openpncfile(self, filename, justdata=False):

        """ Assuming you can obtain the name of the file that you want open.
        The open routine is simple as count, it unzip the pnc file and load the
        files. For last, if justdata will be True, then it will just return
        the title, author and about of the file, deleting the tmp folder.
        Note, the justdata flag is a boolean False, or True. """

        # Creation of paths and check dir

        pathtoopen = self.workingpath + '/' + filename + '.pnc'
        if not os.path.exists(pathtoopen):
            print pathtoopen
            print 'No file to open, return False'
            return False

        self.projecttmpworkingpath = self.tmpworkingpath + '/' + filename
        self.projectdatapath = self.projecttmpworkingpath + '/data'
        if not os.path.exists(self.projecttmpworkingpath):
            os.mkdir(self.projecttmpworkingpath)
        with zipfile.ZipFile(pathtoopen, 'r') as f:
            f.extractall(self.projecttmpworkingpath)

        pni = self.projecttmpworkingpath + '/penca.pni'
        if not os.path.exists(pni):
            print 'No index file, no Penca file. Return False.'
            return False

        """ If all green, in this moment, we have a pnc valid file, or a good approximation. In fact
        we have a pni file, a penca index. The project is extract in the tmp folder, with a folder inside which
        had the name of the opened file. So on. """

        # Beautifulsoup set the tag

        htmltoload = BeautifulSoup(codecs.open(pni, 'r', 'utf8'))
        self.pnctitle = htmltoload.penca['title']
        self.pncauthor = htmltoload.penca['author']
        aboutstr = htmltoload.about.string

        # Removing whitespaces from sboutstr and set

        while aboutstr[0] in [' ', '\n', '\r']:
            aboutstr = aboutstr[1:]
        while aboutstr[-1] in [' ', '\n', '\r']:
            aboutstr = aboutstr[:-1]
        self.pncabout = aboutstr

        if justdata is True:
            ret = (self.pnctitle, self.pncauthor, self.pncabout)
            shutil.rmtree(self.tmpworkingpath + '/' + filename)
            return ret

        # Riempiamo la lista dei documenti

        for element in htmltoload.find_all('doc'):

            documenttext = ''
            synopse = ''

            if element.contents[0] is not None:
                documenttext = self.shrink(element.contents[0])
                if not documenttext:
                    documenttext = ' '
                synopse = self.shrink(element.sin.string)
                if not synopse:
                    synopse = ' '

            chap = PencaChapter(int(element.get('id')), element['title'], synopse, documenttext)

            self.chapters.append(chap)

        # Riempiamo la lista dei personaggi

        for element in htmltoload.find_all('char'):

            name = unicode(element['name'])
            age = int(element['age'])
            imagepath = None
            try:
                imagepath = element['imagepath']
            except(KeyError):
                print "No imagepath, set none"
                imagepath = None
            gender = int(element['gender'])
            bio = unicode(element.string)

            obj = Pencapng()
            obj.name = name
            obj.age = age
            obj.gender = gender
            obj.photoname = imagepath
            obj.bio = bio

            self.characters.append(obj)

        print self.chapters

        return True

    def save(self):

        pni = self.projecttmpworkingpath + '/penca.pni'  # File beautifulsoup da aprire
        if not os.path.exists(pni):
            print 'No index file, no Penca file. Return False.'
            return False

        if self.status is True:
            # Beautifulsoup set the tag
            htmltosave = BeautifulSoup(codecs.open(pni, 'r', 'utf8'))
            htmltosave.docs.clear()
            print htmltosave.docs

            # Capitoli
            for element in self.chapters:

                doctag = htmltosave.new_tag('doc')
                doctag['id'] = element.id
                doctag['title'] = element.title
                doctag.append(element.documentText)
                sintag = htmltosave.new_tag('sin')
                sintag.append(element.synopse)
                doctag.append(sintag)

                htmltosave.docs.append(doctag)

            htmltosave.chars.clear()  # PG's
            print htmltosave.chars

            for element in self.characters:
                print len(self.characters), 'have this chara to save'

                pg = htmltosave.new_tag('char')
                pg['name'] = element.name
                pg['age'] = element.age
                if not element.photoname is None:
                    pg['imagepath'] = element.photoname
                pg['gender'] = element.gender
                pg.append(element.bio)

                htmltosave.chars.append(pg)

            print htmltosave
            prettyhtml = htmltosave.prettify('utf-8')

            os.remove(pni)  # Remove first file

            with codecs.open(pni, 'w') as f:
                f.write(prettyhtml)
            self.setStatus(True)
        elif self.status is False:
            print 'Not saved'

    def newpc(self, name, age, imagepath, gender, bio, index=None):
        try:  # Exception name
            name = unicode(name)
        except():
            print 'No name or invalid, return.'
            return

        age = int(age)
        imagepath = imagepath
        gender = int(gender)
        bio = unicode(bio)

        if index is None:  # Assegnazione DATI
            obj = Pencapng()
            obj.name = name
            obj.age = age
            obj.gender = gender
            obj.bio = bio
            obj.photoname = imagepath
            print obj.photoname, 'PHOTON'

            self.characters.append(obj)
        elif index is not None:
            i = self.characters[index]
            i.name = name
            i.age = age
            i.gender = gender
            i.bio = bio
            i.photoname = imagepath
            print i.photoname, 'PHOTON'

    def delpc(self, index):

        print type(self.projectdatapath)
        prediction = None
        if self.characters[index].photoname is not None:
            prediction = self.projectdatapath + '/' + self.characters[index].photoname
        del self.characters[index]
        self.ordercharlist(True)
        if prediction is not None and os.path.exists(prediction):
            print 'exist photo'
            os.remove(prediction)


class PencaChapter(object):

    """ The class chapter is needed to store chapter relative info. """

    def __init__(self, id, title, synopse, documentText):

        self.id = id
        self.title = title
        self.synopse = synopse
        self.documentText = documentText

class Pencapng(object):

    def __init__(self):

        self.name = None
        self.age = 0
        self.gender = None
        self.bio = None
        self.photoname = None


class Pencastats():

    def countwords (self, text):
        words = len(unicode(text).split())
        return words

    def countchars(self, text):
        words = len(unicode(text))  # Lunghezza del testo
        return words

    def mic(self, text, base, doc):
        words = unicode(text).lower().split()  # parole
        pg = None
        thiscnt = 0
        pgs = []
        for element in doc.characters:  # Carico i personaggi papabili
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
            return None
        elif pg is not None:  # caso non None
            return pg