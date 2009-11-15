# -*- coding: utf-8 -*-
# (C) 2009 copyright by Peter Bouda
"""This module contains classes to access Elan data.

The class Eaf is a low level API to .eaf files.

EafGlossTree, EafPosTree, etc. are the classes to access the data via 
tree, which also contains the original .eaf IDs. Because of this
EafTrees are read-/writeable. 

EafGlossCorpusReader, EafPosCorpusReader, etc. implement a part of the
corpus reader API described in the Natural Language Toolkit (NLTK):
http://nltk.googlecode.com/svn/trunk/doc/howto/corpus.html
"""

__author__ =  'Peter Bouda'
__version__=  '0.2.0'

import os, glob
import re
import pyannotation.data
from copy import deepcopy
from lxml import etree as ET
from lxml.etree import Element

class EafCorpusReader(object):
    """
    The base class for all Elan corpus readers. It provides
    access to all tiers that contain utterances and words.
    """
    def __init__(self, root, files = "*.eaf", locale = None, participant = None, utterancetierType = None, wordtierType = None):
        self.root = root
        self.files = files
        self.locale = locale
        self.participant = participant
        self.eaftrees = []
        for infile in glob.glob( os.path.join(root, files) ):
            eaftree = EafTree(infile)
            if utterancetierType != None:
                eaftree.setUtterancetierType(utterancetierType)
            if wordtierType != None:
                eaftree.setWordtierType(wordtierType)
            eaftree.parse()
            self.eaftrees.append(eaftree.getTree())

    def words(self):
        """
        Returns a list of words from the corpus files.
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

    def sents_with_translations(self):
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

class EafPosCorpusReader(EafCorpusReader):
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

    def tagged_words(self):
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

    def tagged_sents(self):
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

    def tagged_sents_with_translations(self):
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

class EafGlossCorpusReader(EafCorpusReader):
    """The class EafGlossCorpusReader implements a part of the corpus reader API
    described in the Natual Language Toolkit (NLTK). The class reads in all
    the .eaf files (from the linguistics annotation software called Elan)
    in a given directory and makes this data accessible through
    several functions. The data contains "tags", which are annotations
    in "morpheme" and "gloss" tiers in Elan.
    The .eaf files must at least contain a tier with words.
    Access to the data is normally read-only.
    """

    def __init__(self, root, files = "*.eaf", locale = None, participant = None, utterancetierType = None, wordtierType = None,  morphemetierType = None, glosstierType = None):
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
        self.root = root
        self.files = files
        self.locale = locale
        self.participant = participant
        self.eaftrees = []
        for infile in glob.glob( os.path.join(root, files) ):
            eaftree = EafGlossTree(infile)
            if utterancetierType != None:
                eaftree.setUtterancetierType(utterancetierType)
            if wordtierType != None:
                eaftree.setWordtierType(wordtierType)
            if morphemetierType != None:
                eaftree.setMorphemetierType(morphemetierType)
            if glosstierType != None:
                eaftree.setGlosstierType(glosstierType)
            eaftree.parse()
            self.eaftrees.append(eaftree.getTree())

    def morphemes(self):
        """
        Returns a list of morphemes from the corpus files.
        """
        morphemes = []
        for tree in self.eaftrees:
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

    def tagged_morphemes(self):
        """
        Returns a list of (morpheme, list of glosses) tuples.
        """
        morphemes = []
        for tree in self.eaftrees:
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
        
    def tagged_words(self):
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

    def tagged_sents(self):
        """
        Returns a list of (list of (word, tag) tuples). Each tag is
        a list of (morpheme, list of glosses) tuples.
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
                    sents.append(words)
        return sents

    def tagged_sents_with_translations(self):
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

############################################# Builders

class EafAnnotationFileObject(pyannotation.data.AnnotationFileObject):

    def __init__(self, filepath):
        pyannotation.data.AnnotationFileObject.__init__(self, filepath)
        self.setFilepath(filepath)

    def getFile(self):
        return self.file

    def getFilepath(self):
        return self.filepath

    def setFilepath(self, filepath):
        self.filepath = filepath
        self.file = Eaf(self.filepath)

class EafAnnotationFileTiers(pyannotation.data.AnnotationFileTiers):

    def __init__(self, annotationFileObject):
        pyannotation.data.AnnotationFileTiers.__init__(self, annotationFileObject)
        self.eaf = annotationFileObject.getFile()
        self.UTTERANCETIER_TYPEREFS = [ "utterance", "utterances", "Äußerung", "Äußerungen" ]
        self.WORDTIER_TYPEREFS = [ "words", "word", "Wort", "Worte", "Wörter" ]
        self.MORPHEMETIER_TYPEREFS = [ "morpheme", "morphemes",  "Morphem", "Morpheme" ]
        self.GLOSSTIER_TYPEREFS = [ "glosses", "gloss", "Glossen", "Gloss", "Glosse" ]
        self.POSTIER_TYPEREFS = [ "part of speech", "parts of speech", "Wortart", "Wortarten" ]
        self.TRANSLATIONTIER_TYPEREFS = [ "translation", "translations", "Übersetzung",  "Übersetzungen" ]

    def setUtterancetierType(self, type):
        if isinstance(type, list):
            self.UTTERANCETIER_TYPEREFS = type
        else:
            self.UTTERANCETIER_TYPEREFS = [type]

    def setWordtierType(self, type):
        if isinstance(type, list):
            self.WORDTIER_TYPEREFS = type
        else:
            self.WORDTIER_TYPEREFS = [type]

    def setMorphemetierType(self, type):
        if isinstance(type, list):
            self.MORPHEMETIER_TYPEREFS = type
        else:
            self.MORPHEMETIER_TYPEREFS = [type]

    def setGlosstierType(self, type):
        if isinstance(type, list):
            self.GLOSSTIER_TYPEREFS = type
        else:
            self.GLOSSTIER_TYPEREFS = [type]

    def setPostierType(self, type):
        if isinstance(type, list):
            self.POSTIER_TYPEREFS = type
        else:
            self.POSTIER_TYPEREFS = [type]

    def setTranslationtierType(self, type):
        if isinstance(type, list):
            self.TRANSLATIONTIER_TYPEREFS = type
        else:
            self.TRANSLATIONTIER_TYPEREFS = [type]

    def getUtterancetierIds(self, parent = None):
        ret = []
        for type in self.UTTERANCETIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def getWordtierIds(self, parent = None):
        ret = []
        for type in self.WORDTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def getMorphemetierIds(self, parent = None):
        ret = []
        for type in self.MORPHEMETIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def getGlosstierIds(self, parent = None):
        ret = []
        for type in self.GLOSSTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def getPostierIds(self, parent = None):
        ret = []
        for type in self.POSTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def getTranslationtierIds(self, parent = None):
        ret = []
        for type in self.TRANSLATIONTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def addTier(self, tierId, tierType, tierTypeConstraint, parentTier, tierDefaultLocale, tierParticipant):
        self.eaf.addTier(tierId, tierType, parentTier, tierDefaultLocale, tierParticipant)
        if not self.eaf.hasLinguisticType(tierType):
            self.eaf.addLinguisticType(tierType, tierTypeConstraint)

    def getLocaleForTier(self, idTier):
        return self.eaf.getLocaleForTier(idTier)

    def getParticipantForTier(self, idTier):
        return self.eaf.getParticipantForTier(idTier)

