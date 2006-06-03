# -*- coding: utf-8 -*-
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

import unittest
from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase, atctftestcase

import time, transaction
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.atapi import *
from Products.ATContentTypes.tests.utils import dcEdit
import StringIO

from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.migration.atctmigrator import FileMigrator
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IFileContent
from Products.CMFDefault.File import File
from Interface.Verify import verifyObject

# z3 imports
from Products.ATContentTypes.interface import IATFile as Z3IATFile
from Products.ATContentTypes.interface import IFileContent as Z3IFileContent
from zope.interface.verify import verifyObject as Z3verifyObject


file_text = """
foooooo
"""

def editCMF(obj):
    dcEdit(obj)
    obj.edit(file=file_text)

def editATCT(obj):
    dcEdit(obj)
    obj.edit(file=file_text)

tests = []

class TestSiteATFile(atcttestcase.ATCTTypeTestCase):

    klass = ATFile
    portal_type = 'File'
    cmf_portal_type = 'CMF File'
    cmf_klass = File
    title = 'File'
    meta_type = 'ATFile'
    icon = 'file_icon.gif'

    def test_implementsFileContent(self):
        iface = IFileContent
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsZ3FileContent(self):
        iface = Z3IFileContent
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsATFile(self):
        iface = IATFile
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsZ3ATFile(self):
        iface = Z3IATFile
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.compareDC(old, new)
        self.failUnlessEqual(str(old), str(new.getFile()))

    def testCompatibilityFileAccess(self):
        new = self._ATCT
        editATCT(new)
        # test for crappy access ways of CMF :)
        self.failUnlessEqual(str(new), file_text)
        self.failUnlessEqual(new.data, file_text)
        self.failUnlessEqual(str(new.getFile()), file_text)
        self.failUnlessEqual(new.getFile().data, file_text)
        self.failUnlessEqual(new.get_data(), file_text)

    def testCompatibilityContentTypeAccess(self):
        new = self._ATCT
        editATCT(new)
        # TODO: more tests

    def test_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()
        file        = str(old)

        time.sleep(1.5)

        # migrated (needs subtransaction to work)
        transaction.savepoint(optimistic=True)
        m = FileMigrator(old)
        m(unittest=1)

        self.failUnless(id in self.folder.objectIds(), self.folder.objectIds())
        migrated = getattr(self.folder, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)

        self.failUnlessEqual(file, str(migrated.getFile()))
        self.failIfEqual(migrated.data, None)
        self.failIfEqual(migrated.data, '')
        # TODO: more tests

    def test_schema_marshall(self):
        atct = self._ATCT
        schema = atct.Schema()
        marshall = schema.getLayerImpl('marshall')
        marshallers = [PrimaryFieldMarshaller]
        try:
            from Products.Marshall import ControlledMarshaller
            marshallers.append(ControlledMarshaller)
        except ImportError:
            pass
        self.failUnless(isinstance(marshall, tuple(marshallers)), marshall)

    def testInvokeFactoryWithFileContents(self):
        # test for Plone tracker #4939
        class fakefile(StringIO.StringIO):
            pass
        fakefile = fakefile()
        fakefile.filename = 'some_filename'
        id = self.folder.invokeFactory(self.portal_type,
                                       'image.2005-11-18.4066860572',
                                       file=fakefile)
        self.assertEquals(id, fakefile.filename)

    def testUpperCaseFilename(self):
        class fakefile(StringIO.StringIO):
            pass
        fakefile = fakefile()
        fakefile.filename = 'Some_filename_With_Uppercase.txt'
        id = 'file.2005-11-18.4066860573'
        self.folder.invokeFactory(self.portal_type, id)
        self.folder[id].setFile(fakefile)
        self.failIf(id in self.folder.objectIds())
        self.failUnless(fakefile.filename in self.folder.objectIds())

    def testUpperCaseFilenameWithFunnyCharacters(self):
        class fakefile(StringIO.StringIO):
            pass
        fakefile = fakefile()
        fakefile.filename = 'Zope&Plo?ne .txt'
        id = 'file.2005-11-18.4066860574'
        self.folder.invokeFactory(self.portal_type, id)
        self.folder[id].setFile(fakefile)
        self.failIf(id in self.folder.objectIds())
        self.failUnless('Zope-Plo-ne .txt' in self.folder.objectIds())

tests.append(TestSiteATFile)

class TestATFileFields(atcttestcase.ATCTFieldTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATFile)

    def test_fileField(self):
        dummy = self._dummy
        field = dummy.getField('file')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getFile',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setFile',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'file', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AnnotationStorage(migrate=True),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == "(('isNonEmptyFile', V_REQUIRED), ('checkFileMaxSize', V_REQUIRED))",
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, FileWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))
        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)

tests.append(TestATFileFields)

class TestCleanupFilename(unittest.TestCase):

    def test_cleanup_filename(self):
        from Products.ATContentTypes.content.base import cleanupFilename
        text = '????? ??????'
        self.assertEquals(cleanupFilename(text, 'utf-8'), 'Nikos_Tzanos')

tests.append(TestCleanupFilename)

class TestATFileFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'File'
    views = ('file_view', 'download', )

tests.append(TestATFileFunctional)


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
