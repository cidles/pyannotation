# -*- coding: utf-8 -*-
# (C) 2011, 2012 copyright by Peter Bouda
"""This module contains classes to access Elan data.

The class Eaf is a low level API to .eaf files.

EafGlossTree, EafPosTree, etc. are the classes to access the data via 
tree, which also contains the original .eaf IDs. Because of this
EafTrees are read-/writeable. 

"""

import re
import operator

import pyannotation.data

from copy import deepcopy

from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element
from xml.parsers import expat

############################################# Builders

class EafAnnotationFileObject(pyannotation.data.AnnotationFileObject):

    def __init__(self, file_path):
        pyannotation.data.AnnotationFileObject.__init__(self, file_path)

    @property
    def file_path(self, file_path):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        self._file_path = file_path
        self.file = Eaf(file_path)

    def create_tier_handler(self):
        self.tier_handler = EafAnnotationFileTierHandler(self)
        return self.tier_handler

    def create_parser(self, type):
        if type == pyannotation.data.WORDS:
            self.parser = EafAnnotationFileParser(self, self.create_tier_handler())
        elif type == pyannotation.data.MORPHSYNT:
            self.parser = EafAnnotationFileParserMorphsynt(self, self.create_tier_handler())
        else:
            raise(
                pyannotation.data.DataStructureTypeNotSupportedException(
                    "Data structure type {0} not supported".format(type)))
        return self.parser


class EafFromToolboxAnnotationFileObject(pyannotation.data.AnnotationFileObject):

    def __init__(self, file_path):
        pyannotation.data.AnnotationFileObject.__init__(self, file_path)

    @property
    def file_path(self, file_path):
        return _file_path

    @file_path.setter
    def file_path(self, file_path):
        self._file_path = file_path
        self.file = EafPythonic(file_path)

    def create_tier_handler(self):
        if self.tier_handler == None:
            self.tier_handler = EafAnnotationFileTierHandler(self)
            self.tier_handler.set_utterancetier_type("tx")
            self.tier_handler.set_wordtier_type("mo")
            self.tier_handler.set_morphemetier_type("mo")
            self.tier_handler.set_glosstier_type("gl")
            self.tier_handler.set_translationtier_type(["ft", "ot"])
        return self.tier_handler

    def create_parser(self):
        if type == pyannotation.data.MORPHSYNT:
            self.parser = EafFromToolboxAnnotationFileParserMorphsynt(
                self, self.create_tier_handler())
        else:
            raise(
                pyannotation.data.DataStructureTypeNotSupportedException(
                    "Data structure type {0} not supported".format(type)))
        return self.parser