class EafAnnotationFileParser(pyannotation.data.AnnotationFileParser):

    def __init__(self, annotationFileObject, annotationFileTiers):
        pyannotation.data.AnnotationFileParser.__init__(self, annotationFileObject, annotationFileTiers)
        self.tierBuilder = annotationFileTiers
        self.eaf = annotationFileObject.getFile()
        self.lastUsedAnnotationId = self.eaf.getLastUsedAnnotationId()

    def setFile(self, file):
        self.file = file

    def getNextAnnotationId(self):
        self.lastUsedAnnotationId = self.lastUsedAnnotationId + 1
        return self.lastUsedAnnotationId

    def parse(self):
        tree = []
        self.utteranceTierIds = self.tierBuilder.getUtterancetierIds()
        if self.utteranceTierIds != []:
            for uTier in self.utteranceTierIds:
                utterancesIds = self.eaf.getAlignableAnnotationIdsForTier(uTier)
                for uId in utterancesIds:
                    utterance = self.eaf.getAnnotationValueForAnnotation(uTier, uId)
                    translations = []
                    ilElements = []
                    locale = self.eaf.getLocaleForTier(uTier)
                    participant = self.eaf.getParticipantForTier(uTier)
                    translationTierIds = self.tierBuilder.getTranslationtierIds(uTier)
                    for tTier in translationTierIds:
                        transIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(uId, uTier, tTier)
                        for transId in transIds:
                            trans = self.eaf.getAnnotationValueForAnnotation(tTier, transId)
                            if trans != '':
                                translations.append([transId, trans])
                    wordTierIds = self.tierBuilder.getWordtierIds(uTier)
                    for wTier in wordTierIds:
                        wordsIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(uId, uTier, wTier)
                        for wordId in wordsIds:
                            ilElements.append(self.getIlElementForWordId(wordId, wTier))
                        if len(ilElements) == 0:
                            ilElements = [ ['', '',  [ ['', '',  [ ['',  ''] ] ] ] ] ]
                    tree.append([ uId,  utterance,  ilElements, translations, locale, participant, uTier ])
        else: # if self.utterancesTiers != []
            for wTier in self.getWordtierIds():
                translations = []
                locale = self.eaf.getLocaleForTier(wTier)
                participant = self.eaf.getParticipantForTier(wTier)
                wordsIds = self.eaf.getAnnotationIdsForTier(wTier)
                for wordId in wordsIds:
                    ilElements.append(self.getIlElementForWordId(wordId, wTier))   
                if len(ilElements) == 0:
                    ilElements = [ ['', '',  [ ['', '',  [ ['',  ''] ] ] ] ] ]
                tree.append([ '',  '',  ilElements, translations, locale, participant, '' ])
        return tree

    def getIlElementForWordId(self, id, wTier):
        ilElement = []
        word = self.eaf.getAnnotationValueForAnnotation(wTier, id)
        ilElement.append(id)
        ilElement.append(word)
        morphElements = []
        morphemeTierIds = self.tierBuilder.getMorphemetierIds(wTier)
        for mTier in morphemeTierIds:
            morphIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(id, wTier, mTier)
            for morphId in morphIds:
                morphElements.append(self.getFuncElementForMorphemeId(morphId, mTier))
        if len(morphElements) == 0:
            ilElement.append([[ '',  '',  [ ['',  ''] ]]])
        else:
            ilElement.append(morphElements)
        return ilElement

    def getFuncElementForMorphemeId(self, morphId, mTier):
        ilElement = []
        morpheme = self.eaf.getAnnotationValueForAnnotation(mTier, morphId)
        morpheme = re.sub(r'^-', '', morpheme)
        morpheme = re.sub(r'-$', '', morpheme)
        ilElement.append(morphId)
        ilElement.append(morpheme)
        funcElements = []
        glossTierIds = self.tierBuilder.getGlosstierIds(mTier)
        for gTier in glossTierIds:
            funcIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(morphId, mTier, gTier)
            for funcId in funcIds:
                function = self.eaf.getAnnotationValueForAnnotation(gTier, funcId)
                function = re.sub(r'^-', '', function)
                morpheme = re.sub(r'-$', '', function)
                e = [funcId, function]
                funcElements.append(e)
        if len(funcElements) == 0:
            ilElement.append([['',  '']])
        else:
            ilElement.append(funcElements)
        return ilElement

    def removeAnnotationWithId(self, idAnnotation):
        self.eaf.removeAnnotationWithId(idAnnotation)

    def removeAnnotationsWithRef(self, idRefAnn):
        self.eaf.removeAnnotationsWithRef(idRefAnn)

    def updatePrevAnnotationForAnnotation(self, idAnnotation, idPrevAnn = None):
        self.eaf.updatePrevAnnotationForAnnotation(idAnnotation, idPrevAnn)

    def getAsEafXml(self, tree, tierUtterances, tierWords, tierMorphemes, tierGlosses, tierTranslations):
        # make local copy of eaf
        eaf2 = deepcopy(self.eaf)
        utterances = [[u[0], u[1]] for u in tree if u[6] == tierUtterances]
        translations = [[u[3], u[0]] for u in tree if u[6] == tierUtterances and len(u[3])>=1]
        words = [[w[0], w[1]] for u in tree if u[6] == tierUtterances for w in u[2]]
        ilelements = [u[2] for u in tree if u[6] == tierUtterances]
        # save utterances
        for u in utterances:
            eaf2.setAnnotationValueForAnnotation(tierUtterances, u[0], u[1])
        # save translations
        for t1 in translations:
            for t in t1[0]:
                if t[1] != "":
                    if not eaf2.setAnnotationValueForAnnotation(tierTranslations, t[0], t[1]):
                        eaf2.appendRefAnnotationToTier(tierTranslations, t[0], t[1], t1[1])
        # save words
        for w in words:
            eaf2.setAnnotationValueForAnnotation(tierWords, w[0], w[1])
        #save morphemes
        eaf2.removeAllAnnotationsFromTier(tierMorphemes)
        eaf2.removeAllAnnotationsFromTier(tierGlosses)
        for i in ilelements:
            for w in i:
                if len(w) >= 3:
                    refAnnMorph = w[0]
                    prevAnnMorph = None
                    for m in w[2]:
                        if len(m) >= 3:
                            if m[0] != "" and m[1] != "" and refAnnMorph != "":
                                eaf2.appendRefAnnotationToTier(tierMorphemes, m[0], m[1], refAnnMorph, prevAnnMorph)
                            prevAnnMorph = m[0]
                            refAnnGloss = m[0]
                            prevAnnGloss = None
                            for g in m[2]:
                                if len(g) >= 2:
                                    if g[0] != "" and g[1] != "" and refAnnGloss != "":
                                        eaf2.appendRefAnnotationToTier(tierGlosses, g[0], g[1], refAnnGloss, prevAnnGloss)
                                    prevAnnGloss = g[0]
        return eaf2.tostring()


