# -*- coding: utf-8 -*-
# (C) 2011, 2012 copyright by Peter Bouda
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

class AnnotationTree(object):

    def __init__(self, structure_type, file_type = None, file_path = None):
        self.tree = []
        self.annotation_file_object = None
        self.parser = None
        self._next_annoation_id = 0

        self.file_type = file_type
        self.structure_type = structure_type

        if structure_type == pyannotation.data.GRAID:
            self.structure_type_handler = pyannotation.data.DataStructureTypeGraid()

        if file_type and file_path:
            self.load_from_file(file_path)
            self.parser = self.annotation_file_object.create_parser(structure_type)
            self.tier_handler = self.annotation_file_object.create_tier_handler()

        self.MORPHEME_BOUNDARY_BUILD = "-"
        self.GLOSS_BOUNDARY_BUILD = ":"

        self.filters = []
        self.filteredUtteranceIds = [[]]

    @property
    def next_annotation_id(self):
        self._next_annoation_id += 1
        return self._next_annoation_id

    def load_from_file(self, file_path):
         if self.file_type == pyannotation.data.EAF:
             self.annotation_file_object = pyannotation.elan.data.EafAnnotationFileObject(file_path)
         elif self.file_type == pyannotation.data.EAFFROMTOOLBOX:
             self.annotation_file_object = pyannotation.elan.data.EafFromToolboxAnnotationFileObject(file_path)
         elif self.file_type == pyannotation.data.TOOLBOX:
             self.annotation_file_object = pyannotation.toolbox.data.ToolboxAnnotationFileObject(file_path)
         else:
             raise(pyannotation.data.UnknownFileFormatException("File format {0} not supported.".format(self.file_type)))

    def parse(self):
        if self.parser:
            self.tree = self.parser.parse()
            self.reset_filters()
        else:
            raise(pyannotation.data.NoFileSpecifiedException())

    def append_element_without_ids(self, element):
        element_with_ids = self._add_ids_to_annotations(element)
        self.tree.append(element_with_ids)

    def _add_ids_to_annotations(self, elements):
        elements_with_ids = []
        for e in elements:
            if type(e) is str or type(e) is unicode:
                elements_with_ids.append({ 'id': self.next_annotation_id, 'annotation': e })
            elif type(e) is list:
                elements_with_ids.append(self._add_ids_to_annotations(e))
        return elements_with_ids

    def append_empty_element(self):
        empty_element = self.structure_type_handler.empty_element()
        self.tree.append(self._add_ids_to_annotations(empty_element))

    def elements(self):
        return (e for e in self.tree)

    ################## old API
    def get_next_annotation_id(self):
        return self.parser.get_next_annotation_id()

    def add_tier(self, *args):
        return self.parser.add_tier(*args)

    def get_utterance_ids(self):
        return [utterance[0] for utterance in self.tree]

    def get_filtered_utterance_ids(self):
        return self.filtered_itterance_ids[-1]

    def get_utterance_ids_in_tier(self, id_tier=""):
        return [utterance[0] for utterance in self.tree if utterance[6] == id_tier]

    def get_utterance_by_id(self, id_utterance):
        for utterance in self.tree:
            if utterance[0] == id_utterance:
                return utterance[1]
        return ''

    def set_utterance(self, id_utterance, str_utterance):
        for utterance in self.tree:
            if utterance[0] == id_utterance:
                utterance[1] = str_utterance
                return True
        return False

    def get_translation_by_id(self, id_translation):
        for utterance in self.tree:
            for translation in utterance[3][0]:
                if translation[0] == id_translation:
                    return translation[1]
        return ''

    def new_translation_for_utterance_id(self, id_utterance, str_translation):
        id_translation = None
        for utterance in self.tree:
            if utterance[0] == id_utterance:
                id_translation = "a%i" % self.get_next_annotation_id()
                utterance[3][0] = [ [ id_translation, str_translation ] ]
        return id_translation

    def set_translation(self, id_translation, str_translation):
        for utterance in self.tree:
            for translation in utterance[3][0]:
                if translation[0] == id_translation:
                    translation[1] = str_translation
                    return True
        return False

    def get_word_by_id(self, id_word):
        for utterance in self.tree:
            for word in utterance[2]:
                if word[0] == id_word:
                    return word[1]
        return ''

    def get_word_ids_for_utterance(self, id_utterance):
        for utterance in self.tree:
            if utterance[0] == id_utterance:
                return [w[0] for w in utterance[2]]
        return []

    def get_translations_for_utterance(self, id_utterance):
        for utterance in self.tree:
            if utterance[0] == id_utterance:
                return utterance[3][0]
        return ''

    def get_morpheme_string_for_word(self, id_word):
        m = [morpheme[1] for u in self.tree for w in u[2] if w[0] == id_word for morpheme in w[2]]
        return self.MORPHEME_BOUNDARY_BUILD.join(m)

    def il_element_for_string(self, text):
        return self.parser.il_element_for_string(text)

    def get_gloss_string_for_word(self, id_word):
        l = []
        for u in self.tree:
            for w in u[2]:
                if w[0] == id_word:
                    for m in w[2]:
                        f = [gloss[1] for gloss in m[2]]
                        l.append(self.GLOSS_BOUNDARY_BUILD.join(f))
        return self.MORPHEME_BOUNDARY_BUILD.join(l)

    def set_il_element_for_word_id(self, id_word, il_element):
        for u in self.tree:
            for i in range(len(u[2])):
                w = u[2][i]
                if w[0] == id_word:
                    # fill the new ilElement with old Ids, generate new Ids for new elements
                    il_element[0] = id_word
                    for j in range(len(il_element[2])):
                        if j < len(w[2]) and w[2][j][0] != "":
                            il_element[2][j][0] = w[2][j][0]
                        else:
                            il_element[2][j][0] = "a%i" % self.get_next_annotation_id()
                        for k in range(len(il_element[2][j][2])):
                            if j < len(w[2]) and k < len(w[2][j][2]) and w[2][j][2][k][0] != "":
                                il_element[2][j][2][k][0] = w[2][j][2][k][0]
                            else:
                                il_element[2][j][2][k][0] = "a%i" % self.get_next_annotation_id()
                    u[2][i] = il_element
                    return True
        return False

    def remove_utterance_with_id(self, id_utterance):
        i = 0
        for utterance in self.tree:
            if utterance[0] == id_utterance:
                # found utterances, delete all elements from tree
                for w in utterance[2]:
                    for m in w[2]:
                        for g in m[2]:
                            self.parser.remove_annotation_with_id(g[0])
                            self.parser.remove_annotations_with_ref(g[0])
                        self.parser.remove_annotation_with_id(m[0])
                        self.parser.remove_annotations_with_ref(m[0])
                    self.parser.remove_annotation_with_id(w[0])
                    self.parser.remove_annotations_with_ref(w[0])
                for t in utterance[3][0]:
                    self.parser.remove_annotation_with_id(t[0])
                    self.parser.remove_annotations_with_ref(t[0])
                self.parser.remove_annotation_with_id(id_utterance)
                self.parser.remove_annotations_with_ref(id_utterance)
                self.tree.pop(i)
                return True
            i += 1
        return False

    def remove_word_with_id(self, id_word):
        for utterance in self.tree:
            i = 0
            for w in utterance[2]:
                if w[0] == id_word:
                    for m in w[2]:
                        for g in m[2]:
                            self.parser.remove_annotation_with_id(g[0])
                            self.parser.remove_annotations_with_ref(g[0])
                        self.parser.remove_annotation_with_id(m[0])
                        self.parser.remove_annotations_with_ref(m[0])
                    self.parser.remove_annotation_with_id(id_word)
                    # link next word to prev, if those are there
                    if i > 0 and len(utterance[2]) > (i+1):
                        id_prevword = utterance[2][i-1][0]
                        id_nextword = utterance[2][i+1][0]
                        self.parser.update_prev_annotation_for_annotation(id_nextword, id_prevword)
                        # remove link to this word if this is the first word and there is a second
                    if i == 0 and len(utterance[2]) > 1:
                        id_nextword = utterance[2][i+1][0]
                        self.parser.update_prev_annotation_for_annotation(id_nextword)
                    self.parser.remove_annotations_with_ref(id_word)
                    utterance[2].pop(i)
                    return True
                i += 1
        return False

    def get_file(self, tier_utterances, tier_words, tier_morphemes, tier_glosses, tier_translations):
        return self.parser.get_file(self.tree, tier_utterances, tier_words, tier_morphemes, tier_glosses, tier_translations)

    def append_filter(self, filter):
        self.filters.append(filter)
        new_filtered_utterances = [utterance[0] for utterance in self.tree if utterance[0] in self.filtered_utterance_ids[-1] and filter.utterance_passes_filter(utterance)]
        self.filtered_utterance_ids.append(new_filtered_utterances)

    def last_filter(self):
        if len(self.filters) > 0:
            return self.filters[-1]
        else:
            return AnnotationTreeFilter()

    def update_last_filter(self, filter):
        self.pop_filter()
        self.append_filter(filter)

    def pop_filter(self):
        if len(self.filters) > 0:
            self.filtered_utterance_ids.pop()
            return self.filters.pop()
        return None

    def clear_filters(self):
        self.filters = []
        self.filtered_utterance_ids = [self.get_utterance_ids()]

    def reset_filters(self):
        self.filtered_utterance_ids = [self.get_utterance_ids()]
        for filter in self.filters:
            new_filtered_utterances = [utterance[0] for utterance in self.tree if utterance[0] in self.filtered_utterance_ids[-1] and filter.utterancePassesFilter(utterance)]
            self.filtered_utterance_ids.append(new_filtered_utterances)


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
        self.reset_match_object()
        self.inverted = False
        self.boolean_operation = self.AND
        self.contained_matches = False

    def reset_match_object(self):
        self.matchobject = {
            "utterance" : {},
            "translation" : {},
            "word" : {}
        }

    def set_participant_filter(self, string):
        self.filter["participant"] = string

    def set_locale_filter(self, string):
        self.filter["locale"] = string

    def set_utterance_filter(self, string):
        self.filter["utterance"] = string

    def set_word_filter(self, string):
        self.filter["word"] = string

    def set_morpheme_filter(self, string):
        self.filter["morpheme"] = string

    def set_pos_filter(self, string):
        self.filter["pos"] = string

    def set_gloss_filter(self, string):
        self.filter["gloss"] = string

    def set_translation_filter(self, string):
        self.filter["translation"] = string

    def set_inverted_filter(self, inverted):
        self.inverted = inverted

    def set_contained_matches(self, contained_matches):
        self.contained_matches = contained_matches

    def set_boolean_operation(self, type):
        self.boolean_operation = type

    def utterance_passes_filter(self, il_element):
        utterance_match = False
        translation_match = False
        word_match = False
        morpheme_match = False
        gloss_match = False

        # is there a filter defined?
        if self.filter["utterance"] == "" and self.filter["translation"] == "" and self.filter["word"] == "" and self.filter["morpheme"] == "" and self.filter["gloss"] == "":
            return True

        # filter by utterance
        if self.filter["utterance"] != "":
            match = regex.search(self.filter["utterance"], il_element[1])
            if match:
                self.matchobject["utterance"][il_element[0]] = [ [m.start(), m.end()] for m in regex.finditer(self.filter["utterance"], il_element[1]) ]
                utterance_match = True
        elif self.boolean_operation == self.AND:
            utterance_match = True

        # filter by translation
        if self.filter["translation"] != "":
            for translation in il_element[3]:
                match = regex.search(self.filter["translation"], translation[1])
                if match:
                    self.matchobject["translation"][translation[0]] = [ [m.start(), m.end()] for m in regex.finditer(self.filter["translation"], translation[1]) ]
                    translation_match = True
        elif self.boolean_operation == self.AND:
            translation_match = True

        # filter by word
        for word in il_element[2]:
            if self.filter["word"] != "":
                match =  regex.search(self.filter["word"], word[1])
                if match:
                    self.matchobject["word"][word[0]] = True
                    word_match = True

            elif self.boolean_operation == self.AND:
                word_match = True

            # filter by morpheme
            if not self.contained_matches or word_match:
                for morpheme in word[2]:
                    if self.filter["morpheme"] != "":
                        match = regex.search(self.filter["morpheme"], morpheme[1])
                        if match:
                            self.matchobject["word"][word[0]] = True
                            morpheme_match = True
                    elif self.boolean_operation == self.AND:
                        morpheme_match = True

                    # filter by gloss
                    if not self.contained_matches or morpheme_match:
                        if self.filter["gloss"] != "":
                            for gloss in morpheme[2]:
                                match = regex.search(self.filter["gloss"], gloss[1])
                                if match:
                                    self.matchobject["word"][word[0]] = True
                                    gloss_match = True
                        elif self.boolean_operation == self.AND:
                            gloss_match = True

        ret = False
        if self.boolean_operation == self.AND:
            if utterance_match and translation_match and word_match and morpheme_match and gloss_match:
                ret = True
        elif self.boolean_operation == self.OR:
            if utterance_match or translation_match or word_match or morpheme_match or gloss_match:
                ret = True

        if self.inverted:
            ret = not ret

        return ret
