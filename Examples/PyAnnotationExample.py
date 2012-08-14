# -*- coding: utf-8 -*-
# (C) 2012 copyright by Ant�nio Lopes, CIDLeS

from pyannotation import annotationtree
from pyannotation import data

import pickle

# Initialize the variable
annotation_tree = annotationtree.AnnotationTree(data.GLOSS)

# Open the file
file = open('C:\TESTS\Balochi Text1.pickle', "rb")
annotation_tree.tree = pickle.load(file)

# Verify the elements
for element in annotation_tree.elements():
    print(element)
    print("\n")