################################ Trees; only use Builders, delete Trees after conversion to Builders

class EafBaseTree(object):

    def __init__(self, file):
        self.tree = []
        self.file = file
        self.eaf = Eaf(self.file)
        self.lastUsedAnnotationId = self.eaf.getLastUsedAnnotationId()
        self.UTTERANCETIER_TYPEREFS = [ "utterance", "utterances", "Äußerung", "Äußerungen" ]
        self.WORDTIER_TYPEREFS = [ "words", "word", "Wort", "Worte", "Wörter" ]
        self.MORPHEMETIER_TYPEREFS = [ "morpheme", "morphemes",  "Morphem", "Morpheme" ]
        self.GLOSSTIER_TYPEREFS = [ "glosses", "gloss", "Glossen", "Gloss", "Glosse" ]
        self.POSTIER_TYPEREFS = [ "part of speech", "parts of speech", "Wortart", "Wortarten" ]
        self.TRANSLATIONTIER_TYPEREFS = [ "translation", "translations", "Übersetzung",  "Übersetzungen" ]
        self.MORPHEME_BOUNDARY = "-"
        self.GLOSS_BOUNDARY = ":"

    def getTree(self):
        return self.tree

    def parse(self):
        pass

    def getNextAnnotationId(self):
        self.lastUsedAnnotationId = self.lastUsedAnnotationId + 1
        return self.lastUsedAnnotationId

    def setUtterancetierType(self, type):
        if isinstance(type, list):
            self.UTTERANCETIER_TYPEREFS = type
        else:
            self.UTTERANCETIER_TYPEREFS = [type]

    def setWordtierType(self, type):
        if isinstance(type, list):
            self.WORDTIER_TYPEREFS = type
        else:
            self.WORDTIER_TYPEREFS = [type]

    def setMorphemetierType(self, type):
        if isinstance(type, list):
            self.MORPHEMETIER_TYPEREFS = type
        else:
            self.MORPHEMETIER_TYPEREFS = [type]

    def setGlosstierType(self, type):
        if isinstance(type, list):
            self.GLOSSTIER_TYPEREFS = type
        else:
            self.GLOSSTIER_TYPEREFS = [type]

    def setPostierType(self, type):
        if isinstance(type, list):
            self.POSTIER_TYPEREFS = type
        else:
            self.POSTIER_TYPEREFS = [type]

    def setTranslationtierType(self, type):
        if isinstance(type, list):
            self.TRANSLATIONTIER_TYPEREFS = type
        else:
            self.TRANSLATIONTIER_TYPEREFS = [type]

    def getUtterancetierIds(self, parent = None):
        ret = []
        for type in self.UTTERANCETIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def getWordtierIds(self, parent = None):
        ret = []
        for type in self.WORDTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def getMorphemetierIds(self, parent = None):
        ret = []
        for type in self.MORPHEMETIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def getGlosstierIds(self, parent = None):
        ret = []
        for type in self.GLOSSTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def getPostierIds(self, parent = None):
        ret = []
        for type in self.POSTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def getTranslationtierIds(self, parent = None):
        ret = []
        for type in self.TRANSLATIONTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def addEafTier(self, tierId, tierType, tierTypeConstraint, parentTier, tierDefaultLocale, tierParticipant):
        self.eaf.addTier(tierId, tierType, parentTier, tierDefaultLocale, tierParticipant)
        if not self.eaf.hasLinguisticType(tierType):
            self.eaf.addLinguisticType(tierType, tierTypeConstraint)