class EafAnnotationFileTierHandler(pyannotation.data.AnnotationFileTierHandler):

    def __init__(self, annotation_file_object):
        #pyannotation.data.AnnotationFileTierHandler.__init__(self, annotation_file_object)
        self.eaf = annotation_file_object.file
        self.UTTERANCETIER_TYPEREFS = [ "utterance", "utterances", "Äußerung", "Äußerungen" ]
        self.WORDTIER_TYPEREFS = [ "words", "word", "Wort", "Worte", "Wörter" ]
        self.MORPHEMETIER_TYPEREFS = [ "morpheme", "morphemes",  "Morphem", "Morpheme" ]
        self.GLOSSTIER_TYPEREFS = [ "glosses", "gloss", "Glossen", "Gloss", "Glosse" ]
        self.POSTIER_TYPEREFS = [ "part of speech", "parts of speech", "Wortart", "Wortarten" ]
        self.WFWTRANSLATIONTIER_TYPEREFS = [ "wfwtranslation" ]
        self.GRAID1TIER_TYPEREFS = [ "graid1" ]
        self.GRAID2TIER_TYPEREFS = [ "graid2" ]
        self.TRANSLATIONTIER_TYPEREFS = [ "translation", "translations", "Übersetzung",  "Übersetzungen" ]

    def set_utterancetier_type(self, type):
        if isinstance(type, list):
            self.UTTERANCETIER_TYPEREFS = type
        else:
            self.UTTERANCETIER_TYPEREFS = [type]

    def set_wordtier_type(self, type):
        if isinstance(type, list):
            self.WORDTIER_TYPEREFS = type
        else:
            self.WORDTIER_TYPEREFS = [type]

    def set_morphemetier_type(self, type):
        if isinstance(type, list):
            self.MORPHEMETIER_TYPEREFS = type
        else:
            self.MORPHEMETIER_TYPEREFS = [type]

    def set_glosstier_type(self, type):
        if isinstance(type, list):
            self.GLOSSTIER_TYPEREFS = type
        else:
            self.GLOSSTIER_TYPEREFS = [type]

    def set_postier_type(self, type):
        if isinstance(type, list):
            self.POSTIER_TYPEREFS = type
        else:
            self.POSTIER_TYPEREFS = [type]

    def set_wfwtier_type(self, type):
        if isinstance(type, list):
            self.WFWTRANSLATIONTIER_TYPEREFS = type
        else:
            self.WFWTRANSLATIONTIER_TYPEREFS = [type]

    def set_graid1tier_type(self, type):
        if isinstance(type, list):
            self.GRAID1TIER_TYPEREFS = type
        else:
            self.GRAID1TIER_TYPEREFS = [type]

    def set_graid2tier_type(self, type):
        if isinstance(type, list):
            self.GRAID2TIER_TYPEREFS = type
        else:
            self.GRAID2TIER_TYPEREFS = [type]

    def set_translationtier_type(self, type):
        if isinstance(type, list):
            self.TRANSLATIONTIER_TYPEREFS = type
        else:
            self.TRANSLATIONTIER_TYPEREFS = [type]

    def get_utterancetier_ids(self, parent = None):
        ret = []
        for type in self.UTTERANCETIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def get_wordtier_ids(self, parent = None):
        ret = []
        for type in self.WORDTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def get_morphemetier_ids(self, parent = None):
        ret = []
        for type in self.MORPHEMETIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def get_glosstier_ids(self, parent = None):
        ret = []
        for type in self.GLOSSTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def get_postier_ids(self, parent = None):
        ret = []
        for type in self.POSTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def get_translationtier_ids(self, parent = None):
        ret = []
        for type in self.TRANSLATIONTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def get_graid1tier_ids(self, parent = None):
        ret = []
        for type in self.GRAID1TIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def get_graid2tier_ids(self, parent = None):
        ret = []
        for type in self.GRAID2TIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def get_wfwtier_ids(self, parent = None):
        ret = []
        for type in self.WFWTRANSLATIONTIER_TYPEREFS:
            ret.extend(self.eaf.getTierIdsForLinguisticType(type, parent))
        return ret

    def add_tier(self, tier_id, tier_type, tier_type_constraint, parent_tier,
                 tier_default_locale, tier_participant):
        self.eaf.addTier(tier_id, tier_type, parent_tier, tier_default_locale, tier_participant)
        if not self.eaf.hasLinguisticType(tier_type):
            self.eaf.addLinguisticType(tier_type, tier_type_constraint)

    def get_locale_for_tier(self, id_tier):
        return self.eaf.getLocaleForTier(id_tier)

    def get_participant_for_tier(self, id_tier):
        return self.eaf.getParticipantForTier(id_tier)


