# (C) 2009 copyright by Peter Bouda
# -*- coding: utf-8 -*-

import pyannotation.kura.data
from lxml import etree

tree = pyannotation.kura.data.KuraTree('example_data/examples1.xml')
tree.parse()
print tree.tree
#print etree.tostring(xml.tree)
