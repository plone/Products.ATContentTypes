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

from Products.ATContentTypes.config import _ATCT_UNIT_TEST_MODE
from AccessControl import Unauthorized

from Products.ATContentTypes.lib import constraintypes
from Products.ATContentTypes.interfaces import IConstrainTypes
from Products.Archetypes.public import registerType, process_types, listTypes
from Products.Archetypes.Extensions.utils import installTypes
from AccessControl.SecurityManagement import newSecurityManager
from Testing.ZopeTestCase import user_name as default_user

from Products.CMFCore.utils import getToolByName

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

    def test_isMixedIn(self):
        self.failUnless(isinstance(self.af,
                                   constraintypes.ConstrainTypesMixin),
                        "ConstrainTypesMixin was not mixed in to ATFolder")
        self.failUnless(IConstrainTypes.isImplementedBy(self.af),
                        "IConstrainTypes not implemented by ATFolder instance")

    def test_enabled(self):
        self.af.setEnableAddRestrictions(constraintypes.ENABLED)
        self.af.setLocallyAllowedTypes(['Folder', 'Image'])
        self.af.setImmediatelyAddableTypes(['Folder'])
        
        self.failUnlessEqual(self.af.getLocallyAllowedTypes(), 
                                ('Folder', 'Image',))
        self.failUnlessEqual(self.af.getImmediatelyAddableTypes(),
                                ('Folder',))
        
        self.assertRaises(Unauthorized, self.af.invokeFactory, 'Document', 'a')
        try:
            self.af.invokeFactory('Image', 'image', title="death")
        except Unauthorized:
            self.fail()
        
    def test_disabled(self):
        self.af.setEnableAddRestrictions(constraintypes.DISABLED)
        self.af.setLocallyAllowedTypes(['Folder', 'Image'])
        self.af.setImmediatelyAddableTypes(['Folder'])
        
        # We can still set and persist, even though it is disabled - must
        # remember!
        self.failUnlessEqual(self.af.getRawLocallyAllowedTypes(), 
                                ('Folder', 'Image',))
        self.failUnlessEqual(self.af.getRawImmediatelyAddableTypes(), 
                                ('Folder',))
        
        try:
            self.af.invokeFactory('Document', 'whatever', title='life')
            self.af.invokeFactory('Image', 'image', title="more life")
        except Unauthorized:
            self.fail()
            
        # Make sure immediately-addable are all types if we are disabled
        allowedIds = [ctype.getId() for ctype in self.af.allowedContentTypes()]
        self.failUnlessEqual(allowedIds, self.af.getImmediatelyAddableTypes())
        
    def test_acquireFromHomogenousParent(self):
        # Set up outer folder with restrictions enabled
        self.af.setEnableAddRestrictions(constraintypes.ENABLED)
        self.af.setLocallyAllowedTypes(['Folder', 'Image'])
        self.af.setImmediatelyAddableTypes(['Folder'])
        
        # Create inner type to acquire (default)
        self.af.invokeFactory('Folder', 'inner', title='inner')
        inner = self.af.inner
        
        inner.setEnableAddRestrictions(constraintypes.ACQUIRE)
        
        # Test persistence
        inner.setLocallyAllowedTypes(['Document', 'Event'])
        inner.setImmediatelyAddableTypes(['Document'])
        
        self.failUnlessEqual(inner.getRawLocallyAllowedTypes(), 
                                ('Document', 'Event',))
        self.failUnlessEqual(inner.getRawImmediatelyAddableTypes(),
                                ('Document',))
        
        self.assertRaises(Unauthorized, inner.invokeFactory, 'Event', 'a')
        try:
            inner.invokeFactory('Image', 'whatever', title='life')
        except Unauthorized:
            self.fail()
        
        # Make sure immediately-addable are inherited
        self.failUnlessEqual(inner.getImmediatelyAddableTypes(), 
                                self.af.getImmediatelyAddableTypes())
        
        
    def test_acquireFromHetereogenousParent(self):
        
        # Let folder use a restricted set of types
        self.portal.portal_types.Folder.filter_content_types = 1
        self.portal.portal_types.Folder.allowed_content_types = \
            ('Document', 'Image', 'News Item', 'Topic', 'SimpleFolder', 'Folder')
        
        # Set up outer folder with restrictions enabled
        self.af.setEnableAddRestrictions(constraintypes.ENABLED)
        self.af.setLocallyAllowedTypes(['Folder', 'Image', 'SimpleFolder'])
        self.af.setImmediatelyAddableTypes(['Folder'])
  
        # Create inner type to acquire (default)
        self.af.invokeFactory('SimpleFolder', 'outer', title='outer')
        outer = self.af.outer
        
        outer.invokeFactory('Folder', 'inner', title='inner')
        inner = outer.inner 
        
        inner.setEnableAddRestrictions(constraintypes.ACQUIRE)
        
        # Test persistence
        inner.setLocallyAllowedTypes(['Document', 'Event'])
        inner.setImmediatelyAddableTypes(['Document'])
        
        self.failUnlessEqual(inner.getRawLocallyAllowedTypes(), 
                                ('Document', 'Event',))
        self.failUnlessEqual(inner.getRawImmediatelyAddableTypes(),
                                ('Document',))
        
        # Fail - we didn't acquire this, really, since we can't acquire
        # from parent folder of different type
        self.assertRaises(Unauthorized, inner.invokeFactory, 'CMF Folder', 'a')
        self.failIf('CMF Folder' in inner.getLocallyAllowedTypes())
        try:
            # Will be OK, since we've got global defaults since we can't
            # acquire from parent with different type
            inner.invokeFactory('News Item', 'whatever', title='life')
        except Unauthorized:
            self.fail()
        
        # Make sure immediately-addable are set to default
        self.failUnlessEqual(inner.getImmediatelyAddableTypes(), 
                                inner.getLocallyAllowedTypes())
        
        

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
