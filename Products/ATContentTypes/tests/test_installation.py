# -*- coding: utf-8 -*-
from Products.ATContentTypes.config import SWALLOW_IMAGE_RESIZE_EXCEPTIONS
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.tests import atcttestcase
from Products.ATContentTypes.tool.atct import ATCTTool
from Products.CMFCore.utils import getToolByName
import unittest

tests = []


class TestInstallation(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal.aq_explicit, TOOLNAME)
        self.ttool = getattr(self.portal.aq_explicit, 'portal_types')
        self.cat = getattr(self.portal.aq_explicit, 'portal_catalog')

    def test_tool_installed(self):
        t = getToolByName(self.portal, TOOLNAME, None)
        self.assertTrue(t, t)
        self.assertTrue(isinstance(t, ATCTTool), t.__class__)
        self.assertEqual(t.meta_type, 'ATCT Tool')
        self.assertEqual(t.getId(), TOOLNAME)

    def test_skin_installed(self):
        stool = getattr(self.portal.aq_explicit, 'portal_skins')
        self.assertTrue('ATContentTypes' in stool)

    def test_installedAllTypes(self):
        # test that all types are installed well
        ids = ('Document', 'File', 'Folder', 'Image', 'Link',
               'News Item', 'Topic', 'Event')
        for i in ids:
            self.assertTrue(i in self.ttool)

    def test_quickinstallable(self):
        # Test, if the Product is available in Quickinstaller.  For Plone < 5
        # it shouldn't (since it's a core dependency), for Plone >= 5 it should
        # (where plone.app.contenttypes is installed by default instead).
        # Only Plone 5 is supported here.
        try:
            from Products.CMFPlone.utils import get_installer
        except ImportError:
            qi = getattr(self.portal, 'portal_quickinstaller')
            products = [prod['id'] for prod in qi.listInstalledProducts()]
            self.assertTrue('ATContentTypes' in products)
        else:
            qi = get_installer(self.portal)
            self.assertTrue(qi.is_product_installed('Products.ATContentTypes'))

    def test_release_settings_SAVE_TO_FAIL_FOR_DEVELOPMENT(self):
        self.assertEqual(SWALLOW_IMAGE_RESIZE_EXCEPTIONS, True)

    def test_reindex_doesnt_add_tools(self):
        cat = self.cat
        ids = [i for i in self.portal if i.startswith('portal_')]
        # a rought guess
        self.assertFalse(len(ids) < 5)
        for id in ids:
            result = cat(id=id)
            l = len(result)
            self.assertEqual(l, 0, (id, l, result))

    def test_adds_related_items_catalog_index(self):
        self.assertEqual(
            self.cat.Indexes['getRawRelatedItems'].__class__.__name__,
            'KeywordIndex')

    def test_api_import(self):
        import Products.ATContentTypes.atct
        Products.ATContentTypes.atct  # pyflakes

tests.append(TestInstallation)


class TestUninstallation(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.cat = getattr(self.portal.aq_explicit, 'portal_catalog')
        try:
            from Products.CMFPlone.utils import get_installer
        except ImportError:
            qi = getattr(self.portal, 'portal_quickinstaller')
            qi.uninstallProducts(['ATContentTypes'])
        else:
            qi = get_installer(self.portal)
            qi.uninstall_product('Products.ATContentTypes')

    def test_tool_uninstalled(self):
        t = getToolByName(self.portal, TOOLNAME, None)
        self.assertFalse(t, t)

    def test_skin_uninstalled(self):
        stool = getattr(self.portal.aq_explicit, 'portal_skins')
        self.assertFalse('ATContentTypes' in stool)

    def test_uninstalledAllTypes(self):
        # test that all types are uninstalled well
        ids = ('Document', 'File', 'Folder', 'Image', 'Link',
               'News Item', 'Topic', 'Event')
        ttool = getattr(self.portal.aq_explicit, 'portal_types')
        for i in ids:
            self.assertFalse(i in ttool, i)

    def test_quickinstallable(self):
        # Test, if the Product is available in Quickinstaller.  For Plone < 5
        # it shouldn't (since it's a core dependency), for Plone >= 5 it should
        # (where plone.app.contenttypes is installed by default instead).
        # Only Plone 5 is supported here.
        try:
            from Products.CMFPlone.utils import get_installer
        except ImportError:
            qi = getattr(self.portal, 'portal_quickinstaller')
            products = [prod['id'] for prod in qi.listInstalledProducts()]
            self.assertFalse('ATContentTypes' in products)
            products = [prod['id'] for prod in qi.listInstallableProducts()]
            self.assertTrue('ATContentTypes' in products)
        else:
            qi = get_installer(self.portal)
            self.assertFalse(
                qi.is_product_installed('Products.ATContentTypes'))
            self.assertTrue(
                qi.is_product_installable('Products.ATContentTypes'))

    def test_removes_related_items_catalog_index(self):
        self.assertNotIn('getRawRelatedItems', self.cat.Indexes)

tests.append(TestUninstallation)


def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
