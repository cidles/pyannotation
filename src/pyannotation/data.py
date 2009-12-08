# -*- coding: utf-8 -*-
# (C) 2009 copyright by Peter Bouda
"""This module contains the classes to access annotated data in
various formats.

The parsing is done by Builder classes for each file type, i.e.
Elan's .eaf files, Kura's .xml file, Toolbox's .txt files etc.
"""

__author__ =  'Peter Bouda'
__version__=  '0.2.0'

import os, glob
import re
import pyannotation.elan.data, pyannotation.kura.data, pyannotation.toolbox.data

(EAF, KURA, TOOLBOX) = range(3)

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

    def parse(self):
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
        ilElement = [ "", word, [] ]
        arrIl = re.split(self.MORPHEME_BOUNDARY_PARSE, il)
        arrGloss = re.split(self.MORPHEME_BOUNDARY_PARSE, gloss)
        for i in range(len(arrIl)):
            g = ""
            if i < len(arrGloss):
                g = arrGloss[i]
            arrG = re.split(self.GLOSS_BOUNDARY_PARSE, g)
            arrG2 = []
            for g2 in arrG:
                arrG2.append([ "", g2])
            ilElement[2].append([ "", arrIl[i], arrG2 ])
        return ilElement

class AnnotationTree(object):

    def __init__(self, builder, morphemeSep="-", glossSep=":"):
        self.tree = []
        self.builder = builder
        self.MORPHEME_BOUNDARY_BUILD = morphemeSep
        self.GLOSS_BOUNDARY_BUILD = glossSep

    def getTree(self):
        return self.tree

    def parse(self):
        self.tree = self.builder.parse()

    def getNextAnnotationId(self):
        return self.builder.getNextAnnotationId()

    def addTier(self, *args):
        return self.builder.addTier(*args)

    def getUtteranceIds(self):
        return [utterance[0] for utterance in self.tree]

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
            for translation in utterance[3]:
                if translation[0] == translationId:
                    return translation[1]
        return ''

    def newTranslationForUtteranceId(self, utteranceId, strTranslation):
        translationId = None
        for utterance in self.tree:
            if utterance[0] == utteranceId:
                translationId = "a%i" % self.getNextAnnotationId()
                utterance[3] = [ [ translationId, strTranslation ] ]
        return translationId

    def setTranslation(self, translationId, strTranslation):
        for utterance in self.tree:
            for translation in utterance[3]:
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
                return utterance[3]
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
                for t in utterance[3]:
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

    def getAsEafXml(self, tierUtterances, tierWords, tierMorphemes, tierGlosses, tierTranslations):
        return self.builder.getAsEafXml(self.tree, tierUtterances, tierWords, tierMorphemes, tierGlosses, tierTranslations)

######################## Corpus Readers

class CorpusReader(object):
    """
    The base class for all Elan corpus readers. It provides
    access to all tiers that contain utterances and words.
    """
    def __init__(self, root, files, locale = None, participant = None, utterancetierType = None, wordtierType = None):
        self.root = root
        self.files = files
        self.locale = locale
        self.participant = participant
        self.eaftrees = []
        for infile in glob.glob( os.path.join(root, files) ):
        #for infile in files:
            eaftree = EafTree(infile)
            if utterancetierType != None:
                eaftree.setUtterancetierType(utterancetierType)
            if wordtierType != None:
                eaftree.setWordtierType(wordtierType)
            eaftree.parse()
            self.eaftrees.append([infile, eaftree.getTree()])

    def addFile(self, filepath):
        pass

    def words(self):
        """
        Returns a list of words from the corpus files.
        """
        words = []
        for [infile, tree] in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                for word in utterance[2]:
                    if len(word) > 0:
                        words.append(word[1].encode('utf-8'))
        return words

    def sents(self):
        """
        Returns a list of sentences, which are lists of words from the
        corpus files.
        """
        sents = []
        for tree in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        words.append(word[1].encode('utf-8'))
                if len(words) > 0:
                    sents.append(words)
        return sents

    def sentsWithTranslations(self):
        """
        Returns a list of (list of words, translation) tuples from the
        corpus files.
        """
        sents = []
        for tree in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        words.append(word[1].encode('utf-8'))
                if len(words) > 0:
                    sents.append((words, utterance[3]))
        return sents