class EafAnnotationFileParser(pyannotation.data.AnnotationFileParser):

    def __init__(self, annotation_file_object, annotation_file_tiers):
        pyannotation.data.AnnotationFileParser.__init__(self, annotation_file_object, annotation_file_tiers)
        self.tier_handler = annotation_file_tiers
        self.eaf = annotation_file_object.file
        self.last_used_annotation_id = self.eaf.getLastUsedAnnotationId()
        self.empty_il_element = [ '', '', '' ]

    def remove_annotation_with_id(self, id_annotation):
        self.eaf.removeAnnotationWithId(id_annotation)

    def remove_annotations_with_ref(self, id_ref_ann):
        self.eaf.removeAnnotationsWithRef(id_ref_ann)

    def updatePrevAnnotationForAnnotation(self, id_annotation, id_prev_ann = None):
        self.eaf.updatePrevAnnotationForAnnotation(id_annotation, id_prev_ann)

    def _utterances_ids(self):
        utterance_tier_ids = self.tier_handler.get_utterancetier_ids()
        return( (u_id, u_tier) for u_tier in utterance_tier_ids
                           for u_id in (self.eaf.getAlignableAnnotationIdsForTier(u_tier) +
                                       self.eaf.getRefAnnotationIdsForTier(u_tier))
        )

    def utterances(self):
        return ( (u_id, self.eaf.getAnnotationValueForAnnotation(u_tier, u_id), u_tier) \
            for u_id, u_tier in self._utterances_ids() )

    def _translations_for_utterance(self, utterance_tier, id_utterance):
        translations = []
        translation_tier_ids = self.tier_handler.get_translationtier_ids(utterance_tier)
        for t_tier in translation_tier_ids:
            ids_trans = self.eaf.getSubAnnotationIdsForAnnotationInTier(
                id_utterance, utterance_tier, t_tier)
            for id_trans in ids_trans:
                trans = self.eaf.getAnnotationValueForAnnotation(t_tier, id_trans)
                if trans != '':
                    translations.append([id_trans, trans, t_tier])
        return translations

    def _annotations_for_utterance(self, u_tier, u_id):
        translations = self._translations_for_utterance(u_tier, u_id)
        return [ translations ]

    def _ilelements_for_utterance(self, u_tier, u_id):
        ilelements = []
        word_tier_ids = self.tier_handler.get_wordtier_ids(u_tier)
        for w_tier in word_tier_ids:
            words_ids = self.eaf.getSubAnnotationIdsForAnnotationInTier(u_id, u_tier, w_tier)
            for word_id in words_ids:
                word = self.eaf.getAnnotationValueForAnnotation(w_tier, word_id)
                ilelements.append([word_id, word, w_tier])
        return ilelements

    def parse(self):
        tree = []
        for u_id, utterance, u_tier in self.utterances():
            locale = self.eaf.getLocaleForTier(u_tier)
            participant = self.eaf.getParticipantForTier(u_tier)

            utterance_annotations = self._annotations_for_utterance(u_tier, u_id)
            ilelements = self._ilelements_for_utterance(u_tier, u_id)
            if not ilelements:
                ilelements = self.empty_il_element

            tree.append([ u_id,  utterance, ilelements, utterance_annotations, locale, participant, u_tier ])

        return tree

