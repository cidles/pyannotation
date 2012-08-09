# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT

"""This module contains the classes to access annotated data in
various formats.

The parsing is done by Builder classes for each file type, i.e.
Elan's .eaf files, Kura's .xml file, Toolbox's .txt files etc.
"""

import re as regex

# File types
(EAF, EAFFROMTOOLBOX, KURA, TOOLBOX, TREEPICKLE) = range(5)

# Data structure types
(GLOSS, WORDS, GRAID) = range(3)

class UnknownFileFormatError(Exception): pass
class NoFileSpecifiedError(Exception): pass

# Data structure types
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
    """
    Interface of the Builders.

    Methods
    -------
    __init__(annotation_file_object, annotation_file_tiers)
        Class's constructor.
    get_next_annotation_id()
        Return the next annotation.
    parse()
        Interface method.
    get_file(tree=AnnotationTree)
        Interface method.
    remove_annotation_with_id(id_annotation=1)
        Interface method.
    def remove_annotations_with_ref(id_ref_ann=1):
        Interface method.
    update_prev_annotation_for_annotation(id_annotation=1, id_prev_ann=None):
        Interface method.

    """

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
    """
    Annotation file parser using Morphsyntax.

    Methods
    -------
    __init__()
        Class's constructor.
    il_element_for_string(text='Example text.')
        Return an array of words from a text.

    """

    def __init__(self, annotation_file_object, annotation_file_tiers,
                 word_sep = r"[ \n\t\r]+", morpheme_sep = r"[-]",
                 gloss_sep = r"[:]"):
        """Class's constructor.

        ...

        """

        AnnotationFileParser.__init__(self, annotation_file_object, annotation_file_tiers)
        self.WORD_BOUNDARY_PARSE = word_sep
        self.MORPHEME_BOUNDARY_PARSE = morpheme_sep
        self.GLOSS_BOUNDARY_PARSE = gloss_sep
        self.lastUsedAnnotationId = 0

    def il_element_for_string(self, text):
        """Separate the text in words and add them to an array.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.

        Returns
        -------
        ilElement : array_like
            An array with the subelements of the text.

        """

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
    """
    Data structure type constructor.

    Attributes
    ----------
    name : string
        Name of the structure.
    data_hirerarchy : array
        Structure of the array.

    Methods
    -------
    __init__()
        Class's constructor.
    get_siblings_of_type(ann_type='utterance')
        Return all the siblings of a given type in the hierarchy.
    get_parents_of_type(ann_type='utterance')
        Returns all the elements that are above a given type in the type
        hierarchy.
    _get_parents_of_type_helper(
            ann_type='utterance',
            hierarchy=[ 'utterance', ['word'], 'translation'])
        Helper function for get_parents_of_type().
    empty_element()
        Return the appended list of a certain data hierarchy.
    _append_list(element='word')
        Append element values and it's ids to the data structure elements.
    _flatten_hierarchy_elements(elements=['word1','word2'])
        Flat the elements appended to a new list of elements.

    """

    name = "WORDS"

    data_hierarchy = [ 'utterance', ['word'], 'translation']

    def __init__(self):
        """Class's constructor.

        ...

        """

        self.flat_data_hierarchy = self._flatten_hierarchy_elements(
            self.data_hierarchy)
        self.nr_of_types = len(self.flat_data_hierarchy)

    def get_siblings_of_type(self, ann_type):
        """Return all the siblings of a given type in the hierarchy
        including the given type itself.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.

        Returns
        -------
        ann_type : str
            Value of the field in the data structure hierarchy if
            exist.

        Raises
        ------
        UnknownAnnotationTypeError
            If the ann_type doesn't exist.

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
        """Returns all the elements that are above a given type in the type
        hierarchy.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.

        Returns
        -------
        _get_parents_of_type_helper : array_like
            The return result depends on the return of the called method.

        See Also
        --------
        _get_parents_of_type_helper

        """

        if ann_type not in self.flat_data_hierarchy:
            raise UnknownAnnotationTypeError

        return self._get_parents_of_type_helper(ann_type, self.data_hierarchy)[1]

    def _get_parents_of_type_helper(self, ann_type, hierarchy):
        """Helper function for get_parents_of_type.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.
        hierarchy: array_like
            An array that contains the data structure hierarchy.

        Returns
        -------
        found : array_like
            The actual list with the appended elements.
        parents : array_like
            The actual list with the appended elements.

        """

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
        """Return the appended list of a certain data hierarchy.

        Returns
        -------
        _append_list : array_like
            The actual list with the appended elements.

        """

        return self._append_list(self.data_hierarchy)

    def _append_list(self, element):
        """Append element values and it's ids to the data structure elements.

        Parameters
        ----------
        element : str

        Returns
        -------
        ret : array_like
            A list with appended `element`values.

        """

        ret = []
        for e in element:
            if type(e) is str or type(e) is unicode:
                ret.append({ 'id': None, 'annotation': '' })
            elif type(e) is list:
                l = self._append_list(e)
                ret.append([l])
        return ret

    def _flatten_hierarchy_elements(self, elements):
        """Flat the elements appended to a new list of elements.

        Parameters
        ----------
        elements : array_like
            An array of string values.

        Returns
        -------
        flat_elements : array_like
            An array of faltten `elements`.

        """

        flat_elements = []
        for e in elements:
            if type(e) is str or type(e) is unicode:
                flat_elements.append(e)
            elif type(e) is list:
                flat_elements.extend(self._flatten_hierarchy_elements(e))
        return flat_elements

class DataStructureTypeGraid(DataStructureType):

    """
    Data structure type using a GRAID format.

    Attributes
    ----------
    name : str
        Name of the structure.
    data_hirerarchy : array
        Structure of the array.

    """

    name = "GRAID"

    data_hierarchy = \
    [ 'utterance',
        [ 'clause unit',
            [ 'word', 'wfw', 'graid1' ],
          'graid2' ],
      'translation', 'comment' ]

class DataStructureTypeMorphsynt(DataStructureType):

    """
    Data structure type using a Morphsyntax format.

    Attributes
    ----------
    name : str
        Name of the structure.
    data_hirerarchy : array
        Structure of the array.

    """

    name = "MORPHSYNT"

    data_hierarchy =\
    [ 'utterance',
        [ 'word',
            [ 'morpheme',
                [ 'gloss'] ] ],
        'translation', 'comment' ]