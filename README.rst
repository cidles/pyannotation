Python Linguistic Annotation Libary
===================================
PyAnnotation is a Python Library to access and manipulate linguistically
annotated corpus files. Supported file format is currently only Elan XML,
with Kura XML and Toolbox files support planned for future releases. A
Corpus Reader API is provided to support statistical analysis within the
Natural Language Toolkit.
The software is licensed under the GNU General Public License. 


REQUIREMENTS
============
You need to install the following packages:

- Python: http://python.org/download
- If you want to process data with NLTK: http://www.nltk.org/download


INSTALLATION
============
To install PyAnnotation on Windows just start the .exe file you downloaded and
follow the instructions in the setup process.
To install PyAnnotation on Linux, Unix and other platforms you need to unpack
the file and start "setup.py" on the command line. Change to the directory
into which you downloaded the package and unpack it::

  $ tar xzf pyannotation-x.y.z.tar.gz
  $ cd pyannotation-x.y.z

Then, to install the package locally into your python repository (you may need
to have root privileges)::

  $ python setup.py install

The installation process will give you feedback and should finish without
errors.


BASIC USAGE
===========
Here are a few examples what you can do with PyAnnotation. All the examples
process Elan files which are stored in one directory, the directory here is
"example_data" which is part of the package you downloaded. The package also
contains a sample script "example1.py" that runs all the commands presented
here, so you might just call "python example1.py" and see all the results on
your own computer at once. First, start a python interpreter and import
pyanntation for Elan::

  $ python
  Python 2.6.2 (release26-maint, Apr 19 2009, 01:56:41) 
  [GCC 4.3.3] on linux2
  Type "help", "copyright", "credits" or "license" for more information.

First, import the corpus reader module:

>>> import pyannotation.corpusreader

Then load create a corpus reader and load a file into your corpus. The
second argument to the addFile method is the file type (.eaf here):

>>> cr = pyannotation.corpusreader.GlossCorpusReader()
>>> cr.addFile("example_data/turkish.eaf", pyannotation.data.EAF)

To get all sentences with their tags that have a gloss "ANOM" (here: tags
are morphemes and their glosses stored in a kind of tree):

>>> result = [s for s in cr.tagged_sents() for (word, tag) in s
...             for (morphem, gloss) in tag
...             if 'ANOM' in gloss and s not in locals()['_[1]']]
>>> print result
[[('eve', [('ev', ['home']), ('e', ['DIR'])]), ('geldi\xc4\x9fimde', ...

Only the sentences of the result:

>>>sents = [[w for (w, t) in s] for s in result]
>>> print sents
[['eve', 'geldi\xc4\x9fimde', 'ya\xc4\x9fmur',  ...

A word list from the result:

>>> tagged_words = [(w,t) for s in result for (w, t) in s]
>>> print tagged_words
[('eve', [('ev', ['home']), ('e', ['DIR'])]), ('geldi\xc4\x9fimde', ...

A list of morphemes and their tags from the result:

>>> tagged_morphemes = [(m,g) for s in result for (w,t) in s for (m,g) in t]
>>> print tagged_morphemes
[('ev', ['home']), ('e', ['DIR']), ('gel', ['come']), ('di\xc4\x9f', ...

Another query: find all sentences that contain a certain word (here: "home")
in their translation:

>>> import re
>>> result2 = [(s, translations) 
...            for (s, translations) in cr.tagged_sents_with_translations() 
...            for t in translations if re.search(r"\bhome\b", t)]
>>> print result2
[([('d\xc3\xbcn', [('d\xc3\xbcn', ['yesterday'])]), ('ak\xc5\x9fam', ...

And, last but not least, use your Elan corpus with NLTK. An example to get the
concordance for the word "bir" (turkish for "one"):

>>> import nltk.text
>>> text = nltk.text.Text(cr.words())
>>> text.concordance('bir') # find concordance for turkish "bir"
Building index...
Displaying 2 of 2 matches:
 daha rahat ederdim çünkü içimden bir ses yeter artık çalışma derken bi
ir ses yeter artık çalışma derken bir diğer ses de çalışmam gerektiğin


Just try it out for yourself what you can do with the data. PyAnnotation's
corpus reader for .eaf files has the following access methods for data::

  # I{corpus}.mophemes()
  # I{corpus}.words()
  # I{corpus}.sents()
  # I{corpus}.sents_with_translations()
  
  # I{corpus}.tagged_morphemes()
  # I{corpus}.tagged_words()
  # I{corpus}.tagged_sents()
  # I{corpus}.tagged_sents_with_translations()

More documentation is available at:

http://www.cidles.eu/doc/pyannotation/index.html


SITE
====
The website of this project is:

http://www.cidles.eu/ltll/poio-pyannotation
