#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

VERSION = '0.2.1'

setup(
    name='sogl',
    version='%s' % (VERSION, ),
    description='Simplified Object Graph Library',
    author='Klaus Zimmermann',
    author_email='klaus.zimmermann@fmf.uni-freiburg.de',
    maintainer='Alexander Held',
    maintainer_email='alexander.held@fmf.uni-freiburg.de',
    url='https://github.com/SGWissInfo/sogl',
    install_requires=[
        'wxPython',
        ],
    packages=['sogl'],
    license='wxWindows',
    )
