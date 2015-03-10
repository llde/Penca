# -*- coding: utf-8 -*-

import os
import shutil
import codecs
import zipfile
from bs4 import BeautifulSoup

""" Guide to read this code, please read this.
This type of comment will be in english, anyway the sharp '#' comments
will be in italian. Please feel free to translate the sharp comments if you can/will."""


class PencaBaseModule(object):

    """ The base module is needed to store all the core infos of the project. """

    def __init__(self, workingpath):

        # Se non esiste il path di partenza lo crea.
        if not os.path.exists(workingpath):
            os.mkdir(workingpath)
        self.workingpath = workingpath

        # Se non esiste il path tmp lo crea.
        if not os.path.exists(self.workingpath + '/tmp'):
            os.mkdir(self.workingpath + '/tmp')
        self.tmpworkingpath = self.workingpath + '/tmp'

        self.projecttmpworkingpath = None

    def returnbasepaths(self):

        # Ritorno cose
        return self.workingpath, self.tmpworkingpath, self.projecttmpworkingpath

    def createnewfile(self, title, author, abouto):

        """ Now create a new file. Note that the def will assume that the data is stored in the
        Module base data's variable. Use setpncdata for store the data of the project before, else
        it will crash. If pnc file already exist, we cannot create a new project. """

        if os.path.exists(self.workingpath + '/' + str(title) + '.pnc'):
            print 'project already exist, return False'
            return False  # Progetto esiste

        creationpath = self.tmpworkingpath + '/' + str(title)
        if os.path.exists(creationpath):
            shutil.rmtree(creationpath, True)

            """ Assume that we will delete the previous tmp folder, because if we not do it, the routine will crash.
            In fact, os.mkdir will crash itself if dir already exist. """

        os.mkdir(creationpath)

        """ Assume the creation of a single penca.html file, renamed in pni, "PeNca Index".
        The pni file will store all data, and will be really good formatted by libsoup, so in the end
        we will created a good html file. All the text of the project will be stored in this file. """

        htmltosave = BeautifulSoup('<penca><about></about><docs></docs><chars></chars></penca>')

        # Append pnc data to the file

        htmltosave.penca['title'] = str(title)
        if str(author) is not None:
            htmltosave.penca['author'] = str(author)
        else:
            htmltosave.penca['author'] = 'none'
        if str(abouto) is not None:
            htmltosave.about.append(str(abouto))
        else:
            htmltosave.about.append('none')

        # Creation of the new doc and the relative sinopse

        doctag = htmltosave.new_tag('doc')
        doctag['id'] = 0
        doctag['title'] = 'New Title'
        doctag.append('document text')

        sintag = htmltosave.new_tag('sin')
        sintag.append('synopse text')

        # Append of the tag and prepare to save

        doctag.append(sintag)
        htmltosave.docs.append(doctag)
        prettyhtml = htmltosave.prettify('utf-8')

        with codecs.open(creationpath + '/penca.pni', 'w') as f:
            f.write(prettyhtml)

        """ The penca file ".pnc" is a simple zip file renamed, it is the best for keep all united the data of
        Penca, including the html index, the data folder, and so on. I think that in concordance with the development
        of the software, the Penca filesystem will be change a lot, so, until the first first release (1.0) will be
        released, the Penca filesystem will not be marked as "stable"."""

        shutil.make_archive(self.workingpath + '/' + str(title), 'zip', creationpath)
        os.rename(self.workingpath + '/' + str(title) + '.zip', self.workingpath + '/' + str(title) + '.pnc')
        shutil.rmtree(creationpath)
        print 'All is go ok? Return True'
        return True



    def deleteproject(self, name):

        """ A supersimple deleting routine for remove projects. """
        pathdelete = self.workingpath + '/' + name + '.pnc'
        if os.path.exists(pathdelete):
            os.remove(pathdelete)
            self.projecttmpworkingpath = None

    def returnpncfilelist(self):

        """ This is the routine that give all the pnc file in the working folder. """
        returnlist = []
        for element in os.listdir(self.workingpath):
            if element.endswith('.pnc'):
                returnlist.append(element[:-4])
        print returnlist
        return returnlist