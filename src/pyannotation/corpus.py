# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: Peter Bouda <pbouda@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
"""
The corpus module contains classes to handle collections of work items
(currently: annotation trees; later: annotation graphs). It connects those
work items to files on disk to keep track of the corpus the user works with.
Each class provides a simple list of items to go through all work items for
queries and updates. The queries and updates are handle by the classes of the
work items.
"""

from __future__ import unicode_literals

from pyannotation import data
from pyannotation import annotationtree

class CorpusTrees():

    def __init__(self, data_structure_type):
        self.items = []
        self.data_structure_type = data_structure_type

    def add_item(self, filepath, filetype):
        if filetype == data.TREEPICKLE:
            annotation_tree = annotationtree.AnnotationTree(self.data_structure_type)
            annotation_tree.load_tree_from_pickle(filepath)
            annotation_tree.init_filters()
            self.items.append( (filepath, annotation_tree) )
        else:
            raise data.UnknownFileFormatError()
