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
from Products.ATContentTypes.interfaces import IATCTTool
from Interface.Verify import verifyObject
from Products.CMFCore.utils import getToolByName

tests = []

class TestTool(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, TOOLNAME)
        
    def test_cmfftis(self):
        t = self.tool
        ftis = t._getCMFFtis()
        self.failUnless(isinstance(ftis, list))
        self.failUnlessEqual(len(ftis), 10)
        
    def test_cmfmetatypes(self):
        t = self.tool
        mt = t._getCMFMetaTypes()
        expected = ['CMF Event', 'Document', 'Favorite', 'Large Plone Folder',
            'Link', 'News Item', 'Plone Folder', 'Portal File',
            'Portal Image', 'Portal Topic',]
        mt.sort()
        expected.sort()
        self.failUnlessEqual(mt, expected)
        
    def test_cmfportaltypes(self):
        t = self.tool
        pt = t._getCMFPortalTypes()
        expected = ['CMF Document', 'CMF Favorite', 'CMF File',
            'CMF Folder', 'CMF Image', 'CMF Large Plone Folder', 'CMF Link',
            'CMF News Item', 'CMF Topic', 'CMF Event']
        pt.sort()
        expected.sort()
        self.failUnlessEqual(pt, expected)
        
        pt = t._getCMFPortalTypes(metatype="Portal Topic")
        self.failUnlessEqual(pt, ['CMF Topic'])
        
    def test_uncatalogcmf(self):
        t = self.tool
        cat = getToolByName(self.portal, 'portal_catalog')
        mt = t._getCMFMetaTypes()
        pt = t._getCMFPortalTypes()
        
        count, time, cttime = t._removeCMFtypesFromCatalog(count=True)
        
        brains = cat(meta_type=mt)
        self.failUnlessEqual(len(brains), 0)
        
        brains = cat(portal_type=pt)
        self.failUnlessEqual(len(brains), 0)
        
    def test_catalogcmf(self):
        t = self.tool
        cat = getToolByName(self.portal, 'portal_catalog')
        mt = t._getCMFMetaTypes()
        pt = t._getCMFPortalTypes()
        
        # XXX add a cmf based object before cataloging

        result, time, ctime = t._catalogCMFtypes() 

        brains = cat(meta_type=mt)
        #self.failUnless(len(brains) > 0)
        
        brains = cat(portal_type=pt)
        #self.failUnless(len(brains) > 0)
        
    def test_recatalogCMFTypes(self):
        # just to make sure it is callable
        t = self.tool
        t.recatalogCMFTypes()
        
    def test_interface(self):
        t = self.tool
        self.failUnless(IATCTTool.isImplementedBy(t))
        self.failUnless(verifyObject(IATCTTool, t))
        
    def test_names(self):
        t = self.tool
        self.failUnlessEqual(t.meta_type, 'ATCT Tool')
        self.failUnlessEqual(t.getId(), TOOLNAME)
        self.failUnlessEqual(t.title, 'ATContentTypes Tool')
        self.failUnlessEqual(t.plone_tool, True)
        
    def test_copyftiflags(self):
        t = self.tool
        ttool = getToolByName(self.portal, 'portal_types')
        cmfdoc = ttool['CMF Document']
        atctdoc = ttool['Document']
        
        cmfdoc.manage_changeProperties(allow_discussion=True)
        t.copyFTIFlags()
        self.failUnlessEqual(atctdoc.allow_discussion, True)
        
        cmfdoc.manage_changeProperties(allow_discussion=False)
        t.copyFTIFlags()
        self.failUnlessEqual(atctdoc.allow_discussion, False)
        
    def test_copyactions(self):
        t = self.tool
        ttool = getToolByName(self.portal, 'portal_types')
        cmfdoc = ttool['CMF Document']
        atctdoc = ttool['Document']
        
        id = 'test'
        title = 'Test Title'
        expression = 'string: ${object}/getId'
        
        cmfdoc.addAction('test' , name=title, action=expression, condition='',
                         permission='Manage properties', category='object')
        t.copyFTIFlags()
        atct_actions_ids = [action.getId() for action in atctdoc.listActions()]
        self.failUnless(id in atct_actions_ids, atct_actions_ids)

tests.append(TestTool)

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