class EafAnnotationFileParserMorphsynt(pyannotation.data.AnnotationFileParserMorphsynt, EafAnnotationFileParser):

    def __init__(self, annotation_file_object, annotation_file_tiers):
        pyannotation.data.AnnotationFileParserMorphsynt.__init__(self, annotation_file_object, annotation_file_tiers)
        EafAnnotationFileParser.__init__(self, annotation_file_object, annotation_file_tiers)
        self.empty_il_element = [ ['', '',  [ ['', '',  [ ['',  ''] ] ] ] ] ]

    def _morphemes_for_word(self, w_tier, w_id):
        ilelement = []
        word = self.eaf.getAnnotationValueForAnnotation(w_tier, w_id)
        ilelement.append(w_id)
        ilelement.append(word)
        morph_elements = []
        morpheme_tier_ids = self.tier_handler.get_morphemetier_ids(w_tier)
        for m_tier in morpheme_tier_ids:
            morph_ids = self.eaf.getSubAnnotationIdsForAnnotationInTier(w_id, w_tier, m_tier)
            for morph_id in morph_ids:
                morph_elements.append(self._funcs_for_morpheme(m_tier, morph_id))
        if len(morph_elements) == 0:
            ilelement.append([[ '',  '',  [ ['',  ''] ]]])
        else:
            ilelement.append(morph_elements)
        return ilelement

    def _funcs_for_morpheme(self, m_tier, m_id):
        ilelement = []
        morpheme = self.eaf.getAnnotationValueForAnnotation(m_tier, m_id)
        morpheme = re.sub(r'^-', '', morpheme)
        morpheme = re.sub(r'-$', '', morpheme)
        ilelement.append(morph_id)
        ilelement.append(morpheme)
        func_elements = []
        gloss_tier_ids = self.tier_handler.get_glosstier_ids(m_tier)
        for g_tier in gloss_tier_ids:
            func_ids = self.eaf.getSubAnnotationIdsForAnnotationInTier(m_id, m_tier, g_tier)
            for func_id in func_ids:
                function = self.eaf.getAnnotationValueForAnnotation(g_tier, func_id)
                function = re.sub(r'^-', '', function)
                morpheme = re.sub(r'-$', '', function)
                e = [func_id, function]
                func_elements.append(e)
        if len(func_elements) == 0:
            ilelement.append([['',  '']])
        else:
            ilelement.append(func_elements)
        return ilelement

    def _ilelements_for_utterance(self, u_tier, u_id):
        ilelements = []
        word_tier_ids = self.tier_handler.get_wordtier_ids(u_tier)
        for w_tier in word_tier_ids:
            words_ids = self.eaf.getSubAnnotationIdsForAnnotationInTier(u_id, u_tier, w_tier)
            for word_id in words_ids:
                #word = self.eaf.getAnnotationValueForAnnotation(wTier, wordId)
                ilelements.append(self._morphemes_for_word(w_tier, word_id))
        return ilelements

    def get_file(self, tree, tier_utterances, tier_words, tier_morphemes, tier_glosses, tier_translations):
        # make local copy of eaf
        eaf2 = deepcopy(self.eaf)
        utterances = [[u[0], u[1]] for u in tree if u[6] == tier_utterances]
        translations = [[u[3][0], u[0]] for u in tree if u[6] == tier_utterances and len(u[3][0])>=1]
        words = [[w[0], w[1]] for u in tree if u[6] == tier_utterances for w in u[2]]
        ilelements = [u[2] for u in tree if u[6] == tier_utterances]
        # save utterances
        for u in utterances:
            eaf2.setAnnotationValueForAnnotation(tier_utterances, u[0], u[1])
            # save translations
        for t1 in translations:
            for t in t1[0]:
                if t[1] != "":
                    if not eaf2.setAnnotationValueForAnnotation(tier_translations, t[0], t[1]):
                        eaf2.appendRefAnnotationToTier(tier_translations, t[0], t[1], t1[1])
            # save words
        for w in words:
            eaf2.setAnnotationValueForAnnotation(tier_words, w[0], w[1])
            #save morphemes
        eaf2.removeAllAnnotationsFromTier(tier_morphemes)
        eaf2.removeAllAnnotationsFromTier(tier_glosses)
        for i in ilelements:
            for w in i:
                if len(w) >= 3:
                    ref_ann_morph = w[0]
                    prev_ann_morph = None
                    for m in w[2]:
                        if len(m) >= 3:
                            if m[0] != "" and m[1] != "" and ref_ann_morph != "":
                                eaf2.appendRefAnnotationToTier(tier_morphemes, m[0], m[1], ref_ann_morph, prev_ann_morph)
                            prev_ann_morph = m[0]
                            ref_ann_gloss = m[0]
                            prev_ann_gloss = None
                            for g in m[2]:
                                if len(g) >= 2:
                                    if g[0] != "" and g[1] != "" and ref_ann_gloss != "":
                                        eaf2.appendRefAnnotationToTier(tier_glosses, g[0], g[1], ref_ann_gloss, prev_ann_gloss)
                                    prev_ann_gloss = g[0]
        return eaf2.tostring()