class EafTree(EafBaseTree):
    
    def __init__(self, file):
        EafBaseTree.__init__(self, file)

    def parse(self):
        self.utteranceTierIds = self.getUtterancetierIds()
        if self.utteranceTierIds != []:
            for uTier in self.utteranceTierIds:
                utterancesIds = self.eaf.getAlignableAnnotationIdsForTier(uTier)
                for uId in utterancesIds:
                    utterance = self.eaf.getAnnotationValueForAnnotation(uTier, uId)
                    translations = []
                    ilElements = []
                    locale = self.eaf.getLocaleForTier(uTier)
                    participant = self.eaf.getParticipantForTier(uTier)
                    translationTierIds = self.getTranslationtierIds(uTier)
                    for tTier in translationTierIds:
                        transIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(uId, uTier, tTier)
                        for transId in transIds:
                            trans = self.eaf.getAnnotationValueForAnnotation(tTier, transId)
                            if trans != '':
                                translations.append([transId, trans])
                    wordTierIds = self.getWordtierIds(uTier)
                    for wTier in wordTierIds:
                        wordsIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(uId, uTier, wTier)
                        for wordId in wordsIds:
                            word = self.eaf.getAnnotationValueForAnnotation(wTier, wordId)
                            ilElements.append([wordId, word])   
                    self.tree.append([ uId,  utterance,  ilElements, translations, locale, participant, uTier ])
        else: # if self.utterancesTiers != []
            wordTierIds = self.getWordtierIds()
            for wTier in wordTierIds:
                translations = []
                locale = self.eaf.getLocaleForTier(uTier)
                participant = self.eaf.getParticipantForTier(uTier)
                wordsIds = self.eaf.getAnnotationIdsForTier(wTier)
                for wordId in wordsIds:
                    word = self.eaf.getAnnotationValueForAnnotation(wTier, wordId)
                    ilElements.append([wordId, word])   
                self.tree.append([ '',  '',  ilElements, translations, locale, participant, '' ])

    def getUtteranceIdsInTier(self, tierId):
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

#    def getIlElementsForUtterance(self, utteranceId):
#        for utterance in self.tree:
#            if utterance[0] == utteranceId:
#                return utterance[2]
#        return ''
        
    def getTranslationsForUtterance(self, utteranceId):
        for utterance in self.tree:
            if utterance[0] == utteranceId:
                return utterance[3]
        return ''

################################### Gloss Tree

