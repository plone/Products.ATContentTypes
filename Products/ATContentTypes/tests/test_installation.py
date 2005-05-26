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
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.config import SWALLOW_IMAGE_RESIZE_EXCEPTIONS
from Products.ATContentTypes.tool.atct import ATCTTool
from Products.CMFCore.utils import getToolByName

tests = []

class TestInstallation(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal.aq_explicit, TOOLNAME)
        self.ttool = getattr(self.portal.aq_explicit, 'portal_types')
        self.qi = getattr(self.portal.aq_explicit, 'portal_quickinstaller')
        self.cat = getattr(self.portal.aq_explicit, 'portal_catalog')
        
    def test_installed_products(self):
        qi = self.qi
        installed = [ prod['id'] for prod in qi.listInstalledProducts() ]
        self.failUnless('MimetypesRegistry' in installed, installed)
        self.failUnless('PortalTransforms' in installed, installed)
        self.failUnless('Archetypes' in installed, installed)
        self.failUnless('ATContentTypes' in installed, installed)
        self.failUnless('ATReferenceBrowserWidget' in installed, installed)
        
    def test_tool_installed(self):
        t = getToolByName(self.portal, TOOLNAME, None)
        self.failUnless(t, t)
        self.failUnless(isinstance(t, ATCTTool), t.__class__)
        self.failUnlessEqual(t.meta_type, 'ATCT Tool')
        self.failUnlessEqual(t.getId(), TOOLNAME)

    def test_skin_installed(self):
        stool = getattr(self.portal.aq_explicit, 'portal_skins')
        ids = stool.objectIds()
        self.failUnless('ATContentTypes' in ids, ids)

    def test_installedAllTypes(self):
        # test that all types are installed well
        ttool = self.ttool
        ids = ('Document', 'Favorite', 'File',
            'Folder', 'Image', 'Large Plone Folder', 'Link',
            'News Item', 'Topic', 'Event')

        tids = ttool.objectIds()
        for id in ids:
            self.failUnless(id in tids, (id, tids))
            tinfo = ttool[id]
            self.failUnless(tinfo.product == 'ATContentTypes', tinfo.product)

    def test_reinstallKeepsCMFTypes(self):
        # test if CMF types are not removed and are still CMF types
        # reinstall requires manager roles
        self.setRoles(['Manager', 'Member']) 
        qi = self.qi
        ttool = self.ttool
        cmf_ids = ('CMF Document', 'CMF Favorite', 'CMF File',
            'CMF Folder', 'CMF Image', 'CMF Large Plone Folder', 'CMF Link',
            'CMF News Item', 'CMF Topic', 'CMF Event', )
        cmf_prods = ('CMFPlone', 'CMFDefault', 'CMFTopic', 'CMFCalendar')

        qi.reinstallProducts(('ATContentTypes',))

        tids = ttool.objectIds()
        for id in cmf_ids:
            self.failUnless(id in tids, (id, tids))
            tinfo = ttool[id]
            self.failUnless(tinfo.product in cmf_prods, tinfo.product)
            
    def test_uninstallMakesCMFTypes(self):
        # tests if uninstall resets cmf types
        # reinstall requires manager roles
        self.setRoles(['Manager', 'Member']) 
        qi = self.qi
        ttool = self.ttool
        cmf_ids = ('Document', 'Favorite', 'File',
            'Folder', 'Image', 'Large Plone Folder', 'Link',
            'News Item', 'Topic', 'Event')
        cmf_prods = ('CMFPlone', 'CMFDefault', 'CMFTopic', 'CMFCalendar')

        qi.uninstallProducts(('ATContentTypes',))
        get_transaction().commit(1)

        tids = ttool.objectIds()
        for id in cmf_ids:
            self.failUnless(id in tids, (id, tids))
            tinfo = ttool[id]
            self.failUnless(tinfo.product in cmf_prods, tinfo.product)
            
    def test_installsetsCMFcataloged(self):
        t = self.tool
        self.failUnless(t.getCMFTypesAreRecataloged())

    def test_release_settings_SAVE_TO_FAIL_FOR_DEVELOPMENT(self):
        self.failUnlessEqual(SWALLOW_IMAGE_RESIZE_EXCEPTIONS, True)
 
    def test_reindex_doesnt_add_tools(self):
        cat = self.cat
        ids = [id for id in self.portal.objectIds()
               if id.startswith('portal_') ]
        # a rought guess
        self.failIf(len(ids) < 5)
        for id in ids:
                result = cat(id=id)
                l = len(result)
                self.failUnlessEqual(l, 0, (id, l, result))
 
    def test_adds_related_items_catalog_index(self):
        self.assertEqual(self.cat.Indexes['getRawRelatedItems'].__class__.__name__,
                         'KeywordIndex')
        
    
tests.append(TestInstallation)

##class TestSuppressedInstallation(atcttestcase.ATCTSiteTestCase):
##
##    def afterSetUp(self):
##        os.environ['SUPPRESS_ATCT_INSTALLATION'] = 'YES'
##        
##        self.setRoles(['Manager', 'Owner'])
##        self.login()
##        self.app.manage_addProduct['CMFPlone'].manage_addSite('portal2')
##        self.portal2 = self.app.portal2
##        
##        self.ttool = getattr(self.portal2.aq_explicit, 'portal_types')
##        self.qi = getattr(self.portal2.aq_explicit, 'portal_quickinstaller')
##        
##    def test_atct_not_installed(self):
##        self.failUnlessEqual(getToolByName(self.portal2, TOOLNAME, None), None)
##
##    def beforeTearDown(self):
##        del os.environ['SUPPRESS_ATCT_INSTALLATION']
##
##tests.append(TestSuppressedInstallation)

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
