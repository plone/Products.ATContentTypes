from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase, atctftestcase

import transaction
from Acquisition import aq_base

from Products.Archetypes.atapi import *
from Products.ATContentTypes.tests.utils import dcEdit

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATBTreeFolder
from OFS.interfaces import IOrderedContainer as OFSIOrderedContainer
from Products.CMFPlone.interfaces.OrderedContainer import IOrderedContainer
from Products.ATContentTypes.interfaces import IATFolder
from Products.ATContentTypes.interfaces import IATBTreeFolder

from zope.interface.verify import verifyClass

from zope.interface.verify import verifyObject
from Products.ATContentTypes.interface import ISelectableConstrainTypes

def editATCT(obj):
    dcEdit(obj)

tests = []


class FolderTestMixin:
    """Contains some general tests for both ATFolder and ATBTreeFolder
    """
    def test_implementsConstrainTypes(self):
        self.failUnless(ISelectableConstrainTypes.providedBy(self._ATCT))
        self.failUnless(verifyObject(ISelectableConstrainTypes, self._ATCT))


class TestSiteATFolder(atcttestcase.ATCTTypeTestCase, FolderTestMixin):

    klass = ATFolder
    portal_type = 'Folder'
    title = 'Folder'
    meta_type = 'ATFolder'
    icon = 'folder_icon.png'

    def test_implementsOrderInterface(self):
        self.failUnless(OFSIOrderedContainer.providedBy(self._ATCT))
        self.failUnless(IOrderedContainer.providedBy(self._ATCT))
        self.failUnless(verifyObject(OFSIOrderedContainer, self._ATCT))
        self.failUnless(verifyObject(IOrderedContainer, self._ATCT))

    def test_implementsATFolder(self):
        iface = IATFolder
        self.failUnless(iface.providedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsConstrainTypes(self):
        iface = ISelectableConstrainTypes
        self.failUnless(iface.providedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_edit(self):
        new = self._ATCT
        editATCT(new)

    def test_get_size(self):
        atct = self._ATCT
        self.failUnlessEqual(atct.get_size(), 1)

    def test_schema_marshall(self):
        pass

tests.append(TestSiteATFolder)

class TestSiteATBTreeFolder(atcttestcase.ATCTTypeTestCase, FolderTestMixin):

    klass = ATBTreeFolder
    portal_type = 'Large Plone Folder'
    title = 'Large Folder'
    meta_type = 'ATBTreeFolder'
    icon = 'folder_icon.png'

    def test_implementsATBTreeFolder(self):
        iface = IATBTreeFolder
        self.failUnless(iface.providedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsConstrainTypes(self):
        iface = ISelectableConstrainTypes
        self.failUnless(iface.providedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_isNotOrdered(self):
        iface = OFSIOrderedContainer
        self.failIf(iface.providedBy(self._ATCT))

    def test_edit(self):
        new = self._ATCT
        editATCT(new)
        self.failUnless('Test title' == new.Title())
        self.failUnless('Test description' == new.Description())

    def test_get_size(self):
        atct = self._ATCT
        self.failUnlessEqual(atct.get_size(), 1)

    def test_schema_marshall(self):
        pass

tests.append(TestSiteATBTreeFolder)

class TestATFolderFields(atcttestcase.ATCTFieldTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATFolder)

    def test_field_enableConstrainMixin(self):
        pass
        #self.fail('not implemented')

    def test_field_locallyAllowedTypes(self):
        pass
        #self.fail('not implemented')

tests.append(TestATFolderFields)

class TestATBTreeFolderFields(TestATFolderFields):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATBTreeFolder)

tests.append(TestATBTreeFolderFields)


class TestATFolderFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'Folder'
    views = ('folder_listing', 'atct_album_view', )

    def test_dynamic_view_without_view(self):
        # dynamic view mixin should work
        response = self.publish('%s/' % self.obj_path, self.basic_auth)
        self.failUnlessEqual(response.getStatus(), 200) #
        
    def test_selectViewTemplate(self):
        # create an object using the createObject script
        response = self.publish(self.obj_path +
                                '/selectViewTemplate?templateId=atct_album_view',
                                self.owner_auth)
        self.failUnlessEqual(self.obj.getLayout(), 'atct_album_view')

tests.append(TestATFolderFunctional)

class TestATBTreeFolderFunctional(atctftestcase.ATCTIntegrationTestCase):

    portal_type = 'Large Plone Folder'
    views = ('folder_listing', 'atct_album_view', )

    def afterSetUp(self):
        # enable global allow for BTree Folder
        fti = getattr(self.portal.portal_types, self.portal_type)
        fti.manage_changeProperties(global_allow=1)
        atctftestcase.ATCTIntegrationTestCase.afterSetUp(self)

    def test_templatemixin_view_without_view(self):
        # template mixin magic should work
        response = self.publish('%s/' % self.obj_path, self.basic_auth)
        self.failUnlessEqual(response.getStatus(), 200) #

tests.append(TestATBTreeFolderFunctional)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
