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

__author__ = 'Alec Mitchell <apm13@columbia.edu>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.public import *
from Products.ATContentTypes.tests.utils import dcEdit
import time

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.tests.utils import TidyHTMLValidator
from Products.ATContentTypes.migration.atctmigrator import DocumentMigrator, \
                                                           FolderMigrator
from Products.CMFDefault.Document import Document
from Products.ATContentTypes.interfaces import IHistoryAware
from Products.ATContentTypes.interfaces import ITextContent
from Products.ATContentTypes.interfaces import IATDocument
from Interface.Verify import verifyObject
from Products.Archetypes.public import Schema, BaseSchema, BaseContent, \
                                       TextField, RichWidget
from Products.ATContentTypes.config import PROJECTNAME
from Products.CMFPlone import transaction


example_stx = """
Header

 Text, Text, Text

   * List
   * List
"""

example_rest = """
Header
======

Text, text, text

* List
* List
"""

def editCMF(obj):
    text_format='stx'
    dcEdit(obj)
    obj.edit(text_format = text_format, text = example_stx)

def editATCT(obj):
    text_format='text/structured'
    dcEdit(obj)
    obj.setText(example_stx, mimetype = text_format)

tests = []

class TestTypeMigrations(atcttestcase.ATCTTypeTestCase):

    klass = ATDocument
    portal_type = 'Document'
    cmf_portal_type = 'CMF Document'
    cmf_klass = Document
    title = 'Page'
    meta_type = 'ATDocument'
    icon = 'document_icon.gif'

    def afterSetUp(self):
        atcttestcase.ATCTTypeTestCase.afterSetUp(self)
        self.old = old =  self._cmf
        self.id  = old.getId()

        self.pm          = self.portal.portal_membership
        self.wf          = self.portal.portal_workflow
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('user2', 'secret', ['Member'], [])

    def migrateObject(self):
        # edit
        editCMF(self.old)
        self.title       = self.old.Title()
        self.description = self.old.Description()
        self.mod         = self.old.ModificationDate()
        self.created     = self.old.CreationDate()
        self.body        = self.old.CookedBody(stx_level=2)

        # migrated (needs subtransaction to work)
        transaction.commit(1)
        m = DocumentMigrator(self.old)
        m(unittest=1)
        transaction.commit(1)

        self.migrated = getattr(self.folder, self.id)

    def test_base_migration(self):
        self.migrateObject()
        self.failUnless(self.id in self.folder.objectIds(), self.folder.objectIds())
        self.compareAfterMigration(self.migrated, mod=self.mod,
                                                created=self.created)
        self.compareDC(self.migrated, title=self.title,
                                        description=self.description)

    def test_role_migration(self):
        self.pm.setLocalRoles( obj=self.old,
                               member_ids=('user1',),
                               member_role='Reviewer')
        self.pm.setLocalRoles( obj=self.old,
                               member_ids=('user2',),
                               member_role='Manager')
        getLR = self.portal.acl_users.getLocalRolesForDisplay
        old_local_roles = getLR(self.old)
        self.migrateObject()

        self.assertEquals(getLR(self.migrated), old_local_roles)

    def test_workflow_migration(self):
        self.wf.doActionFor(self.old, 'hide')
        getWFstate = self.wf.getInfoFor
        old_wf = getWFstate(self.old, 'review_state', None)
        self.login('user1')
        self.failIf(self.pm.checkPermission('View',self.old))
        self.login()
        self.migrateObject()

        self.assertEquals(getWFstate(self.migrated, 'review_state', None),
                                old_wf)

        # check transfer of permissions
        self.login('user1')
        self.failIf(self.pm.checkPermission('View',self.migrated))

    def test_owner_migration(self):
        user = self.portal.acl_users.getUser('user1')
        self.old.changeOwnership(user)
        self.migrateObject()

        self.assertEquals(self.migrated.owner_info()['id'],'user1')


tests.append(TestTypeMigrations)

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
