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
from Products.ATContentTypes.tests.utils import dcEdit, PACKAGE_HOME
from AccessControl import Unauthorized

tests = []

TEST_JPEG = open(os.path.join(PACKAGE_HOME, 'CanonEye.jpg'), 'rb').read()

class TestATImageFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'Image'
    views = ('image_view', 'download', 'atct_image_transform')

    def afterSetUp(self):
        atctftestcase.ATCTIntegrationTestCase.afterSetUp(self)
        self.obj.setImage(TEST_JPEG, content_type="image/jpeg")
        dcEdit(self.obj)

    def test_url_returns_image(self):
        response = self.publish(self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        
    def test_bobo_hook_security(self):
        # Make sure that users with 'View' permission can use the
        # bobo_traversed image scales, even if denied to anonymous
        response1 = self.publish(self.obj_path+'/image', self.basic_auth)
        self.assertStatusEqual(response1.getStatus(), 200) # OK
        # deny access to anonymous
        self.obj.manage_permission('View', ['Manager','Member'],0)
        response2 = self.publish(self.obj_path+'/image', self.basic_auth)
        # Should be allowed for member
        self.assertStatusEqual(response2.getStatus(), 200) # OK
        # Should fail for anonymous
        response3 = self.publish(self.obj_path+'/image')
        self.assertStatusEqual(response3.getStatus(), 401)
        

tests.append(TestATImageFunctional)

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
