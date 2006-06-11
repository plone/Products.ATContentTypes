#
# Tests for migration components
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase
from Products.ATContentTypes.config import TOOLNAME
from Products.CMFCore.utils import getToolByName


class TestMigrations_v1(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, TOOLNAME)

    # XXX tests for existing migrations missing

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations_v1))
    return suite

if __name__ == '__main__':
    framework()
