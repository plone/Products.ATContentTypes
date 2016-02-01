# -*- coding: utf-8 -*-
from plone.app.testing.bbb import PloneTestCase
from Products.CMFCore.utils import getToolByName


class TestBaseProfile(PloneTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        qi = self.portal.portal_quickinstaller
        qi.uninstallProducts(['ATContentTypes'])
        portal_setup = self.portal.portal_setup
        portal_setup.runAllImportStepsFromProfile(
            'profile-Products.ATContentTypes:base')

    def test_attypes_not_installed(self):
        tt = getToolByName(self.portal, 'portal_types')
        types = tt.listTypeInfo()
        for t in types:
            self.assertNotEqual(t.product, 'ATContentTypes')
