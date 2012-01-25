# -*- coding: utf-8 -*-
# (C) 2011 copyright by Peter Bouda
"""This module contains the classes to access annotated data in
various formats.

The parsing is done by Builder classes for each file type, i.e.
Elan's .eaf files, Kura's .xml file, Toolbox's .txt files etc.
"""

import os, glob
import re
import regex

# file types
(EAF, EAFFROMTOOLBOX, KURA, TOOLBOX) = range(4)

class AnnotationFileObject(object):

    def __init__(self, filepath):
        self.tierHandler = None
        self.parser = None

    def getFile(self):
        pass

    def getFilepath(self):
        pass

    def setFilepath(self):
        pass
    
    def createTierHandler(self):
        if self.tierHandler == None:
            self.tierHandler = AnnotationFileTierHandler(self)
        return self.tierHandler

    def createParser(self):
        if self.parser == None:
            self.parser = AnnotationFileParser(self, self.createTierHandler())
        return self.parser

class AnnotationFileTierHandler(object):

    def __init__(self, annotationFileObject):
        pass

    def setUtterancetierType(self, type):
        pass

    def setWordtierType(self, type):
        pass

    def setMorphemetierType(self, type):
        pass

    def setGlosstierType(self, type):
        pass

    def setPostierType(self, type):
        pass

    def setTranslationtierType(self, type):
        pass

    def getUtterancetierIds(self, parent = None):
        pass

    def getWordtierIds(self, parent = None):
        pass

    def getMorphemetierIds(self, parent = None):
        pass

    def getGlosstierIds(self, parent = None):
        pass

    def getPostierIds(self, parent = None):
        pass

    def getTranslationtierIds(self, parent = None):
        pass

    def addTier(self, tierId, tierType, tierTypeConstraint, parentTier, tierDefaultLocale, tierParticipant):
        pass

    def getLocaleForTier(self, idTier):
        pass

    def getParticipantForTier(self, idTier):
        pass

class AnnotationFileParser(object):
    """Just the interface of the Builders."""

    def __init__(self, annotationFileObject, annotationFileTiers, wordSep = r"[ \n\t\r]+", morphemeSep = r"[-]", glossSep = r"[:]"):
        self.WORD_BOUNDARY_PARSE = wordSep
        self.MORPHEME_BOUNDARY_PARSE = morphemeSep
        self.GLOSS_BOUNDARY_PARSE = glossSep
        self.lastUsedAnnotationId = 0

    def parse(self):
        pass

    def getFile(self, tree):
        pass

    def removeAnnotationWithId(self, idAnnotation):
        pass

    def removeAnnotationsWithRef(self, idRefAnn):
        pass

    def updatePrevAnnotationForAnnotation(self, idAnnotation, idPrevAnn = None):
        pass

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


