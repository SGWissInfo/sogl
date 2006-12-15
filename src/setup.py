#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

from setuptools import setup

__id__ = '$Id$'
__revision__ = '$Revision$'
VERSION = '0.2'

setup(name='sogl',
      version='%s-%s'%(VERSION, __revision__[11:-2]),
      description='Simplified Object Graph Library',
      author='Klaus Zimmermann',
      author_email='klaus.zimmermann@fmf.uni-freiburg.de',
      url='http://www.fmf.uni-freiburg.de/service/Servicegruppen/sg_wissinfo/Software/Pyphant',
      packages=['sogl'],
      license='wxWindows',
      )
