"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests


"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.ftests import atctftestcase

tests = []

class TestATFolderFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'ATFolder'
    views = ('folder_listing', 'folder_contents', )

    def test_templatemixin_view_without_view(self):
        # template mixin magic should work
        # XXX more tests?
        response = self.publish('%s/' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) #

tests.append(TestATFolderFunctional)

from Products.ATContentTypes.config import ATCT_PORTAL_TYPE

class TestATBTreeFolderFunctional(atctftestcase.ATCTIntegrationTestCase):

    portal_type = ATCT_PORTAL_TYPE('ATBTreeFolder')
    views = ('folder_listing', 'folder_contents', )

    def afterSetUp(self):
        # enable global allow for BTree Folder
        fti = getattr(self.portal.portal_types, self.portal_type)
        fti.manage_changeProperties(global_allow=1)
        atctftestcase.ATCTIntegrationTestCase.afterSetUp(self)

    def test_templatemixin_view_without_view(self):
        # template mixin magic should work
        # XXX more tests?
        response = self.publish('%s/' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) #

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
