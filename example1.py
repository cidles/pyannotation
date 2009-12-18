# (C) 2009 copyright by Peter Bouda
# -*- coding: utf-8 -*-

import pyannotation.corpusreader
import glob, os

cr = pyannotation.corpusreader.GlossCorpusReader()
files = glob.glob(os.path.join("example_data", "*.eaf"))

for f in files:
    print "add %s to corpus reader..." % f
    cr.addFile(f, pyannotation.data.EAF)

# find all (unique) sentences that contain a morpheme with gloss "ANOM"
print "\nfind all (unique) sentences that contain a morpheme with gloss \"ANOM\":"
result = [s for s in cr.taggedSents() for (word, tag) in s for (morphem, gloss) in tag if 'ANOM' in gloss and s not in locals()['_[1]']]
print result

# get a list of sentences from the result
print "\nget a list of sentences from the result:"
sents = [[w for (w, t) in s] for s in result]
print sents

# get a list of tagged words from the result
print "\nget a list of tagged words from the result:"
tagged_words = [(w,t) for s in result for (w, t) in s]
print tagged_words

# get a list of tagged morphemes from the result
print "\nget a list of tagged morphemes from the result:"
tagged_morphemes = [(m,g) for s in result for (w,t) in s for (m,g) in t]
print tagged_morphemes

# find all sentences with a translation containing "house"
print "\nfind all sentences with a translation containing \"house\":"
import re
result2 = [(s, translations) for (s, translations) in cr.taggedSentsWithTranslations() for t in translations if re.search(r"\bhome\b", t[1])]
print result2

# NLTK concordance
print "\nNLTK concordance for word \"bir\":"
import nltk.text
text = nltk.text.Text(cr.words())
text.concordance('bir') # find concordance for turkish "bir"
