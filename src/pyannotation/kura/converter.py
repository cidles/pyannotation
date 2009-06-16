# (C) 2009 copyright by Peter Bouda
# -*- coding: utf-8 -*-
"""
A class to convert Kura XML files to other formats.
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
        
    def toHtmllgr(text):
        """
        Convert a Kura XML string to a HTML string, displayed
        as an interlinear text.
        Call this as a static function:
        
        html = pyannotation.elan.converter.Convert.toHtmllgr(kura_xml)

        """
        xsl_path = os.path.join(os.path.dirname(__file__), '..',  'xsl', 'kura2htmllgr.xsl')
        xslt_doc = etree.parse(xsl_path)
        transform = etree.XSLT(xslt_doc)
        document = etree.parse(StringIO(text.encode('utf-8')))
        result = transform(document)
        result = str(result)
        result = result.decode('utf-8')
        return result
        
    def toTextwolines(text):
        """
        Convert a Kura XML string to a Tex string, displayed
        as an interlinear text.
        Call this as a static function:
        
        html = pyannotation.elan.converter.Convert.toTextwolines(kura_xml)

        """
        xsl_path = os.path.join(os.path.dirname(__file__), '..', 'xsl', 'kura2textwolines.xsl')
        xslt_doc = etree.parse(xsl_path)
        transform = etree.XSLT(xslt_doc)
        document = etree.parse(StringIO(text.encode('utf-8')))
        result = transform(document)
        result = str(result)
        result = result.decode('utf-8')
        return result

    toHtmllgr = Callable(toHtmllgr)
    toTextwolines = Callable(toTextwolines)
 
