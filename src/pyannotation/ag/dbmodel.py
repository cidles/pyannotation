# (C) 2009 copyright by Peter Bouda
# -*- coding: utf-8 -*-
from elixir import *

metadata.bind = "sqlite:///movies.sqlite"
metadata.bind.echo = True

class AGSet(Entity):
    agsetid = Field(Unicode(50), primary_key=True)
    version = Field(Unicode(10))
    xmlns = Field(Unicode(30))
    xlink = Field(Unicode(30))
    ag = OneToMany('AG')
    timeline = OneToMany('Timeline')
    
class AG(Entity):
    agid = Field(Unicode(50), primary_key=True)
    type = Field(Unicode(10))
    agset = ManyToOne('AGSet')
    timeline = ManyToOne('Timeline')
    annotation = OneToMany('Annotation')
    anchor = OneToMany('Anchor')
    
class Timeline(Entity):
    timelineid = Field(Unicode(50), primary_key=True)
    agset = ManyToOne('AGSet')
    ag = OneToOne('AG')
    signal = OneToMany('Signal')
    
class Signal(Entity):
    signalid = Field(Unicode(50), primary_key=True)
    mimeclass = Field(Unicode(50))
    mimetype = Field(Unicode(50))
    encoding = Field(Unicode(50))
    unit = Field(Unicode(50))
    xlinktype = Field(Unicode(50))
    xlinkhref = Field(Unicode(50))
    track = Field(Unicode(50))
    timeline = ManyToOne('Timeline')
    
class Annotation(Entity):
    annotationid = Field(Unicode(50), primary_key=True)
    startanchor =  Field(Unicode(50)) #???
    endanchor =  Field(Unicode(50)) #???
    type = Field(Unicode(50))
    ag = ManyToOne('AG')
    
class Anchor(Entity):
    anchorid = Field(Unicode(50), primary_key=True)
    offset = Field(Float)
    unit = Field(Unicode(50))
    signals = Field(Unicode(50))
    ag = ManyToOne('AG')
