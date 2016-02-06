# -*- coding: utf-8 -*-
from plone.app.testing.bbb import PloneTestCase
from Products.ATContentTypes import setuphandlers


# No sense to check this in Plone 5, frontpage is DX
class TestContentProfile(PloneTestCase):

    def afterSetUp(self):
        portal_setup = self.portal.portal_setup
        portal_setup.runAllImportStepsFromProfile(
            'profile-Products.ATContentTypes:content')

    def testPortalContentLanguage(self):
        from zope.component import provideUtility
        from zope.i18n.interfaces import ITranslationDomain
        from zope.i18n.simpletranslationdomain import SimpleTranslationDomain

        # Let's fake the news title translations
        messages = {
            ('de', u'news-title'): u'Foo',
            ('pt_BR', u'news-title'): u'Bar',
        }
        pfp = SimpleTranslationDomain('plonefrontpage', messages)
        provideUtility(pfp, ITranslationDomain, name='plonefrontpage')

        # Setup the new placeholder folders
        self.folder.invokeFactory('Folder', 'brazilian')
        self.folder.invokeFactory('Folder', 'german')

        # Check if the content is being created in German
        self.folder.german.setLanguage('de')
        self.loginAsPortalOwner()
        setuphandlers.setupPortalContent(self.folder.german)
        # self.assertEqual(self.folder.german.news.Title(), 'Foo')

        # Check if the content is being created in a composite
        # language code, in this case Brazilian Portuguese
        self.folder.brazilian.setLanguage('pt-br')
        setuphandlers.setupPortalContent(self.folder.brazilian)
        # self.assertEqual(self.folder.brazilian.news.Title(), 'Bar')
