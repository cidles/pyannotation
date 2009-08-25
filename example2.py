# (C) 2009 copyright by Peter Bouda
# -*- coding: utf-8 -*-

import pyannotation.kura.data
from lxml import etree

xml = pyannotation.kura.data.KuraXML('example_data/examples1.xml')

print etree.tostring(xml.tree)