class EafFromToolboxAnnotationFileParserMorphsynt(EafAnnotationFileParserMorphsynt):

    def __init__(self, annotation_file_object, annotation_file_tiers):
        EafAnnotationFileParserMorpsynt.__init__(self, annotation_file_object, annotation_file_tiers)
        self.empty_il_element = [ ['', '',  [ ['', '',  [ ['',  ''] ] ] ] ] ]

    def parse(self):
        tree = []
        self.utterance_tier_ids = self.tier_handler.get_utterancetier_ids()
        for u_tier in self.utterance_tier_ids:
            utterancesIds = self.eaf.getAlignableAnnotationIdsForTier(u_tier) + \
                            self.eaf.getRefAnnotationIdsForTier(u_tier)
            for u_id in utterances_ids:
                utterance = self.eaf.getAnnotationValueForAnnotation(u_tier, u_id)
                utterance = re.sub(r"[\n\r\t ]+", " ", utterance)

                ref_id = self.eaf.getRefAnnotationIdForAnnotationId(u_tier, u_id)
                toolbox_id = self.eaf.getAnnotationValueForAnnotation("ref", ref_id)

                locale = self.eaf.getLocaleForTier(u_tier)
                participant = self.eaf.getParticipantForTier(u_tier)
                translations = self._translations_for_utterance(u_tier, u_id)
                ilelements = []

                arr_text_words = re.split(self.WORD_BOUNDARY_PARSE, utterance)
                arr_text_words = filter(lambda i: i != '', arr_text_words)
                
                arr_morph_words = []
                arr_gloss_words = []
                word_tier_ids = self.tier_handler.get_wordtier_ids("ref")
                for w_tier in word_tier_ids:
                    words_ids = self.eaf.getSubAnnotationIdsForAnnotationInTier(ref_id, "ref", w_tier)
                    for word_id in words_ids:
                        word = self.eaf.getAnnotationValueForAnnotation(w_tier, word_id)
                        arr_morph_words.append(word)
                        gloss_tier_ids = self.tier_handler.get_glosstier_ids(w_tier)
                        for g_tier in gloss_tier_ids:
                            gloss_ids = self.eaf.getSubAnnotationIdsForAnnotationInTier(word_id, w_tier, g_tier)
                            for gloss_id in gloss_ids:
                                gloss = self.eaf.getAnnotationValueForAnnotation(g_tier, gloss_id)
                                arr_gloss_words.append(gloss)

                for i,word in enumerate(arr_text_words):
                    morphemes = ""
                    glosses = ""
                    if i < len(arr_morph_words):
                        morphemes = arr_morph_words[i]
                    if i < len(arr_gloss_words):
                        glosses = arr_gloss_words[i]
                    ilElement = self.il_element_for_string("%s %s %s" % (word, morphemes, glosses))
                    
                    ilelements.append(ilElement)
                if len(ilelements) == 0:
                    ilelements = [ ['', '',  [ ['', '',  [ ['',  ''] ] ] ] ] ]

                tree.append([ toolbox_id,  utterance,  ilelements, [ translations ], locale, participant, u_tier ])
                
        tree.sort()
        return tree

