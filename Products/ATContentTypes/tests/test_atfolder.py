#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
"""

__author__ = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase
from Acquisition import aq_base

from Products.Archetypes.public import *
from Products.ATContentTypes.tests.utils import dcEdit

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATBTreeFolder
from Products.ATContentTypes.migration.atctmigrator import FolderMigrator, \
                                                        LargeFolderMigrator, \
                                                        DocumentMigrator
from Products.CMFPlone.PloneFolder import PloneFolder
from Products.CMFPlone.LargePloneFolder import LargePloneFolder
from OFS.IOrderSupport import IOrderedContainer as IZopeOrderedContainer
from Products.CMFPlone.interfaces.OrderedContainer import IOrderedContainer
from Products.ATContentTypes.interfaces import IATFolder
from Products.ATContentTypes.interfaces import IATBTreeFolder
from Products.Five.traversable import FakeRequest
from Products.ATContentTypes.tests.utils import FakeRequestSession

from zope.interface.verify import verifyClass

from Products.ATContentTypes.interfaces import IAutoSortSupport
from Products.ATContentTypes.interfaces import IAutoOrderSupport
from Interface.Verify import verifyObject
from Products.CMFPlone import transaction

from Products.CMFPlone.interfaces.ConstrainTypes import ISelectableConstrainTypes

# z3 imports
from Products.ATContentTypes.interface import IAutoSortSupport as Z3IAutoSortSupport
from Products.ATContentTypes.interface import IAutoOrderSupport as Z3IAutoOrderSupport
from Products.ATContentTypes.interface import IATFolder as Z3IATFolder
from Products.ATContentTypes.interface import IATBTreeFolder as Z3IATBTreeFolder
from zope.interface.verify import verifyObject as Z3verifyObject

def editCMF(obj):
    dcEdit(obj)

def editATCT(obj):
    dcEdit(obj)

tests = []


class FolderTestMixin:
    """Contains some general tests for both ATFolder and ATBTreeFolder
    """
    def test_implementsConstrainTypes(self):
        self.failUnless(ISelectableConstrainTypes.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(ISelectableConstrainTypes, self._ATCT))

    def test_implements_autosort(self):
        self.failUnless(IAutoSortSupport.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(IAutoSortSupport, self._ATCT))

    def test_implementsZ3_autosort(self):
        iface = Z3IAutoSortSupport
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_migrationKeepsLocallyAddedRoles(self):
        atct = self.portal.portal_atct
        ttool = self.portal.portal_types
        old_fti = ttool[self.cmf_portal_type]
        role = 'testrole'
        
        # create old object
        self.setRoles(['Manager',])
        old_fti.global_allow = 1
        self.folder.invokeFactory(self.cmf_portal_type, 'rolecheck')
        obj = self.folder.rolecheck
        self.failUnlessEqual(obj.portal_type, self.cmf_portal_type)
        
        # add a role
        self.failIf(role in obj.valid_roles())
        obj._addRole(role)
        self.failUnless(role in obj.userdefined_roles(), obj.userdefined_roles())

        del obj # keep no references when migrating
        # migrate types
        transaction.savepoint() # subtransaction
        atct.migrateContentTypesToATCT()

        # check the new
        obj = self.folder.rolecheck
        self.failUnlessEqual(obj.portal_type, self.portal_type)
        self.failUnless(role in obj.userdefined_roles(), obj.userdefined_roles())

class TestSiteATFolder(atcttestcase.ATCTTypeTestCase, FolderTestMixin):

    klass = ATFolder
    portal_type = 'Folder'
    cmf_portal_type = 'CMF Folder'
    cmf_klass = PloneFolder
    title = 'Folder'
    meta_type = 'ATFolder'
    icon = 'folder_icon.gif'

    def test_implementsOrderInterface(self):
        self.failUnless(IZopeOrderedContainer.isImplementedBy(self._ATCT))
        self.failUnless(IOrderedContainer.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(IZopeOrderedContainer, self._ATCT))  
        self.failUnless(verifyObject(IOrderedContainer, self._ATCT))  

    def test_implementsATFolder(self):
        iface = IATFolder
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_Z3implementsATFolder(self):
        iface = Z3IATFolder
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsConstrainTypes(self):
        iface = ISelectableConstrainTypes
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.Title() == new.Title(), 'Title mismatch: %s / %s' \
                        % (old.Title(), new.Title()))
        self.failUnless(old.Description() == new.Description(), 'Description mismatch: %s / %s' \
                        % (old.Description(), new.Description()))

    def test_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()

        # migrated (needs subtransaction to work)
        transaction.commit(1)
        m = FolderMigrator(old)
        m(unittest=1)

        self.failUnless(id in self.folder.objectIds(), self.folder.objectIds())
        migrated = getattr(self.folder, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)

        # TODO: more tests

    def test_migrator_doesnt_migrate_non_contentish_sub_objects(self):
        # Test that we don't try to migrate contained non-content objects
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()

        # Add non-contentish subobject to inherit portal_type from parent
        factory = old.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('index_html')
        index = old.index_html

        # Catalog it so that migration thinks it's a folder.
        self.portal.portal_catalog.indexObject(index)

        # migration will raise an error if it attempts to incorrectly migrate
        # the index_html
        transaction.commit(1)
        m = FolderMigrator(index)
        try:
            m(unittest=1)
        except Exception, e:
            import sys, traceback
            self.fail('Error raised in Folder migration of non-content sub-object: %s \n %s'%(e,''.join(traceback.format_tb(sys.exc_traceback))))

    def test_implements_autoorder(self):
        self.failUnless(IAutoOrderSupport.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(IAutoOrderSupport, self._ATCT))

    def test_Z3implements_autoorder(self):
        pass
        #iface = Z3IAutoOrderSupport
        #self.failUnless(Z3verifyObject(iface, self._ATCT))
        # XXX Archetypes not ready for Zope3 OrderedContainer (see zope.app.container.interfaces)

    def test_get_size(self):
        atct = self._ATCT
        self.failUnlessEqual(atct.get_size(), 1)

    def test_schema_marshall(self):
        pass

tests.append(TestSiteATFolder)

class TestSiteATBTreeFolder(atcttestcase.ATCTTypeTestCase, FolderTestMixin):

    klass = ATBTreeFolder
    portal_type = 'Large Plone Folder'
    cmf_portal_type = 'CMF Large Plone Folder'
    cmf_klass = LargePloneFolder
    title = 'Large Folder'
    meta_type = 'ATBTreeFolder'
    icon = 'folder_icon.gif'

    def test_implementsATBTreeFolder(self):
        iface = IATBTreeFolder
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_Z3implementsATBTreeFolder(self):
        iface = Z3IATBTreeFolder
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsConstrainTypes(self):
        iface = ISelectableConstrainTypes
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))
    
    def test_isNotOrdered(self):
        iface = IZopeOrderedContainer
        self.failIf(iface.isImplementedBy(self._ATCT))

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.Title() == new.Title(), 'Title mismatch: %s / %s' \
                        % (old.Title(), new.Title()))
        self.failUnless(old.Description() == new.Description(), 'Description mismatch: %s / %s' \
                        % (old.Description(), new.Description()))

    def test_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()

        # Add subobject to test child migration
        old.invokeFactory('Document','bogus')
        bogus = old.bogus

        # migrated (needs subtransaction to work)
        transaction.commit(1)
        m = LargeFolderMigrator(old)
        m(unittest=1)

        self.failUnless(id in self.folder.objectIds(), self.folder.objectIds())
        migrated = getattr(self.folder, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)
        self.assertEqual(aq_base(migrated.bogus), aq_base(bogus))

    def test_subobj_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()

        # Add subobject to test child migration
        
        bogus = self._createType(old, 'CMF Document', 'bogus')
        bogus = old.bogus

        # migrated (needs subtransaction to work)
        transaction.commit(1)
        m = DocumentMigrator(bogus)
        try:
            m(unittest=1)
        except Exception, e:
            import sys, traceback
            self.fail("Failed migrating subobject of LargePloneFolder: %s \n %s"%(e,''.join(traceback.format_tb(sys.exc_traceback))))

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

class TestAutoSortSupport(atcttestcase.ATCTSiteTestCase):
    
    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.folder.invokeFactory('Folder', 'fobj', title='folder 1')
        self.fobj = self.folder.fobj
        self.objs = (('Document', 'x1', 'Document 3'),
                     ('Document', 'x2', 'Document 4'),
                     ('Document', 'doc1', 'Document 1'),
                     ('Document', 'doc2', 'Document 2'),
                     ('Folder', 'folder1', 'Folder 1'),
                     ('Folder', 'folder2', 'Folder 2'),
                    )
        for pt, id, title in self.objs:
            self.fobj.invokeFactory(pt, id, title=title)
        
    def test_autoordering(self):
        f = self.fobj
        self.failUnlessEqual(f.getDefaultSorting(), ('Title', False))
        self.failUnlessEqual(f.getSortFolderishFirst(), True)
        self.failUnlessEqual(f.getSortReverse(), False)
        self.failUnlessEqual(f.getSortAuto(), True)
        
        f.setDefaultSorting('getId', reverse=True)
        f.setSortFolderishFirst(False)
        f.setSortReverse(True)
        f.setSortAuto(False)
        
        self.failUnlessEqual(f.getDefaultSorting(), ('getId', True))
        self.failUnlessEqual(f.getSortFolderishFirst(), False)
        self.failUnlessEqual(f.getSortReverse(), True)
        self.failUnlessEqual(f.getSortAuto(), False)

    def test_strangeUnallowedIds(self):
        """ Certain IDs used to give an error and are unusable

        They're set in zope's lib/python/App/Product.py. Examples:
        home, version. This test used to include 'icon', too, but that's
        apparently really an id that's already been taken (instead of
        a bug).
        """
        strangeIds = ['home', 'version']
        for id in strangeIds:
            self.folder.invokeFactory('Folder', id)
            self.assert_(id in self.folder.objectIds())

    # TODO: more tests

tests.append(TestAutoSortSupport)


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