class EafGlossTree(EafTree):
    def __init__(self, file):
        EafTree.__init__(self, file)

    def parse(self):
        self.utteranceTierIds = self.getUtterancetierIds()
        if self.utteranceTierIds != []:
            for uTier in self.utteranceTierIds:
                utterancesIds = self.eaf.getAlignableAnnotationIdsForTier(uTier)
                for uId in utterancesIds:
                    utterance = self.eaf.getAnnotationValueForAnnotation(uTier, uId)
                    translations = []
                    ilElements = []
                    locale = self.eaf.getLocaleForTier(uTier)
                    participant = self.eaf.getParticipantForTier(uTier)
                    translationTierIds = self.getTranslationtierIds(uTier)
                    for tTier in translationTierIds:
                        transIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(uId, uTier, tTier)
                        for transId in transIds:
                            trans = self.eaf.getAnnotationValueForAnnotation(tTier, transId)
                            if trans != '':
                                translations.append([transId, trans])
                    wordTierIds = self.getWordtierIds(uTier)
                    for wTier in wordTierIds:
                        wordsIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(uId, uTier, wTier)
                        for wordId in wordsIds:
                            ilElements.append(self.getIlElementForWordId(wordId, wTier))
                        if len(ilElements) == 0:
                            ilElements = [ ['', '',  [ ['', '',  [ ['',  ''] ] ] ] ] ]
                    self.tree.append([ uId,  utterance,  ilElements, translations, locale, participant, uTier ])
        else: # if self.utterancesTiers != []
            for wTier in self.getWordtierIds():
                translations = []
                locale = self.eaf.getLocaleForTier(wTier)
                participant = self.eaf.getParticipantForTier(wTier)
                wordsIds = self.eaf.getAnnotationIdsForTier(wTier)
                for wordId in wordsIds:
                    ilElements.append(self.getIlElementForWordId(wordId, wTier))   
                if len(ilElements) == 0:
                    ilElements = [ ['', '',  [ ['', '',  [ ['',  ''] ] ] ] ] ]
                self.tree.append([ '',  '',  ilElements, translations, locale, participant, '' ])
 
    def getIlElementForWordId(self, id, wTier):
        ilElement = []
        word = self.eaf.getAnnotationValueForAnnotation(wTier, id)
        ilElement.append(id)
        ilElement.append(word)
        morphElements = []
        morphemeTierIds = self.getMorphemetierIds(wTier)
        for mTier in morphemeTierIds:
            morphIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(id, wTier, mTier)
            for morphId in morphIds:
                morphElements.append(self.getFuncElementForMorphemeId(morphId, mTier))
        if len(morphElements) == 0:
            ilElement.append([[ '',  '',  [ ['',  ''] ]]])
        else:
            ilElement.append(morphElements)
        return ilElement

    def getFuncElementForMorphemeId(self, morphId, mTier):
        ilElement = []
        morpheme = self.eaf.getAnnotationValueForAnnotation(mTier, morphId)
        morpheme = re.sub(r'^-', '', morpheme)
        morpheme = re.sub(r'-$', '', morpheme)
        ilElement.append(morphId)
        ilElement.append(morpheme)
        funcElements = []
        glossTierIds = self.getGlosstierIds(mTier)
        for gTier in glossTierIds:
            funcIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(morphId, mTier, gTier)
            for funcId in funcIds:
                function = self.eaf.getAnnotationValueForAnnotation(gTier, funcId)
                function = re.sub(r'^-', '', function)
                morpheme = re.sub(r'-$', '', function)
                e = [funcId, function]
                funcElements.append(e)
        if len(funcElements) == 0:
            ilElement.append([['',  '']])
        else:
            ilElement.append(funcElements)
        return ilElement

    def getMorphemeStringForWord(self, wordId):
        m = [morpheme[1] for u in self.tree for w in u[2] if w[0] == wordId for morpheme in w[2]]
        return self.MORPHEME_BOUNDARY.join(m)

    def getGlossStringForWord(self, wordId):
        l = []
        for u in self.tree:
            for w in u[2]:
                if w[0] == wordId:
                    for m in w[2]:
                        f = [gloss[1] for gloss in m[2]]
                        l.append(self.GLOSS_BOUNDARY.join(f))
        return self.MORPHEME_BOUNDARY.join(l)

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
        arrIl = il.split(self.MORPHEME_BOUNDARY)
        arrGloss = gloss.split(self.MORPHEME_BOUNDARY)
        for i in range(len(arrIl)):
            g = ""
            if i < len(arrGloss):
                g = arrGloss[i]
            arrG = g.split(self.GLOSS_BOUNDARY)
            arrG2 = []
            for g2 in arrG:
                arrG2.append([ "", g2])
            ilElement[2].append([ "", arrIl[i], arrG2 ])
        return ilElement

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
                            self.eaf.removeAnnotationWithId(g[0])
                            self.eaf.removeAnnotationsWithRef(g[0])
                        self.eaf.removeAnnotationWithId(m[0])
                        self.eaf.removeAnnotationsWithRef(m[0])
                    self.eaf.removeAnnotationWithId(w[0])
                    self.eaf.removeAnnotationsWithRef(w[0])
                for t in utterance[3]:
                    self.eaf.removeAnnotationWithId(t[0])                    
                    self.eaf.removeAnnotationsWithRef(t[0])
                self.eaf.removeAnnotationWithId(utteranceId)
                self.eaf.removeAnnotationsWithRef(utteranceId)
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
                            self.eaf.removeAnnotationWithId(g[0])
                            self.eaf.removeAnnotationsWithRef(g[0])
                        self.eaf.removeAnnotationWithId(m[0])
                        self.eaf.removeAnnotationsWithRef(m[0])
                    self.eaf.removeAnnotationWithId(wordId)
                    # link next word to prev, if those are there
                    if i > 0 and len(utterance[2]) > (i+1):
                        prevwordId = utterance[2][i-1][0]
                        nextwordId = utterance[2][i+1][0]
                        self.eaf.updatePrevAnnotationForAnnotation(nextwordId, prevwordId)
                    # remove link to this word if this is the first word and there is a second
                    if i == 0 and len(utterance[2]) > 1:
                        nextwordId = utterance[2][i+1][0]
                        self.eaf.updatePrevAnnotationForAnnotation(nextwordId)
                    self.eaf.removeAnnotationsWithRef(wordId)
                    utterance[2].pop(i)
                    return True
                i = i + 1
        return False

    def getAsEafXml(self, tierUtterances, tierWords, tierMorphemes, tierGlosses, tierTranslations):
        # make local copy of eaf
        eaf2 = deepcopy(self.eaf)
        utterances = [[u[0], u[1]] for u in self.tree if u[6] == tierUtterances]
        translations = [[u[3], u[0]] for u in self.tree if u[6] == tierUtterances and len(u[3])>=1]
        words = [[w[0], w[1]] for u in self.tree if u[6] == tierUtterances for w in u[2]]
        ilelements = [u[2] for u in self.tree if u[6] == tierUtterances]
        # save utterances
        for u in utterances:
            eaf2.setAnnotationValueForAnnotation(tierUtterances, u[0], u[1])
        # save translations
        for t1 in translations:
            for t in t1[0]:
                if t[1] != "":
                    if not eaf2.setAnnotationValueForAnnotation(tierTranslations, t[0], t[1]):
                        eaf2.appendRefAnnotationToTier(tierTranslations, t[0], t[1], t1[1])
        # save words
        for w in words:
            eaf2.setAnnotationValueForAnnotation(tierWords, w[0], w[1])
        #save morphemes
        eaf2.removeAllAnnotationsFromTier(tierMorphemes)
        eaf2.removeAllAnnotationsFromTier(tierGlosses)
        for i in ilelements:
            for w in i:
                if len(w) >= 3:
                    refAnnMorph = w[0]
                    prevAnnMorph = None
                    for m in w[2]:
                        if len(m) >= 3:
                            if m[0] != "" and m[1] != "" and refAnnMorph != "":
                                eaf2.appendRefAnnotationToTier(tierMorphemes, m[0], m[1], refAnnMorph, prevAnnMorph)
                            prevAnnMorph = m[0]
                            refAnnGloss = m[0]
                            prevAnnGloss = None
                            for g in m[2]:
                                if len(g) >= 2:
                                    if g[0] != "" and g[1] != "" and refAnnGloss != "":
                                        eaf2.appendRefAnnotationToTier(tierGlosses, g[0], g[1], refAnnGloss, prevAnnGloss)
                                    prevAnnGloss = g[0]
        return eaf2.tostring()


