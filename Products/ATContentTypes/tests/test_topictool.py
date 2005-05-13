"""Skeleton ATContentTypes tests

Use this file as a skeleton for your own tests


"""

__author__ = 'Alec Mitchell'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.interfaces import IATCTTopicsTool
from Interface.Verify import verifyObject


tests = []
index_def = {'index'        : 'end',
             'friendlyName' : 'End Date',
             'description'  : 'This is an end Date',
             'criteria'     : ['ATDateCriteria','ATDateRangeCriteria']
            }
meta_def =  {'metadata'        : 'ModificationDate',
             'friendlyName' : 'Modification Date',
             'description'  : ''
            }

class TestTool(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal.aq_explicit, TOOLNAME)

    def test_interface(self):
        self.failUnless(IATCTTopicsTool.isImplementedBy(self.tool))
        self.failUnless(verifyObject(IATCTTopicsTool, self.tool))
 
    #Index tests
    def test_add_index(self):
        t = self.tool
        t.addIndex(enabled = True, **index_def)
        index = t.getIndex(index_def['index'])
        self.failUnlessEqual(index.index, index_def['index'])
        self.failUnlessEqual(index.friendlyName, index_def['friendlyName'])
        self.failUnlessEqual(index.description, index_def['description'])
        #Only need to test truth not actual value
        self.failUnlessEqual(not index.enabled, not True)
        self.failUnlessEqual(index.criteria, tuple(index_def['criteria']))

        self.failUnless(index in t.getEnabledIndexes())
        self.failUnless(index_def['index'] in [a[0] for a in t.getEnabledFields()])
        self.failUnless(index_def['index'] in t.getIndexDisplay(True).keys())
        self.failUnless(index_def['friendlyName'] in t.getIndexDisplay(True).values())
        self.failUnless(index_def['index'] in t.getIndexes(1))
        
    def test_disable_index(self):
        t = self.tool
        t.addIndex(enabled = False, **index_def)
        index = t.getIndex(index_def['index'])
        self.failUnlessEqual(index.index, index_def['index'])
        self.failUnlessEqual(index.friendlyName, index_def['friendlyName'])
        self.failUnlessEqual(index.description, index_def['description'])
        #Only need to test truth not actual value
        self.failUnlessEqual(not index.enabled, not False)
        self.failUnlessEqual(index.criteria, tuple(index_def['criteria']))

        self.failUnless(index not in t.getEnabledIndexes())
        self.failUnless(index_def['index'] not in [a[0] for a in t.getEnabledFields()])
        self.failUnless(index_def['index'] not in t.getIndexes(1))
        self.failUnless(index_def['index'] not in t.getIndexDisplay(True).keys())
        self.failUnless(index_def['friendlyName'] not in t.getIndexDisplay(True).values())
        #Make sure it's still in the un-limited list
        self.failUnless(index_def['index'] in t.getIndexDisplay(False).keys())
        self.failUnless(index_def['friendlyName'] in t.getIndexDisplay(False).values())
        self.failUnless(index_def['index'] in t.getIndexes())

    def test_add_bogus_index(self):
        """An metdatum that's not in the catalog should be deleted automatically
           on any call to one of the index list methods."""
        t = self.tool
        t.addIndex('bogosity', enabled = True)
        error = False
        #The methods getEnabledFields, getEnabledIndexes, getIndexes,
        #getIndexDisplay, and getIndex all automatically restore fields
        #from the catalog
        
        try:
            t.getIndex('bogosity')
        except AttributeError:
            error = True
        self.failUnless(error)
        
        #Add
        t.addIndex('bogosity', enabled = True)
        self.failUnless('bogosity' not in [a[0] for a in t.getEnabledFields()])
        #Add
        t.addIndex('bogosity', enabled = True)
        self.failUnless('bogosity' not in t.getIndexDisplay(True).keys())
        #Add
        t.addIndex('bogosity', enabled = True)
        self.failUnless('bogosity' not in t.getIndexes(1))
        #Add
        t.addIndex('bogosity', enabled = True)
        self.failUnless('bogosity' not in [i.index for i in t.getEnabledIndexes()])
        
    def test_remove_index(self):
        t = self.tool
        t.addIndex(**index_def)
        t.removeIndex(index_def['index'])
        error = None
        try:
            index = t.topic_indexes[index_def['index']]
        except KeyError:
            error = True
        self.failUnless(error)
        #Should be restored automatically by getIndex and friends
        error = None
        try:
            index = t.getIndex(index_def['index'])
        except AttributeError:
            error = True
        self.failUnless(not error)
        #Make sure the FriendlyName is reset to default
        self.failUnless(index.friendlyName != index_def['friendlyName'])
        
    def test_update_index(self):
        """An index with no criteria set should set all available criteria,
           also changes made using updateIndex should not reset already set
           values"""
        t = self.tool
        t.addIndex(enabled = True, **index_def)
        t.updateIndex(index_def['index'], criteria = None,
                      description = 'New Description')
        index = t.getIndex(index_def['index'])
        self.failUnless(index.criteria)
        self.failUnless(index.criteria != index_def['criteria'])
        self.failUnless(index.description == 'New Description')
        self.failUnless(index.friendlyName == index_def['friendlyName'])
        self.failUnlessEqual(not index.enabled, not True)

    def test_all_indexes(self):
        """Ensure that the tool includes all indexes in the catalog"""
        t = self.tool
        cat = getToolByName(self.tool, CatalogTool.id)
        indexes = [field for field in cat.indexes()]
        init_indexes = list(t.getIndexes())
        unique_indexes = [i for i in indexes if i not in init_indexes]
        unique_indexes = unique_indexes + [i for i in init_indexes if i not in indexes]
        self.failUnless(not unique_indexes)

    def test_change_catalog_index(self):
        """Make sure tool updates when indexes are added to or deleted from
           the catalog"""
        t = self.tool
        cat = getToolByName(self.tool, CatalogTool.id)
        #add
        error = False
        cat.manage_addIndex('nonsense', 'FieldIndex')
        try:
            t.getIndex('nonsense')
        except AttributeError:
            error = True
        self.failUnless(not error)
        #remove
        error = False
        cat.delIndex('nonsense')
        try:
            t.getIndex('nonsense')
        except AttributeError:
            error = True
        self.failUnless(error)


    #Metadata tests
    def test_add_metadata(self):
        t = self.tool
        t.addMetadata(enabled = True, **meta_def)
        meta = t.getMetadata(meta_def['metadata'])
        self.failUnlessEqual(meta.index, meta_def['metadata'])
        self.failUnlessEqual(meta.friendlyName, meta_def['friendlyName'])
        self.failUnlessEqual(meta.description, meta_def['description'])
        #Only need to test truth not actual value
        self.failUnlessEqual(not meta.enabled, not True)

        self.failUnless(meta in t.getEnabledMetadata())
        self.failUnless(meta_def['metadata'] in t.getMetadataDisplay(True).keys())
        self.failUnless(meta_def['friendlyName'] in t.getMetadataDisplay(True).values())
        self.failUnless(meta_def['metadata'] in t.getAllMetadata(1))
        
    def test_disable_metadata(self):
        t = self.tool
        t.addMetadata(enabled = False, **meta_def)
        meta = t.getMetadata(meta_def['metadata'])
        self.failUnlessEqual(meta.index, meta_def['metadata'])
        self.failUnlessEqual(meta.friendlyName, meta_def['friendlyName'])
        self.failUnlessEqual(meta.description, meta_def['description'])
        #Only need to test truth not actual value
        self.failUnlessEqual(not meta.enabled, not False)

        self.failUnless(meta not in t.getEnabledMetadata())
        self.failUnless(meta_def['metadata'] not in t.getAllMetadata(1))
        self.failUnless(meta_def['metadata'] not in t.getMetadataDisplay(True).keys())
        self.failUnless(meta_def['friendlyName'] not in t.getMetadataDisplay(True).values())
        #Make sure it's still in the un-limited list
        self.failUnless(meta_def['metadata'] in t.getMetadataDisplay(False).keys())
        self.failUnless(meta_def['friendlyName'] in t.getMetadataDisplay(False).values())
        self.failUnless(meta_def['metadata'] in t.getAllMetadata())

    def test_add_bogus_metadata(self):
        """An metdatum that's not in the catalog should be deleted automatically
           on any call to one of the index list methods"""
        t = self.tool
        t.addMetadata('bogosity', enabled = True)
        
        error = False
        #The methods getEnabledMetadata, getAllMetadata, getMetadataDisplay,
        #and getMetadata all automatically restore fields from the catalog
        try:
            t.getMetadata('bogosity')
        except AttributeError:
            error = True
        self.failUnless(error)

        #Add
        t.addMetadata('bogosity', enabled = True)
        self.failUnless('bogosity' not in t.getMetadataDisplay(True).keys())
        #Add
        t.addMetadata('bogosity', enabled = True)
        self.failUnless('bogosity' not in t.getAllMetadata(1))
        #Add
        t.addMetadata('bogosity', enabled = True)
        self.failUnless('bogosity' not in [i.index for i in t.getEnabledMetadata()])

    def test_remove_metadata(self):
        t = self.tool
        t.addMetadata(**meta_def)
        t.removeMetadata(meta_def['metadata'])
        error = None
        try:
            meta = t.topic_metadata[meta_def['metadata']]
        except KeyError:
            error = True
        self.failUnless(error)
        #Should be restored automatically by getMetadata and friends
        error = None
        try:
            meta = t.getMetadata(meta_def['metadata'])
        except AttributeError:
            error = True
        self.failUnless(not error)
        #Make sure the FriendlyName is reset to default
        self.failUnless(meta.friendlyName != meta_def['friendlyName'])
        
    def test_update_metadata(self):
        """Changes made using updateMetadata should not reset already set
           values"""
        t = self.tool
        t.addMetadata(enabled = True, **meta_def)
        t.updateMetadata(meta_def['metadata'], friendlyName = 'New Name')
        meta = t.getMetadata(meta_def['metadata'])
        self.failUnless(meta.friendlyName == 'New Name')
        self.failUnlessEqual(not meta.enabled, not True)

    def test_all_metadata(self):
        """Ensure that the tool includes all metadata in the catalog"""
        t = self.tool
        cat = getToolByName(self.tool, CatalogTool.id)
        metadata = [field for field in cat.schema()]
        init_metadata = list(t.getAllMetadata())
        unique_metadata = [i for i in metadata if i not in init_metadata]
        unique_metadata = unique_metadata + [i for i in init_metadata if i not in metadata]
        self.failUnless(not unique_metadata)

    def test_change_catalog_schema(self):
        """Make sure tool updates when columns are added to or deleted from
           the catalog"""
        t = self.tool
        cat = getToolByName(self.tool, CatalogTool.id)
        #add
        error = False
        cat.manage_addColumn('nonsense')
        try:
            t.getMetadata('nonsense')
        except AttributeError:
            error = True
        self.failUnless(not error)
        #remove
        error = False
        cat.delColumn('nonsense')
        try:
            t.getMetadata('nonsense')
        except AttributeError:
            error = True
        self.failUnless(error)

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