class AnnotationTree(object):

    def __init__(self, builder, morphemeSep="-", glossSep=":"):
        self.tree = []
        self.builder = builder
        self.MORPHEME_BOUNDARY_BUILD = morphemeSep
        self.GLOSS_BOUNDARY_BUILD = glossSep
        self.filters = []
        self.filteredUtteranceIds = [[]]

    def getTree(self):
        return self.tree

    def parse(self):
        self.tree = self.builder.parse()
        self.resetFilters()

    def getNextAnnotationId(self):
        return self.builder.getNextAnnotationId()

    def addTier(self, *args):
        return self.builder.addTier(*args)

    def getUtteranceIds(self):
        return [utterance[0] for utterance in self.tree]

    def getFilteredUtteranceIds(self):
        return self.filteredUtteranceIds[-1]

    def getUtteranceIdsInTier(self, tierId=""):
        return [utterance[0] for utterance in self.tree if utterance[6] == tierId]

    def getUtteranceById(self, utteranceId):
        for utterance in self.tree:
            if utterance[0] == utteranceId:
                return utterance[1]
        return ''

    def setUtterance(self, utteranceId, strUtterance):
        for utterance in self.tree:
            if utterance[0] == utteranceId:
                utterance[1] = strUtterance
                return True
        return False
        
    def getTranslationById(self, translationId):
        for utterance in self.tree:
            for translation in utterance[3][0]:
                if translation[0] == translationId:
                    return translation[1]
        return ''

    def newTranslationForUtteranceId(self, utteranceId, strTranslation):
        translationId = None
        for utterance in self.tree:
            if utterance[0] == utteranceId:
                translationId = "a%i" % self.getNextAnnotationId()
                utterance[3][0] = [ [ translationId, strTranslation ] ]
        return translationId

    def setTranslation(self, translationId, strTranslation):
        for utterance in self.tree:
            for translation in utterance[3][0]:
                if translation[0] == translationId:
                    translation[1] = strTranslation
                    return True
        return False

    def getWordById(self, wordId):
        for utterance in self.tree:
            for word in utterance[2]:
                if word[0] == wordId:
                    return word[1]
        return ''

    def getWordIdsForUtterance(self, utteranceId):
        for utterance in self.tree:
            if utterance[0] == utteranceId:
                return [w[0] for w in utterance[2]]
        return []

    def getTranslationsForUtterance(self, utteranceId):
        for utterance in self.tree:
            if utterance[0] == utteranceId:
                return utterance[3][0]
        return ''

    def getMorphemeStringForWord(self, wordId):
        m = [morpheme[1] for u in self.tree for w in u[2] if w[0] == wordId for morpheme in w[2]]
        return self.MORPHEME_BOUNDARY_BUILD.join(m)

    def ilElementForString(self, text):
        return self.builder.ilElementForString(text)

    def getGlossStringForWord(self, wordId):
        l = []
        for u in self.tree:
            for w in u[2]:
                if w[0] == wordId:
                    for m in w[2]:
                        f = [gloss[1] for gloss in m[2]]
                        l.append(self.GLOSS_BOUNDARY_BUILD.join(f))
        return self.MORPHEME_BOUNDARY_BUILD.join(l)

    def setIlElementForWordId(self, wordId, ilElement):
        for u in self.tree:
            for i in range(len(u[2])):
                w = u[2][i]
                if w[0] == wordId:
                    # fill the new ilElement with old Ids, generate new Ids for new elements
                    ilElement[0] = wordId
                    for j in range(len(ilElement[2])):
                        if j < len(w[2]) and w[2][j][0] != "":
                            ilElement[2][j][0] = w[2][j][0]
                        else:
                            ilElement[2][j][0] = "a%i" % self.getNextAnnotationId()
                        for k in range(len(ilElement[2][j][2])):
                            if j < len(w[2]) and k < len(w[2][j][2]) and w[2][j][2][k][0] != "":
                                ilElement[2][j][2][k][0] = w[2][j][2][k][0]
                            else:
                                ilElement[2][j][2][k][0] = "a%i" % self.getNextAnnotationId()
                    u[2][i] = ilElement
                    return True
        return False

    def removeUtteranceWithId(self, utteranceId):
        i = 0
        for utterance in self.tree:
            if utterance[0] == utteranceId:
                # found utterances, delete all elements from tree
                for w in utterance[2]:
                    for m in w[2]:
                        for g in m[2]:
                            self.builder.removeAnnotationWithId(g[0])
                            self.builder.removeAnnotationsWithRef(g[0])
                        self.builder.removeAnnotationWithId(m[0])
                        self.builder.removeAnnotationsWithRef(m[0])
                    self.builder.removeAnnotationWithId(w[0])
                    self.builder.removeAnnotationsWithRef(w[0])
                for t in utterance[3][0]:
                    self.builder.removeAnnotationWithId(t[0])                    
                    self.builder.removeAnnotationsWithRef(t[0])
                self.builder.removeAnnotationWithId(utteranceId)
                self.builder.removeAnnotationsWithRef(utteranceId)
                self.tree.pop(i)
                return True
            i = i + 1
        return False

    def removeWordWithId(self, wordId):
        for utterance in self.tree:
            i = 0
            for w in utterance[2]:
                if w[0] == wordId:
                    for m in w[2]:
                        for g in m[2]:
                            self.builder.removeAnnotationWithId(g[0])
                            self.builder.removeAnnotationsWithRef(g[0])
                        self.builder.removeAnnotationWithId(m[0])
                        self.builder.removeAnnotationsWithRef(m[0])
                    self.builder.removeAnnotationWithId(wordId)
                    # link next word to prev, if those are there
                    if i > 0 and len(utterance[2]) > (i+1):
                        prevwordId = utterance[2][i-1][0]
                        nextwordId = utterance[2][i+1][0]
                        self.builder.updatePrevAnnotationForAnnotation(nextwordId, prevwordId)
                    # remove link to this word if this is the first word and there is a second
                    if i == 0 and len(utterance[2]) > 1:
                        nextwordId = utterance[2][i+1][0]
                        self.builder.updatePrevAnnotationForAnnotation(nextwordId)
                    self.builder.removeAnnotationsWithRef(wordId)
                    utterance[2].pop(i)
                    return True
                i = i + 1
        return False

    def getFile(self, tierUtterances, tierWords, tierMorphemes, tierGlosses, tierTranslations):
        return self.builder.getFile(self.tree, tierUtterances, tierWords, tierMorphemes, tierGlosses, tierTranslations)
        
    def appendFilter(self, filter):
        self.filters.append(filter)
        newFilteredUtterances = [utterance[0] for utterance in self.tree if utterance[0] in self.filteredUtteranceIds[-1] and filter.utterancePassesFilter(utterance)]
        self.filteredUtteranceIds.append(newFilteredUtterances)
        
    def lastFilter(self):
        if len(self.filters) > 0:
            return self.filters[-1]
        else:
            return AnnotationTreeFilter()
        
    def updateLastFilter(self, filter):
        self.popFilter()
        self.appendFilter(filter)
        
    def popFilter(self):
        if len(self.filters) > 0:
            self.filteredUtteranceIds.pop()
            return self.filters.pop()
        return None

    def clearFilters(self):
        self.filters = []
        self.filteredUtteranceIds = [self.getUtteranceIds()]
        
    def resetFilters(self):
        self.filteredUtteranceIds = [self.getUtteranceIds()]
        for filter in self.filters:
            newFilteredUtterances = [utterance[0] for utterance in self.tree if utterance[0] in self.filteredUtteranceIds[-1] and filter.utterancePassesFilter(utterance)]
            self.filteredUtteranceIds.append(newFilteredUtterances)


