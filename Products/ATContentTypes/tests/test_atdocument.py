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

__author__ = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.public import *
from Products.ATContentTypes.tests.utils import dcEdit
import time

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.tests.utils import TidyHTMLValidator
from Products.ATContentTypes.migration.atctmigrator import DocumentMigrator
from Products.CMFDefault.Document import Document
from Products.ATContentTypes.interfaces import IHistoryAware
from Products.ATContentTypes.interfaces import ITextContent
from Products.ATContentTypes.interfaces import IATDocument
from Interface.Verify import verifyObject
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

class TestSiteATDocument(atcttestcase.ATCTTypeTestCase):

    klass = ATDocument
    portal_type = 'Document'
    cmf_portal_type = 'CMF Document'
    cmf_klass = Document
    title = 'Page'
    meta_type = 'ATDocument'
    icon = 'document_icon.gif'

    def test_doesImplementHistoryAware(self):
        iface = IHistoryAware
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsTextContent(self):
        iface = ITextContent
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsATDocument(self):
        iface = IATDocument
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.CookedBody(stx_level=2) == new.CookedBody(), 'Body mismatch: %s / %s' \
                        % (old.CookedBody(stx_level=2), new.CookedBody()))

    def test_cmf_edit_failure(self):
        self._ATCT.edit(thisisnotcmfandshouldbeignored=1)

    def test_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()
        body        = old.CookedBody(stx_level=2)

        time.sleep(1.0)

        # migrated (needs subtransaction to work)
        transaction.commit(1)
        m = DocumentMigrator(old)
        m(unittest=1)
        transaction.commit(1)

        self.failUnless(id in self.folder.objectIds(), self.folder.objectIds())
        migrated = getattr(self.folder, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)

        self.assertEquals(migrated.Schema()['text'].getContentType(migrated),
                            'text/structured')
        self.failUnless(migrated.CookedBody() == body, 'Body mismatch: %s / %s' \
                        % (migrated.CookedBody(), body))

    def test_rename_keeps_contenttype(self):
        doc = self._ATCT
        doc.setText(example_rest, mimetype="text/x-rst")
        self.failUnless(str(doc.getField('text').getContentType(doc)) == "text/x-rst")
        #make sure we have _p_jar
        transaction.commit(1)

        cur_id = 'ATCT'
        new_id = 'WasATCT'
        self.folder.manage_renameObject(cur_id, new_id)
        doc = getattr(self.folder, new_id)
        field = doc.getField('text')
        self.failUnless(str(field.getContentType(doc)) == "text/x-rst")

    def test_x_safe_html(self):
        doc = self._ATCT
        mimetypes = (
            ('text/html', '<p>test</p>'),
            # MTR doens't know about text/stx, and transforming
            # doubles the tags. Yuck.
            ('text/structured', '<p><p>test</p></p>\n'),
            # XXX
            # ('text/x-rst', ("<p>&lt;p&gt;test&lt;/p&gt;&lt;script&gt;"
            #                 "I'm a nasty boy&lt;p&gt;nested&lt;/p&gt;"
            #                 "&lt;/script&gt;</p>\n")),
            # ('text/python-source', '<p>test</p>'),
            # XXX
            # ('text/plain', ("<p>&lt;p&gt;test&lt;/p&gt;&lt;script&gt;"
            #                 "I'm a nasty boy&lt;p&gt;nested&lt;/p&gt;"
            #                 "&lt;/script&gt;</p>\n")),
            )
        for mimetype, expected in mimetypes:
            # scrub html is removing unallowed tags
            text = "<p>test</p><script>I'm a nasty boy<p>nested</p></script>"
            doc.setText(text, mimetype=mimetype)
            txt = doc.getText()
            self.failUnlessEqual(txt, expected, (txt, expected, mimetype))
            
    def test_get_size(self):
        atct = self._ATCT
        editATCT(atct)
        self.failUnlessEqual(atct.get_size(), len(example_stx))

tests.append(TestSiteATDocument)

class TestATDocumentFields(atcttestcase.ATCTFieldTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATDocument)

    def test_text_field_mutator_filename(self):
        dummy = self._dummy
        field = dummy.getField('text')
        mutator = field.getMutator(dummy)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/html')
        mutator('', filename='foo.txt')
        self.assertEquals(field.getFilename(dummy), 'foo.txt')
        self.assertEquals(field.getContentType(dummy), 'text/plain')

    def test_text_field_mutator_mime(self):
        dummy = self._dummy
        field = dummy.getField('text')
        mutator = field.getMutator(dummy)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/html')
        mutator('', mimetype='text/plain')
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/plain')

    def test_text_field_mutator_none_mime(self):
        dummy = self._dummy
        field = dummy.getField('text')
        mutator = field.getMutator(dummy)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/html')
        mutator('', mimetype=None)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/plain')

    def test_text_field_mutator_none_filename(self):
        dummy = self._dummy
        field = dummy.getField('text')
        mutator = field.getMutator(dummy)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/html')
        mutator('', filename=None)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/plain')

    def test_textField(self):
        dummy = self._dummy
        field = dummy.getField('text')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getText',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setText',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'text', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AnnotationStorage(migrate=True),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == TidyHTMLValidator,
                        'Value is %s' % repr(field.validators))
        self.failUnless(isinstance(field.widget, RichWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)
        self.failUnless(field.default_content_type == 'text/html',
                        'Value is %s' % field.default_content_type)
        self.failUnless(field.default_output_type == 'text/x-html-safe',
                        'Value is %s' % field.default_output_type)
        
        self.failUnless('text/html' in field.allowable_content_types)
        self.failUnless('text/structured'  in field.allowable_content_types)

tests.append(TestATDocumentFields)

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
