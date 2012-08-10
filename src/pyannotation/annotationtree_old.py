# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
"""This module contains the classes to access annotated data in
an annotation tree. An annotation tree is a tree-like structure,
dependant on the "data structure type". Data structure types are
for example "morpho-syntactic", "part-of-speech", "GRAID", ...

Depending on the data structure type the necessary annoations are
read from the input file. The class pyannotation.data.AnnotationFileObject
and sub-classes are used to read and write files.
"""

import pyannotation.elan.data
import pyannotation.toolbox.data
import pyannotation.data
import pickle
import regex
import operator

class AnnotationTree():
    """
    AnnotationTree tree-like structure constructor.

    """

    def __init__(self, data_structure_type):
        """Class's constructor

        """

        self.tree = []
        self._next_annotation_id = 0

        self.data_structure_type = data_structure_type

        if data_structure_type == pyannotation.data.GRAID:
            self.structure_type_handler = pyannotation.data.DataStructureTypeGraid()
        elif data_structure_type == pyannotation.data.MORPHSYNT:
            self.structure_type_handler = pyannotation.data.DataStructureTypeMorphsynt()

        self.filters = []
        self.filtered_element_ids = [[]]

    @property
    def next_annotation_id(self):
        """Returns the next annotation id.

        Returns
        -------
        _next_annotation_id : int
            The return result is the increment of the previous annotation
            id.

        """

        self._next_annotation_id += 1
        return self._next_annotation_id

    @next_annotation_id.setter
    def next_annotation_id(self, next_id):
        """Increment the id of the next_annotation_id.

        Parameters
        ----------
        next_id : int
            The next id value.

        Returns
        -------
        _next_annotation_id : int
            The return result is the increment of the previous annotation
            id.

        Raises
        ------
        TypeError
            If the next_id is not a int value type.

        """

        if type(next_id) is not int:
            raise(TypeError, "annotation ID must be int")
        self._next_annotation_id = next_id

    def save_tree_as_pickle(self, filepath):
        """Save the project annotation tree in a pickle
        file.

        Parameters
        ----------
        filepath : str
            The absolute path to a file.

        """

        file = open(filepath, "wb")
        pickle.dump(self.tree, file)
        file.close()

    def load_tree_from_pickle(self, filepath):
        """Load the project annotation tree from a pickle
        file.

        Parameters
        ----------
        filepath : str
            The absolute path to a file.

        """

        file = open(filepath, "rb")
        self.tree = pickle.load(file)
        file.close()

        #    def load_from_file(self, file_path):
    #         if self.file_type == pyannotation.data.EAF:
    #             self.annotation_file_object = pyannotation.elan.data.EafAnnotationFileObject(file_path)
    #         elif self.file_type == pyannotation.data.EAFFROMTOOLBOX:
    #             self.annotation_file_object = pyannotation.elan.data.EafFromToolboxAnnotationFileObject(file_path)
    #         elif self.file_type == pyannotation.data.TOOLBOX:
    #             self.annotation_file_object = pyannotation.toolbox.data.ToolboxAnnotationFileObject(file_path)
    #         else:
    #             raise(pyannotation.data.UnknownFileFormatException("File format {0} not supported.".format(self.file_type)))

    #    def parse(self):
    #        if self.parser:
    #            self.tree = self.parser.parse()
    #            self.reset_filters()
    #        else:
    #            raise(pyannotation.data.NoFileSpecifiedError())

    def append_element(self, element, update_ids = False):
        """Append an element to the annotation tree.

        Parameters
        ----------
        element : str
            Value of a field in the data structure annotation tree.
        update_ids: bool
            To update or not the ids of the annotation tree.

        """

        if update_ids:
            self.tree.append(self._update_ids_of_element(element))
        else:
            self.tree.append(element)

    def _update_ids_of_element(self, element):
        """Update the ids of the element in the annotation tree.

        Parameters
        ----------
        element : str
            Value of a field in the data structure annotation tree.

        Returns
        -------
        element_with_ids : array_like
            An array filled with the updated ids of the tree.

        """

        element_with_ids = []
        for e in element:
            if type(e) is dict:
                element_with_ids.append({ 'id': self.next_annotation_id, 'annotation': e['annotation'] })
            elif type(e) is list:
                element_with_ids.append(self._update_ids_of_element(e))
        return element_with_ids

    def empty_element(self):
        """Retrieve the array with the updated ids.

        Returns
        -------
        _update_ids_of_element : array_like
            The return result depends on the return of the called method.

        See Also
        --------
        _update_ids_of_element

        """

        empty_element = self.structure_type_handler.empty_element()
        return self._update_ids_of_element(empty_element)

    def append_empty_element(self):
        """Append an element with the ids.

        See Also
        --------
        empty_element

        """

        empty_element = self.empty_element()
        self.tree.append(empty_element)

    def elements(self):
        """Retrieve the elements of the tree.

        Returns
        -------
        e : array_like
            Return elements of the tree.

        """

        return (e for e in self.tree)

    def remove_element(self, id_element):
        """Remove an element with a certain id.

        Parameters
        ----------
        id_element : int
            Id of an element.

        Returns
        -------
        remove_element : bool
            Return an answer true or false.

        """

        for i, e in enumerate(self.tree):
            if e[0]['id'] == id_element:
                self.tree.pop(i)
                return True
        return False

    def insert_element(self, element, id_element, after = False,
                       update_ids = False):
        """Insert an element with a certain id.

        Parameters
        ----------
        element : str
            Value of a field in the data structure annotation tree.
        id_element : int
            Id of an element.
        after : bool
        update_ids: bool
            To update or not the ids of the annotation tree.

        Returns
        -------
        insert_element : bool
            Return an answer true or false.

        """

        if update_ids:
            element = self._update_ids_of_element(element)
        for i, e in enumerate(self.tree):
            if e[0]['id'] == id_element:
                if after:
                    self.tree.insert(i + 1, element)
                else:
                    self.tree.insert(i, element)
                return True
        return False

    def __len__(self):
        """Return the size of the tree, number of elements.

        Returns
        -------
        len(tree) : int
            Return the size of the tree, number of elements.

        """

        return len(self.tree)

    def append_filter(self, filter):
        """Append a filter to the search.

        Parameters
        ----------
        filter : str
            Value to set the fiter.

        """

        self.filters.append(filter)
        new_filtered_elements = [i
                                 for i, e in enumerate(self.tree)
                                 if i in self.filtered_element_ids[-1] and
                                    filter.element_passes_filter(e)]
        self.filtered_element_ids.append(new_filtered_elements)

    def last_filter(self):
        """Return the latest added filter.

        Returns
        -------
        filters = array_like
            An array with the filters.
        AnnotationTreeFilter : class
            Return the class AnnotationTreeFilter.

        """

        if len(self.filters) > 0:
            return self.filters[-1]
        else:
            return AnnotationTreeFilter()

    def update_last_filter(self, filter):
        """Update the last filter added.

        Parameters
        ----------
        filter : str
            Value to set the fiter.

        """

        self.pop_filter()
        self.append_filter(filter)

    def pop_filter(self):
        """Remove and return item at index.

        Returns
        -------
        filters.pop = str
            Item at index.

        """

        if len(self.filters) > 0:
            self.filtered_element_ids.pop()
            return self.filters.pop()
        return None

    def init_filters(self):
        """Initialize the filters array.

        """

        self.filters = []
        self.filtered_element_ids = [ range(len(self.tree)) ]

    def reset_filters(self):
        """Reset the filters array.

        """

        self.filtered_element_ids = [ range(len(self.tree)) ]
        for filter in self.filters:
            new_filtered_elements = [i for i, e in enumerate(self.tree)
                                     if i in self.filtered_element_ids[-1] and
                                        filter.element_passes_filter(e)]
            self.filtered_element_ids.append(new_filtered_elements)

    def as_html(self, filtered = False, html_frame = True):
        """Return the search result in a html page.

        Parameters
        ----------
        filtered : bool
            To know if the search if filtered or not.
        html_frame: bool
            Set or not the an html frame.

        Returns
        -------
        html = str
            Html page.

        """

        html = ""
        if html_frame:
            html = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /></head><body>\n"
        for i, element in enumerate(self.tree):
            if filtered and i not in self.filtered_element_ids[-1]:
                continue
            html += "<table>\n"
            table = [dict() for _ in range(len(
                self.data_structure_type.flat_data_hierarchy))]
            self._element_as_table(
                element, self.data_structure_type.data_hierarchy, table, 0)
            #print table
            for j, row in enumerate(table):
                html += "<tr>\n"
                if j == 0:
                    html += "<td rowspan=\"{0}\" "\
                            "class=\"element_id\">{1}</td>\n".format(
                        len(self.data_structure_type.flat_data_hierarchy), i)
                html += "<td class=\"ann_type\">{0}</td>".format(
                    self.data_structure_type.flat_data_hierarchy[j])
                for _, column in sorted(row.iteritems(), key=operator.itemgetter(0)):
                    html +=\
                    u"<td colspan=\"{0}\" class=\"{2}\">{1}</td>\n".format(
                        column[1], column[0],
                        self.data_structure_type.flat_data_hierarchy[j])
                html += "</tr>\n"
            html += "</table>\n"
        if html_frame:
            html += "</body></html>"
        return html

    def _element_as_table(self, elements, hierarchy, table, column):
        """Insert an element into a table.

        Parameters
        ----------
        elements : array_like
            An array with the elements.
        hierarchy: array_like
            An array with the data structure hierarchy.
        table : array_like
            Table number.
        column: int
            Column number.

        Returns
        -------
        inserted = int
            Number of elements inserted.

        """

        inserted = 0
        for i, t in enumerate(hierarchy):
            if type(t) is list:
                elements_list = elements[i]
                for i, e in enumerate(elements_list):
                    inserted += self._element_as_table(
                        e, t, table, column + i + inserted)
                inserted = inserted + len(elements_list) - 1
                merge_rows = [ r for r in hierarchy if type(r) is not list]
                for r in merge_rows:
                    row = self.data_structure_type.flat_data_hierarchy.index(r)
                    if column in table[row]:
                        table[row][column] = (table[row][column][0], inserted + 1)
                    else:
                        table[row][column] = (u"", inserted + 1)
            else:
                row = self.data_structure_type.flat_data_hierarchy.index(t)
                a = elements[i]["annotation"]
                if a == "":
                    a = "&nbsp;"
                    #if (column + 1) > len(table[row]):
                if column in table[row]:
                    table[row][column] = (a, table[row][column][1])
                else:
                    table[row][column] = (a, 1)

        return inserted


        ################## old API
