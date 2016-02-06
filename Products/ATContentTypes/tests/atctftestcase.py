# -*- coding: utf-8 -*-
from hashlib import sha1 as sha
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.keyring.interfaces import IKeyManager
from Products.ATContentTypes.config import HAS_LINGUA_PLONE
from Products.ATContentTypes.tests import atcttestcase
from zope.component import getUtility

import hmac


class IntegrationTestCase(atcttestcase.ATCTFunctionalSiteTestCase):

    views = ()

    def afterSetUp(self):
        super(IntegrationTestCase, self).afterSetUp()

        # basic data
        self.folder_url = self.folder.absolute_url()
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.basic_auth = '%s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD)
        self.owner_auth = '%s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        # object
        self.setupTestObject()

    def setupTestObject(self):
        raise NotImplementedError

    def getAuthToken(self, user=TEST_USER_ID):
        manager = getUtility(IKeyManager)
        try:
            ring = manager[u"_forms"]
        except KeyError:
            ring = manager[u'_system']

        secret = ring.random()
        return hmac.new(secret, user, sha).hexdigest()


class ATCTIntegrationTestCase(IntegrationTestCase):
    """Integration tests for view and edit templates
    """

    portal_type = None

    def beforeTearDown(self):
        del self.folder[self.obj_id]

    def setupTestObject(self):
        # create test object
        self.obj_id = 'test_object'
        self.title = u'test \xf6bject'
        if self.obj_id not in self.folder:
            self.folder.invokeFactory(
                self.portal_type, self.obj_id, title=self.title)
        self.obj = getattr(self.folder.aq_explicit, self.obj_id)
        self.obj_url = self.obj.absolute_url()
        self.obj_path = '/%s' % self.obj.absolute_url(1)

    def test_createObject(self):
        # create an object using the createObject script
        auth = self.getAuthToken()
        response = self.publish(
            '%s/createObject?type_name=%s&_authenticator=%s' % (
                self.folder_path, self.portal_type, auth),
            self.basic_auth)

        self.assertEqual(response.getStatus(), 302)  # Redirect to edit

        body = response.getBody()

        self.assertTrue(body.startswith(self.folder_url), body)
        # The url may end with /edit or /atct_edit depending on method aliases
        self.assertTrue('edit' in body, body)

        # Perform the redirect
        edit_form_path = body[len(self.layer['request'].SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)  # OK
        temp_id = body.split('/')[-2]

        new_obj = self.folder.portal_factory._getTempFolder(self.portal_type)[
            temp_id]
        # object is not yet edited
        self.assertEqual(new_obj.checkCreationFlag(), True)

    def check_newly_created(self):
        """Objects created programmatically should not have creation flag set.
        """
        self.assertEqual(self.obj.checkCreationFlag(),
                         False)  # object is fully created

    def test_edit_view(self):
        # edit should work
        response = self.publish(
            '%s/atct_edit?_authenticator=%s' % (
                self.obj_path, self.getAuthToken()),
            self.basic_auth)
        self.assertTrue(response.getBody().startswith('<!DOCTYPE html'))
        self.assertTrue(response.getStatus() in (302, 200))  # OK

    def test_base_view(self):
        # base view should work
        response = self.publish('%s/base_view' %
                                self.obj_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)  # OK

    def test_dynamic_view(self):
        # dynamic view magic should work
        response = self.publish('%s/view' % self.obj_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)  # OK

    def test_local_sharing_view(self):
        # sharing tab should work
        response = self.publish('%s/sharing' % self.obj_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)  # OK

    # LinguaPlone specific tests
    if HAS_LINGUA_PLONE:

        def test_linguaplone_views(self):
            response = self.publish('%s/translate_item' %
                                    self.obj_path, self.basic_auth)
            self.assertEqual(response.getStatus(), 200)  # OK
            response = self.publish(
                '%s/manage_translations_form' % self.obj_path, self.basic_auth)
            self.assertEqual(response.getStatus(), 200)  # OK

        def test_linguaplone_create_translation(self):
            # create translation creates a new object
            response = self.publish(
                '{}/createTranslation?language=de&set_language=de'.format(
                    self.obj_path), self.basic_auth)
            self.assertEqual(response.getStatus(), 302)  # Redirect

            body = response.getBody()
            self.assertTrue(body.startswith(self.folder_url))
            self.assertTrue(body.endswith('/translate_item'))

            # Perform the redirect
            form_path = body[len(self.app.REQUEST.SERVER_URL):]
            response = self.publish(form_path, self.basic_auth)
            self.assertEqual(response.getStatus(), 200)  # OK

            translated_id = "%s-de" % self.obj_id
            self.assertTrue(translated_id in self.folder,
                            self.folder)

    def test_additional_view(self):
        # additional views:
        for view in self.views:
            response = self.publish(
                '%s/%s' % (self.obj_path, view), self.basic_auth)
            self.assertEqual(response.getStatus(), 200,
                             "%s: %s" % (view, response.getStatus()))  # OK

    def test_dynamicViewContext(self):
        # register and add a testing template (it's a script)
        self.setRoles(['Manager', 'Member'])

        ttool = self.portal.portal_types
        fti = getattr(ttool, self.portal_type)
        view_methods = fti.getAvailableViewMethods(
            self.obj) + ('unittestGetTitleOf',)
        fti.manage_changeProperties(view_methods=view_methods)

        self.obj.setLayout('unittestGetTitleOf')
        self.folder.setTitle('the folder')
        self.obj.setTitle('the obj')

        self.setRoles(['Member'])

        response = self.publish('%s/view' % self.obj_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)  # OK

        output = response.getBody().split(',')
        self.assertEqual(len(output), 4, output)

        self.assertEqual(
            output, ['the obj', 'the folder', 'the obj', 'the folder'])
