# (C) 2009 copyright by Peter Bouda
# -*- coding: utf-8 -*-
"""This module contains classes to access Toolbox data.

The class ToolboxTXT is a low level API to Toolbox .txt files.

ToolboxTree is the class to access the data via a tree.
ToolboxTrees are read-only.

ToolboxCorpusReader implements a part of the corpus reader API
described in the Natural Language Toolkit (NLTK):
http://nltk.googlecode.com/svn/trunk/doc/howto/corpus.html
"""

__author__ =  'Peter Bouda'
__version__=  '0.2.0'

import re
import pyannotation.data

############################ Builders

class ToolboxAnnotationFileObject(pyannotation.data.AnnotationFileObject):

    def __init__(self, filepath):
        pyannotation.data.AnnotationFileObject.__init__(self, filepath)
        self.setFilepath(filepath)

    def getFile(self):
        return self.filepath

    def getFilepath(self):
        return self.filepath

    def setFilepath(self, filepath):
        self.filepath = filepath

    def createParser(self):
        if self.parser == None:
            self.parser = ToolboxAnnotationFileParser(self, self.createTierHandler())
        return self.parser


class ToolboxAnnotationFileParser(pyannotation.data.AnnotationFileParser):

    def __init__(self, annotationFileObject, annotationFileTiers, wordSep = r"[ \n\t\r]+", morphemeSep = r"[-]", glossSep = r"[:]"):
        pyannotation.data.AnnotationFileParser.__init__(self, annotationFileObject, annotationFileTiers, wordSep, morphemeSep, glossSep)
        self.lastUsedAnnotationId = 0
        self.annotationFileObject = annotationFileObject
        #self.parse(file, wordSep, morphemeSep, glossSep)
        #print self.tree

    def parse(self):
        f = open(self.annotationFileObject.getFilepath(), 'r')
        strInRef = ""
        strText = ""
        strMorph = ""
        strGloss = ""
        strTrans = ""
        tree = []    
        for line in f:
            line = unicode(line, "iso-8859-1")
            if re.search(r"^\\ref ", line):
                # new ref starts, so process data
                if strInRef != "":
                    strText = re.sub(r"[\.,\?!]", "", strText)
                    strText = re.sub(self.WORD_BOUNDARY_PARSE, " ", strText)
                    strText.strip()
                    strTrans.strip()
                    strMorph.strip()
                    strGloss.strip()
                    # stupid python does not strip windows line ends
                    strTrans = re.sub(r"\r\n", " ", strTrans)
                    strText = re.sub(r"\r\n", " ", strText)
                    strMorph = re.sub(r"\r\n", " ", strMorph)
                    strGloss = re.sub(r"\r\n", " ", strGloss)
                    arrTextWords = re.split(self.WORD_BOUNDARY_PARSE, strText)
                    arrTextWords = filter(lambda i: i != '', arrTextWords)
                    arrMorphWords = re.split(self.WORD_BOUNDARY_PARSE, strMorph)
                    arrMorphWords = filter(lambda i: i != '', arrMorphWords)
                    arrGlossWords = re.split(self.WORD_BOUNDARY_PARSE, strGloss)
                    arrGlossWords = filter(lambda i: i != '', arrGlossWords)
                    ilElements = []
                    for i,word in enumerate(arrTextWords):
                        morphemes = ""
                        glosses = ""
                        if i < len(arrMorphWords):
                            morphemes = arrMorphWords[i]
                        if i < len(arrGlossWords):
                            glosses = arrGlossWords[i]
                        ilElements.append(self.ilElementForString("%s %s %s" % (word, morphemes, glosses)))
                    if len(ilElements) == 0:
                        ilElements = [ ['', '',  [ ['', '',  [ ['',  ''] ] ] ] ] ]
                    tree.append([ strInRef,  strText,  ilElements, [["a%i" % self.useNextAnnotationId(), strTrans]], "", "", "" ])
                    strInRef = ""
                    strText = ""
                    strMorph = ""
                    strGloss = ""
                    strTrans = ""
                line = line.strip()
                line = re.sub(r"^\\ref ", "", line)
                strInRef = line
            elif re.search(r"^\\tx ", line):
                line = re.sub(r"^\\tx ", "", line)
                strText = strText + line
            elif re.search(r"^\\mo ", line):
                line = re.sub(r"^\\mo ", "", line)
                strMorph = strMorph + line
            elif re.search(r"^\\gl ", line):
                line = re.sub(r"^\\gl ", "", line)
                strGloss = strGloss + line
            elif re.search(r"^\\ft ", line):
                line = re.sub(r"^\\ft ", "", line)
                strTrans = line            
        return tree

    def ilElementForString(self, text):
        arrT = text.split(" ")
        word = arrT[0]
        il = ""
        gloss = ""
        if len(arrT) > 1:
            il = arrT[1]
        if len(arrT) > 2:
            gloss = arrT[2]
        ilElement = [ "a%i" % self.useNextAnnotationId(), word, [] ]
        arrIl = re.split(self.MORPHEME_BOUNDARY_PARSE, il)
        arrGloss = re.split(self.MORPHEME_BOUNDARY_PARSE, gloss)
        for i in range(len(arrIl)):
            g = ""
            if i < len(arrGloss):
                g = arrGloss[i]
            arrG = re.split(self.GLOSS_BOUNDARY_PARSE, g)
            arrG2 = []
            for g2 in arrG:
                arrG2.append([ "a%i" % self.useNextAnnotationId(), g2])
            ilElement[2].append([ "a%i" % self.useNextAnnotationId(), arrIl[i], arrG2 ])
        return ilElement

    def getLastUsedAnnotationId(self):
        return self.lastUsedAnnotationId

    def useNextAnnotationId(self):
        a = self.lastUsedAnnotationId
        self.lastUsedAnnotationId = self.lastUsedAnnotationId + 1
        return a