#    def get_next_annotation_id(self):
#        return self.parser.get_next_annotation_id()
#
#    def add_tier(self, *args):
#        return self.parser.add_tier(*args)
#
#    def get_utterance_ids(self):
#        return [utterance[0] for utterance in self.tree]
#
#    def get_filtered_utterance_ids(self):
#        return self.filtered_itterance_ids[-1]
#
#    def get_utterance_ids_in_tier(self, id_tier=""):
#        return [utterance[0]
#                for utterance in self.tree if utterance[6] == id_tier]
#
#    def get_utterance_by_id(self, id_utterance):
#        for utterance in self.tree:
#            if utterance[0] == id_utterance:
#                return utterance[1]
#        return ''
#
#    def set_utterance(self, id_utterance, str_utterance):
#        for utterance in self.tree:
#            if utterance[0] == id_utterance:
#                utterance[1] = str_utterance
#                return True
#        return False
#
#    def get_translation_by_id(self, id_translation):
#        for utterance in self.tree:
#            for translation in utterance[3][0]:
#                if translation[0] == id_translation:
#                    return translation[1]
#        return ''
#
#    def new_translation_for_utterance_id(self, id_utterance, str_translation):
#        id_translation = None
#        for utterance in self.tree:
#            if utterance[0] == id_utterance:
#                id_translation = "a%i" % self.get_next_annotation_id()
#                utterance[3][0] = [ [ id_translation, str_translation ] ]
#        return id_translation
#
#    def set_translation(self, id_translation, str_translation):
#        for utterance in self.tree:
#            for translation in utterance[3][0]:
#                if translation[0] == id_translation:
#                    translation[1] = str_translation
#                    return True
#        return False
#
#    def get_word_by_id(self, id_word):
#        for utterance in self.tree:
#            for word in utterance[2]:
#                if word[0] == id_word:
#                    return word[1]
#        return ''
#
#    def get_word_ids_for_utterance(self, id_utterance):
#        for utterance in self.tree:
#            if utterance[0] == id_utterance:
#                return [w[0] for w in utterance[2]]
#        return []
#
#    def get_translations_for_utterance(self, id_utterance):
#        for utterance in self.tree:
#            if utterance[0] == id_utterance:
#                return utterance[3][0]
#        return ''
#
#    def get_morpheme_string_for_word(self, id_word):
#        m = [morpheme[1] for u in self.tree for w in u[2] if w[0] == id_word for morpheme in w[2]]
#        return self.MORPHEME_BOUNDARY_BUILD.join(m)
#
#    def il_element_for_string(self, text):
#        return self.parser.il_element_for_string(text)
#
#    def get_gloss_string_for_word(self, id_word):
#        l = []
#        for u in self.tree:
#            for w in u[2]:
#                if w[0] == id_word:
#                    for m in w[2]:
#                        f = [gloss[1] for gloss in m[2]]
#                        l.append(self.GLOSS_BOUNDARY_BUILD.join(f))
#        return self.MORPHEME_BOUNDARY_BUILD.join(l)
#
#    def set_il_element_for_word_id(self, id_word, il_element):
#        for u in self.tree:
#            for i in range(len(u[2])):
#                w = u[2][i]
#                if w[0] == id_word:
#                    # fill the new ilElement with old Ids, generate new Ids for new elements
#                    il_element[0] = id_word
#                    for j in range(len(il_element[2])):
#                        if j < len(w[2]) and w[2][j][0] != "":
#                            il_element[2][j][0] = w[2][j][0]
#                        else:
#                            il_element[2][j][0] = "a%i" % self.get_next_annotation_id()
#                        for k in range(len(il_element[2][j][2])):
#                            if j < len(w[2]) and k < len(w[2][j][2]) and w[2][j][2][k][0] != "":
#                                il_element[2][j][2][k][0] = w[2][j][2][k][0]
#                            else:
#                                il_element[2][j][2][k][0] = "a%i" % self.get_next_annotation_id()
#                    u[2][i] = il_element
#                    return True
#        return False
#
#    def remove_utterance_with_id(self, id_utterance):
#        i = 0
#        for utterance in self.tree:
#            if utterance[0] == id_utterance:
#                # found utterances, delete all elements from tree
#                for w in utterance[2]:
#                    for m in w[2]:
#                        for g in m[2]:
#                            self.parser.remove_annotation_with_id(g[0])
#                            self.parser.remove_annotations_with_ref(g[0])
#                        self.parser.remove_annotation_with_id(m[0])
#                        self.parser.remove_annotations_with_ref(m[0])
#                    self.parser.remove_annotation_with_id(w[0])
#                    self.parser.remove_annotations_with_ref(w[0])
#                for t in utterance[3][0]:
#                    self.parser.remove_annotation_with_id(t[0])
#                    self.parser.remove_annotations_with_ref(t[0])
#                self.parser.remove_annotation_with_id(id_utterance)
#                self.parser.remove_annotations_with_ref(id_utterance)
#                self.tree.pop(i)
#                return True
#            i += 1
#        return False
#
#    def remove_word_with_id(self, id_word):
#        for utterance in self.tree:
#            i = 0
#            for w in utterance[2]:
#                if w[0] == id_word:
#                    for m in w[2]:
#                        for g in m[2]:
#                            self.parser.remove_annotation_with_id(g[0])
#                            self.parser.remove_annotations_with_ref(g[0])
#                        self.parser.remove_annotation_with_id(m[0])
#                        self.parser.remove_annotations_with_ref(m[0])
#                    self.parser.remove_annotation_with_id(id_word)
#                    # link next word to prev, if those are there
#                    if i > 0 and len(utterance[2]) > (i+1):
#                        id_prevword = utterance[2][i-1][0]
#                        id_nextword = utterance[2][i+1][0]
#                        self.parser.update_prev_annotation_for_annotation(id_nextword, id_prevword)
#                        # remove link to this word if this is the first word and there is a second
#                    if i == 0 and len(utterance[2]) > 1:
#                        id_nextword = utterance[2][i+1][0]
#                        self.parser.update_prev_annotation_for_annotation(id_nextword)
#                    self.parser.remove_annotations_with_ref(id_word)
#                    utterance[2].pop(i)
#                    return True
#                i += 1
#        return False
#
#    def get_file(self, tier_utterances, tier_words, tier_morphemes, tier_glosses, tier_translations):
#        return self.parser.get_file(self.tree, tier_utterances, tier_words, tier_morphemes, tier_glosses, tier_translations)
#

