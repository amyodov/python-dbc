#!/usr/bin/env python
"""Design by Contract capabilities in Python.

This project enables to use the basics of Design by Contract capabilities in Python,
such as enforcing the contracts defined in the epydoc code documentation.

For the most important functionality of this module, you must have epydoc installed.
Please refer to epydoc site or your Unix/Linux distribution regarding the installation details.
"""
try:
    from setuptools import setup
except:
    from distutils.core import setup


from contrib.distutils_googlecode_upload.googlecode_distutils_upload import upload as googlecode_upload
from contrib.wikir.commands import publish_wiki

# Classifiers as in http://pypi.python.org/pypi?:action=list_classifiers
CLASSIFIERS = """\
Development Status :: 2 - Pre-Alpha
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Topic :: Software Development
Topic :: Software Development :: Documentation
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Quality Assurance
Topic :: Software Development :: Testing
"""

setup(
    name = "dbc",
    version = "0.1",
    description = __doc__.split("\n", 1)[0],
    long_description = __doc__.split("\n", 2)[-1],
    author = "Alexander Myodov",
    author_email = "amyodov@gmail.com",
    url = "http://code.google.com/p/python-dbc/",
    packages = ["dbc",],
    classifiers = [c for c in CLASSIFIERS.split("\n") if c],
    license = "New BSD License",
    platforms = ["any"],
    cmdclass = {"googlecode_upload" : googlecode_upload,
                "publish_wiki"      : publish_wiki,}
)
