# -*- coding: utf-8 -*-
# (C) 2011, 2012 copyright by Peter Bouda
"""This module contains the classes to access annotated data in
various formats.

The parsing is done by Builder classes for each file type, i.e.
Elan's .eaf files, Kura's .xml file, Toolbox's .txt files etc.
"""

#import regex
import re as regex

# file types
(EAF, EAFFROMTOOLBOX, KURA, TOOLBOX) = range(4)
class UnknownFileFormatError(Exception): pass
class NoFileSpecifiedError(Exception): pass

# data structure types
(WORDS, MORPHSYNT, GRAID) = range(3)
class UnknownDataStructureTypeError(Exception): pass
class DataStructureTypeNotSupportedError(Exception): pass
class UnknownAnnotationTypeError(Exception): pass

class AnnotationFileObject(object):

    def __init__(self, file_path):
        self.file_path = file_path

    def create_tier_handler(self):
        return None

    def create_parser(self, type):
        raise(
            DataStructureTypeNotSupportedError(
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
            ilElement[2].append(
                [ "a%i" % self.get_next_annotation_id(), arrIl[i], arrG2 ])
        return ilElement


class DataStructureType(object):

    data_hierarchy = [ 'utterance', ['word'], 'translation']

    def __init__(self):
        self.flat_data_hierarchy = self._flatten_hierarchy_elements(
            self.data_hierarchy)
        self.nr_of_types = len(self.flat_data_hierarchy)

    def get_siblings_of_type(self, ann_type):
        """
        Return all the siblings of a given type in the hierarchy
        including the given type itself.

        """
        if ann_type not in self.flat_data_hierarchy:
            raise UnknownAnnotationTypeError

        if ann_type in self.data_hierarchy:
            return [s for s in self.data_hierarchy if type(s) is str]

        for e in self.data_hierarchy:
            if type(e) is list:
                if ann_type in e:
                    return [s for s in e if type(s) is str]

    def get_parents_of_type(self, ann_type):
        """
        Returns all the elements that are above a given type in the type
        hierarchy.

        """
        if ann_type not in self.flat_data_hierarchy:
            raise UnknownAnnotationTypeError

        return self._get_parents_of_type_helper(ann_type, self.data_hierarchy)[1]

    def _get_parents_of_type_helper(self, ann_type, hierarchy):
        """Helper function for get_parents_of_type()"""
        parents = []
        found = False
        for e in hierarchy:
            if type(e) is list and not found:
                if ann_type in e:
                    found = True
                else:
                    found, add_parents = self._get_parents_of_type_helper(
                        ann_type, e)
                    if found:
                        parents += add_parents
            else:
                parents.append(e)
        return found, parents

    def empty_element(self):
        return self._append_list(self.data_hierarchy)

    def _append_list(self, element):
        ret = []
        for e in element:
            if type(e) is str or type(e) is unicode:
                ret.append({ 'id': None, 'annotation': '' })
            elif type(e) is list:
                l = self._append_list(e)
                ret.append([l])
        return ret

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
        [ 'clause unit',
            [ 'word', 'wfw', 'graid1' ],
          'graid2' ],
      'translation', 'comment' ]

class DataStructureTypeMorphsynt(DataStructureType):

    data_hierarchy =\
    [ 'utterance',
        [ 'word',
            [ 'morpheme',
                [ 'gloss'] ] ],
        'translation', 'comment' ]