class PosCorpusReader(CorpusReader):
    """
    The class EafPosCorpusReader implements a part of the corpus reader API
    described in the Natual Language Toolkit (NLTK). The class reads in all
    the .eaf files (from the linguistics annotation software called Elan)
    in a given directory and makes this data accessible through
    several functions. The data contains "tags", which are annotations
    in "part of speech" tiers in Elan.
    The .eaf files must at least contain a tier with words.
    Access to the data is normally read-only.
    """
    
    def __init__(self, root, files = "*.eaf", locale = None, participant = None, utterancetierType = None, wordtierType = None, postierType = None):
        """
        root: is the directory where your .eaf files are stored. Only the
            files in the given directory are read, there is no recursive
            reading right now. This parameter is obligatory.
        files: a regular expression for the filenames to read. The
            default value is "*.eaf"
        locale: restricts the corpus data to tiers with the given locale.
        participant: restricts the corpus data to tiers with the given
            particiapant.
        utterancetierType: the type of the tier you gave to your
            "utterances" in Elan. The EafTrees have several default values
            for this tier type: [ "utterance", "utterances", "Äußerung",
            "Äußerungen" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        wordtierType: the type of the tier you gave to your
            "words" in Elan. The EafTrees have several default values
            for this tier type: [ "words", "word", "Wort", "Worte",
            "Wörter" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        postierType: the type of the tier you gave to your
            "parts of speeches" in Elan. The EafTrees have several default
            values for this tier type: [ "part of speech", "parts of speech",
            "Wortart", "Wortarten" ]. If you used a different tier type in
            Elan you can specify it as a parameter here. The parameter
            may either be a string or a list of strings.
        """
        self.root = root
        self.files = files
        self.locale = locale
        self.participant = participant
        self.eaftrees = []
        for infile in glob.glob( os.path.join(root, files) ):
            eaftree = EafPosTree(infile)
            if utterancetierType != None:
                eaftree.setUtterancetierType(utterancetierType)
            if wordtierType != None:
                eaftree.setWordtierType(wordtierType)
            if postierType != None:
                eaftree.setPostierType(postierType)
            eaftree.parse()
            self.eaftrees.append(eaftree.getTree())

    def taggedWords(self):
        """
        Returns a list of (word, tag) tuples. Each tag is a list of
        parts of speech.
        """
        words = []
        for tree in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for (id, pos) in word[2]:
                            tag.append(pos)
                        words.append((word[1].encode('utf-8'), tag))
        return words

    def taggedSents(self):
        """
        Returns a list of (list of (word, tag) tuples). Each tag is a list
        of parts of speech.
        """
        sents = []
        for tree in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for id, pos in word[2]:
                            tag.append(pos)
                        words.append((word[1].encode('utf-8'), tag))
                if len(words) > 0:
                    sents.append(words)
        return sents

    def taggedSentsWithTranslations(self):
        """
        Returns a list of (sentence, translation) tuples. Sentences
        are lists of (word, tag) tuples. Each tag is a list of
        parts of speech.
        """
        sents = []
        for tree in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for id, pos in word[2]:
                            tag.append(pos)
                        words.append((word[1].encode('utf-8'), tag))
                if len(words) > 0:
                    sents.append((words, utterance[3]))
        return sents

