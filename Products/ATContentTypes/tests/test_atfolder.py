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

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests.utils import dcEdit
from Products.ATContentTypes.tests import atcttestcase

from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.public import *
from Products.ATContentTypes.tests.utils import dcEdit
import time

from Products.ATContentTypes.types.ATFolder import ATFolder
from Products.ATContentTypes.types.ATFolder import ATBTreeFolder
from Products.ATContentTypes.types.ATFolder import ATFolderSchema
from Products.ATContentTypes.tests.utils import TidyHTMLValidator
from Products.ATContentTypes.migration.ATCTMigrator import FolderMigrator
from Products.CMFPlone.PloneFolder import PloneFolder
from Products.CMFPlone.LargePloneFolder import LargePloneFolder
from OFS.IOrderSupport import IOrderedContainer as IZopeOrderedContainer
from Products.CMFPlone.interfaces.OrderedContainer import IOrderedContainer
from Products.ATContentTypes.interfaces import IConstrainTypes
from Products.ATContentTypes.interfaces import IATFolder
from Products.ATContentTypes.interfaces import IATBTreeFolder
from Interface.Verify import verifyObject

def editCMF(obj):
    dcEdit(obj)

def editATCT(obj):
    dcEdit(obj)

tests = []


class FolderTestMixin:
    """Contains some general tests for both ATFolder and ATBTreeFolder
    """

    def test_implementsConstrainTypes(self):
        self.failUnless(IConstrainTypes.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(IConstrainTypes, self._ATCT)) 
        
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

    def test_implementsConstrainTypes(self):
        iface = IConstrainTypes
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
        get_transaction().commit(1)
        m = FolderMigrator(old)
        m(unittest=1)

        self.failUnless(id in self.folder.objectIds(), self.folder.objectIds())
        migrated = getattr(self.folder, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)


        # XXX more

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

    def test_implementsConstrainTypes(self):
        iface = IConstrainTypes
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
