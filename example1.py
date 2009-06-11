import pyannotation.elan.data

cr = pyannotation.elan.data.EafCorpusReader('example_data')

# find all (unique) sentences that contain a morpheme with gloss "ANOM"
result = [s for s in cr.tagged_sents() for (word, tag) in s for (morphem, gloss) in tag if 'ANOM' in gloss and s not in locals()['_[1]']]
print result

# get a list of sentences of the result
sents = [[w for (w, t) in s] for s in result]
print sents

# get a list of tagged words of the result
tagged_words = [(w,t) for s in result for (w, t) in s]
print tagged_words

# get a list of tagged morphemes of the result
tagged_morphemes = [(m,g) for s in result for (w,t) in s for (m,g) in t]
print tagged_morphemes

# NLTK concordance
import nltk.text
text = nltk.text.Text(cr.words())
text.concordance('bir') # find concordance for turkish "bir"