class GlossCorpusReader(CorpusReader):
    """The class EafGlossCorpusReader implements a part of the corpus reader API
    described in the Natual Language Toolkit (NLTK). The class reads in all
    the .eaf files (from the linguistics annotation software called Elan)
    in a given directory and makes this data accessible through
    several functions. The data contains "tags", which are annotations
    in "morpheme" and "gloss" tiers in Elan.
    The .eaf files must at least contain a tier with words.
    Access to the data is normally read-only.
    """

    def __init__(self, locale = None, participant = None, utterancetierTypes = None, wordtierTypes = None,  morphemetierTypes = None, glosstierTypes = None, translationtierTypes = None):
        """
        root: is the directory where your .eaf files are stored. Only the
            files in the given directory are read, there is no recursive
            reading right now. This parameter is obligatory.
        files: a regular expression for the filenames to read. The
            default value is "*.eaf"
        locale: restricts the corpus data to tiers with the given locale.
        participant: restricts the corpus data to tiers with the given
            particiapant.
        utterancetierType: the type of the tier you gave to your
            "utterances" in Elan. The EafTrees have several default values
            for this tier type: [ "utterance", "utterances", "Äußerung",
            "Äußerungen" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        wordtierType: the type of the tier you gave to your
            "words" in Elan. The EafTrees have several default values
            for this tier type: [ "words", "word", "Wort", "Worte",
            "Wörter" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        morphemetierType: the type of the tier you gave to your
            "morphemes" in Elan. The EafTrees have several default values
            for this tier type: [ "morpheme", "morphemes",  "Morphem",
            "Morpheme" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        glosstierType: the type of the tier you gave to your
            "glosses" in Elan. The EafTrees have several default values
            for this tier type: [ "glosses", "gloss", "Glossen", "Gloss",
            "Glosse" ]. If you used a different tier type in Elan you
            can specify it as a parameter here. The parameter may either
            be a string or a list of strings.
        """
        self.locale = locale
        self.participant = participant
        self.utterancetierTypes = utterancetierTypes
        self.wordtierTypes = wordtierTypes
        self.morphemetierTypes = utterancetierTypes
        self.glosstierTypes = utterancetierTypes
        self.translationtierTypes = translationtierTypes
        self.eaftrees = []

    def addFile(self, filepath, filetype):
        annotationFileObject = None
        if filetype == EAF:
            annotationFileObject = pyannotation.elan.data.EafAnnotationFileObject(filepath)
        elif filetype == TOOLBOX:
            annotationFileObject = pyannotation.toolbox.data.ToolboxAnnotationFileObject(filepath)
        if annotationFileObject != None:
            annotationTierHandler = self.annotationFileObject.createTierHandler()
            annotationParser = self.annotationFileObject.createParser()
            annotationTree = AnnotationTree(self.annotationParser)
            # Setting the tier types for the parse
            if self.utterancetierTypes != None:
                annotationTierHandler.setUtterancetierType(self.utterancetierTypes)
            if self.wordtierTypes != None:
                annotationTierHandler.setWordtierType(self.wordtierTypes)
            if self.morphemetierTypes != None:
                annotationTierHandler.setMorphemetierType(self.morphemetierTypes)
            if self.glosstierTypes != None:
                annotationTierHandler.setGlosstierType(self.glosstierTypes)
            if self.translationtierTypes != None:
                annotationTierHandler.setTranslationtierType(translationtierTypes)
            annotationTree.parse()
            self.eaftrees.append([filepath, annotationTree])

    def morphemes(self):
        """
        Returns a list of morphemes from the corpus files.
        """
        morphemes = []
        for (infile, tree) in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                for word in utterance[2]:
                    if len(word) > 0:
                        for morpheme in word[2]:
                            if morpheme[1] != '':
                                morphemes.append(morpheme[1].encode('utf-8'))
        return morphemes

    def taggedMorphemes(self):
        """
        Returns a list of (morpheme, list of glosses) tuples.
        """
        morphemes = []
        for (infile, tree) in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                for word in utterance[2]:
                    if len(word) > 0:
                        for morpheme in word[2]:
                            if morpheme[1] != '':
                                glosses = []
                                for gloss in morpheme[2]:
                                    if gloss[1] != '':
                                        glosses.append(gloss[1].encode('utf-8'))
                                morphemes.append((morpheme[1].encode('utf-8'), glosses))
        return morphemes
        
    def taggedWords(self):
        """
        Returns a list of (word, tag) tuples. Each tag is a list of
        (morpheme, list of glosses) tuples.
        """
        words = []
        for tree in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for morpheme in word[2]:
                            if morpheme[1] != '':
                                glosses = []
                                for gloss in morpheme[2]:
                                    if gloss[1] != '':
                                        glosses.append(gloss[1].encode('utf-8'))
                                tag.append((morpheme[1].encode('utf-8'), glosses))
                        words.append((word[1].encode('utf-8'), tag))
        return words

    def taggedSents(self):
        """
        Returns a list of (list of (word, tag) tuples). Each tag is
        a list of (morpheme, list of glosses) tuples.
        """
        sents = []
        for (infile, tree) in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for morpheme in word[2]:
                            if morpheme[1] != '':
                                glosses = []
                                for gloss in morpheme[2]:
                                    if gloss[1] != '':
                                        glosses.append(gloss[1].encode('utf-8'))
                                tag.append((morpheme[1].encode('utf-8'), glosses))
                        words.append((word[1].encode('utf-8'), tag))
                if len(words) > 0:
                    sents.append(words)
        return sents

    def taggedSentsWithTranslations(self):
        """
        Returns a list of (sentence, translation) tuples. Sentences
        are lists of (word, tag) tuples. Each tag is a list of
        (morpheme, list of glosses) tuples.
        """
        sents = []
        for tree in self.eaftrees:
            for utterance in tree:
                if self.locale != None and utterance[4] != self.locale:
                    continue
                if self.participant != None and utterance[5] != self.participant:
                    continue
                words = []
                for word in utterance[2]:
                    if len(word) > 0:
                        tag = []
                        for morpheme in word[2]:
                            if morpheme[1] != '':
                                glosses = []
                                for gloss in morpheme[2]:
                                    if gloss[1] != '':
                                        glosses.append(gloss[1].encode('utf-8'))
                                tag.append((morpheme[1].encode('utf-8'), glosses))
                        words.append((word[1].encode('utf-8'), tag))
                if len(words) > 0:
                    sents.append((words, utterance[3]))
        return sents