class AnnotationTreeFilter(object):

    (AND, OR)  = range(2)
    
    def __init__(self):
        self.filter = {
            "participant": "",
            "locale": "",
            "utterance": "",
            "word": "",
            "morpheme": "",
            "pos": "",
            "gloss": "",
            "translation": ""
        }
        self.resetMatchObject()
        self.inverted = False
        self.boolean_operation = self.AND
        self.contained_matches = False
        
    def resetMatchObject(self):
        self.matchobject = {
            "utterance" : {},
            "translation" : {},
            "word" : {}
        }
        
    def setParticipantFilter(self, string):
        self.filter["participant"] = string
        
    def setLocaleFilter(self, string):
        self.filter["locale"] = string
        
    def setUtteranceFilter(self, string):
        self.filter["utterance"] = string
        
    def setWordFilter(self, string):
        self.filter["word"] = string
        
    def setMorphemeFilter(self, string):
        self.filter["morpheme"] = string
        
    def setPosFilter(self, string):
        self.filter["pos"] = string
        
    def setGlossFilter(self, string):
        self.filter["gloss"] = string
        
    def setTranslationFilter(self, string):
        self.filter["translation"] = string
        
    def setInvertedFilter(self, inverted):
        self.inverted = inverted
        
    def setContainedMatches(self, contained_matches):
        self.contained_matches = contained_matches

    def setBooleanOperation(self, type):
        self.boolean_operation = type
        
    def utterancePassesFilter(self, ilElement):
        utteranceMatch = False
        translationMatch = False
        wordMatch = False
        morphemeMatch = False
        glossMatch = False

        # is there a filter defined?
        if self.filter["utterance"] == "" and self.filter["translation"] == "" and self.filter["word"] == "" and self.filter["morpheme"] == "" and self.filter["gloss"] == "":
            return True
        
        # filter by utterance
        if self.filter["utterance"] != "":
            match = regex.search(self.filter["utterance"], ilElement[1])
            if match:
                self.matchobject["utterance"][ilElement[0]] = [ [m.start(), m.end()] for m in regex.finditer(self.filter["utterance"], ilElement[1]) ]
                utteranceMatch = True
        elif self.boolean_operation == self.AND:
            utteranceMatch = True

        # filter by translation
        if self.filter["translation"] != "":
            for translation in ilElement[3]:
                match = regex.search(self.filter["translation"], translation[1])
                if match:
                    self.matchobject["translation"][translation[0]] = [ [m.start(), m.end()] for m in regex.finditer(self.filter["translation"], translation[1]) ]
                    translationMatch = True
        elif self.boolean_operation == self.AND:
            translationMatch = True
                
        # filter by word
        for word in ilElement[2]:
            if self.filter["word"] != "":
                match =  regex.search(self.filter["word"], word[1])
                if match:
                    self.matchobject["word"][word[0]] = True
                    wordMatch = True
                    
            elif self.boolean_operation == self.AND:
                wordMatch = True
            
            # filter by morpheme
            if not self.contained_matches or wordMatch:
                for morpheme in word[2]:
                    if self.filter["morpheme"] != "":
                        match = regex.search(self.filter["morpheme"], morpheme[1])
                        if match:
                            self.matchobject["word"][word[0]] = True   
                            morphemeMatch = True
                    elif self.boolean_operation == self.AND:
                        morphemeMatch = True
                            
                    # filter by gloss
                    if not self.contained_matches or morphemeMatch:
                        if self.filter["gloss"] != "":
                            for gloss in morpheme[2]:
                                match = regex.search(self.filter["gloss"], gloss[1])
                                if match:
                                    self.matchobject["word"][word[0]] = True
                                    glossMatch = True
                        elif self.boolean_operation == self.AND:
                            glossMatch = True

        ret = False
        if self.boolean_operation == self.AND:
            if utteranceMatch and translationMatch and wordMatch and morphemeMatch and glossMatch:
                ret = True
        elif self.boolean_operation == self.OR:
            if utteranceMatch or translationMatch or wordMatch or morphemeMatch or glossMatch:
                ret = True
                
        if self.inverted:
            ret = not ret

        return ret
