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

__author__ = 'Leonardo Almeida and Martin Aspeli <optilude@gmx.net>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

from Products.ATContentTypes.config import _ATCT_UNIT_TEST_MODE
from AccessControl import Unauthorized

from Products.ATContentTypes.lib import browserdefault
from Products.ATContentTypes import permission
from Products.CMFPlone.interfaces.BrowserDefault import ISelectableBrowserDefault
from Products.Archetypes.public import registerType, process_types, listTypes
from Products.Archetypes.Extensions.utils import installTypes
from AccessControl.SecurityManagement import newSecurityManager
from Testing.ZopeTestCase import user_name as default_user

from Products.CMFCore.utils import getToolByName

tests = []

class TestBrowserDefaultMixin(atcttestcase.ATCTSiteTestCase):
    folder_type = 'Folder'
    image_type = 'Image'
    document_type = 'Document'
    file_type = 'File'

    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.folder.invokeFactory(self.folder_type, id='af')
        # an ATCT folder
        self.af = self.folder.af
        
    def test_000enabledforunittest(self):
        self.failUnless(_ATCT_UNIT_TEST_MODE)

    def test_isMixedIn(self):
        self.failUnless(isinstance(self.af,
                                   browserdefault.BrowserDefaultMixin),
                        "ISelectableBrowserDefault was not mixed in to ATFolder")
        self.failUnless(ISelectableBrowserDefault.isImplementedBy(self.af),
                        "ISelectableBrowserDefault not implemented by ATFolder instance")


    def test_defaultFolderViews(self):
        self.assertEqual(self.af.getLayout(), 'folder_listing')
        self.assertEqual(self.af.getDefaultPage(), None)
        self.assertEqual(self.af.defaultView(), 'folder_listing')
        self.assertEqual(self.af.getDefaultLayout(), 'folder_listing')
        self.failUnless('folder_listing' in self.af.getAvailableLayouts())
        self.failUnless('atct_album_view' in self.af.getAvailableLayouts())
        self.assertEqual(self.af.__browser_default__(None), (self.af, ['folder_listing',]))
        
    def test_canSetLayout(self):
        self.failUnless(self.af.canSetLayout())
        self.af.invokeFactory('Document', 'ad')
        self.failIf(self.af.ad.canSetLayout()) # Can only select one
        self.portal.manage_permission(permission.ModifyViewTemplate, [], 0)
        self.failIf(self.af.canSetLayout()) # Not permitted
    
    def test_setLayout(self):
        self.af.setLayout('atct_album_view')
        self.assertEqual(self.af.getLayout(), 'atct_album_view')
        self.assertEqual(self.af.getDefaultPage(), None)
        self.assertEqual(self.af.defaultView(), 'atct_album_view')
        self.assertEqual(self.af.getDefaultLayout(), 'folder_listing')
        self.failUnless('folder_listing' in self.af.getAvailableLayouts())
        self.failUnless('atct_album_view' in self.af.getAvailableLayouts())
        self.assertEqual(self.af.__browser_default__(None), (self.af, ['atct_album_view',]))
        
    def test_canSetDefaultPage(self):
        self.failUnless(self.af.canSetDefaultPage())
        self.af.invokeFactory('Document', 'ad')
        self.failIf(self.af.ad.canSetDefaultPage()) # Not folderish
        self.portal.manage_permission(permission.ModifyViewTemplate, [], 0)
        self.failIf(self.af.canSetDefaultPage()) # Not permitted
        
    def test_setDefaultPage(self):
        self.af.invokeFactory('Document', 'ad')
        self.af.setDefaultPage('ad')
        self.assertEqual(self.af.getDefaultPage(), 'ad')
        self.assertEqual(self.af.defaultView(), 'ad')
        self.assertEqual(self.af.__browser_default__(None), (self.af, ['ad',]))
        
        # still have layout settings
        self.assertEqual(self.af.getLayout(), 'folder_listing')
        self.assertEqual(self.af.getDefaultLayout(), 'folder_listing')
        self.failUnless('folder_listing' in self.af.getAvailableLayouts())
        self.failUnless('atct_album_view' in self.af.getAvailableLayouts())
    
    def test_setLayoutUnsetsDefaultPage(self):
        self.af.invokeFactory('Document', 'ad')
        self.af.setDefaultPage('ad')
        self.assertEqual(self.af.getDefaultPage(), 'ad')
        self.assertEqual(self.af.defaultView(), 'ad')
        self.af.setLayout('folder_listing')
        self.assertEqual(self.af.getDefaultPage(), None)
        self.assertEqual(self.af.defaultView(), 'folder_listing')
        self.assertEqual(self.af.__browser_default__(None), (self.af, ['folder_listing',]))

tests.append(TestBrowserDefaultMixin)

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
