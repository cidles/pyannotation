# -*- coding: utf-8 -*-
# (C) 2012 copyright by Peter Bouda
"""
The corpus module contains classes to handle collections of work items
(currently: annotation trees; later: annotation graphs). It connects those
work items to files on disk to keep track of the corpus the user works with.
Each class provides a simple list of items to go through all work items for
queries and updates. The queries and updates are handle by the classes of the
work items.
"""

import pyannotation

class CorpusTrees():

    def __init__(self, data_structure_type):
        self.items = []
        self.data_structure_type = data_structure_type

    def add_item(self, filepath, filetype):
        if filetype == pyannotation.data.TREEPICKLE:
            annotation_tree = pyannotation.annotationtree.AnnotationTree(self.data_structure_type)
            annotation_tree.load_tree_from_pickle(filepath)
        else:
            raise pyannotation.data.UnknownFileFormatError()
