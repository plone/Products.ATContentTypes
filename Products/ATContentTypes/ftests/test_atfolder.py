"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests


"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

tests = []

class TestATFolderFunctional(atcttestcase.ATCTFuncionalTestCase):
    
    portal_type = 'ATFolder'
    views = ('folder_listing', 'folder_contents', )

tests.append(TestATFolderFunctional)

class TestATBTreeFolderFunctional(atcttestcase.ATCTFuncionalTestCase):
    
    portal_type = 'ATBTreeFolder'
    views = ('folder_listing', 'folder_contents', )

tests.append(TestATBTreeFolderFunctional)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite
