from distutils.core import setup
setup(name='pyannotation',
      version='0.3.0',
      description='Python Linguistic Annotation Library',
      long_description='PyAnnotation is a Python Library to access and manipulate linguistically annotated corpus files. Supported file format is currently only Elan XML, with Kura XML and Toolbox files support planned for future releases. A Corpus Reader API is provided to support statistical analysis within the Natural Language Toolkit. ',
      author='Peter Bouda',
      author_email='pbouda@cidles.eu',
      url='http://www.cidles.eu/ltll/poio-pyannotation',
      packages=[ 'pyannotation', 'pyannotation.ag', 'pyannotation.elan', 'pyannotation.kura', 'pyannotation.toolbox' ],
      package_dir={'pyannotation': 'src/pyannotation'},
      package_data={'pyannotation': ['xsl/*.xsl', 'xsd/*.xsd']},
      )
