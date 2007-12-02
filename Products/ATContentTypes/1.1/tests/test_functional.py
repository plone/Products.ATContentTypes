# -*- coding: UTF-8 -*-
"""
"""

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.ATContentTypes.tests.atcttestcase import ATCTFunctionalSiteTestCase 

FILES = ['webdav.txt', 'http_access.txt']

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    from Testing.ZopeTestCase import FunctionalDocFileSuite as FileSuite
    for file in FILES:
        suite.addTest(FileSuite(file, package="Products.ATContentTypes.tests",
                                test_class=ATCTFunctionalSiteTestCase)
                     )
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
