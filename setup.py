from setuptools import setup
import os, io

from sinutils import __version__

here = os.path.abspath(os.path.dirname(__file__))
README = io.open(os.path.join(here, 'README.md'), encoding='UTF-8').read()
CHANGES = io.open(os.path.join(here, 'CHANGES.md'), encoding='UTF-8').read()
setup(name="sinutils",
      version=__version__,
      keywords=('utils'),
      description="A Python Utitlity Modules containing various useful functions.",
      long_description=README + '\n\n\n' + CHANGES,
      long_description_content_type="text/markdown",
      url='https://github.com/sintrb/sinutils/',
      author="trb",
      author_email="sintrb@gmail.com",
      packages=['sinutils'],
      zip_safe=False
      )