class EafAnnotationFileParserGraid(EafAnnotationFileParser):

    def __init__(self, annotationFileObject, annotationFileTiers):
        EafAnnotationFileParser.__init__(self, annotationFileObject, annotationFileTiers)
        self.emptyIlElement = [ ['', '',  [ [ ['', '', ''] ], [ ['', '', ''] ] ], '' ] ]

    def _graid2ForUtterance(self, uTier, uId):
        graid2 = []
        graid2TierIds = self.tierBuilder.getGraid2tierIds(uTier)
        for g2Tier in graid2TierIds:
            graid2Ids = self.eaf.getSubAnnotationIdsForAnnotationInTier(uId, uTier, g2Tier)
            for g2Id in graid2Ids:
                g2 = self.eaf.getAnnotationValueForAnnotation(g2Tier, g2Id)
                if g2 != '':
                    graid2.append([g2Id, g2, g2Tier])
        return graid2

    def _annotationsForUtterance(self, uTier, uId):
        translations = self._translationsForUtterance(uTier, uId)
        graid2 = self._graid2ForUtterance(uTier, uId)
        return [ translations, graid2 ]

    def _graid1ForWord(self, wTier, wId):
        graid1 = []
        graid1TierIds = self.tierBuilder.getGraid1tierIds(wTier)
        for g1Tier in graid1TierIds:
            g1Ids = self.eaf.getSubAnnotationIdsForAnnotationInTier(wId, wTier, g1Tier)
            for g1Id in g1Ids:
                g1 = self.eaf.getAnnotationValueForAnnotation(g1Tier, g1Id)
                graid1.append([ g1Id, g1, g1Tier ])
        return graid1

    def _wfwtranslationsForWord(self, wTier, wId):
        wfw = []
        wfwTierIds = self.tierBuilder.getWfwtierIds(wTier)
        for wfwTier in wfwTierIds:
            wfwIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(wId, wTier, wfwTier)
            for wfwId in wfwIds:
                w = self.eaf.getAnnotationValueForAnnotation(wfwTier, wfwId)
                wfw.append([ wfwId, w, wfwTier ])
        return wfw

    def _ilelementsForUtterance(self, uTier, uId):
        ilelements = []
        wordTierIds = self.tierBuilder.getWordtierIds(uTier)
        for wTier in wordTierIds:
            wordsIds = self.eaf.getSubAnnotationIdsForAnnotationInTier(uId, uTier, wTier)
            for wordId in wordsIds:
                word = self.eaf.getAnnotationValueForAnnotation(wTier, wordId)
                wfw = self._wfwtranslationsForWord(wTier, wordId)
                graid1 = self._graid1ForWord(wTier, wordId)
                ilelements.append([wordId, word, [ wfw, graid1 ] , wTier])
        return ilelements

####################################### Files

class Eaf(object):

    def __init__(self, file):
        self.tree = ET.parse(file)

    def tostring(self):
        return ET.tostring(self.tree.getroot(), encoding="utf-8")

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

    def getLocaleForTier(self, id):
        locale = ''
        tier = self.tree.find("TIER[@TIER_ID='%s']" % id)
        if 'DEFAULT_LOCALE' in tier.attrib:
            locale = tier.attrib['DEFAULT_LOCALE']
            if locale == None:
                locale = ''
        return locale
        
    def getParticipantForTier(self, id):
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

    def getRefAnnotationIdForAnnotationId(self, idTier, idAnnotation):
        a = self.tree.find( "TIER[@TIER_ID='%s']/ANNOTATION/REF_ANNOTATION[@ANNOTATION_ID='%s']" % (idTier, idAnnotation) )
        if a is not None:
            return a.attrib["ANNOTATION_REF"]
        else:
            return None
        
    def getRefAnnotationIdsForTier(self, idTier, annRef = None,  prevAnn = None):
        ret = []
        foundann = []
        prevs = {}
        if annRef == None:
            allAnnotations = self.tree.findall("TIER[@TIER_ID='%s']/ANNOTATION/REF_ANNOTATION" % idTier)
            for a in allAnnotations:
                ret.append(a.attrib['ANNOTATION_ID'])
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
        alist = sorted(ts.items(), key=operator.itemgetter(1))
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


