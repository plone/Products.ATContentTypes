"""
"""
__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import common
from Products import ATContentTypes
from Testing.ZopeTestCase.zopedoctest import ZopeDocTestSuite
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.CMFCore.utils import getToolByName

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(ZopeDocTestSuite(ATContentTypes,
                                   test_class=PortalTestCase,
                                   globs={'getToolByName' : getToolByName}
                                  ))
    return suite

if __name__ == '__main__':
    framework()