############################### POS Tree

class EafPosTree(EafTree):

    def __init__(self, file):
        EafTree.__init__(self, file)

    def parse(self):
        eaf = Eaf(self.file)
        self.utteranceTiers = self.getUtterancetierIds(eaf)
        if self.utteranceTiers != []:
            for uTier in self.utteranceTiers:
                utterancesIds = eaf.getAlignableAnnotationIdsForTier(uTier)
                for uId in utterancesIds:
                    utterance = eaf.getAnnotationValueForAnnotation(uTier, uId)
                    translations = []
                    words = []
                    locale = eaf.getLocaleForTier(uTier)
                    participant = eaf.getParticipantForTier(uTier)
                    for tTier in self.getTranslationtierIds(eaf, uTier):
                        transIds = eaf.getSubAnnotationIdsForAnnotationInTier(uId, uTier, tTier)
                        for transId in transIds:
                            trans = eaf.getAnnotationValueForAnnotation(tTier, transId)
                            if trans != '':
                                translations.append(trans)
                    for wTier in self.getWordtierIds(eaf, uTier):
                        wordsIds = eaf.getSubAnnotationIdsForAnnotationInTier(uId, uTier, wTier)
                        for wordId in wordsIds:
                            posAnnotations = self.getPosAnnotationsForWordId(wordId, wTier,  eaf) 
                            words.append(posAnnotations)
                    self.tree.append([ uId,  utterance,  words, translations, locale, participant, uTier ])
        else: # if self.utterancesTiers != []
            for wTier in self.getWordtierIds(eaf):
                translations = []
                locale = eaf.getLocaleForTier(uTier)
                participant = eaf.getParticipantForTier(uTier)
                wordsIds = eaf.getAnnotationIdsForTier(wTier)
                for wordId in wordsIds:
                    posAnnotations = self.getPosAnnotationsForWordId(wordId, wTier,  eaf) 
                    words.append(posAnnotations)
                self.tree.append([ '',  '',  ilElements, translations, locale, participant, '' ])
 
    def getPosAnnotationsForWordId(self, id, wTier, eaf):
        ilElement = []
        word = eaf.getAnnotationValueForAnnotation(wTier, id)
        ilElement.append(id)
        ilElement.append(word)
        posElements = []
        for pTier in self.getPostierIds(eaf, wTier):
            posIds = eaf.getSubAnnotationIdsForAnnotationInTier(id, wTier, pTier)
            for posId in posIds:
                pos = eaf.getAnnotationValueForAnnotation(pTier, posId)
                posElements.append((posId, pos))
        ilElement.append(posElements)
        return ilElement

####################################### Files

