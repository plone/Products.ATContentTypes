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
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'


import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.ftests import atctftestcase

tests = []

class TestATFolderFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'Folder'
    views = ('folder_listing', 'atct_album_view', )

    def test_templatemixin_view_without_view(self):
        # template mixin should work
        response = self.publish('%s/' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) #
        
    def test_selectViewTemplate(self):
        # create an object using the createObject script
        response = self.publish(self.obj_path +
                                '/selectViewTemplate?templateId=atct_album_view',
                                self.owner_auth)
        self.failUnlessEqual(self.obj.getLayout(), 'atct_album_view')

tests.append(TestATFolderFunctional)

class TestATBTreeFolderFunctional(atctftestcase.ATCTIntegrationTestCase):

    portal_type = 'Large Plone Folder'
    views = ('folder_listing', 'atct_album_view', )

    def afterSetUp(self):
        # enable global allow for BTree Folder
        fti = getattr(self.portal.portal_types, self.portal_type)
        fti.manage_changeProperties(global_allow=1)
        atctftestcase.ATCTIntegrationTestCase.afterSetUp(self)

    def test_templatemixin_view_without_view(self):
        # template mixin magic should work
        response = self.publish('%s/' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) #


tests.append(TestATBTreeFolderFunctional)

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
