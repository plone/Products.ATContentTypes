import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

from zope.component import getUtility

from Products.ATContentTypes.interface import IATCTTool
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.migration.v1_2 import upgradeATCTTool


class TestMigrations_v1_2(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.tool = getUtility(IATCTTool)

    def testUpgradeATCTTool(self):
        self.assertEquals(self.tool.getProperty('album_batch_size'), 30)
        self.tool._setPropValue('album_batch_size', 99)
        self.tool._setPropValue('_version', '1.1.x (svn/testing)')
        upgradeATCTTool(self.portal, [])
        self.assertEquals(self.tool.getProperty('album_batch_size'), 99)

    def testUpgradeATCTToolTwice(self):
        self.assertEquals(self.tool.getProperty('album_batch_size'), 30)
        self.tool._setPropValue('album_batch_size', 99)
        self.tool._setPropValue('_version', '1.1.x (svn/testing)')
        upgradeATCTTool(self.portal, [])
        upgradeATCTTool(self.portal, [])
        self.assertEquals(self.tool.getProperty('album_batch_size'), 99)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations_v1_2))
    return suite

if __name__ == '__main__':
    framework()
