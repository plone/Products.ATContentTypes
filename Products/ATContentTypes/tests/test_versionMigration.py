#
# Tests for migration components
#


__author__ = 'Alec Mitchell <apm13@columbia.edu>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.interfaces import IATCTTool
from Interface.Verify import verifyObject
from Products.CMFCore.utils import getToolByName
import os, sys

from Products.ATContentTypes.migration.v1.alphas import updateDateCriteria
from Products.ATContentTypes.migration.v1.alphas import updateIntegerCriteria
from Products.ATContentTypes.migration.v1.alphas import addUnfriendlyTypesSiteProperty
from Products.ATContentTypes.migration.v1.alphas import migrateCMFLeftovers



class MigrationTest(atcttestcase.ATCTSiteTestCase):

    def removeSiteProperty(self, property_id):
        # Removes a site property from portal_properties
        tool = getattr(self.portal, 'portal_properties')
        sheet = getattr(tool, 'site_properties')
        if sheet.hasProperty(property_id):
            sheet.manage_delProperties([property_id])

    def _createType(self, context, portal_type, id):
        """Helper method to create a new type 
        """
        ttool = getToolByName(context, 'portal_types')
        fti = ttool.getTypeInfo(portal_type)
        fti.constructInstance(context, id)
        return getattr(context.aq_inner.aq_explicit, id)


class TestMigrations_v1(MigrationTest):

    def afterSetUp(self):
        self.setRoles(['Manager', 'Member'])
        self.tool = getToolByName(self.portal, TOOLNAME)
        self.properties = self.portal.portal_properties
        self.catalog = self.portal.portal_catalog
        self.cmf_topic = self._createType(self.folder, 'CMF Topic', 'test_cmftopic')
        self.catalog.indexObject(self.folder.test_cmftopic)
        self.at_topic = self._createType(self.folder, 'Topic', 'test_attopic')
        self.date_crit = self.at_topic.addCriterion('created','ATFriendlyDateCriteria')
        #Set obselete values to test migration
        self.date_crit.setOperation('min')
        self.date_crit.setDateRange('-')
        self.date_crit.setValue(35)
        #Set only the value parameter
        self.int_crit = self.at_topic.addCriterion('Subject','ATSimpleIntCriterion')
        self.int_crit.setValue(35)

    def testAddUnfriendlyTypesSiteProperty(self):
        # Should add the unfriendly_types property
        self.removeSiteProperty('unfriendly_types')
        self.failIf(self.properties.site_properties.hasProperty('unfriendly_types'))
        addUnfriendlyTypesSiteProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('unfriendly_types'))

    def testAddUnfriendlyTypesSitePropertyTwice(self):
        # Should not fail if migrated again
        self.removeSiteProperty('unfriendly_types')
        self.failIf(self.properties.site_properties.hasProperty('unfriendly_types'))
        addUnfriendlyTypesSiteProperty(self.portal, [])
        addUnfriendlyTypesSiteProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('unfriendly_types'))

    def testAddUnfriendlyTypesSitePropertyNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        addUnfriendlyTypesSiteProperty(self.portal, [])

    def testAddUnfriendlyTypesSitePropertyNoSheet(self):
        # Should not fail if site_properties is missing
        self.properties._delObject('site_properties')
        addUnfriendlyTypesSiteProperty(self.portal, [])

    def testMigrateCMFLeftovers(self):
        # Should convert the CMFTopic
        migrateCMFLeftovers(self.portal,[])
        migrated = getattr(self.folder, 'test_cmftopic')
        self.assertEqual(migrated.portal_type,'Topic')

    def testMigrateCMFLeftoversTwice(self):
        # Should not fail if migrated again
        migrateCMFLeftovers(self.portal,[])
        migrateCMFLeftovers(self.portal,[])
        migrated = getattr(self.folder, 'test_cmftopic')
        self.assertEqual(migrated.portal_type,'Topic')

    def testUpdateDateCriteria(self):
        # Should fix our broken date criteria
        updateDateCriteria(self.portal,[])
        self.assertEqual(self.date_crit.getOperation(),'less')
        self.assertEqual(self.date_crit.getDateRange(),'-')
        self.assertEqual(self.date_crit.Value(),35)

    def testUpdateDateCriteriaTwice(self):
        # Should not fail if migrated again
        updateDateCriteria(self.portal,[])
        updateDateCriteria(self.portal,[])
        self.assertEqual(self.date_crit.getOperation(),'less')

    def testUpdateDateCriteriaNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        updateDateCriteria(self.portal,[])

    def testUpdateIntegerCriteria(self):
        # Should fix our incomplete integer criteria
        # XXX this relies on the current AttributeStorage implementation
        updateIntegerCriteria(self.portal,[])
        self.assertEqual(self.int_crit.value2,None)
        self.assertEqual(self.int_crit.direction,'')
        self.assertEqual(self.int_crit.Value(),35)

    def testUpdateIntegerCriteriaTwice(self):
        # Should not fail if migrated again
        updateIntegerCriteria(self.portal,[])
        updateIntegerCriteria(self.portal,[])

    def testUpdateIntegerCriteriaNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        updateIntegerCriteria(self.portal,[])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations_v1))
    return suite

if __name__ == '__main__':
    framework()
