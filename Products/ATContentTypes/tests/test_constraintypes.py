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

__author__ = 'Leonardo Almeida'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

from Products.ATContentTypes.config import ENABLE_CONSTRAIN_TYPES_MIXIN
from Products.ATContentTypes.config import _ATCT_UNIT_TEST_MODE

from AccessControl import Unauthorized
from Products.ATContentTypes import ConstrainTypesMixin
from Products.ATContentTypes.interfaces import IConstrainTypes
from Products.Archetypes.public import registerType, process_types, listTypes
from Products.Archetypes.Extensions.utils import installTypes
from AccessControl.SecurityManagement import newSecurityManager
from Testing.ZopeTestCase import user_name as default_user


tests = []

class TestConstrainTypes(atcttestcase.ATCTSiteTestCase):
    folder_type = 'Folder'
    image_type = 'Image'
    document_type = 'Document'
    file_type = 'File'

    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.folder.invokeFactory(self.folder_type, id='af')
        self.tt = self.portal.portal_types
        # an ATCT folder
        self.af = self.folder.af
        # portal_types object for ATCT folder
        self.at = self.tt.getTypeInfo(self.af)
        
    def test_000enabledforunittest(self):
        self.failUnless(_ATCT_UNIT_TEST_MODE)
        self.failUnless(ENABLE_CONSTRAIN_TYPES_MIXIN)

    def test_isMixedIn(self):
        self.failUnless(isinstance(self.af,
                                   ConstrainTypesMixin.ConstrainTypesMixin),
                        "ConstrainTypesMixin was not mixed in to ATFolder")
        self.failUnless(IConstrainTypes.isImplementedBy(self.af),
                        "IConstrainTypes not implemented by ATFolder instance")

    def test_unconstrained(self):
        # unlimited types at portal_types tool
        # no portal_type filtered at object
        af = self.af
        at = self.at
        at.manage_changeProperties(filter_content_types=False)
        self.failIf(at.filter_content_types,
                    "ContentTypes are still being filtered at factory")
        af.setLocallyAllowedTypes([])
        possible_types_ids = [fti.id for fti in af._ct_getPossibleTypes()]
        self.failIf(self.image_type not in possible_types_ids,
                    'Image not available to be filtered!')
        allowed_ids = [fti.id for fti in af.allowedContentTypes()]
        self.failIf(self.image_type not in allowed_ids,
                    'Image not available to add!')
        af.invokeFactory(self.image_type, id='anATImage')
        afi = af.anATImage # will bail if invokeFactory didn't work
        self.failIf(self.document_type not in possible_types_ids,
                    'Document not available to add!')
        af.invokeFactory(self.document_type, id='anATDocument')
        afd = af.anATDocument # will bail if invokeFactory didn't work

    def test_constrained(self):
        af = self.af
        at = self.at
        af.setEnableConstrainMixin(True)
        at.manage_changeProperties(filter_content_types=False)
        self.failIf(at.filter_content_types,
                    "ContentTypes are still being filtered at factory")
        af.setLocallyAllowedTypes([self.image_type])
        allowed_ids = [fti.id for fti in af.allowedContentTypes()]
        af.invokeFactory(self.image_type, id='anATImage')
        afi = af.anATImage # will bail if invokeFactory didn't work
        self.assertEquals(allowed_ids, [self.image_type])
        self.assertRaises(Unauthorized, af.invokeFactory,
                          self.document_type, id='anATDocument')

    def test_ftiInteraction(self):
        af = self.af
        at = self.at
        tt = self.tt
        af.setEnableConstrainMixin(True)
        af_allowed_types = [self.document_type, self.image_type,
                            self.file_type, self.folder_type, ]
        af_allowed_types.sort()
        at.manage_changeProperties(filter_content_types=True,
                                   allowed_content_types=af_allowed_types)
        af.setLocallyAllowedTypes([])
        af_local_types = [fti.getId() for fti in af.allowedContentTypes()]
        af_local_types.sort()
        self.assertEquals(af_allowed_types, af_local_types)
        #                  "fti allowed types don't match local ones")
        # let's limit locally and see what happens
        types1 = [self.image_type, self.file_type, self.folder_type]
        types1.sort()
        af.setLocallyAllowedTypes(types1)
        af_local_types = [fti.getId() for fti in af.allowedContentTypes()]
        af_local_types.sort()
        self.assertEquals(types1, af_local_types,
                          "constrained types don't match local ones")
        # now let's unlimit globally to see if the local constrains remain
        at.manage_changeProperties(filter_content_types=False)
        af_local_types = [fti.getId() for fti in af.allowedContentTypes()]
        af_local_types.sort()
        self.assertEquals(types1, af_local_types,
                          "constrained types don't match local ones")
        
        # XXX this test does't work because it expects a CMF Folder!
        
        # now let's see if inheritance kicks in even thru a non
        # constrained type
        af.invokeFactory('Folder', id='nf')
        af.nf.invokeFactory('Folder', id='bf')
        bf = af.nf.bf
        bf_local_types = [fti.getId() for fti in af.allowedContentTypes()]
        bf_local_types.sort()
        self.assertEquals(types1, bf_local_types,
                          "constrained types don't match inherited ones")

    def test_unconstrainedButUnauthorized(self):
        user = self.portal.portal_membership.getMemberById(default_user)
        self.logout()
        newSecurityManager(None, user)
        af = self.af
        self.assertRaises(Unauthorized,
                          af.invokeFactory, self.folder_type, id='bf')
        self.logout()

tests.append(TestConstrainTypes)

import unittest
def test_suite():
    # framework.py test_suite is trying to run ATCT*TestCase
    # so we have to provide our own
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

if __name__ == '__main__':
    framework()
