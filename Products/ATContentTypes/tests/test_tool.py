"""
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase
from Products.ATContentTypes.config import TOOLNAME

tests = []

class TestTool(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal.aq_explicit, TOOLNAME)
        
    def test_cmfftis(self):
        t = self.tool
        ftis = t._getCMFFtis()
        self.failUnless(isinstance(ftis, list))
        self.failUnlessEqual(len(ftis), 10)
        
    def test_cmfmetatypes(self):
        t = self.tool
        mt = t._getCMFMetaTypes()
        expected = ['Document', 'Favorite', 'Large Plone Folder',
        'Link', 'News Item', 'Plone Folder', 'Plone Site', 'Portal File',
        'Portal Image', 'Portal Topic']
        mt.sort()
        expected.sort()
        self.failUnlessEqual(mt, expected)
        
    def test_cmfportaltypes(self):
        t = self.tool
        pt = t._getCMFPortalTypes()
        expected = ['CMF Document', 'CMF Favorite', 'CMF File',
        'CMF Folder', 'CMF Image', 'CMF Large Plone Folder', 'CMF Link',
        'CMF News Item', 'CMF Topic', 'Plone Site', ]
        pt.sort()
        expected.sort()
        self.failUnlessEqual(pt, expected)
        
        pt = t._getCMFPortalTypes(metatype="Portal Topic")
        self.failUnlessEqual(pt, ['CMF Topic'])
        
    def test_uncatalogcmf(self):
        t = self.tool
        cat = self.portal.portal_catalog
        mt = t._getCMFMetaTypes()
        pt = t._getCMFPortalTypes()
        
        count, time, cttime = t._removeCMFtypesFromCatalog(count=True)
        
        brains = cat(meta_type=mt)
        self.failUnlessEqual(len(brains), 0)
        
        brains = cat(portal_type=pt)
        self.failUnlessEqual(len(brains), 0)
        
    def test_catalogcmf(self):
        t = self.tool
        cat = self.portal.portal_catalog
        mt = t._getCMFMetaTypes()
        pt = t._getCMFPortalTypes()
        
        # XXX add a cmf based object before cataloging

        result, time, ctime = t._catalogCMFtypes() 

        brains = cat(meta_type=mt)
        #self.failUnless(len(brains) > 0)
        
        brains = cat(portal_type=pt)
        #self.failUnless(len(brains) > 0)
        
    def test_recatalogCMFTypes(self):
        # just to make sure it is callable
        t = self.tool
        t.recatalogCMFTypes()

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
