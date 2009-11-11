# (C) 2009 copyright by Peter Bouda
# -*- coding: utf-8 -*-
"""This module contains classes to access Kura data.

The class KuraXML is a low level API to Kura .xml files.

KuraTree is the class to access the data via a tree, which also
contains the original .xml IDs. Because of this KuraTrees are
read-/writeable. 

KuraCorpusReader implements a part of the corpus reader API
described in the Natural Language Toolkit (NLTK):
http://nltk.googlecode.com/svn/trunk/doc/howto/corpus.html
"""

__author__ =  'Peter Bouda'
__version__=  '0.1.2'


from lxml import etree
from lxml.etree import Element

class KuraTree(object):

    def __init__(self, file):
        self.kuraxml = KuraXML(file)
        self.tree = []
        self.file = file
        self.MORPHEME_BOUNDARY = "-"
        self.GLOSS_BOUNDARY = ":"

    def parse(self):
        self.phraseIds = self.kuraxml.getPhraseIds()
        for pId in self.phraseIds:
            phrase = self.kuraxml.getPhraseForId(pId)
            translations = self.kuraxml.getTranslationsForPhraseId(pId)
            translationsWithIds = []
            ilElements = []
            for t in translations:
                translationsWithIds.append([pId, t])
            wordsIds = self.kuraxml.getWordIdsForPhraseId(pId)
            for wordId in wordsIds:
                ilElements.append(self.getIlElementForWordId(wordId))
            if len(ilElements) == 0:
                ilElements = [ ['', '',  [ ['', '',  [ ['',  ''] ] ] ] ] ]
            self.tree.append([ pId,  phrase,  ilElements, translationsWithIds])

    def getIlElementForWordId(self, wordId):
        ilElement = []
        word = self.kuraxml.getWordForId(wordId)
        ilElement.append(wordId)
        ilElement.append(word)
        morphElements = []
        morphIds = self.kuraxml.getMorphIdsForWordId(wordId)
        for morphId in morphIds:
            morpheme = self.kuraxml.getMorphForId(morphId)
            glosses = self.kuraxml.getGlossesForMorphId(morphId)
            glossElements = []
            for gloss in glosses:
                glossElements.append(['', gloss])
            morphElements.append([ morphId, morpheme, glossElements ])
        if len(morphIds) == 0:
            ilElement.append([[ '',  '',  [ ['',  ''] ]]])
        else:
            ilElement.append(morphElements)
        return ilElement

class KuraXML(object):

    def __init__(self, file):
        self.tree = etree.parse(file)

        # phrases and words and morphs with ids
        aid = self.getLastUsedAnnotationId()
        items = self.tree.findall("//phrase") + self.tree.findall("//word") + self.tree.findall("//morph")
        for i in items:
            if not 'id' in i.attrib:
                i.set('id', "a%i" % aid)
                aid = aid + 1

    def getLastUsedAnnotationId(self):
        aid = 0
        items = self.tree.findall("//phrase") + self.tree.findall("//word") + self.tree.findall("//morph")
        for i in items:
            if 'id' in i.attrib and int(i.attrib['id']) > aid:
                aid = int(i.attrib['id'])
        return aid

    def getPhraseIds(self):
        ids = []
        phrases = self.tree.findall("phrases/phrase")
        for p in phrases:
            ids.append(p.attrib["id"])
        return ids

    def getPhraseForId(self, idPhrase):
        ret = None
        phrase = self.tree.find("phrases/phrase[@id='%s']" % idPhrase)
        if phrase != None:
            ret = phrase.findtext("item[@type='text']")
        return ret

    def getTranslationsForPhraseId(self, idPhrase):
        translations = []
        items = self.tree.findall("phrases/phrase[@id='%s']/item[@type='TR']" % idPhrase)
        if items != None:
            for i in items:
                t = i.findtext(".")
                if t != None:
                    translations.append(t)
        return translations

    def getWordIdsForPhraseId(self, idPhrase):
        ids = []
        words = self.tree.findall("phrases/phrase[@id='%s']/words/word" % idPhrase)
        for w in words:
            ids.append(w.attrib["id"])
        return ids

    def getWordForId(self, idWord):
        ret = None
        word = self.tree.find("phrases/phrase/words/word[@id='%s']" % idWord)
        if word != None:
            ret = word.findtext("item[@type='text']")
        return ret

    def getMorphIdsForWordId(self, idWord):
        ids = []
        morphs = self.tree.findall("phrases/phrase/words/word[@id='%s']/morphemes/morph" % idWord)
        for m in morphs:
            ids.append(m.attrib["id"])
        return ids

    def getMorphForId(self, idMorph):
        ret = None
        morph = self.tree.find("phrases/phrase/words/word/morphemes/morph[@id='%s']" % idMorph)
        if morph != None:
            ret = morph.findtext("item[@type='text']")
        return ret

    def getGlossesForMorphId(self, idMorph):
        glosses = []
        items = self.tree.findall("phrases/phrase/words/word/morphemes/morph[@id='%s']/item[@type='ABBR']" % idMorph)
        if items == None:
            items = []
        items2 = self.tree.findall("phrases/phrase/words/word/morphemes/morph[@id='%s']/item[@type='GL']" % idMorph)
        if items2 == None:
            items2 = []
        for i in items + items2:
            g = i.findtext(".")
            if g != None:
                glosses.append(g)
        return glosses