class Eaf(object):

    def __init__(self, file):
        self.tree = ET.parse(file)

    def tostring(self):
        return ET.tostring(self.tree.getroot(), pretty_print=True, encoding="utf-8")

    def tiers(self):
        # returns tiers as dictionary: id -> type
        ret = {}
        for tier in self.tree.findall('TIER'):
            ret[tier.attrib['TIER_ID']] = tier.attrib['LINGUISTIC_TYPE_REF']
        return ret
        
    def childTiersFor(self,  id):
        ret = {}
        childTiers = self.tree.findall("TIER[@PARENT_REF='%s']" % id)
        for tier in childTiers:
            child_id = tier.attrib['TIER_ID']
            if child_id not in ret.keys():
                ret2 = self.childTiersFor(child_id)
                for k,  v in ret2.items():
                    ret[k] = v
            ret[child_id] = tier.attrib['LINGUISTIC_TYPE_REF']
        return ret

    def getIndexOfTier(self, id):
        ret = None
        i = 0
        for node in self.tree.getroot():
            if node.tag == 'TIER' and 'TIER_ID' in node.attrib and node.attrib['TIER_ID'] == id:
                ret = i
            i = i + 1
        return ret

    def getIndexOfLastTier(self):
        ret = None
        i = 0
        for node in self.tree.getroot():
            if node.tag == 'TIER':
                ret = i
            i = i + 1
        if ret == None:
            ret = i
        return ret

    def getLastUsedAnnotationId(self):
        strId = self.tree.findtext("HEADER/PROPERTY[@NAME='lastUsedAnnotationId']")
        lastId = 0
        if strId != None:
            lastId = int(strId)
        else:
            annotations = self.tree.findall("TIER/ANNOTATION/ALIGNABLE_ANNOTATION")
            for a in annotations:
                i = a.attrib['ANNOTATION_ID']
                i = int(re.sub(r"\D", "", i))
                if i > lastId:
                    lastId = i
            annotations = self.tree.findall("TIER/ANNOTATION/REF_ANNOTATION")
            for a in annotations:
                i = a.attrib['ANNOTATION_ID']
                i = int(re.sub(r"\D", "", i))
                if i > lastId:
                    lastId = i
        return lastId

    def getTierIdsForLinguisticType(self, type, parent = None):
        ret = []
        if parent == None:
            tiers = self.tree.findall("TIER[@LINGUISTIC_TYPE_REF='%s']" % type) #.decode('utf-8')
        else:
            tiers = self.tree.findall("TIER[@LINGUISTIC_TYPE_REF='%s'][@PARENT_REF='%s']" % (type, parent)) #.decode('utf-8')
        for tier in tiers:
            ret.append(tier.attrib['TIER_ID'])
        return ret

    def getParameterDictForTier(self, id):
        tier = self.tree.find("TIER[@TIER_ID='%s']" % id)
        return tier.attrib
        
    def getParameterDictForLinguisticType(self, id):
        tier = self.tree.find("LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID='%s']" % id)
        return tier.attrib

    def getLinguisticTypeForTier(self, id):
        tier = self.tree.find("TIER[@TIER_ID='%s']" % id)
        if 'LINGUISTIC_TYPE_REF' in tier.attrib:
            return tier.attrib['LINGUISTIC_TYPE_REF']
        return None
        
    def getConstraintForLinguisticType(self, id):
        tier = self.tree.find("LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID='%s']" % id)
        if 'CONSTRAINTS' in tier.attrib:
            return tier.attrib['CONSTRAINTS']
        return None
        
    def linguisticTypeIsTimeAlignable(self, id):
        tier = self.tree.find("LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID='%s']" % id)
        if 'TIME_ALIGNABLE' in tier.attrib:
            if tier.attrib['TIME_ALIGNABLE'] == 'true':
                return True
            else:
                return False
        return None

    def getIndexOfLastLinguisticType(self):
        ret = None
        i = 0
        for node in self.tree.getroot():
            if node.tag == 'LINGUISTIC_TYPE':
                ret = i
            i = i + 1
        if ret == None:
            ret = i
        return ret

    def getLocaleForTier(self,  id):
        locale = ''
        tier = self.tree.find("TIER[@TIER_ID='%s']" % id)
        if 'DEFAULT_LOCALE' in tier.attrib:
            locale = tier.attrib['DEFAULT_LOCALE']
            if locale == None:
                locale = ''
        return locale
        
    def getParticipantForTier(self,  id):
        participant = ''
        tier = self.tree.find("TIER[@TIER_ID='%s']" % id)
        if 'PARTICIPANT' in tier.attrib:
            participant = tier.attrib['PARTICIPANT']
            if participant == None:
                participant = ''
        participant = participant
        return participant

    def addLinguisticType(self, type, constraints, timeAlignable = False, graphicReferences = False, extRef = None):
        newtype = Element("LINGUISTIC_TYPE")
        newtype.attrib['LINGUISTIC_TYPE_ID'] = type
        newtype.attrib['CONSTRAINTS'] = constraints
        if timeAlignable:
            newtype.attrib['TIME_ALIGNABLE'] = 'true'
        else:
            newtype.attrib['TIME_ALIGNABLE'] = 'false'
        if graphicReferences:
            newtype.attrib['GRAPHIC_REFERENCES'] = 'true'
        else:
            newtype.attrib['GRAPHIC_REFERENCES'] = 'false'
        if extRef != None:
            newtype.attrib['EXT_REF'] = extRef
        newIndex = self.getIndexOfLastLinguisticType()
        self.tree.getroot().insert(newIndex, newtype)

    def hasLinguisticType(self, type):
        node = self.tree.find("LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID='%s']" % type)
        if node == None:
            return False
        else:
            return True

    def addTier(self,  id,  type,  parent = None, defaultLocale = None,  participant = ''):
        newtier = Element("TIER")
        newtier.attrib['TIER_ID'] = id
        newtier.attrib['LINGUISTIC_TYPE_REF'] = type
        if parent != None:
            newtier.attrib['PARENT_REF'] = parent
        if defaultLocale != None:
            newtier.attrib['DEFAULT_LOCALE'] = defaultLocale
        newtier.attrib['PARTICIPANT'] = participant
        newIndex = self.getIndexOfLastTier()
        if parent != None:
            i = self.getIndexOfTier(parent)
            if i != None:
                newIndex = i
        self.tree.getroot().insert(newIndex, newtier)                

    def getStartTsForAnnotation(self,  idTier,  idAnnotation):
        a = self.tree.find("TIER[@TIER_ID='%s']/ANNOTATION/ALIGNABLE_ANNOTATION[@ANNOTATION_ID='%s']" % (idTier,  idAnnotation))
        ret = a.attrib['TIME_SLOT_REF1']
        return ret

    def getEndTsForAnnotation(self,  idTier,  idAnnotation):
        a = self.tree.find("TIER[@TIER_ID='%s']/ANNOTATION/ALIGNABLE_ANNOTATION[@ANNOTATION_ID='%s']" % (idTier,  idAnnotation))
        ret = a.attrib['TIME_SLOT_REF2']
        return ret

    def getSubAnnotationIdsForAnnotationInTier(self, idAnn, idTier, idSubTier):
        type = self.getLinguisticTypeForTier(idSubTier)
        ret = []
        if self.linguisticTypeIsTimeAlignable(type):
            startTs = self.getStartTsForAnnotation(idTier, idAnn)
            endTs = self.getEndTsForAnnotation(idTier, idAnn)
            ret = self.getAlignableAnnotationIdsForTier(idSubTier, startTs, endTs)
        else:
            ret = self.getRefAnnotationIdsForTier(idSubTier, idAnn)
        return ret

    def getAnnotationIdsForTier(self, idTier):
        type = self.getLinguisticTypeForTier(idTier)
        ret = []
        if self.linguisticTypeIsTimeAlignable(type):
            ret = self.getAlignableAnnotationIdsForTier(idtier)
        else:
            ret = self.getRefAnnotationIdsForTier(idTier)
        return ret

    def getRefAnnotationIdsForTier(self, idTier, annRef = None,  prevAnn = None):
        ret = []
        foundann = []
        prevs = {}
        if annRef == None:
            allAnnotations = self.tree.findall("TIER[@TIER_ID='%s']/ANNOTATION/REF_ANNOTATION" % idTier)
        else:
            if prevAnn == None:
                allAnnotations = self.tree.findall("TIER[@TIER_ID='%s']/ANNOTATION/REF_ANNOTATION[@ANNOTATION_REF='%s']" % (idTier, annRef))
            else:
                allAnnotations = self.tree.findall("TIER[@TIER_ID='%s']/ANNOTATION/REF_ANNOTATION[@ANNOTATION_REF='%s'][@PREVIOUS_ANNOTATION='%s']" % (idTier, annRef, prevAnn))
        for a in allAnnotations:
            if prevAnn == None and 'PREVIOUS_ANNOTATION' in a.attrib:
                continue
            ret.append(a.attrib['ANNOTATION_ID'])
            foundann.append(a.attrib['ANNOTATION_ID'])
        for id in foundann:
            ret.extend(self.getRefAnnotationIdsForTier(idTier, annRef,  id))
        return ret

    def appendRefAnnotationToTier(self, idTier, idAnnotation, strAnnotation, annRef, prevAnn = None):
        t = self.tree.find("TIER[@TIER_ID='%s']" % idTier)
        if t == None:
            return False
        eAnnotation = Element("ANNOTATION")
        if prevAnn == None:
            eRefAnn = ET.SubElement(eAnnotation, "REF_ANNOTATION", ANNOTATION_ID=idAnnotation, ANNOTATION_REF=annRef)
        else:
            eRefAnn = ET.SubElement(eAnnotation, "REF_ANNOTATION", ANNOTATION_ID=idAnnotation, ANNOTATION_REF=annRef, PREVIOUS_ANNOTATION=prevAnn)
        eAnnVal = ET.SubElement(eRefAnn, "ANNOTATION_VALUE")
        eAnnVal.text = strAnnotation
        t.append(eAnnotation)
        return True

    def getAlignableAnnotationIdsForTier(self, id, startTs = None,  endTs = None):
        ret = []
        ts = {}
        if startTs != None and endTs != None:
            iStartTs = int(re.sub(r"\D", '', startTs))
            iEndTs = int(re.sub(r"\D", '', endTs))
        allAnnotations = self.tree.findall("TIER[@TIER_ID='%s']/ANNOTATION/ALIGNABLE_ANNOTATION" % id)
        for a in allAnnotations:
            aStartTs = a.attrib['TIME_SLOT_REF1']
            aEndTs = a.attrib['TIME_SLOT_REF2']
            iAStartTs = int(re.sub(r"\D", '', aStartTs))
            iAEndTs = int(re.sub(r"\D", '', aEndTs))
            if startTs != None and endTs != None:
                if iStartTs > iAStartTs or iEndTs < iAEndTs:
                    continue
            id = None
            v = []
            id = a.attrib['ANNOTATION_ID']
            if id:
                ts[id] = iAStartTs
        # sort ids via start timestamp
        alist = sorted(ts.iteritems(), key=lambda (k,v): (v,k))
        for k, v in alist:
            ret.append(k)
        return ret

    def removeAllAnnotationsFromTier(self, idTier):
        t = self.tree.find("TIER[@TIER_ID='%s']" % idTier)
        annotations = self.tree.findall("TIER[@TIER_ID='%s']/ANNOTATION" % idTier)
        if t == None or annotations == None:
            return False
        for a in annotations:
            t.remove(a)
        return True

    def removeAnnotationWithId(self, idAnnotation):
        a = self.tree.find("TIER/ANNOTATION/ALIGNABLE_ANNOTATION[@ANNOTATION_ID='%s']" % idAnnotation)
        if a != None:
            a.getparent().getparent().remove(a.getparent())
        else:
            a = self.tree.find("TIER/ANNOTATION/REF_ANNOTATION[@ANNOTATION_ID='%s']" % idAnnotation)
            if a != None:
                a.getparent().getparent().remove(a.getparent())

    def removeAnnotationsWithRef(self, idRefAnn):
        allAnnotations = self.tree.findall("TIER/ANNOTATION/REF_ANNOTATION[@ANNOTATION_REF='%s']" % idRefAnn)
        for a in allAnnotations:
            a.getparent().getparent().remove(a.getparent())

    def getAnnotationValueForAnnotation(self, idTier, idAnnotation):
        type = self.getLinguisticTypeForTier(idTier)
        ret = ''
        if self.linguisticTypeIsTimeAlignable(type):
            a = self.tree.find("TIER[@TIER_ID='%s']/ANNOTATION/ALIGNABLE_ANNOTATION[@ANNOTATION_ID='%s']" % (idTier,  idAnnotation))
            ret = a.findtext('ANNOTATION_VALUE')
        else:
            a = self.tree.find("TIER[@TIER_ID='%s']/ANNOTATION/REF_ANNOTATION[@ANNOTATION_ID='%s']" % (idTier,  idAnnotation))
            ret = a.findtext('ANNOTATION_VALUE')
        if ret == None:
            ret = ''
        return ret

    def setAnnotationValueForAnnotation(self, idTier, idAnnotation, strAnnotation):
        type = self.getLinguisticTypeForTier(idTier)
        ret = ''
        a = None
        if self.linguisticTypeIsTimeAlignable(type):
            a = self.tree.find("TIER[@TIER_ID='%s']/ANNOTATION/ALIGNABLE_ANNOTATION[@ANNOTATION_ID='%s']/ANNOTATION_VALUE" % (idTier,  idAnnotation))
        else:
            a = self.tree.find("TIER[@TIER_ID='%s']/ANNOTATION/REF_ANNOTATION[@ANNOTATION_ID='%s']/ANNOTATION_VALUE" % (idTier,  idAnnotation))
        if a == None:
            return False
        a.text = strAnnotation
        return True

    def updatePrevAnnotationForAnnotation(self, idAnnotation, idPrevAnn = None):
        # this will just do nothing for time-aligned tiers
        # if idPrevAnn is None, then the attribute will be removed
        a = self.tree.find("TIER/ANNOTATION/REF_ANNOTATION[@ANNOTATION_ID='%s']" % idAnnotation)
        if a != None:
            if idPrevAnn == None:
                del(a.attrib['PREVIOUS_ANNOTATION'])
            else:
                a.attrib['PREVIOUS_ANNOTATION'] = idPrevAnn

