# -*- coding: utf-8 -*-
from Acquisition import aq_base
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ILanguageSchema
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import bodyfinder
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.locales import locales


def assignTitles(portal):
    ''' Check for those objects inside portal.
    If they are found we assign title to them.
    '''
    titles = {
        'portal_atct': 'Collection and image scales settings',
        'portal_factory': 'Responsible for the creation of content objects',
        'portal_form_controller': 'Registration of form and validation chains',
        'portal_metadata': 'Controls metadata like keywords, copyrights, etc',
    }
    for oid, obj in portal.items():
        title = titles.get(oid, None)
        if title:
            setattr(aq_base(obj), 'title', title)


def setupPortalContent(p):
    """
    Import default plone content
    """
    existing = p.keys()
    wftool = getToolByName(p, "portal_workflow")

    reg = queryUtility(IRegistry, context=p)
    language = reg['plone.default_language']

    # language = p.Language()
    parts = (language.split('-') + [None, None])[:3]
    locale = locales.getLocale(*parts)
    target_language = base_language = locale.id.language

    # If we get a territory, we enable the combined language codes
    use_combined = False
    if locale.id.territory:
        use_combined = True
        target_language += '_' + locale.id.territory

    # As we have a sensible language code set now, we disable the
    # start neutral functionality
    pprop = getToolByName(p, "portal_properties")
    sheet = pprop.site_properties

    registry = getUtility(IRegistry)
    language_settings = registry.forInterface(
        ILanguageSchema,
        prefix='plone'
    )
    language_settings.use_combined_language_codes = use_combined
    language_settings.default_language = language
    language_settings.available_languages = [language]

    # Enable visible_ids for non-latin scripts

    # See if we have an url normalizer
    normalizer = queryUtility(IURLNormalizer, name=target_language)
    if normalizer is None:
        normalizer = queryUtility(IURLNormalizer, name=base_language)

    # If we get a script other than Latn we enable visible_ids
    if locale.id.script is not None:
        if locale.id.script.lower() != 'latn':
            sheet.visible_ids = True

    # If we have a normalizer it is safe to disable the visible ids
    if normalizer is not None:
        sheet.visible_ids = False

    request = getattr(p, 'REQUEST', None)
    # The front-page
    if 'front-page' not in existing:
        front_title = u'Welcome to Plone'
        front_desc = u'Congratulations! You have successfully installed Plone.'
        front_text = None
        _createObjectByType('Document', p, id='front-page',
                            title=front_title, description=front_desc)
        fp = p['front-page']
        if wftool.getInfoFor(fp, 'review_state') != 'published':
            wftool.doActionFor(fp, 'publish')

        if base_language != 'en':
            util = queryUtility(ITranslationDomain, 'plonefrontpage')
            if util is not None:
                front_title = util.translate(
                    u'front-title',
                    target_language=target_language,
                    default="Welcome to Plone")
                front_desc = util.translate(
                    u'front-description',
                    target_language=target_language,
                    default="Congratulations! You have successfully installed "
                            "Plone.")
                translated_text = util.translate(
                    u'front-text', target_language=target_language)
                if translated_text != u'front-text':
                    front_text = translated_text

        if front_text is None and request is not None:
            view = queryMultiAdapter((p, request),
                                     name='plone-frontpage-setup')
            if view is not None:
                front_text = bodyfinder(view.index()).strip()

        fp.setTitle(front_title)
        fp.setDescription(front_desc)
        fp.setLanguage(language)
        fp.setText(front_text, mimetype='text/html')

        # Show off presentation mode
        if hasattr(fp, 'setPresentation'):
            fp.setPresentation(True)

        # Mark as fully created
        fp.unmarkCreationFlag()

        p.setDefaultPage('front-page')
        fp.reindexObject()

    # News topic
    if 'news' not in existing:
        news_title = 'News'
        news_desc = 'Site News'
        if base_language != 'en':
            util = queryUtility(ITranslationDomain, 'plonefrontpage')
            if util is not None:
                news_title = util.translate(u'news-title',
                                            target_language=target_language,
                                            default='News')
                news_desc = util.translate(u'news-description',
                                           target_language=target_language,
                                           default='Site News')

        _createObjectByType('Folder', p, id='news',
                            title=news_title, description=news_desc)
        _createObjectByType('Collection', p.news, id='aggregator',
                            title=news_title, description=news_desc)

        folder = p.news
        folder.setOrdering('unordered')
        folder.setConstrainTypesMode(constraintypes.ENABLED)
        folder.setLocallyAllowedTypes(['News Item'])
        folder.setImmediatelyAddableTypes(['News Item'])
        folder.setDefaultPage('aggregator')
        folder.unmarkCreationFlag()
        folder.setLanguage(language)

        if wftool.getInfoFor(folder, 'review_state') != 'published':
            wftool.doActionFor(folder, 'publish')

        topic = p.news.aggregator
        topic.setLanguage(language)

        query = [{'i': 'portal_type',
                  'o': 'plone.app.querystring.operation.selection.any',
                  'v': ['News Item']},
                 {'i': 'review_state',
                  'o': 'plone.app.querystring.operation.selection.any',
                  'v': ['published']}]
        topic.setQuery(query)

        topic.setSort_on('effective')
        topic.setSort_reversed(True)
        topic.setLayout('folder_summary_view')
        topic.unmarkCreationFlag()

        if wftool.getInfoFor(topic, 'review_state') != 'published':
            wftool.doActionFor(topic, 'publish')

    # Events topic
    if 'events' not in existing:
        events_title = 'Events'
        events_desc = 'Site Events'
        if base_language != 'en':
            util = queryUtility(ITranslationDomain, 'plonefrontpage')
            if util is not None:
                events_title = util.translate(u'events-title',
                                              target_language=target_language,
                                              default='Events')
                events_desc = util.translate(u'events-description',
                                             target_language=target_language,
                                             default='Site Events')

        _createObjectByType('Folder', p, id='events',
                            title=events_title, description=events_desc)
        _createObjectByType('Collection', p.events, id='aggregator',
                            title=events_title, description=events_desc)
        folder = p.events
        folder.setOrdering('unordered')
        folder.setConstrainTypesMode(constraintypes.ENABLED)
        folder.setLocallyAllowedTypes(['Event'])
        folder.setImmediatelyAddableTypes(['Event'])
        folder.setDefaultPage('aggregator')
        folder.unmarkCreationFlag()
        folder.setLanguage(language)

        if wftool.getInfoFor(folder, 'review_state') != 'published':
            wftool.doActionFor(folder, 'publish')

        topic = folder.aggregator
        topic.unmarkCreationFlag()
        topic.setLanguage(language)

        query = [{'i': 'portal_type',
                  'o': 'plone.app.querystring.operation.selection.any',
                  'v': ['Event']},
                 {'i': 'start',
                  'o': 'plone.app.querystring.operation.date.afterToday',
                  'v': ''},
                 {'i': 'review_state',
                  'o': 'plone.app.querystring.operation.selection.any',
                  'v': ['published']}]
        topic.setQuery(query)
        topic.setSort_on('start')
    else:
        topic = p.events

    if wftool.getInfoFor(topic, 'review_state') != 'published':
        wftool.doActionFor(topic, 'publish')

    # configure Members folder
    members_title = 'Users'
    members_desc = "Site Users"
    if 'Members' not in existing:
        _createObjectByType('Folder', p, id='Members',
                            title=members_title, description=members_desc)

    if 'Members' in p.keys():
        if base_language != 'en':
            util = queryUtility(ITranslationDomain, 'plonefrontpage')
            if util is not None:
                members_title = util.translate(u'members-title',
                                               target_language=target_language,
                                               default='Users')
                members_desc = util.translate(u'members-description',
                                              target_language=target_language,
                                              default="Site Users")

        members = getattr(p, 'Members')
        members.setTitle(members_title)
        members.setDescription(members_desc)
        members.setOrdering('unordered')
        if getattr(members, 'unmarkCreationFlag', None) is not None:
            # An Archetypes object that we have just created.  If the attribute
            # is not there, members is probably a plone.app.contenttypes
            # folder, which does not need this.
            members.unmarkCreationFlag()
        members.setLanguage(language)
        members.reindexObject()

        if wftool.getInfoFor(members, 'review_state') != 'published':
            wftool.doActionFor(members, 'publish')

        members.layout = '@@member-search'

        # Block all right column portlets by default
        manager = queryUtility(IPortletManager, name='plone.rightcolumn')
        if manager is not None:
            assignable = queryMultiAdapter(
                (members, manager),
                ILocalPortletAssignmentManager)
            assignable.setBlacklistStatus('context', True)
            assignable.setBlacklistStatus('group', True)
            assignable.setBlacklistStatus('content_type', True)


def importContent(context):
    # Only run step if a flag file is present
    if context.readDataFile('atct-content.txt') is None:
        return
    site = context.getSite()
    setupPortalContent(site)
    assignTitles(site)
