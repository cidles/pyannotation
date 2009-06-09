from distutils.core import setup
setup(name='pyannotation',
      version='0.1.0',
      description='Python Linguistic Annotation Library',
      author='Peter Bouda',
      author_email='p.bouda@gmx.de',
      url='http://www.peterbouda.de/downloads/pyannotation',
      packages=[ 'pyannotation', 'pyannotation.ag', 'pyannotation.elan', 'pyannotation.kura' ],
      package_dir={'pyannotation': 'src/pyannotation'},
      package_data={'pyannotation': ['xsl/*.xsl', 'xsd/*.xsd']},
      )
