#!/usr/bin/env python

import os
import glob
from distutils.core import setup


def find_packages(base):
    result = []
    for path, dirs, files in os.walk(base):
        if '__init__.py' in files:
            result.append(path.replace(os.sep, '.'))
    result.sort()
    return result


setup(
    name='srcnip',
    version='0.2.0',
    license='GPL',
    description='Source code snippets',
    long_description='Source code snippets', #ToDo: reStructuredText
    author='Krzysztof Kosyl',
    author_email='krzysztof.kosyl@gmail.com',
    packages=find_packages('srcnip'),
    data_files=[
        ('/usr/bin',                               ['bin/srcnip']),
        ('/usr/share/srcnip',                      ['data/srcnip.png']),
        ('/usr/share/srcnip',                      ['README']),
        ('/usr/share/applications',                ['data/srcnip.desktop']),
        ('/usr/share/icons/hicolor/32x32/apps',    ['data/srcnip.png']),
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: KDE',
        #'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Editors :: Documentation',
        #'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
 