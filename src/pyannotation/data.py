# -*- coding: utf-8 -*-
# (C) 2011, 2012 copyright by Peter Bouda
"""This module contains the classes to access annotated data in
various formats.

The parsing is done by Builder classes for each file type, i.e.
Elan's .eaf files, Kura's .xml file, Toolbox's .txt files etc.
"""

import regex

# file types
(EAF, EAFFROMTOOLBOX, KURA, TOOLBOX) = range(4)
class UnknownFileFormatException(Exception): pass
class NoFileSpecifiedException(Exception): pass

# data structure types
(WORDS, MORPHSYNT, GRAID) = range(3)
class UnknownDataStructureTypeException(Exception): pass
class DataStructureTypeNotSupportedException(Exception): pass

class AnnotationFileObject(object):

    def __init__(self, file_path):
        self.file_path = file_path

    def create_tier_handler(self):
        return None

    def create_parser(self, type):
        raise(
            DataStructureTypeNotSupportedException(
                "Data structure type {0} not supported".format(type)))

class AnnotationFileTierHandler(object):
    pass

class AnnotationFileParser(object):
    """Just the interface of the Builders."""

    def __init__(self, annotation_file_object, annotation_file_tiers):
        self.lastUsedAnnotationId = 0

    def get_next_annotation_id(self):
        a = self.last_used_annotation_id
        self.last_used_annotation_id +=  1
        return a

    def parse(self):
        pass

    def get_file(self, tree):
        pass

    def remove_annotation_with_id(self, id_annotation):
        pass

    def remove_annotations_with_ref(self, id_ref_ann):
        pass

    def update_prev_annotation_for_annotation(self, id_annotation, id_prev_ann = None):
        pass

class AnnotationFileParserMorphsynt(AnnotationFileParser):

    def __init__(self, annotation_file_object, annotation_file_tiers,
                 word_sep = r"[ \n\t\r]+", morpheme_sep = r"[-]",
                 gloss_sep = r"[:]"):
        AnnotationFileParser.__init__(self, annotation_file_object, annotation_file_tiers)
        self.WORD_BOUNDARY_PARSE = word_sep
        self.MORPHEME_BOUNDARY_PARSE = morpheme_sep
        self.GLOSS_BOUNDARY_PARSE = gloss_sep
        self.lastUsedAnnotationId = 0

    def il_element_for_string(self, text):
        arrT = text.split(" ")
        word = arrT[0]
        il = ""
        gloss = ""
        if len(arrT) > 1:
            il = arrT[1]
        if len(arrT) > 2:
            gloss = arrT[2]
        ilElement = [ "a%i" % self.get_next_annotation_id(), word, [] ]
        arrIl = regex.split(self.MORPHEME_BOUNDARY_PARSE, il)
        arrGloss = regex.split(self.MORPHEME_BOUNDARY_PARSE, gloss)
        for i in range(len(arrIl)):
            g = ""
            if i < len(arrGloss):
                g = arrGloss[i]
            arrG = regex.split(self.GLOSS_BOUNDARY_PARSE, g)
            arrG2 = []
            for g2 in arrG:
                arrG2.append([ "a%i" % self.get_next_annotation_id(), g2])
            ilElement[2].append([ "a%i" % self.get_next_annotation_id(), arrIl[i], arrG2 ])
        return ilElement


class DataStructureType(object):

    data_hierarchy = [ 'utterance', ['word'], 'translation']

    def __init__(self):
        self.flat_data_hierarchy = self._flatten_hierarchy_elements(self.data_hierarchy)
        self.nr_of_tiers = len(self.flat_data_hierarchy)

    def empty_element(self):
        return self._append_list(self.data_hierarchy)

    def _append_list(self, element):
        list = []
        for e in element:
            if type(element) is str or tpye(element) is unicode:
                list.append(['', '', ''])
            elif type(element) is list:
                l = cls._append_list(list)
                list.append(l)
        return list

    def _flatten_hierarchy_elements(self, elements):
        flat_elements = []
        for e in elements:
            if type(e) is str or type(e) is unicode:
                flat_elements.append(e)
            elif type(e) is list:
                flat_elements.extend(self._flatten_hierarchy_elements(e))
        return flat_elements

class DataStructureTypeGraid(DataStructureType):

    data_hierarchy = \
    [ 'utterance',
        [ 'phrase',
            [ 'word', 'wfw', 'graid1' ],
          'graid2' ],
      'translation', 'comment' ]
