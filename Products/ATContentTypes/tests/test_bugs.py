#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
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
"""Test module for bug reports
"""

__author__ = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase
from Products.validation.interfaces.IValidator import IValidationChain
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from Products.Archetypes.atapi import *

tests = []

class TestBugs(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.qi = self.portal.portal_quickinstaller
        self.pt = self.portal.portal_types
        self.tool = self.portal.portal_atct
        self.wf = self.portal.portal_workflow

    def test_reinstall_keeps_obj_wf_state(self):
        wf = self.wf
        self.folder.invokeFactory('Document', 'testdoc', title="test doc",
                                  text="test body")
        obj = self.folder.testdoc

        state = wf.getInfoFor(obj, 'review_state', default=None)
        self.failUnlessEqual(state, 'visible')

        self.qi.reinstallProducts(('ATContentTypes',))

        state = wf.getInfoFor(obj, 'review_state', default=None)
        self.failUnlessEqual(state, 'visible')

        wf.doActionFor(obj, 'submit')

        state = wf.getInfoFor(obj, 'review_state', default=None)
        self.failUnlessEqual(state, 'pending')

        self.qi.reinstallProducts(('ATContentTypes',))

        state = wf.getInfoFor(obj, 'review_state', default=None)
        self.failUnlessEqual(state, 'pending')

    def test_wfmapping(self):
        default = ('plone_workflow',)
        folder = ('folder_workflow',)

        mapping = {
            'Document' : default,
            'Event' : default,
            'Favorite' : default,
            'File' : default,
            'Folder' : folder,
            'Large Plone Folder' : folder,
            'Image' : default,
            'Link' : default,
            'News Item' : default,
            'Topic' : folder,
            }

        for pt, wf in mapping.items():
            pwf = self.wf.getChainFor(pt)
            self.failUnlessEqual(pwf, wf, (pt, pwf, wf))

    def test_reinstall_keeps_wfmapping(self):
        pt = 'Document'
        wf = ('folder_workflow',)

        self.wf.setChainForPortalTypes((pt,), wf)
        pwf = self.wf.getChainFor(pt)
        self.failUnlessEqual(pwf, wf, (pt, pwf, wf))

        self.qi.reinstallProducts(('ATContentTypes',))

        pwf = self.wf.getChainFor(pt)
        self.failUnlessEqual(pwf, wf, (pt, pwf, wf))

    def test_striphtmlbug(self):
        # Test for Plone tracker #4944
        self.folder.invokeFactory('Document', 'document')
        d = getattr(self.folder, 'document')
        d.setTitle("HTML end tags start with </ and end with >")
        self.assertEqual(d.Title(), "HTML end tags start with </ and end with >")

    def test_validation_layer_from_id_field_from_base_schema_was_initialized(self):
        field = ATContentTypeSchema['id']
        self.failUnless(IValidationChain.isImplementedBy(field.validators))


tests.append(TestBugs)


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
