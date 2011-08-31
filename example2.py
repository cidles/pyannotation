#!/usr/bin/env python3
# (C) 2011 copyright by Peter Bouda
# -*- coding: utf-8 -*-

import pyannotation.kura.data

tree = pyannotation.kura.data.KuraTree('example_data/examples1.xml')
tree.parse()
print(tree.tree)
#print etree.tostring(xml.tree)