class EafPythonic(object):
    
    def __init__(self, filename):
        self.tiersDict = {}
        self.alignableAnnotationsDict = {}
        self.refAnnotationsDict = {}
        self.refAnnotationsDictByTierAndAnnRef = {}
        self.linguistictypesDict = {}
        
        parser = Xml2Obj()
        rootElement = parser.parse(filename)

        for ltElement in rootElement.getElements("LINGUISTIC_TYPE"):
            ta = False
            idLt = ltElement.getAttribute("LINGUISTIC_TYPE_ID")
            if ltElement.getAttribute("TIME_ALIGNABLE") == "true":
                ta = True
            self.linguistictypesDict[idLt] = ta

        for tierElement in rootElement.getElements("TIER"):
            idTier = tierElement.getAttribute("TIER_ID")
            linguisticType = tierElement.getAttribute("LINGUISTIC_TYPE_REF")
            timeAlignable = self.linguistictypesDict[linguisticType]
            participant = tierElement.getAttribute("PARTICIPANT")
            locale = tierElement.getAttribute("PARTICIPANT")
            parent = tierElement.getAttribute("PARENT_REF")
            
            self.tiersDict[idTier] = {
                'linguistic_type' : linguisticType,
                'time_alignable' : timeAlignable,
                'participant' : participant,
                'locale' : locale,
                'parent' : parent
            }
            
            for annotationElement in tierElement.getElements("ANNOTATION"):
                if timeAlignable:
                    for alignableElement in annotationElement.getElements("ALIGNABLE_ANNOTATION"):
                        idAnn = alignableElement.getAttribute("ANNOTATION_ID")
                        ts1 = alignableElement.getAttribute("TIME_SLOT_REF1")
                        ts2 = alignableElement.getAttribute("TIME_SLOT_REF2")
                        value = alignableElement.getElements("ANNOTATION_VALUE")[0].getData()
                        self.alignableAnnotationsDict[idAnn] = {
                            'id' : idAnn,
                            'tierId' : idTier,
                            'ts1' : ts1,
                            'ts2' : ts2,
                            'value' : value
                        }
                else:
                    for refElement in annotationElement.getElements("REF_ANNOTATION"):
                        idAnn = refElement.getAttribute("ANNOTATION_ID")
                        annRef = refElement.getAttribute("ANNOTATION_REF")
                        prevAnn = refElement.getAttribute("PREVIOUS_ANNOTATION")
                        value = refElement.getElements("ANNOTATION_VALUE")[0].getData()
                        self.refAnnotationsDict[idAnn] = {
                            'id' : idAnn,
                            'tierId' : idTier,
                            'annRef' : annRef,
                            'prevAnn' : prevAnn,
                            'value' : value
                        }
                        idByTierAndAnnRef = "%s.%s" % (idTier, annRef)
                        if idByTierAndAnnRef in self.refAnnotationsDictByTierAndAnnRef:
                            self.refAnnotationsDictByTierAndAnnRef[idByTierAndAnnRef].append(idAnn)
                        else:
                            self.refAnnotationsDictByTierAndAnnRef[idByTierAndAnnRef] = [ idAnn ]
                            
    def getLastUsedAnnotationId(self):
        return 0

    def getLocaleForTier(self, idTier):
        return self.tiersDict[idTier]["locale"]

    def getParticipantForTier(self, idTier):
        return self.tiersDict[idTier]["participant"]

    def getTierIdsForLinguisticType(self, type, parent = None):
        return [ id for id in self.tiersDict
                if self.tiersDict[id]["linguistic_type"] == type
                and (parent == None or self.tiersDict[id]["parent"] == parent)]

    def getRefAnnotationIdForAnnotationId(self, idTier, idAnnotation):
        return self.refAnnotationsDict[idAnnotation]["annRef"]

    def getRefAnnotationIdsForTier(self, idTier, annRef = None,  prevAnn = None):
        if annRef != None and prevAnn == None:
            idByTierIdAndAnnRef = "%s.%s" % (idTier, annRef)
            if idByTierIdAndAnnRef in self.refAnnotationsDictByTierAndAnnRef:
                ret = self.refAnnotationsDictByTierAndAnnRef[idByTierIdAndAnnRef]
                #ret.sort()
                return ret
            else:
                return []
        else:
            ret = [ id for id in self.refAnnotationsDict
                    if self.refAnnotationsDict[id]["tierId"] == idTier
                    and (annRef == None or self.refAnnotationsDict[id]["annRef"] == annRef)
                    and (prevAnn == None or self.refAnnotationsDict[id]["prevAnn"] == prevAnn)]
            #ret.sort()
            return ret

    def getAlignableAnnotationIdsForTier(self, idTier, startTs = None,  endTs = None):
        ret = [ id for id in self.alignableAnnotationsDict
                if self.alignableAnnotationsDict[id]["tierId"] == idTier
                and (startTs == None or self.alignableAnnotationsDict[id]["ts1"] == startTs)
                and (endTs == None or self.alignableAnnotationsDict[id]["ts2"] == endTs)]
        #ret.sort()
        return ret

    def getStartTsForAnnotation(self, idTier, idAnn):
        return self.alignableAnntotationsDict[idAnn]["ts1"]
        
    def getEndTsForAnnotation(self, idTier, idAnn):
        return self.alignableAnntotationsDict[idAnn]["ts2"]

    def getAnnotationValueForAnnotation(self, idTier, idAnn):
        if self.tiersDict[idTier]["time_alignable"]:
            return self.alignableAnnotationsDict[idAnn]["value"]
        else:
            return self.refAnnotationsDict[idAnn]["value"]

    def getLinguisticTypeForTier(self, idTier):
        return self.tiersDict[idTier]["linguistic_type"]

    def getSubAnnotationIdsForAnnotationInTier(self, idAnn, idTier, idSubTier):
        ret = []
        if self.tiersDict[idSubTier]["time_alignable"]:
            startTs = self.getStartTsForAnnotation(idTier, idAnn)
            endTs = self.getEndTsForAnnotation(idTier, idAnn)
            ret = self.getAlignableAnnotationIdsForTier(idSubTier, startTs, endTs)
        else:
            ret = self.getRefAnnotationIdsForTier(idSubTier, idAnn)
        return ret

