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

from Testing import ZopeTestCase
from Products.ATContentTypes.tests import atcttestcase
try:
    from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
    NO_PAS = False
except ImportError:
    NO_PAS = True

if ZopeTestCase.hasProduct('kupu'):
    ZopeTestCase.installProduct('kupu')
    HAS_KUPU = True
else:
    HAS_KUPU = False
if ZopeTestCase.hasProduct('Epoz'):
    ZopeTestCase.installProduct('Epoz')
    HAS_EPOZ = True
else:
    HAS_EPOZ = False

import time
from Products.Archetypes.tests.atsitetestcase import ATFunctionalSiteTestCase
from Products.Archetypes.tests.attestcase import default_user
from Products.Archetypes.tests.atsitetestcase import portal_owner
from Products.ATContentTypes.config import HAS_LINGUA_PLONE
from Products.ATContentTypes.tests.utils import FakeRequestSession
from Products.ATContentTypes.tests.utils import DummySessionDataManager
from Products.CMFPlone import transaction

class IntegrationTestCase(ATFunctionalSiteTestCase):

    views = ()

    def afterSetUp(self):
        # Put dummy sdm and dummy SESSION object into REQUEST
        request = self.app.REQUEST
        self.app._setObject('session_data_manager', DummySessionDataManager())
        sdm = self.app.session_data_manager
        request.set('SESSION', sdm.getSessionData())

        # basic data
        self.folder_url = self.folder.absolute_url()
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.basic_auth = '%s:secret' % default_user
        self.owner_auth = '%s:secret' % portal_owner

        # error log
        from Products.SiteErrorLog.SiteErrorLog import temp_logs
        temp_logs = {} # clean up log
        self.error_log = self.portal.error_log
        self.error_log._ignored_exceptions = ()

        # We want 401 responses, not redirects to a login page
        if NO_PAS:
            self.portal._delObject('cookie_authentication')
        else:
            plugins = self.portal.acl_users.plugins
            for id in plugins.listPluginIds(IChallengePlugin):
                plugins.deactivatePlugin(IChallengePlugin, id)

        # disable portal_factory as it's a nuisance here
        self.portal.portal_factory.manage_setPortalFactoryTypes(listOfTypeIds=[])

        # object
        self.setupTestObject()

    def setupTestObject(self):
        self.obj_id = 'test_object'
        self.obj = None
        self.obj_url = self.obj.absolute_url()
        self.obj_path = '/%s' % self.obj.absolute_url(1)

    def assertStatusEqual(self, a, b, msg=''):
        """Helper method that uses the error log to output useful debug infos
        """
        now = time.time()
        if a != b:
            entries = self.error_log.getLogEntries()
            if entries:
                msg = entries[0]['tb_text']
            else:
                if not msg:
                    msg = 'no error log msg available'
        self.failUnlessEqual(a, b, msg)


