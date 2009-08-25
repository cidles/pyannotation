# (C) 2009 copyright by Peter Bouda
# -*- coding: utf-8 -*-
"""This module contains classes to access Kura data.

The class KuraXML is a low level API to Kura .xml files.

KuraTree is the class to access the data via a tree, which also
contains the original .eaf IDs. Because of this KuraTrees are
read-/writeable. 

KuraCorpusReader implements a part of the corpus reader API
described in the Natural Language Toolkit (NLTK):
http://nltk.googlecode.com/svn/trunk/doc/howto/corpus.html
"""

__author__ =  'Peter Bouda'
__version__=  '0.1.1'


from lxml import etree
from lxml.etree import Element

class KuraXML(object):

    def __init__(self, file):
        self.kuraxml = KuraXML(file)

    def parse(self):
        

class KuraXML(object):

    def __init__(self, file):
        self.tree = etree.parse(file)

        # phrases and words and morphs with ids
        aid = self.getLastUsedAnnotationId()
        items = self.tree.findall("//phrase") + self.tree.findall("//word") + self.tree.findall("//morph")
        for i in items:
            if not 'id' in i.attrib:
                i.set('id', "%i" % aid)
                aid = aid + 1

    def getLastUsedAnnotationId(self):
        aid = 0
        items = self.tree.findall("//phrase") + self.tree.findall("//word") + self.tree.findall("//morph")
        for i in items:
            if 'id' in i.attrib and int(i.attrib['id']) > aid:
                aid = int(i.attrib['id'])
        return aid

    def getPhrasesIds(self):
        ids = []
        phrases = self.tree.findall("/interlinear-text/phrases/phrase")
        for p in phrases:
            ids.append(p.attrib["id"]

    def getPhraseForId(self, idPhrase):
        ret = None
        phrase = self.tree.find("/interlinear-text/phrases/phrase[@id='%s']" % idPhrase)
        if phrase != None:
            ret = phrase.findtext("item[@type='text']")
        return ret

    def getWordIdsForPhraseId(self, idPhrase):
        pass

    def getWordForId(self, idWord):
        pass

    def getMorphIdsForWordId(self, idWord):
        pass

    def getMorphForId(self, idMorph):
        pass

    def getGlossesForMorphId(self, idMorph):
        pass


