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

class TestInstallation(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal.aq_explicit, TOOLNAME)
        self.pt = getattr(self.portal.aq_explicit, 'portal_types')
        self.qi = getattr(self.portal.aq_explicit, 'portal_quickinstaller')
        
    def test_installed_products():
        qi = self.qi
        installed = [ prod['id'] for prod in qi.listInstalledProducts() ]
        self.failUnless('MimetypesRegistry' in installed, installed)
        self.failUnless('PortalTransforms' in installed, installed)
        self.failUnless('Archetypes' in installed, installed)
        self.failUnless('ATContentTypes' in installed, installed)
        self.failUnless('ATReferenceBrowserWidget' in installed, installed)
        
    def test_types_installed():
        pass

    def test_tool_installed():
        pass

    def test_skin_installed():
        stool = getattr(self.portal.aq_explicit, 'portal_skins')
        ids = stool.objectIds()
        self.failUnless('ATContentTypes' in ids, ids)
        
        
tests.append(TestInstallation)

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
