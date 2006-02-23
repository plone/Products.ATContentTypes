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
__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'


import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.ftests import atctftestcase

tests = []

class TestATDocumentFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'Document'
    views = ('document_view', )

    def test_atct_history_view(self):
        # atct history view is restricted, we have to log in as portal ownr
        response = self.publish('%s/atct_history' % self.obj_path, self.owner_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_id_change_on_initial_edit(self):
        """Make sure Id is taken from title on initial edit and not otherwise"""
        # first create an object using the createObject script

        response = self.publish(self.folder_path +
                                '/createObject?type_name=%s' % self.portal_type,
                                self.basic_auth)

        self.assertStatusEqual(response.getStatus(), 302) # Redirect to edit

        # omit ?portal_status_message=...
        location = response.getHeader('Location').split('?')[0]

        self.failUnless(location.startswith(self.folder_url), location)
        self.failUnless(location.endswith('edit'), location)

        # Perform the redirect
        edit_form_path = location[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

        #Change the title
        temp_id = location.split('/')[-2]
        obj_title = "New Title for Object"
        new_id = "new-title-for-object"
        new_obj = getattr(self.folder.aq_explicit, temp_id)
        new_obj_path = '/%s' % new_obj.absolute_url(1)
        self.failUnlessEqual(new_obj.checkCreationFlag(), True) # object is not yet edited

        response = self.publish('%s/atct_edit?form.submitted=1&title=%s&text=Blank' % (new_obj_path, obj_title,), self.basic_auth) # Edit object
        self.assertStatusEqual(response.getStatus(), 302) # OK
        self.failUnlessEqual(new_obj.getId(), new_id) # does id match
        self.failUnlessEqual(new_obj.checkCreationFlag(), False) # object is fully created
        new_title = "Second Title"
        response = self.publish('%s/atct_edit?form.submitted=1&title=%s&text=Blank' % ('/%s' % new_obj.absolute_url(1), new_title,), self.basic_auth) # Edit object
        self.assertStatusEqual(response.getStatus(), 302) # OK
        self.failUnlessEqual(new_obj.getId(), new_id) # id shouldn't have changed

tests.append(TestATDocumentFunctional)

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