class XmlElement(object):
    ''' A parsed XML element '''
    
    def __init__(self, name, attributes):
        # Record tagname and attributes dictionary
        self.name = name
        self.attributes = attributes
        # Initialize the element's cdata and children to empty
        self.cdata = ''
        self.children = [  ]
        
    def addChild(self, element):
        self.children.append(element)
        
    def getAttribute(self, key):
        return self.attributes.get(key)
        
    def getData(self):
        return self.cdata
    
    def getElements(self, name=''):
        if name:
            return [c for c in self.children if c.name == name]
        else:
            return list(self.children)

class Xml2Obj(object):
    
    def __init__(self):
        self.root = None
        self.nodeStack = [  ]

    def startElement(self, name, attributes):
        'Expat start element event handler'
        # Instantiate an Element object
        element = XmlElement(name.encode( ), attributes)
        # Push element onto the stack and make it a child of parent
        if self.nodeStack:
            parent = self.nodeStack[-1]
            parent.addChild(element)
        else:
            self.root = element
        self.nodeStack.append(element)

    def endElement(self, name):
        'Expat end element event handler'
        self.nodeStack.pop( )

    def characterData(self, data):
        'Expat character data event handler'
        if data: # .strip( )
            #data = data.decode("utf-8")
            #data = data.encode( )
            element = self.nodeStack[-1]
            element.cdata += data

    def parse(self, filename):
        # Create an Expat parser
        Parser = expat.ParserCreate("utf-8")
        # Set the Expat event handlers to our methods
        Parser.StartElementHandler = self.startElement
        Parser.EndElementHandler = self.endElement
        Parser.CharacterDataHandler = self.characterData
        # Parse the XML File
        ParserStatus = Parser.Parse(open(filename).read( ), 1)
        return self.root
