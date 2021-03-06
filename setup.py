#!/usr/bin/env python
#-*- coding: utf-8 -*-


"""
Copyright (C) 2010 Krzysztof Kosyl <krzysztof.kosyl@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""


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


def extract_desc(filename):
    """ Return first section from reStructuredText file """
    lines = open(filename).read().splitlines()
    result, in_desc = [], False
    for line in lines:
        separator = line.startswith(('-----', '====='))
        if in_desc and separator:
            return '\n'.join(result[:-1]).strip()
        if in_desc:
            result.append(line)
        else:
            in_desc = separator


version = __import__('srcnip').__version__


setup(
    name='srcnip',
    version=version,
    license='GPL',
    description='Source code snippets',
    long_description=extract_desc('README.md'),
    author='Krzysztof Kosyl',
    author_email='krzysztof.kosyl@gmail.com',
    packages=find_packages('srcnip'),
    data_files=[
        ('/usr/bin',                               ['bin/srcnip']),
        ('/usr/share/srcnip',                      ['data/srcnip.png']),
        ('/usr/share/srcnip',                      ['README.md', 'LICENSE']),
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

