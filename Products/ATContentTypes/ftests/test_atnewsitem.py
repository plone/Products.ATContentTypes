"""
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

tests = []

class TestATNewsItemFunctional(atcttestcase.ATCTFuncionalTestCase):
    
    portal_type = 'ATNewsItem'
    views = ('newsitem_view', )

    def test_atct_history_view(self):
        # atct history view is restricted, we have to log in as portal ownr
        response = self.publish('%s/atct_history' % self.obj_path, self.owner_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

tests.append(TestATNewsItemFunctional)

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
