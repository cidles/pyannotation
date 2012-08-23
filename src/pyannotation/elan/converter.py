# (C) 2009 copyright by Peter Bouda
# -*- coding: utf-8 -*-
"""
A class to convert Elan's .eaf files to other formats.
"""
__author__ =  'Peter Bouda'
__version__=  '0.1.1'

import os
from lxml import etree
from StringIO import StringIO

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

class Convert(object):
    def __init__(self):
        pass
        
    def toAg(text):
        """
        Convert an Elan XML string to a Annotation Graph XML string.
        Call this as a static function:
        
        ag_xml = pyannotation.elan.converter.Convert.toAg(elan_xml)

        """
        xsl_path = os.path.join(os.path.dirname(__file__), '..',  'xsl', 'elan2ag.xsl')
        xslt_doc = etree.parse(xsl_path)
        transform = etree.XSLT(xslt_doc)
        document = etree.parse(StringIO(text.encode('utf-8')))
        result = transform(document)
        result = str(result)
        result = result.decode('utf-8')
        return result
 
    toAg = Callable(toAg)
 
