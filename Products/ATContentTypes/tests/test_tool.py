"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests


"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests.common import *
import Products.ATContentTypes.tests.ATCTSiteTestCase
from Products.Archetypes.tests import ArchetypesTestCase

tests = []

class TestTool(ArchetypesTestCase.ArcheSiteTestCase):

    def afterSetUp(self):
        self.tool = self.portal.aq_explicit.portal_atct
        
    def test_cmfftis(self):
        t = self.tool
        ftis = t._getCMFftis()
        self.failUnless(isinstance(ftis, list))
        self.failUnlessEqual(len(ftis), 10)
        
    def test_cmfmetadata(self):
        t = self.tool
        mt = t._getCMFmetatypes()
        mt.sort()
        self.failUnlessEqual(mt, ['Document', 'Favorite', 'Large Plone Folder',
        'Link', 'News Item', 'Plone Folder', 'Plone Site', 'Portal File',
        'Portal Image', 'Portal Topic'])
        
    def test_cmfportaltypes(self):
        t = self.tool
        pt = t._getCMFportaltypes()
        pt.sort()
        self.failUnlessEqual(pt, ['Document', 'Favorite', 'File', 'Folder',
        'Image', 'Large Plone Folder', 'Link', 'News Item', 'Plone Site',
        'Topic'])
        
    def test_uncatalogcmf(self):
        t = self.tool
        cat = self.portal.portal_catalog
        mt = t._getCMFmetatypes()
        pt = t._getCMFportaltypes()
        
        count, time, cttime = t._removeCMFtypesFromCatalog(count=True)
        
        brains = cat(meta_type=mt)
        self.failUnlessEqual(len(brains), 0)
        
        brains = cat(portal_type=pt)
        self.failUnlessEqual(len(brains), 0)
        
    def test_catalogcmf(self):
        t = self.tool
        cat = self.portal.portal_catalog
        mt = t._getCMFmetatypes()
        pt = t._getCMFportaltypes()

        result, time, ctime = t._catalogCMFtypes() 

        brains = cat(meta_type=mt)
        self.failUnless(len(brains) > 0)
        
        brains = cat(portal_type=pt)
        self.failUnless(len(brains) > 0)

tests.append(TestTool)

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