class ATCTIntegrationTestCase(IntegrationTestCase):
    """Integration tests for view and edit templates
    """
    
    portal_type = None
        
    def setupTestObject(self):
        # create test object
        self.obj_id = 'test_object'
        self.folder.invokeFactory(self.portal_type, self.obj_id, title=self.obj_id)
        self.obj = getattr(self.folder.aq_explicit, self.obj_id)
        self.obj_url = self.obj.absolute_url()
        self.obj_path = '/%s' % self.obj.absolute_url(1)
        
    def test_createObject(self):
        # create an object using the createObject script
        response = self.publish(self.folder_path +
                                '/createObject?type_name=%s' % self.portal_type,
                                self.basic_auth)

        self.assertStatusEqual(response.getStatus(), 302) # Redirect to edit

        # omit ?portal_status_message=...
        body = response.getBody().split('?')[0]
        
        self.failUnless(body.startswith(self.folder_url), body)
        # The url may end with /edit or /atct_edit depending on method aliases
        self.failUnless(body.endswith('edit'), body)

        # Perform the redirect
        edit_form_path = body[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        temp_id = body.split('/')[-2]

        new_obj = getattr(self.folder.portal_factory, temp_id)
        self.failUnlessEqual(self.obj.checkCreationFlag(), True) # object is not yet edited
        

    def check_newly_created(self):
        """Objects created programmatically should not have the creation flag set"""
        self.failUnlessEqual(self.obj.checkCreationFlag(), False) # object is fully created

    def test_edit_view(self):
        # edit should work        
        response = self.publish('%s/atct_edit' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_metadata_edit_view(self):
        # metadata edit should work
        response = self.publish('%s/base_metadata' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_base_view(self):
        # base view should work
        response = self.publish('%s/base_view' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_dynamic_view(self):
        # dynamic view magic should work
        response = self.publish('%s/view' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_local_sharing_view(self):
        # sharing tab should work
        response = self.publish('%s/folder_localrole_form' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK    

    def test_workflow_view(self):
        # workflow tab should work
        response = self.publish('%s/content_status_history' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        
    def test_linguaplone_views(self):
        if not HAS_LINGUA_PLONE:
            return
        
        response = self.publish('%s/translate_item' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        response = self.publish('%s/manage_translations_form' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_linguaplone_create_translation(self):
        if not HAS_LINGUA_PLONE:
            return
        
        # create translation creates a new object
        response = self.publish('%s/createTranslation?language=de&set_language=de' 
                                 % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 302) # Redirect

        # omit ?portal_status_message=...
        body = response.getBody().split('?')[0]
        
        self.failUnless(body.startswith(self.folder_url))
        self.failUnless(body.endswith('/translate_item'))

        # Perform the redirect
        form_path = body[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(form_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        
        translated_id = "%s-de" % self.obj_id
        self.failUnless(translated_id in self.folder.objectIds(),
                        self.folder.objectIds())
    
    def test_additional_view(self):
        # additional views:
        for view in self.views:
            response = self.publish('%s/%s' % (self.obj_path, view), self.basic_auth)
            self.assertStatusEqual(response.getStatus(), 200, 
                "%s: %s" % (view, response.getStatus())) # OK
                
    def test_discussion(self):
        # enable discussion for  the type
        ttool = getToolByName(self.portal, 'portal_types')
        ttool[self.portal_type].allow_discussion = True
        
        response = self.publish('%s/discussion_reply_form' 
                                 % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # ok
        
        response = self.publish('%s/discussion_reply?subject=test&body_text=testbody' 
                                 % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 302) # Redirect
        
        # omit ?portal_status_message=...
        body = response.getBody().split('?')[0]
        
        self.failUnless(body.startswith(self.folder_url))
        
        # Perform the redirect
        form_path = body[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(form_path, self.basic_auth)
#         self.assertStatusEqual(response.getStatus(), 200) # OK
        
        self.failUnless(hasattr(self.obj.aq_explicit, 'talkback'))

    def test_dynamicViewContext(self):
        # register and add a testing template (it's a script)
        self.setRoles(['Manager', 'Member'])
        
        ttool = self.portal.portal_types
        fti = getattr(ttool, self.portal_type)
        view_methods = fti.getAvailableViewMethods(self.obj) + ('unittestGetTitleOf',)
        fti.manage_changeProperties(view_methods=view_methods)
        
        self.obj.setLayout('unittestGetTitleOf')
        self.folder.setTitle('the folder')
        self.obj.setTitle('the obj')

        self.setRoles(['Member'])
        
        response = self.publish('%s/view' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        
        output = response.getBody().split(',')
        self.failUnlessEqual(len(output), 4, output)
        
        self.failUnlessEqual(output, ['the obj', 'the folder', 'the obj', 'the folder'])

from Products.CMFCore.utils import getToolByName
from Products.CMFQuickInstallerTool.QuickInstallerTool import AlreadyInstalled
from Products.Archetypes.tests.atsitetestcase import portal_name
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

def setupEditors(app, id=portal_name, quiet=False):
    transaction.begin()
    _start = time.time()
    portal = app[id]

    # login as manager
    user = app.acl_users.getUserById(portal_owner).__of__(app.acl_users)
    newSecurityManager(None, user)
    qi = getToolByName(portal, 'portal_quickinstaller') 
    # add kupu
    if HAS_KUPU:
        if not quiet: ZopeTestCase._print('Adding kupu ... ')
        try:
            qi.installProduct('kupu')
        except AlreadyInstalled:
            # EAFP = easier ask for forgiveness than permission
            if not quiet: ZopeTestCase._print('kupu already installed ...\n')

    # add Epoz
    if HAS_EPOZ:
        if not quiet: ZopeTestCase._print('Adding Epoz ...')
        try:
            qi.installProduct('Epoz')
        except AlreadyInstalled:
            # EAFP = easier ask for forgiveness than permission
            if not quiet: ZopeTestCase._print('Epoz already installed ... \n')

    noSecurityManager()
    transaction.commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
setupEditors(app)
ZopeTestCase.close(app)
