# -*- coding: utf-8 -*-
from plone.app.testing.bbb_at import PloneTestCase
from Products.CMFCore.utils import getToolByName


class TestBaseProfile(PloneTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        from Products.CMFPlone.utils import get_installer
        qi = get_installer(self.portal)
        qi.uninstall_product('Products.ATContentTypes')
        portal_setup = self.portal.portal_setup
        # It looks like the hiddenprofile utility from CMFPlone is not loaded
        # in these tests.  So our default profile is installed, instead of only
        # our base profile.  This explains why our portal_types are available
        # at all.  This means we need to manually apply the fullinstall
        # profile.
        portal_setup.runAllImportStepsFromProfile(
            'Products.ATContentTypes:fulluninstall')
        # Now we apply the base profile.
        portal_setup.runAllImportStepsFromProfile(
            'profile-Products.ATContentTypes:base')

    def test_attypes_not_installed(self):
        tt = getToolByName(self.portal, 'portal_types')
        types = tt.listTypeInfo()
        for t in types:
            self.assertNotEqual(t.product, 'ATContentTypes')