class AnnotationTreeFilter():
    """
    AnnotationTreeFilter tree-like structure constructor.

    The main objective of this class is to make it possible
    to make searches in the AnnotationTree.

    """
    (AND, OR)  = range(2)

    def __init__(self, data_structure_type):
        """Class constructor.

        """

        self.data_structure_type = data_structure_type
        if data_structure_type == pyannotation.data.GRAID:
            self.structure_type_handler = pyannotation.data.DataStructureTypeGraid()

        self.filter = dict()
        for e in self.data_structure_type.flat_data_hierarchy:
            self.filter[e] = ""

        self.reset_match_object()
        self.inverted = False
        self.boolean_operation = self.AND
        self.contained_matches = False

    def reset_match_object(self):
        """Reset a match object.

        """

        self.matchobject = dict()
        for e in self.data_structure_type.flat_data_hierarchy:
            self.matchobject[e] = dict()

    def set_filter_for_type(self, ann_type, filter_string):
        """Set a filter for a given type.

        Parameters
        ----------
        ann_type : str
            Value of the field in the data structure hierarchy.
        filter_string: str
            String of the filter.

        """

        self.filter[ann_type] = filter_string

    #    def set_participant_filter(self, string):
    #        self.filter["participant"] = string
    #
    #    def set_locale_filter(self, string):
    #        self.filter["locale"] = string
    #
    #    def set_utterance_filter(self, string):
    #        self.filter["utterance"] = string
    #
    #    def set_word_filter(self, string):
    #        self.filter["word"] = string
    #
    #    def set_morpheme_filter(self, string):
    #        self.filter["morpheme"] = string
    #
    #    def set_pos_filter(self, string):
    #        self.filter["pos"] = string
    #
    #    def set_gloss_filter(self, string):
    #        self.filter["gloss"] = string
    #
    #    def set_translation_filter(self, string):
    #        self.filter["translation"] = string

    def set_inverted_filter(self, inverted):
        """Set the inverted value to a filter.

        Parameters
        ----------
        inverted : bool

        """

        self.inverted = inverted

    def set_contained_matches(self, contained_matches):
        """Set the contained matches for a filter.

        Parameters
        ----------
        contained_matches : bool

        """

        self.contained_matches = contained_matches

    def set_boolean_operation(self, type):
        """Set the operation type to the filter.

        Parameters
        ----------
        type : str
            Could be AND or OR

        """

        self.boolean_operation = type

    def element_passes_filter(self, element):
        """Verify if a specific element passes in through a filter.

        Parameters
        ----------
        type : str
            Could be AND or OR

        Returns
        -------
        passed : bool
            Passes or not.

        See also
        --------
        _passes_filter
        
        """

        #        utterance_match = False
        #        translation_match = False
        #        word_match = False
        #        morpheme_match = False
        #        gloss_match = False
        #
        #        element_passed = False

        # is there a filter defined?
        all_filter_empty = True
        for ann_type in self.filter.keys():
            if self.filter[ann_type] != "":
                all_filter_empty = False
        if all_filter_empty:
            return True

        #if self.filter["utterance"] == "" and self.filter["translation"] == "" and self.filter["word"] == "" and self.filter["morpheme"] == "" and self.filter["gloss"] == "":
        #    return True

        if self.boolean_operation == self.AND:
            passed = True
        else:
            passed = False

        passed = self._passes_filter(passed, element, self.data_structure_type.data_hierarchy)

        #        # filter by utterance
        #        if self.filter["utterance"] != "":
        #            match = regex.search(self.filter["utterance"], il_element[1])
        #            if match:
        #                self.matchobject["utterance"][il_element[0]] = [ [m.start(), m.end()] for m in regex.finditer(self.filter["utterance"], il_element[1]) ]
        #                utterance_match = True
        #        elif self.boolean_operation == self.AND:
        #            utterance_match = True
        #
        #        # filter by translation
        #        if self.filter["translation"] != "":
        #            for translation in il_element[3]:
        #                match = regex.search(self.filter["translation"], translation[1])
        #                if match:
        #                    self.matchobject["translation"][translation[0]] = \
        #                    [ [m.start(), m.end()] for m in regex.finditer(
        #                        self.filter["translation"], translation[1]) ]
        #                    translation_match = True
        #        elif self.boolean_operation == self.AND:
        #            translation_match = True
        #
        #        # filter by word
        #        for word in il_element[2]:
        #            if self.filter["word"] != "":
        #                match =  regex.search(self.filter["word"], word[1])
        #                if match:
        #                    self.matchobject["word"][word[0]] = True
        #                    word_match = True
        #
        #            elif self.boolean_operation == self.AND:
        #                word_match = True
        #
        #            # filter by morpheme
        #            if not self.contained_matches or word_match:
        #                for morpheme in word[2]:
        #                    if self.filter["morpheme"] != "":
        #                        match = regex.search(self.filter["morpheme"], morpheme[1])
        #                        if match:
        #                            self.matchobject["word"][word[0]] = True
        #                            morpheme_match = True
        #                    elif self.boolean_operation == self.AND:
        #                        morpheme_match = True
        #
        #                    # filter by gloss
        #                    if not self.contained_matches or morpheme_match:
        #                        if self.filter["gloss"] != "":
        #                            for gloss in morpheme[2]:
        #                                match = regex.search(self.filter["gloss"], gloss[1])
        #                                if match:
        #                                    self.matchobject["word"][word[0]] = True
        #                                    gloss_match = True
        #                        elif self.boolean_operation == self.AND:
        #                            gloss_match = True
        #
        #        ret = False
        #        if self.boolean_operation == self.AND:
        #            if utterance_match and translation_match and word_match and morpheme_match and gloss_match:
        #                ret = True
        #        elif self.boolean_operation == self.OR:
        #            if utterance_match or translation_match or word_match or morpheme_match or gloss_match:
        #                ret = True

        if self.inverted:
            passed = not passed

        return passed

    def _passes_filter(self, passed, elements, hierarchy):
        """Verify if a specific element passes in through a filter.

        Parameters
        ----------
        passed : bool
            Passes or not.
        elements : array_like
            An array of string values.
        hirerarchy : array_like
            Structure of the array.
        Returns
        -------
        passed : bool
            Passes or not.

        """

        for i, t in enumerate(hierarchy):
            if type(t) is list:
                elements_list = elements[i]
                local_passes = False
                for i, e in enumerate(elements_list):
                    passes = self._passes_filter(passed, e, t)
                    local_passes = (local_passes or passes)

                if self.boolean_operation == self.AND:
                    passed = (passed and local_passes)
                else:
                    passed = (passed or local_passes)
            else:
                passes = False
                if self.filter[t] != "":
                    match = regex.search(
                        self.filter[t], elements[i]["annotation"])
                    if match:
                        self.matchobject[t][elements[i]["id"]] =\
                        [ [m.start(), m.end()] for m in regex.finditer(
                            self.filter[t], elements[i]["annotation"]) ]
                        passes = True
                elif self.boolean_operation == self.AND:
                    passes = True

                if self.boolean_operation == self.AND:
                    passed = (passed and passes)
                else:
                    passed = (passed or passes)

        return passed

