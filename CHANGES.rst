Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

3.0.7 (2022-03-16)
------------------

Bug fixes:


- Fix test after PortalTransforms uses lxml html method to serialize (instead of xml method).
  [gotcha] (#68)


3.0.6 (2022-01-28)
------------------

Bug fixes:


- Security fix: prevent cache poisoning with the Referer header.
  See `security advisory <https://github.com/plone/Products.ATContentTypes/security/advisories/GHSA-g4c2-ghfg-g5rh>`.
  [maurits] (#1)


3.0.5 (2021-10-07)
------------------

Bug fixes:


- Prevent installation on Python 3, as we know Archetypes does not work there.
  [maurits] (#3330)


3.0.4 (2020-09-28)
------------------

Bug fixes:


- Drop use of test() in templates [pbauer] (#24)


3.0.3 (2020-04-20)
------------------

Bug fixes:


- Updated tests to work on Zope 4.2.1/4.2.  [maurits] (#644)


3.0.2 (2019-06-19)
------------------

Bug fixes:


- Fix full_folder_view view in Plone 5.2
  [pbauer] (#64)


3.0.1 (2019-05-21)
------------------

Bug fixes:


- Fix traversing in portal_factory with url-quoted type-name. During redirecting in Zope4 spaces in the URL (e.g. in "News Item") get quoted to `%20`. This prevented finding the portal_type in `__bobo_traverse__`. See https://github.com/plone/buildout.coredev/pull/586
  [pbauer] (#63)


3.0.0 (2018-10-30)
------------------

New features:


- Added isExpired.py and getObjSize.py skin scripts as they will be removed from CMFPlone. (#58)


Bug fixes:


- Zope4 compatibility.
  Fixed tests in combination with Zope 4.0b4.
  Do not call views in TAL.
  Fix checkPermission call (it was acquired from portal_membership until CMF 2.3).
  Fix doctests to adapt to changes in http-headers.
  [davisagli, pbauer, maurits] (#50)

- Added verbosity to the multiple GS profiles popping up.
  Mark all as ``old`` and ``backward compatibility``.
  This hopefully reduces the error rate in site setup.
  [jensens] (#51)

- Handle no content icon in folder_tabular_view
  [davisagli] (#53)

- Switch to new TestCase using AT after PloneTestcase is now DX.
  [pbauer] (#56)

- Use new utils.check_id from CMFPlone.  [maurits] (#60)


2.3.6 (2017-06-26)
------------------

Bug fixes:

- Fix MimeTypeException deprecation warnings
  [ale-rt]


2.3.5 (2017-05-29)
------------------

Bug fixes:

- Add a conditional import of ``processQueue`` as this package is still used on 5.0.
  [gforcada]

- removed "change portal events" permission
  [kakshay21]


2.3.4 (2017-04-01)
------------------

Bug fixes:

- Adapt tests to the new indexing operations queueing.
  Part of PLIP 1343: https://github.com/plone/Products.CMFPlone/issues/1343
  [gforcada]


2.3.3 (2017-02-12)
------------------

Bug fixes:

- Fix tests on Zope 4.
  [davisagli, pbauer, mauritsvanrees]


2.3.2 (2017-01-20)
------------------

New features:

- Move plone_content skin templates from Products.CMFPlone here.
  [gforcada]


2.3.1 (2016-11-17)
------------------

Bug fixes:

- Fix imports from Globals that was removed in Zope4
  [pbauer]

- Require plone.app.imaging even if Plone itself does not. [davisagli]


2.3 (2016-10-03)
----------------

New features:

- Do not try to install p.a.imaging/widgets.  Their default profiles
  are dummies in Plone 5.  [maurits]

- Added fulluninstall profile.  This profile belongs to the 'default'
  profile, which can only be installed through portal_setup.  [maurits]

- Added uninstall profile.  This profile belongs to the 'base'
  profile, which is the one that gets applied when you install
  ATContentTypes.  [maurits]

- No longer register the archetypes skin, because Products.Archetypes
  does that itself.  [maurits]


2.2.13 (2016-07-29)
-------------------

New features:

- Make tests work with old and new safe HTML cleaner (PLIP 1441)
  [tomgross]

Bug fixes:

- Use zope.interface decorator.
  [gforcada]


2.2.12 (2016-05-15)
-------------------

Fixes:

- Removed docstrings from some methods to avoid publishing them.  From
  Products.PloneHotfix20160419.  [maurits]

- Fixed AttributeError ``unmarkCreationFlag`` during installation.
  This could happen when there was already a Members folder from
  ``plone.app.contenttypes``.  Fixes issue
  https://github.com/plone/Products.CMFPlone/issues/1519 [maurits]


2.2.11 (2016-02-14)
-------------------

Fixes:

- Added security decorators.  [maurits]

- Removed double line from simpleint criterion.  This had the effect
  that post_validate always gave an error for value2.  Possibly this
  is used nowhere, because this has been in there for years.  [maurits]

- Added utf-8 coding magic comment.  [maurits]

- Sorted imports with isort.  [maurits]

- Fixed pep8 errors.  [maurits]

- Prevent topic-criteria from having unicode as id. A unicode-id broke
  indexing the criteria in ZCatalog since obj.getPhysicalPath() prefers
  obj.id over obj.getId() in zope4.
  [pbauer]


2.2.10 (2015-12-21)
-------------------

Fixes:

- Fixed Unauthorized error causing a redirect loop in old style
  Topics.  This only happened for anonymous users.
  Fixes issue https://github.com/plone/Products.CMFPlone/issues/1292
  [maurits]


2.2.9 (2015-11-26)
------------------

Fixes:

- Updated Site Setup link in all control panels.
  Fixes https://github.com/plone/Products.CMFPlone/issues/1255
  [davilima6]

- Create standard news/events collections with ``selection.any``.
  Issue https://github.com/plone/Products.CMFPlone/issues/1040
  [maurits]


2.2.8 (2015-10-28)
------------------

Fixes:

- White space only pep8 cleanup.  Not in the skins.
  [maurits]

- Removed use_folder_tabs from Topic.
  [maurits]


2.2.7 (2015-09-20)
------------------

- Pull value for link_redirect, types_view_action_in_listings
  settings from the configuration registry.
  [esteele]

2.2.6 (2015-07-18)
------------------

- createObject moved to Archetpyes.
  [tomgross]

- Add CSRF authenticator in createObject script
  [ebrehault]


2.2.5 (2015-05-04)
------------------

- Move tests from PloneTestCase to plone.app.testing.
  [tomgross,timo]

- Set language settings in setupPortalContent on the new registry.
  [timo]


2.2.4 (2015-03-26)
------------------

- Merge PLIP 13091, plone.app.multilingual
  [bloodbare]

2.2.3 (2015-03-08)
------------------

- Define ``default_page_types`` in the ``propertiestool.xml`` profile.
  [thet]

- Add profile 'base' to allow addons to depend on ATContentTypes in Plone 5
  without uninstalling the dexterity default-types.
  [pbauer]


2.2.2 (2014-10-23)
------------------

- Update template markup to match Barcelonetta
  [albertcasado, sneridagh]

- Remove deprecated imports.
  [tomgross]


2.2.1 (2014-04-13)
------------------

- Remove DL's from portalMessage templates.
  https://github.com/plone/Products.CMFPlone/issues/153
  [khink]


2.2.0 (2014-03-01)
------------------

- Don't use spamProtect script in event_view; it doesn't do much.
  [davisagli]

- Use the new member search form as the layout for the Members folder.
  [davisagli]

- Moved Products.CMFFormController dependency
  from Products.CMFPlone to Products.ATContentTypes (PLIP #13770)
  [ale-rt]

- Moved portal_factory and portal_metadata from Products.CMFPlone
  to Products.ATContentTypes. (PLIP #13770)
  [ale-rt]

- Remove test_discussion test which tests the old discussion (pre Plone 4.1)
  tool.
  [timo]

- Add 'content' profile which adds demo/test content.
  This used to be in CMFPlone and is still used by PloneTestCase
  in Plone 5.
  [davisagli]

- Update ICONMAP (.gif to .png).
  [mathias.leimgruber]

- Move content type profile definitions from Products.CMFPlone into here.
  (Merge of PLIP 12344)
  [davisagli et al.]

- Remove the presentation mode setting from documents.
  If the feature is still desired, use the plone.app.s5slideshow
  addon.
  [davisagli]

- Removed backwards compatibility stub Products.ATReferenceBrowserWidget
  [tomgross]

- Don't throw a traceback if atct_topic_view is called on a non topic.
  Redirect to the default view of context instead
  [tomgross]

- Move ATContent types views in there instead of CMFPlone
  [encolpe]

2.1.12 (2013-03-05)
-------------------

- Fix missing references on copy of (old-style) Collection path
  criterion and relatedItems on stock content using the schema
  flag keepReferencesOnCopy.  Refs: https://dev.plone.org/ticket/9919
  [seanupton]


2.1.11 (2013-01-13)
-------------------

- Fix deprecated import from Archetypes: use atapi instead of public
  [toutpt]

2.1.10 (2012-12-09)
-------------------

- change string ownership to creators as it makes more sense
  refs http://dev.plone.org/ticket/8725
  [maartenkling]

- Make sure ATTopic.queryCatalog cannot be published. This fixes
  http://plone.org/products/plone/security/advisories/20121106/14
  [davisagli]

2.1.9 (2012-10-11)
------------------

- Silence false security warning during startup complaining about
  `ATTopic.setText`.
  [hannosch]

- Notify modified when an image is transformed
  through transform image tab.
  This updates modification date and refresh Etag.
  Refs http://dev.plone.org/ticket/13169.
  [thomasdesvenain]

- add @@download view for IFileContent
  [vangheem]

- Implement ISyndicatable for folder and topic in 4.3
  [vangheem]


2.1.8 (2012-08-18)
------------------

- Fixes album view - when scales generation failed,
  file name appeared twice.
  Refs http://dev.plone.org/ticket/13082.
  [thomasdesvenain]

- PEP 8 (ignoring W602, E301, E501 and E701).
  [hvelarde]

- Deprecated aliases were replaced on tests.
  [hvelarde]

- iCal export: Don't escape COLON character in TEXT property.
  Fixes http://dev.plone.org/ticket/11540.
  [patch by jenskl, applied by kleist]

- Changed deprecated getSiteEncoding to hardcoded `utf-8`
  [tom_gross]

2.1.7 (2012-04-09)
------------------

- Restored icon display in topic tabular view
  [tom_gross]


2.1.6 (2012-01-26)
------------------

- Fix the change/modify permission used for changing or managing
  Topic/Collection criteria.
  [rossp]

- Calculate the localized datetime string based on UTC time. Refs
  https://dev.plone.org/ticket/12197.
  [malthe, ajung]

- Replace getParentNode() with __parent__ / aq_parent as appropriate.
  [elro]

2.1.5 (2011-10-06)
------------------

- Enable sorting by the getObjPositionInParent index.
  [davisagli]


2.1.4 (2011-08-31)
------------------

- Avoid critical error if for any reason,
  constrain type mode is set to ACQUIRE on a folder at the root level.
  Refs http://dev.plone.org/plone/ticket/11950#comment:3
  [yulka, thomasdesvenain]

- Fixed a bug in listSubtopics that caused unauthorized exceptions when
  subtopics were private
  [afd]

- Make relatedItems sortable. Fixes http://dev.plone.org/plone/ticket/12098
  [fRiSi]

2.1.3 (2011-07-12)
------------------

- PortalType-criteria should use archetype_name as value when querying for the
  Type-index. Fixes http://dev.plone.org/plone/ticket/11913
  [WouterVH]

- NonRefCatalogContent-objects, e.g. criteria, should not obtain a UUID.
  Fixes http://dev.plone.org/plone/ticket/11904
  [WouterVH]

- When a folder is not of the same type than its parent,
  if this folder acquires constraint,
  the allowed types are the intersection of globally allowed types in folder
  and locally allowed types of its parent.
  This fixes http://dev.plone.org/plone/ticket/11950.
  [thomasdesvenain]

- For collections displayed in table view, show localized date-format.
  Fixes http://dev.plone.org/plone/ticket/11155
  [WouterVH]

- Fixed: adding a disallowed subobject raises ValueError instead of Unauthorized
  if disallow is related to content types restriction.
  [thomasdesvenain]

- Activate manual sorting on relatedItems field.
  [toutpt]

2.1.2 (2011-05-12)
------------------

- Use DateTime's built-in support to do `datetime.datetime` conversions.
  [hannosch]

- Fixed `atdocument` tests to be compatible with Archetypes 1.7.5.
  [hannosch]

- Optimize images and icon file sizes.
  [hannosch]

- The implementations of HEAD for folderish objects were severely outdated
  and never made much sense to begin with. Replace with basic
  WebdavResource.HEAD.
  [stefan]

2.1.1 (2011-02-04)
------------------

- Added support for the new BooleanIndex and UUIDIndex for collections.
  [hannosch]

- Remove superfluous and/or operator for "Item type" criterion.
  This fixes http://dev.plone.org/plone/ticket/10882
  [msmith64]

2.1.0 (2011-01-03)
------------------

- Depend on ``Products.CMFPlone`` instead of ``Plone``.
  [elro]

- Added CSS id to subtopics-header in atct_topic_view.pt to allow styling.
  [tom_gross]

- Make sure topic criteria get a valid UUID using plone.uuid.
  [toutpt, davisagli]

2.0.7 (2011-01-03)
------------------

- Pass on batching arguments into the catalog query call inside the collections
  `queryCatalog` method.
  [hannosch]

- Add Site Administrator role to various permissions, for forward compatibility
  with Plone 4.1.
  [davisagli]

- Avoid some deprecation warnings under Zope 2.13.
  [hannosch]

- Add missing content-core macro definition to atct_topic_view template.
  [davisagli]

2.0.6 (2010-09-28)
------------------

- Fixed: album view of a collection of Image items
  displayed images on three sections (images, folders, others)
  due to atctListAlbum script bad use of topic API.
  [thomasdesvenain]

2.0.5 (2010-09-08)
------------------

- Changed order of input fields in ``atct_manageTopicIndex.cpt`` and
  ``atct_manageTopicMetadata.cpt``. Checkbox field *must not* be the first one
  because http request ``:records`` gets messed up otherwise. This fixes
  http://dev.plone.org/plone/ticket/10896.
  [petschki]

- Added browser tests for collection management templates.
  [petschki]

2.0.4 (2010-08-08)
------------------

- Adjusted tests to reflect new sub-collections default policy.
  [hannosch]

2.0.3 (2010-08-04)
------------------

- Fixed a test failure.
  [davisagli]

2.0.2 (2010-07-29)
------------------

- Fixed missing manage_beforeDelete declaration on the LinguaPlone folder class
  variation. This closes http://plone.org/products/linguaplone/issues/241.
  [hannosch]

- Corrected timezone name generation in the DateTime -> datetime conversion
  code.
  [mj]

2.0.1 (2010-07-18)
------------------

- Provide some minimal backwards compatibility for the ancient favorite type.
  This closes http://dev.plone.org/plone/ticket/10677.
  [hannosch]

- Remove duplicate batching navigation in atct_topic_view.
  Refs http://dev.plone.org/plone/ticket/10754.
  [esteele]

- Removed try/except in atctListAlbum.py that had no effect because
  calling aq_base in a skin script always throws an Unauthorized
  error.  Refs http://dev.plone.org/plone/ticket/9796.
  [maurits]

- Make sure the atct_album_view calls getText with a full acquisition
  chain to avoid an AttributeError: kupu_captioned_image, but avoid
  getting the text field from an acquisition parent.
  See http://dev.plone.org/plone/ticket/8463
  and http://dev.plone.org/plone/ticket/8190.
  [maurits]

- Removed REQUEST parameter from searchResults call in queryCatalog() of
  the Topic class. searchResults should not be called with regular
  parameters AND REQUEST.
  [do3cc]

2.0 (2010-07-01)
----------------

- Removed some ancient hardcoded HTML in the Collection Settings control panel.
  [limi]

- Deleting objects referred by path criterions resulted in the collection
  being neither view- nor editable. This fixes
  http://dev.plone.org/plone/ticket/10708.
  [fRiSi]

2.0b11 (2010-06-13)
-------------------

- Avoid deprecation warnings under Zope 2.13.
  [hannosch]

- Avoid testing dependency on zope.app.testing.
  [hannosch]

2.0b10 (2010-06-03)
-------------------

- Ensure text is shown for the various Collection views.
  Related to http://dev.plone.org/plone/changeset/36850
  Which fixed http://dev.plone.org/plone/ticket/10226

- Products.ATContentTypes.content.folder.ATBTreeFolder is now deprecated.
  Normal ATFolders (as implemented in plone.app.folder) are now suitable for
  storing large numbers of items in most cases.  If you need a folder that
  doesn't track order at all, use a normal ATFolder (from plone.app.folder)
  with the ordering attribute set to u'unordered'.
  [davisagli]

- Merge fix of test_queryCatalogOverrideCriteria from 1.3.6 branch
  [toutpt]

2.0b9 (2010-05-01)
------------------

- Values in dropdown "criterion_type" in criterion_edit_form template are now
  properly translated. This closes http://dev.plone.org/plone/ticket/9715
  [vincentfretin]


2.1.4 - Unreleased
------------------

- Nothing changed yet.


2.0b8 - 2010-05-01
------------------

- Check the ISO of the stored date, not the ISO8601 (with timezone) that is
  now returned by the accessors
  [davisagli]


2.0b7 - 2010-04-12
------------------

- List subcollections, not all subobjects, in the subcollections view.
  [elvix]

- Fixed Collection control panel to show the prefs portlet again.
  [davisagli]

- Fixed displaying the links and icons when 'display as table' is checked.
  Links are shown using 'typesUseViewActionInListings', icons are shown using
  plone_view.getIcon.
  [kcleong]


2.0b6 - 2010-03-08
------------------

- Adjust the tests now that `DateTime` objects are stored with a time zone.
  Refs http://dev.plone.org/plone/ticket/10141
  [witsch]


2.0b5 - 2010-03-07
------------------

- Adjust the tests regarding content id generation to expect the re-instated,
  previous behavior.  Refs http://dev.plone.org/plone/ticket/8591
  [witsch]


2.0b4 - 2010-03-05
------------------

- Fix issues with sliding modification/publishing dates by using `DateTime`'s
  `ISO8601` method instead of `ISO`, which doesn't include time zones.
  Refs http://dev.plone.org/plone/ticket/10140, 10141 & 10171.
  [davisagli, witsch]

- Polished markup for "tabs simulation" on collection management screens to
  play nice in Sunburst.
  [spliter]

- Fixed validation for atct_manageTopicMetadata.cpt and
  atct_manageTopicIndex.cpt
  [spliter]

- Updating atct_manageTopicMetadata.cpt and atct_manageTopicIndex.cpt to
  recent markup conventions. References
  http://dev.plone.org/plone/ticket/9981.
  [spliter]


2.0b3 - 2010-02-17
------------------

- Removing redundant .documentContent markup.
  This refs http://dev.plone.org/plone/ticket/10231.
  [limi]

- Updated templates to follow recent markup conventions.
  References http://dev.plone.org/plone/ticket/9981
  [spliter]

- Fixed the portal type criterion to use the really user friendly types
  vocabulary, which makes it independent of the types selection allowed for
  searching. We also provide the proper translated title of all types and sort
  by it now. This closes http://dev.plone.org/plone/ticket/9802.
  [hannosch]

2.0b2 - 2010-01-25
------------------

- Removed a displayContentsTab related hack from topic.py. Whatever this was
  supposed to do, has long changed.
  [hannosch]

- Ported fix for http://dev.plone.org/plone/ticket/7324 - it was not possible
  to empty Collection's 'text' field. Again fixes #7324
  [naro]

2.0b1 - 2010-01-02
------------------

- Don't specify PIL as a direct dependencies. It is not installed as an egg on
  all platforms.
  [hannosch]

2.0a6 - 2009-12-27
------------------

- Respect "show content type icons" setting for collection table view.
  This fixes http://dev.plone.org/plone/ticket/9630.
  [dukebody]

- Removed cmf_klass leftovers from tests.
  [hannosch]

- Removed useless manual tests of the icon names of all types.
  [hannosch]

- Removed overly creative code using access rules in webdav tests.
  [hannosch]

- Added manage_options restriction for new folderish types.
  [hannosch]

- Removed no longer required ATCTContent.manage_options restriction.
  [hannosch]

- Corrected package dependencies.
  [hannosch]

2.0a5 - 2009-12-16
------------------

- Apply patch from mr_savage. Fixes a broken call to normalizeString in
  atct_topic_view. http://dev.plone.org/plone/ticket/9897
  [esteele]

2.0a4 - 2009-12-03
------------------

- Use "Modify portal content" and "Add portal content" for topic and event
  instead of the type-specific permissions previously used.
  [esteele]

2.0a3 - 2009-12-03
------------------

- Replace the custom __bobo_traverse__ for handling image scales on ATNewsItem
  and ATImage, because it's still needed for path traversal to scales to work.
  This fixes http://dev.plone.org/plone/ticket/9706.
  [davisagli]

2.0a2 - 2009-12-02
------------------

- Attempt to Acquisition unwrap the context but allow the (potentially)
  wrapped object through if unwrapping fails. This closes
  http://dev.plone.org/old/plone/ticket/9796.
  [matthewwilkes]

- Adjust the reindex tests for the change I just made in Archetypes.
  [davisagli]

- Remove the eventType field and merge it into the subject field.
  Closes http://dev.plone.org/old/plone/ticket/5058.
  [rossp]

2.0a1 - 2009-11-18
------------------

- Pass an _initializing_ flag when updating fields on object initialization,
  to avoid indexing twice (since CMF indexes on the item's ObjectAddedEvent,
  which now takes place after the call to initializeArchetype).
  [davisagli]

- Replaced date criterion "ago/from now" by "in the past/in the future".
  [vincentfretin]

- help_criteria_field_name msgid was used twice but with different default
  messages. Fixed that.
  [vincentfretin]

- Made ATImage compute its ID from its title if provided. Closes
  http://dev.plone.org/old/plone/ticket/9186.
  [erikrose]

- Changed the canonical location of interfaces to be in a subpackage called
  interfaces in its standard plural form. Leave BBB imports behind in
  interface.py.
  [hannosch, davisagli, witsch]

- Updated the ATCT tool upgrade to register the new tool with the portal
  site manager.
  [davisagli]

- Subtopics shouldn't always acquire the 'start' query. Fixes
  http://dev.plone.org/plone/ticket/8827
  [pelle]

- Use correct location for IObjectEvent.
  [hannosch]

- Removed test only PluggableAuthService dependency.
  [hannosch]

- Moved content type specific GenericSetup related functionality from CMFPlone
  into this package.
  [hannosch]

- Drop the dependency on simplejson. It's integrated into Python 2.6 as json.
  [hannosch]

- Avoid acquiring `portal_properties` and call it via a proper API.
  [hannosch]

- Changed objectIds and objectValues calls to use the IContainer API.
  [hannosch]

- Don't assume regular (non-btree) folders for next/previous support.
  [witsch]

- Removed various dependencies on CMFPlone.
  [hannosch]

- Cleaned up tests some more. No longer rely on the testfixture extension
  profile but adapt the tests to default Plone instead.
  [hannosch]

- Declare package dependencies and fixed deprecation warnings for use
  of Globals.
  [hannosch]

- Changed parameter name at script getXMLSelectVocab.py from 'method' to
  'vocab_method' to avoid getting overridden from ZPublisher.HTTPRequest.
  This closes http://dev.plone.org/plone/ticket/6960.
  [igbun]

- Changed description label to summary for page and news item. This closes
  http://dev.plone.org/plone/ticket/8700.
  [hannosch]

- Adjusted functional tests to not rely on login portlet.
  [hannosch]

- Moved a manage_renameObject method from the autosort code into the ordered
  base class. It wasn't quite obvious, but the code was actually used.
  [hannosch]

- Removed icalendar package from the thirdparty folder. We don't use it
  ourselves and it's easy installable nowadays for anyone who wants it.
  [hannosch]

- Removed never fully implemented autosort and urlupload modules.
  [hannosch]

- Removed the weird Zope2 Interface to zope.interface bridging code.
  [hannosch]

- Removed annoying license statements from the source files. We have a central
  license.txt for that.
  [hannosch]

- Removed module aliases for content created before ATCT 1.0.
  [hannosch]

- Adjusted code to current Plone trunk after some deprecated code got removed.
  Moved old_folder_contents code into atct_topic_subtopics.
  [hannosch]

- Fixed some test failures concerning criterion editing.
  [hannosch]

- Adjusted reindex sanity tests to changed order of the indexing calls.
  [hannosch]

- Increase the version number to 2.0, to make it possible to release minor
  feature releases for the Plone 3.x line.
  [hannosch]

- Adjusted events test to new reality including zope.app.container and
  DCWorkflow events.
  [hannosch]

- Removed half-implemented and unmaintained archive and adapters code.
  [hannosch]

- Removed unmaintained and unused Favorite content type.
  [hannosch]

- Removed references to external editor in comments.
  [hannosch]

- Removed empty test_getobjpositioninparent test from the base test case.
  [hannosch]

- Adjusted tests to reflect using png instead of gifs for content types.
  [hannosch]

- Use human understandable language for describing the relative date range
  criteria. This closes http://dev.plone.org/plone/ticket/6841.
  [hannosch]

- Fixed duplicate link icon in the custom topic view. This closes
  http://dev.plone.org/plone/ticket/6049.
  [hannosch]

- Removed confusing behavior of ATEvent mixing eventType and Subject.
  This closes http://dev.plone.org/plone/ticket/5058.
  [hannosch]

- Added application/x-shockwave-flash to the inline mimetypes, so they can
  be shown in a page without causing a download prompt. This closes
  http://dev.plone.org/plone/ticket/5778.
  [hannosch]

- Removed a shortcut in the relative path criterion, which wouldn't work in
  all cases. This closes http://dev.plone.org/plone/ticket/7785.
  [hannosch]

- The photo album view never showed the number of images in subfolders.
  This closes http://dev.plone.org/plone/ticket/7759.
  [hannosch]

- Removed txng_get method from file content type. The hook is deprecated and
  TextIndexNG 3 doesn't use it anymore. This closes
  http://dev.plone.org/plone/ticket/4297.
  [hannosch]

- Fixed problem in parsing GPS information in exif metadata. This closes
  http://dev.plone.org/plone/ticket/7057.
  [hannosch]

- Increased the maxlength for the url field of links from 255 to 511. This
  closes http://dev.plone.org/plone/ticket/6422.
  [hannosch]

- Purged old Zope 2 Interface interfaces for Zope 2.12 compatibility.
  Consider branching before this revision if release required before Plone 4.
  [elro]

- Remove __bobo_traverse__ from ATNewsItem and ATImage. Instead rely on the
  generic ImageTraverse publish traverser from Archetypes and removed the
  accompanying tests for it.
  [wichert, hannosch]

- Added tests for utils.dt2DT and utils.DT2dt that expose a bug as found
  in Vice regarding converted dates becoming naive of timezones. Fixed.
  [matthewwilkes]

- Moved interface declarations from ZCML to the classes themselves.
  [hannosch]

- Ported editing.txt, events.txt, reindex_sanity.txt and traversal.txt tests
  from Archetypes and adjusted them for the ATContentTypes specific behavior.
  [hannosch]

- Adjusted tests to changed test base classes of Archetypes.
  [hannosch]

- Removed the unmaintained utilities folder including the report scripts.
  [hannosch]

- Moved old_folder_contents over from CMFPlone as it is still used in
  atct_topic_subtopics.pt.
  [hannosch]

- Fixed editing.txt browser test by opening 'http://nohost/plone' instead
  of 'http://nohost/plone/login_form', because the latter incorrectly
  redirected to 'http://nohost/plone/localhost'
  [sirgarr]


1.3.4 - unreleased
------------------

- Fix my previous Chameleon fix in criterion_edit_form.cpt, which broke
  creation of new criteria. This closes http://dev.plone.org/ticket/9522
  [davisagli]

1.3.3 - 2009-09-06
------------------

- Subtopics shouldn't always acquire the 'start' query. Fixes
  http://dev.plone.org/plone/ticket/8827
  [pelle]

- Internationalized "Also in this section" in atct_topic_subtopics.pt.
  This closes http://dev.plone.org/plone/ticket/8383
  [massimo]

- Modified lib/constraintypes.py:getDefaultAddableTypes method to check
  isConstructionAllowed only for allowed types, not for all content types
  in portal_types. isConstructionAllowed was called twice for each types.
  [vincentfretin]

- Fix XHTML error in criterion_edit_form.cpt
  [davisagli]

1.3.2 2009-05-20
----------------

- Added proper multi-lingual handling to the reference criterion. It should
  only show referenced content in the same or the neutral language if the
  uid catalog is language aware.
  [hannosch]

1.3.1 2009-04-28
----------------

- Made it possible to set an empty value to a topic text field. This closes
  http://dev.plone.org/plone/ticket/7324.
  [dunlapm]

1.3.0 - 2009-03-11
------------------

- Add support for generating iCal feeds for topics.
  This refs http://plone.org/products/plone/roadmap/246.
  [witsch]

- Add view for rendering events as an iCal feed as proposed by PLIP 246,
  http://plone.org/products/plone/roadmap/246.
  [witsch]

- Remove all code related to auto-sorting / auto-ordering folder as proposed
  by PLIP 241, http://plone.org/products/plone/roadmap/241.
  [witsch]

- Made the relative path criterion less prone for funky Acquisition chains.
  This refs http://dev.plone.org/plone/ticket/7686.
  [hannosch, maurits]

1.2.7 - 2009-01-30
------------------

- Don't assume regular (non-btree) folders for next/previous support.
  [witsch]

- Made Flash files display inline since Flash 10 requires this.  Fixes
  http://dev.plone.org/plone/ticket/8624
  [alecm]

1.2.6 - 2008-10-06
------------------

- Fixed the tidy validation which errored out and rasied the wrong error.
  This closes http://dev.plone.org/plone/ticket/8243.
  [jlagarde, garbas, calvinhp]

- Avoid acquiring getText from parent objects in atct_album_view. This refs
  http://dev.plone.org/plone/ticket/8190.
  [hannosch]

- Already quoted characters in a "Link" url should not be quoted again
  on edit. This closes http://dev.plone.org/plone/ticket/8336.
  [witsch]

- Removed parameters that has to be controlled through CSS from
  atct_topic_view.pt. This closes http://dev.plone.org/plone/ticket/6803
  [spliter]

- Made it possible to set an empty value to a document text field.  This closes
  http://dev.plone.org/plone/ticket/7324.
  [davisagli]

- Fixed invalid field condition that prevented you from being able to edit
  the "Inherit Criteria" value on a collection once it had been created.
  This closes http://dev.plone.org/plone/ticket/6527.
  [hannosch]

- Changed a msgid for the url field of events to have a distinct value.
  This closes http://dev.plone.org/plone/ticket/8197.
  [hannosch]

- Changed "Contained Collections" text to "Also in this section".
  This closes http://dev.plone.org/plone/ticket/8106.
  [davisagli]

- Changed default topic view to alway show body text (if available) even if the
  collection does not have any results. This closes
  http://dev.plone.org/plone/ticket/8270.
  [dunlapm]

1.2.5 - 2008-04-22
------------------

- Remove leading whitespace in hrefs.
  [wichert]

- Corrected i18n markup in schemata.py for the nextprevious field. This closes
  http://dev.plone.org/plone/ticket/7517.
  [hannosch]

1.2.4 - 2008-01-03
------------------

- The edit tab in ZMI should not be displayed for ATImage/ATFIle objects.
  http://dev.plone.org/archetypes/ticket/763
  [deo]

- Fixed #7467 http://dev.plone.org/plone/ticket/7467: Modify
  "Item Type" criterion to store the untranslated Type instead
  of portal_type, but to show the translated Type to the user.
  Added a browser test for #6981
  http://dev.plone.org/plone/ticket/6981 which is currently
  disabled because the test browser does not translate pages
  [sirgarr]

1.2.3 - 2007-12-02
------------------

- Fixed http://dev.plone.org/plone/ticket/7102: uploading xhtml
  files was not working correctly.  Thanks to lucie for the patch.
  [alecm]

- Fixed bug in portaltype criterion - it used portal type Title as both
  key and value in multiselection widget, but Id and Title should be used.
  Title (as DisplayList key) was incorrectly translated and caused #6981
  http://dev.plone.org/plone/ticket/6981
  [naro, jensens]

- Fix Unicode encode error in formatCatalogMetadata.py when atct_topic_view.py
  uses it to display in a table a text field (like 'location') whose contents
  can't be encoded to ascii.
  http://dev.plone.org/plone/ticket/7237
  [stevem]

- Reorder ATDateCriteria schema fields => more intuitive for users.
  [zegor]

- Fixed a mysterious error that happened when the ATContentTypeSchema
  was directly used: the validation layer for the 'id' field wasn't
  being initialized. This fixes http://dev.plone.org/plone/ticket/7221
  [deo]

1.2.2 - 2007-10-05
------------------

- Fix ATLink XSS issue.
  [alecm, reinout]

- Update catalogue indexes and metadata list in collection control panel when
  'All fields' requested.
  [ldr]

- Files and Images don't need to enforce the Title field, since it is pulled
  from the uploaded file name if missing. This fixes
  http://dev.plone.org/plone/ticket/6051, which is a common source of user
  frustration when uploading files/images.

1.2.1 - 2007-09-12
------------------

- Make subject field read-only and invisible for events.  This fixes
  http://dev.plone.org/plone/ticket/6967
  [alecm]

- Use widget views for standard view templates to simpify inline editing.
  [limi]

1.2.0-final - 2007-08-16
------------------------

- No longer enforce vocabularies on constraintypes fields, it's essentially
  pointless, and not enforcing them helps workaround a strange bug:
  http://dev.plone.org/plone/ticket/6734
  [alecm]

- Fixed i18n markup for event date validation error messages.
  [hannosch]

- Only show related items once instead of twice.
  [wichert]

1.2.0-rc2 - 2007-06-11
----------------------

- Add link validation to event field.
  [alecm]

1.2.0-rc1 - 2007-06-08
----------------------

- Fix concatenation issues between related items and query results in Topics.
  [alecm]

- Fixed migration bug in the atct tool migration. This closes
  http://dev.plone.org/plone/ticket/6549 and
  http://dev.plone.org/plone/ticket/6550.
  [hannosch]

- Show the text field and related items in the Topic view.
  [wichert]

- Properly i18n-ize imagetransforms TRANSPOSE_MAP by using ATCTMessageFactory.
  [hannosch]

- Removed all usage of PloneMessageFactory and replaced it by using ATCT's own
  message factory. The extraction tools aren't able to deal with two different
  message factories used for a single package.
  [hannosch]

- Fixed some i18n markup to use new ids for the collections related messages,
  so these do not conflict with the old ones using smart folder.
  [hannosch]

- Hide the fields properly. The user may not have permission to edit them!
  Also fix related typo-induced security hole.
  [optilude]

- Corrected cmf_edit_kws on the new ATDocumentBase class, which is used as a
  base for ATNewsItem. It's absence caused a test failure in CMFPlone for the
  text_format which needs special handling.
  [hannosch]

1.2.0-beta2 - 2007-04-29
------------------------

- Changed some status messages to type 'error'.
  [hannosch]

- Add support for updating existing topic indexes and metadata from
  GenericSetup profiles
  [wichert]

- Removed tests/runalltests.py and tests/framework.py.
  To run tests use Zope's testrunner:
  ./bin/zopectl test --nowarn -s Products.ATContentTypes
  [stefan]

1.2.0-beta1 - 2007-03-04
------------------------

- Adjusted tests to deal with the new default vocabulary for boolean fields.
  [wichert]

- Adjusted tests to deal with the removal of the old CMF types from the
  GenericSetup profiles. This refs http://dev.plone.org/plone/ticket/6156.
  [hannosch]

- Set ATFile's file field to be 'searchable'.  This means that it'll
  be indexed correctly including transforms.  If you don't want this,
  set your own 'index_method', or set 'searchable' to False in your
  code.
  [nouri]

- Extinguished last occurrences of old portal_status_message in URL support.
  [hannosch]

- Merged plip174-reusable-i18n branch. Normalization of uploaded file names
  is now based on plone.i18n.normalizer.
  [hannosch]

1.2.0-alpha2 - 2007-02-08
-------------------------

- Removed various obsolete class attributes from content type classes. These
  are managed by GenericSetup profiles now.
  [hannosch]

- Updated installation tests, as ATCT is no longer 'quickinstalled' anymore.
  [hannosch]

- removed schemata='default' for allowDiscussion field in finalizeATCTSchema.
  It makes no sense and prevents customization by patching.
  [ender]

- Moved fields of content types into several schemas.
  [fschulze]

- Removed properties tab, as we now use the all-schemas-on-one-page feature
  of Archetypes.
  [fschulze]

- Some general test cleanup in order to make the test output readable.
  [hannosch]

- Removed the view alias of index.html for all standard content types. This
  makes it possible to create and upload files called index.html to the
  site, which is quite common when batch importing old sites into the site.
  As someone might rely on the former behaviour, we do not migrate
  any existing type information. This closes
  http://dev.plone.org/plone/ticket/4837.
  [hannosch]

- Got rid of last remnants of zLOG. Grep is our friend!
  [stefan]

1.2.0-alpha1 - 2006-10-02
-------------------------

- Fixed some minor i18n issues.
  [hannosch]

- Reworked i18n of Python scripts to use the new MessageFactory and based
  portal status messages on the statusmessages product.
  [hannosch]

- Changed criteria definitions to use Zope3 Messages for localizing
  descriptions and labels instead of the old Archetypes approach using special
  attributes. Added a ATCTMessageFactory for the Messages in the
  'atcontenttypes' i18n domain.
  [hannosch]

- Fixed some imports of transaction_note from CMFPlone to CMFPlone.utils.
  [hannosch]

- Fixed deprecation warnings for TALValidator.
  [hannosch]

- Changed type definitions to use Zope3 Messages for localizing descriptions
  and labels instead of the old Archetypes approach using special attributes.
  [hannosch]

- Removed ZConfig based configuration of the topic tool as it is now handled
  by the GenericSetup profile. Removed magical recreation of indexes and
  metadata on get* calls.
  [hannosch]

- Added an exportimport handler for the ATCT tool which is used by the Plone
  base profile.
  [hannosch]

- Adjusted some deprecated getActionById to getActionInfo calls.
  [hannosch]

- Removed five:traversable statements as they are no longer needed in Zope2.10.
  [hannosch]

- Simplified test setup and adjusted some tests accordingly.
  [hannosch]

- Adjusted import locations of Archetypes.public to Archetypes.atapi for AT1.5.
  [hannosch]

1.1.4-final - 2006-12-18
------------------------

- Reenabled editing the names and descriptions of the smart folder indices
  and metadata.
  [alecm]

- Setting a sort criterion should not prevent search criteria for the same
  field from being set.  Fixes http://dev.plone.org/plone/ticket/5435
  [alecm]

- ATEvent.setSubject needs to set multiple EventTypes to avoid pruning
  the subject list. Applied patch from rossp. Fixes
  http://dev.plone.org/plone/ticket/5770
  [alecm]

- Add alt attributes to Topic table view type icons.  This closes
  http://dev.plone.org/plone/ticket/5562
  [alecm]

- Fixed validation of filenames uploaded from IE.  This closes
  http://dev.plone.org/plone/ticket/5889.
  [alecm]

- Reenabled translation of AJAX-ified smart folder info. This closes
  http://dev.plone.org/plone/ticket/5806.
  [hannosch]

- Got rid of last remnants of zLOG. Grep is our friend!
  [stefan]

- Added a relative path criterion for Smart Folders to allow search paths
  like "../somefolder"
  [ender, elvix]

1.1.3-final - 2006-09-20
------------------------

- Disabled translation of AJAX-ified smart folder info to temporarily remedy
  http://dev.plone.org/plone/ticket/5806
  [jensens]

1.1.2-final - 2006-09-11
------------------------

- Changed integration tests to test Unicode titles instead of plain ascii.
  [hannosch]

- Added review state coloring to atct_topic_view. This closes
  http://dev.plone.org/plone/ticket/5481.
  [hannosch]

- Don't setup a 'ATCT Setup' control panel category anymore, it's not used.
  [hannosch]

1.1.1-final - 2006-06-08
------------------------

- Changed two logging.PROBLEM to logging.WARNING. PROBLEM level was zLOG only.
  [hannosch]

1.1.0-final - 2006-06-03
------------------------

- Added TextIndexNG3 to list of indexes.
  [ajung]

- Moved css rules for the photo album view inside Plone's public.css, instead
  of having them inline in the template. This way they can be overridden.
  This closes http://dev.plone.org/plone/ticket/4765.
  [hannosch]

- Made ATTopic queryCatalog properly support b_size, thanks to patch from
  Bader. Fixes http://dev.plone.org/plone/ticket/5526
  [alecm]

- Removed the unused locales folder. Translation files are part of the
  PloneTranslation product.
  [hannosch]

- Uploading HTML via WebDAV now supports reading <title> tag to use
  as the title of the new content item.
  http://dev.plone.org/plone/ticket/4877
  [rocky]

- Semi-intelligent sniffing adding for figuring out the charset
  when using mx.Tidy. This closes http://dev.plone.org/plone/ticket/5006.
  [rocky]

- Internal links didn't work for event url field. This closes
  http://dev.plone.org/plone/ticket/5004
  [hannosch]

- Various fixes for the iCal/vCal export (thx Steve for the patch):

    - timezone problems
    - folding lines longer than 75 octests (per RFC)
    - escaping commas, colons and semi-colons (per RFC)
    - adding URL and CONTACT fields

  This closes http://dev.plone.org/plone/ticket/4512.
  [hannosch]

- the EventType field in an event lists all relevant event types for
  an event, not just one. Modify the iCal output logic to properly
  produce comma-seperated event types. Fixes
  http://dev.plone.org/plone/ticket/4881
  [wichert]

- Applied patch from Plone issue #5384 to do proper UTC conversion for iCal
  and vCal output. Added tests. Fixes #5384.
  [alecm]

- Made use Zope 3 interfaces for constrain types and browser default. Depends
  on changes to CMFDynamicViewFTI trunk and Plone 2.5 branch.
  [optildue]

- Made HistoryAwareMixin a subclass of Archetypes ATHistoryAwareMixin, which
  is a working historyaware implementation for archetypes.
  [mj]

- Added a z3 module and an alias for BBB (Ploneboard).
  [alecm]

- Updated thirdparty/icalendar to version iCalendar-0.11. Dropped the
  svn:external to codespeak SVN. This has the side-effect of ridding us
  of the annoying test failure with the Zope 2.9 testrunner which would
  pick up the icalendar tests even though they are neither importable nor
  pass in this setting.
  [stefan]

1.1.0-beta1
-----------

- Integrated ftests into normal tests. Removed dependency on Archetypes tests.
  [hannosch]

- Update transaction imports, remove subtransaction usage, use python logger
  everywhere, other deprecation related cleanup, whitespace cleanup.
  [alecm]

- Use KeywordWidget for eventType.
  [fschulze]

- Body of news items and event types can be empty now.
  [fschulze]

1.1.0-alpha2 - 2006-02-22
-------------------------

- Reorganized z3 interfaces into the interface package, created a complete
  set of z3 interfaces, as well as tests for those interfaces.
  [jfroche, russf]

- Added some adapters and views for exporting Folders and Documents (and
  other types, given additional configuration) as zip files.
  [jfroche, russf]

1.1.0-alpha1 - 2006-01-26
-------------------------

- make trunk compatible with cmf > 1.5, by changing references to
  cmfcore.permissions and removing use of format_stx
  [k_vertigo, hannosch]

1.0.6-final - unreleased
------------------------

- Disabled the possibility to change index and metadata names and descriptions
  on the smart folder configuration screens. Saving these with a browser locale
  set to non-english would destroy the internationalization of all these texts.
  This closes http://dev.plone.org/plone/ticket/5612.
  [hannosch]

- Sanitized some more index and metadata friendly names and descriptions.
  [hannosch]

- Changed index friendly name of index id to the same as the getId index.
  [hannosch]

- We don't translate the catalog and metadata id's anymore. Removed i18n markup
  from the configuration screens.
  [hannosch]

1.0.5-final - 2006-06-03
------------------------

- Made ATTopic queryCatalog properly support b_size, thanks to patch from
  Bader.  Fixes http://dev.plone.org/plone/ticket/5526
  [alecm]

- Added TextIndexNG3 to list of indexes.
  [ajung]

1.0.4-final - 2006-05-17
------------------------

- Folded ftests into unit tests. The distinction was arbitrary anyway.
  [stefan]

- Removed the unused locales folder. Translation files are part of the
  PloneTranslation product.
  [hannosch]

- Uploading HTML via WebDAV now supports reading <title> tag to use
  as the title of the new content item.
  http://dev.plone.org/plone/ticket/4877
  [rocky]

- Semi-intelligent sniffing adding for figuring out the charset
  when using mx.Tidy.  This closes
  http://dev.plone.org/plone/ticket/5006
  [rocky]

- Internal links didn't work for event url field. This closes
  http://dev.plone.org/plone/ticket/5004
  [hannosch]

- the EventType field in an event lists all relevant event types for
  an event, not just one. Modify the iCal output logic to properly
  produce comma-seperated event types. Fixes
  http://dev.plone.org/plone/ticket/4881
  [wichert]

- Updated thirdparty/icalendar to version iCalendar-0.11. Dropped the
  svn:external to codespeak SVN. This has the side-effect of ridding us
  of the annoying test failure with the Zope 2.9 testrunner which would
  pick up the icalendar tests even though they are neither importable nor
  pass in this setting.
  [stefan]

- Made manage_afterPUT and manage_afterMKCOL use PATH_INFO to get at
  the original id for usage in the Title, so that in a WebDAV
  name-mangling environment the Title gets set to the original
  filename.
  [sidnei]

- Added test for ATFolder and ATBTreeFolder MKCOL.
  [sidnei]

- Modify getLocallyAllowedTypes and getImmediatelyAddableTypes to take
  a context in which type creation is to be tested. This is used to determine
  if a user can create a type in the current context instead of in a parent
  folder.
  http://dev.plone.org/plone/ticket/5255
  [wichert]

1.0.3-final - 2006-01-20
------------------------

- Fixed non-clickable thumbnails in thumbnail view for IE.
  http://dev.plone.org/plone/ticket/5119
  [hannosch]

1.0.2-final - 2006-01-03
------------------------

- Fixed #5028: constraintypes.py doesn't work properly with PortalFactory when
  acquiring types.
  http://dev.plone.org/plone/ticket/5028
  [panjunyong]

- fixed styles for thumbnailview.
  [spliter]

- content/events.py: made event type look-up respect dynamic types.
  [raphael]

- Don't return "n/a" in get_size(). This fixes Plone's #5030.
  [nouri]

- Fixed #5026: Setting a ZCatalog sort limit was interfering with result
  batching. Only use the sort_limit optimization when batching is disabled.
  http://dev.plone.org/plone/ticket/5026
  [alecm]

- Fixed #4567: Added portal_atct method to fix portal_type on CMF objects that
  have empty portal_type because they were incorrectly instantiated. Such
  situations caused migration to fail. This method is available in the type
  migration form, and also runs automatically on install.
  http://dev.plone.org/plone/ticket/4567
  [alecm]

- Fixed #4937: Removed list criteria from text indices, because it makes no
  sense, AND and OR must be used explicitly.
  http://dev.plone.org/plone/ticket/4937
  [alecm]

- Added migration for #4865 to fix the grammar on existing instances.
  [alecm]

- Made the criteria to index type mapping a little more sane.
  [alecm]

- Fixed #4915: Smart Folders with path criteria where throwing errors on
  unindex due to partial reference support.
  http://dev.plone.org/plone/ticket/4915
  [alecm]

- Added And/Or operator to selection criterion.
  [alecm]

- Fixed #4590: Subfolders inherit the selected layout of their parent folders
  if they are of the same type.
  http://dev.plone.org/plone/ticket/4590
  [alecm]

- Fixed #4512 - vCal export was not working with outlook.
  http://dev.plone.org/plone/ticket/4512.
  [hannosch]

- Use the ControlledMarshaller from the Marshall product if
  available. Fallbacks to existing marshaller.
  [sidnei]

- Enable __dav_marshall__ by default on ATTopic, ATFolder and
  ATBTreeFolder.
  [sidnei]

- Fixed #4572 and #4909 - Unicode problems with using kupu together
  with mxTidy
  [hannosch]

- Fixed #4865 - Spelling error on location criteria.
  [hannosch]

- On invalid mimetypes the getIcon method of ATFile doesn't throw an exception
  anymore but generates a log entry. This should minimize some migration
  problems or at least tell the exact object with an invalid mimetype.
  This should fix http://plone.org/collector/4979.
  [hannosch]

- Correct some wrong security settings.
  [hannosch]

- Code cleanup removing lots of unused import statements.
  [hannosch]

- Fixed two issues with PathCriterion.  It was using depth 0 to get subfolders,
  the proper parameter is depth -1.  Also, in order to properly handle the
  references it holds, it must itself be cataloged in the UID catalog, and
  have its references cataloged.
  [alecm]

- Fixed issue causing archetypes schema update to fail due to topic not
  checking syndication state in initializeArchetype.
  [alecm]

- Added missing alternate views for folderish types.
  [alecm]

1.0.1-final - 2005-10-13
------------------------

- Fixes for http://plone.org/collector/4709 __bobo_traverse__ doesn't
  need or want a RESPONSE argument.
  [alecm]

- Fixed http://plone.org/collector/4734 It is generally a bad idea
  to check permissions in bobo_traverse methods, especially permissions
  that don't exist, especially if you then try to raise an exception that
  you haven't actually imported.
  [alecm]

- Fix two small i18n default text inconsistencies
  [hannosch]

1.0.0-final - 2005-09-05
------------------------

- Packaged 1.0.0 final with a tip of the hat to Christian Heimes who has
  disappeared from our radar. We miss you, dude.
  [stefan]

- Made migration more tolerant of conflicting ids due to auto-created content
  from manage_afterAdd or similar.  Fixes http://plone.org/collector/4468
  [alecm]

- Moved the exclude from navigation checkbox back to the properties tab, on
  folderish objects, per request from limi.
  [alecm]

- Fixed two Smart folder issues: http://plone.org/collector/4594 we now fail
  gracefully on bad limit settings, and http://plone.org/collector/4601 added
  show/hide all link to the medatata control panel.
  [alecm]

- Changed Subject index/metadata title to Keywords, and added appropriate
  description.
  [alecm]

1.0.0-rc5 - 2005-08-18
----------------------

- Fixed http://plone.org/collector/4429 by updating the modifySelectList.js
  to deal with IE deficiencies.
  [alecm]

- Display files inline if they are of mimetype text/- thanks to LaurenceRowe
  for the patch.
  [alecm]

- Fixed http://plone.org/collector/4448 index titles in smart folder's
  criteria edit form were not translated
  [hannosch]

1.0.0-rc4 - 2005-08-09
----------------------

- Implemented the custom PUT_factory in both ATCTOrderedFolder and
  ATCTBTreeFolder, as inheriting it from ATCTFolderMixin breaks when
  LinguaPlone comes into play.
  [stefan]

- Enable syndication on topics by default.
  [alecm]

- Made inherit criteria field only appear when the parent of a Smart Folder
  is also a Smart folder.
  [alecm]

- Added permissions checks to listSubTopics.
  [alecm]

- Remove Smart Folder syndication action as the action category has changed
  in CMF.
  [alecm]

- Fixed bug in subtopic listing.
  [alecm]

1.0.0-rc3 - 2005-08-01
----------------------

- Change manage_copyObjects' permission to Copy or move, just copy from
  Plone's PortalFolder.
  [panjunyong]

- Added method to fix the portal type name of CMF based objects
  that were imported or copied from an unmigrated site to a migrated
  site. The fix method is available in the type migration tab.
  [tiran]

- Added code to remove deprecated external methods.
  [tiran]

- Fixed an error in the module alias code for the exif library. Fixes
  http://plone.org/collector/4352 - Uploading certain images causes ATCT
  pickling errors
  [tiran]

- Expose some advanced migration options to the user by using new propertites
  in the portal_atct tool.
  [tiran]

- Enhanced and updated documentation, mostly the feature documentations in
  the portal_atct tool.
  [tiran]

- Moved migration related code from tool/atct.py to tool/migration.py. The
  tool class was getting too long.
  [tiran]

1.0.0-rc2 - 2005-07-28
----------------------

- Updated requirements to CMFDynamicViewFTI 1.0.0 and ATRefBrowserWidget
  1.1.
  [tiran]

- Fixed error in config loader code. The loader must stop after the first
  conf file is loaded or the conf file is overwritten by the default file.
  [panjunyong]

- Add optional arguments to ATTopic.queryCatalog to make it compatible with
  getFolderContents (optional batching, return full objects instead of
  brains).  Make the album_view compatible with Smart Folders.
  [alecm]

- Added fix for exif issue when rescaling the original image.  The exif
  information is now stored before the image is set.
  [tiran]

- Added a main macro to a few templates so they display nicely when used in
  discussion_reply_form.
  [alecm]

- Added workaround for broken WebDAV/FTP clients like Mac OS X Finder.
  PUT_factory is patched to use the default_PUT_factory which creates
  standard Zope objects instead of CMF/AT content objects.
  Thx to Nate and ATAudio for the idea.
  [tiran]

- Fixed http://members.plone.org/collector/4321 which was caused by three
  distinct bugs. 1) The initial rename of the CMF object didn't preserve
  order, but rather moved the object to the end of the list.  2) When
  migrating folders the check for orderability on self.new always failed
  because self.new is None at this point, so ordering wasn't attempted.
  3) When going through the subobjects of a folder the position was noted,
  and then the object deleted, the next object was now in the same position
  as the prior one and the order was lost.  Now there is a seperate loop to
  delete the objects after the loop which marks the order and preserves the
  object.
  [alecm]

- Fixed some minor issues with the relative url and CMF uid handling in
  ATFavorite.
  [tiran]

- Added AT and CMF uid migration to the migration system.
  [tiran]

- Fixed the unit test fixture and ATFavorite unit tests. Now tests aren't
  running as Manager only when really needed.
  [tiran]

1.0.0-rc1 - 2005-07-23
----------------------

- Fixed error in version parsing which somehow made portal_types disappear.
  [alecm]

- Enabled swallowResizeExceptions by default and added warning that original
  image resizing destroies the exif information before the data is saved.
  [tiran]

- Fixed spelling error in a security declaration of ATTopic.
  [tiran]

- Fixed critical migration issue. Locally added roles and locally changed
  permissions are now migrated. Also added unit tests to verify the
  migration.
  [tiran]

- Cleanup up unit tests and logging to reduce the noise
  [tiran]

- Removed 'MakerNote JPEGThumbnail' from the exif tags. Some cameras might
  store the thumbnail in this tag.
  [tiran]

- Removed unused customization policy including unit test. Plone 2.1 always
  installing ATCT.
  [tiran]

- Fixed 4330 Inter-version ATCT migration fails to migrate types
  to CMFDynamicViewFTI. Migration to the new FTI is part of the version
  migration again.
  [tiran]

- Added migration step + unit test for '(selected layout)' change.
  [tiran]

- Optimized getRawRelatedItems index addition. There is no need to reindex
  the *whole* catalog when adding a *single* index.
  [tiran]

- Made the 'view' method aliases point to '(selected layout)' instead of
  '(default view)'. This assures consistency with previous behaviour,
  so that /view at the end of a URL always gets the item itself, ignoring
  any default-page that may be set. Note that the 'view' *action* still
  points to 'string:${object_url}', so that the 'view' tab, as well as
  the '(Default)' target, still get '(dynamic view)' (and thus default
  pages) for types other than File and Image.
  [optilude]

- Added migration/othermigrator.py for other migrators like CMFPhoto and
  CMFPhotoAlbum. These migrators are written but not yet available to end
  users. Some glue code needs to be written.
  [tiran]

- Moved exif library to a new directory thirdparty/. This directory should
  contain all third party extensions that are required to run ATCT. Well
  lib/ was added for this purpose the first time. thirdparty/ is added to
  sys.path at position three which is right after Zope's instance home
  and zope home in most cases.
  [tiran]

- Removed lot's of unused imports.
  [tiran]

- Fixed http://plone.org/collector/4083 for atct_album_view.pt
  [ender]

- Fixed
  http://sf.net/tracker/?func=detail&atid=645337&aid=1215755&group_id=55262
  by making the template sane.
  [alecm]

- Fixed get_size for ATImage. It should return only the file size of the
  original image.
  [tiran]

- HEAD fixes for folder based content types.
  [tiran]

- Fixed permission issue in formatCatalogMetadata.py.
  [alecm]

- ConstrainTypes should default to disabled unless the parent object is of
  the same portal type.
  [alecm]

- General get_size fixes. The get_size() method returns either the size
  of the primary field or 1 for folders.
  [tiran]

- Moved not yet implemented URL upload feature out of the main code.
  [tiran]

- Fixed constraintypes's allowedContentTypes and invokeFactory to make
  ENABLED mode work when the portal_type is different with parent's.
  [panjunyong]

- Added http access functionl http tests.
  [tiran]

- Added HEAD() method to Topic. If the topic has at least one criterion or
  it can acquire a query 200 OK is return else 404 NotFound
  [tiran]

- Fixed [Plone] 4295/ 1 Request "ATCT and related items fields".
  [tiran]

- Added workaround for [ 1229206 ] 2.0.5 > 2.1 migration fails. Failing
  reorder is mostly harmless.
  [tiran]

- Added workarounds for EXIF MakerNote errors. Some cameras are *really*
  broken. Better no make notes than no exif infos at all.
  [tiran]

- Fixed and improved recent changes to cleanupFilename(). You can't remove
  features w/o keeping backward compatibility and new features must be
  bullet proof!
  [tiran]

- Clean up multiple Topic folder_contents tabs.
  [alecm]

- Readded a seperate _cleanupFilename method for ATCTFileContent to make it
  better for patch.
  [panjunyong]

- Fixed http://plone.org/collector/4218 ATCT now uses normalizeString from
  PloneTool.
  [hannosch]

- Fixed http://plone.org/collector/4170 Link checking is crazy and [ 1197068 ]
  [hannosch]

- made constraintypes default ACQUIRE mode works with portal_factory
  [panjunyong]

- Added Five/Zope3 interface bridges
  [tiran]

- Disabled text/x-python and text/plain-pre by default. Customize the
  atcontenttypes.conf if you need them.
  [tiran]

- Removed relatedItems field from folderish objects.
  [tiran]

- Made download tab for File and Image invisible.
  [tiran]

- Fixed __bobo_traverse__ in ATImage, security check was unnecessary and
  required anonymous to have 'View' in order for anyone to use it.
  [alecm]

- Yet another migration optimization: Added catalogpatch to the migration
  system. The patch is altering portal_catalog.catalog_object and
  uncatalog_object. Read migration/catalogpatch.py for more informations.
  The catalog patch can be enabled by passing use_catalog_patch=True to
  the migration functions.
  [tiran]

- Fixed last bit of http://plone.org/collector/3060  Don't let missing CMF
  types crash portal_atct.disableCMFTypes().
  [alecm]

- Enhanced migration code:
   - CatalogWalkerWithLevel is now based on ExtendedPathIndex
     and behaves like CatalogWalker.
   - Added walker arguments for transaction size, full transactions.
     and savepoints. The migration system can use ZODB savepoints to
     roll back to a sane point.
   - Migrators are also registered by (src,dst) meta_type.
   - The new function migratePortalType() can be used to migrate a single
     content type by just passing the src and dst portal type to the
     function. Both portal types must be registerd in portal_types and a
     migration from src to dst meta_type must exist.

  [tiran]

- Don't catalog all types in _catalogTypesByMetatype it the passed list is
  empty.
  [jenner, alecm]

- Modified templates to use the new pretty_title_or_id feature from plone.
  [alecm]

- Made atct_album_view use the catalog like other listings, and reuse the
  nice macro from folder_listing.
  [alecm]

- Zope2.7 compatibility again: replaced import transaction with from
  Products.CMFPlone import transaction.
  [hannosch]

- Some minor i18n tweaks.
  [hannosch]

- Updated INSTALL.txt for CMF 1.5. Zope 2.8 and more
  [tiran]

- CMF 1.5 / Zope2.8 compatibility:
   - replaced CMFCorePermissions with permissions
   - replaced get_transaction() with transaction
   - removed product argument from TooolInit()
   - logging.getLogger() and LOG.debug() etc.

  [tiran]

- Greatly enhanced logging during migration.
  [tiran]

- Chunked migration in smaller pieces. To be continued!
  [tiran]

- Fixed finalize migration so that it doesn't reinitialize the workflow
  state.  Added unit tests for workflow, local_role, and owner migration.
  [alecm]

- Using migration code from DynamicViewFTI instead of own FTI migration code
  [tiran]

- Moved ATCTImageTransform class to lib
  [tiran]

- Added configuration options for PIL quality and resize algo.
  [tiran]

- Couple of bug fixes in the FTI->FTI w/ dynamic views migration
  [rafrombrc]

- Renamed max_size config option to max_file_size. Added max_image_dimension
  config option to set the maximum border for the original size of an image.
  [tiran]

- Added some additional i18n markup.
  [hannosch]

Snapshot 2005-07-05
-------------------

- Don't run version migration when installing the first time. People should run it
  after type migration.
  [tiran]

- Disabled full catalog updated after type migration. If people need it they could
  do it after migration.
  [tiran]

- Added migration to DynamicFTIs.
  [fschulze]

- Changed index_html method on ATCTOrderedFolder to gracefully handle
  situation where acquisition of index_html attribute returns None.
  [rafrombrc]

- Added syndication support to Smart Folders.
  [alecm]

- Fixing up aliases and actions for CMF 1.5-style browser-default code, using
  CMFDynamicViewFTI.
  [optilude]

- Some code related to browser default is moved to CMFDynamicViewFTI. All
  new versions of ATCT depend on this product now.
  [tiran]

- Fixed some tests on Windows. Image files must be opened with 'rb'.
  [hannosch]

- Moved around some fields. excludeFromNav is on the property sheet expect for
  folderish items and discussion is on the main sheet expecpt for folderish and
  Favorite.
  [tiran]

- Added finalizeATCTSchema function to move the fields in the right position
  [tiran]

- Fixed http://plone.org/collector/4127 permission incorrect on
  listSubtopics.
  [alecm]

- Added migration to change the name of the Topic configlet.
  [alecm]

- Fixed http://members.plone.org/collector/4076, adding exclude_from_nav to
  all content schemas.
  [optilude]

- Fixes for migration of cataloged non-contentish objects.  Now checking
  meta_type and portal_type before migration steps.
  [alecm]

- Fixed http://members.plone.org/collector/3804 added validation of filename
  when appropriate using check_id if available.
  [alecm]

- Added index for relatedItems, and migration to install it into already
  installed instances.
  [alecm]

- Made the tool check if a config entry is available whenever it finds a new
  index, so that it is automatically enabled if desirable, and to minimize
  the need for migrations.
  [alecm]

- Disabled all indexes in criteria form by default, only those with
  default values are automatically enabled.  This prevents things like ZWiki
  from messing up our nice edit form.  They can be enabled and prettified in
  the tool.
  [alecm]

- Spring i18n cleanup:
  - changed i18n:domain from plone to atcontenttypes
  - added missing i18n markup
  - fixed page templates XHTML errors
  - reindented and cleaned up whitespaces
  [deo]

- Made portal_type, selection, and reference criteria return reasonably
  sorted lists.
  [alecm]

- Updated folderlisting actions to work properly with optiludes new
  browserdefault behavior.
  [alecm]

- Localized date in Topic custom view.
  [alecm]

1.0-alpha2
----------

- Disabled history tab.
  [tiran]

- Fixed a small bug in the exif support. The signatur of the process_file
  method has changed.
  [tiran]

- Catch KeyErrors on third party index types in the catalog.  Fix bad import
  of list criteria.  Fix some unit tests that I broke, and added some more
  (CriterionRegistry) in penance.
  [alecm]

- Updated exif lib.
  [russf]

- Added default values for the index/metadata friendly names, descriptions,
  and criteria restrictions for Smart Folders using ZConfig.  Added the
  ability to have an index with no criteria (useful for sort only criteria).
  Made the descriptions for the criteria types more sensible (I hope this
  doesn't screw up existing translations, but the current names are terrible).
  Also, added some missing criteria related strings to manual.pot.
  [alecm]

- Added a getCriteriaUniqueWidgetAttr method to topics to compile things like
  'helper_js' in one place for the edit form.
  [alecm]

- Fixed [ 1196809 ] Use getMutator(self) instead of mutator(self) in base.py.
  [stefan]

- Added new path criterion for use with ExtendedPathIndex that allows users
  to select paths to search in using a sitemap.  This now uses the
  lovely ATReferenceBrowserWidget.
  [alecm]

- Add Topic to the list of allowed sub-objects for Topic during Migration.
  It was missing before because the class allowed_content_types property
  was being overwritten by the one from CMFTopics.
  [alecm]

- BrowserDefaultMixin.getAvailableLayouts() now returns a list of tuples
  instead of a DisplayList. Required by interface change in Plone.
  [optilude]

- Added cool icons for vCal/iCal export and image rotation/flipping made by
  the legendary Vidar Anderson.
  [blacktar, tiran]

- Replaced AttributeStorage with AnnotationStorage for Document:text,
  File:file, Image:image, Event:text and NewsItem:text,image. This requires
  Archetypes 1.3.5.
  [tiran]

- Added new Current Author criterion which, when used with the Creator index,
  gets all objects authored by the currently logged in user.  Also fixed some
  permissions that were preventing normal users from viewing published topics.
  Fixes issue [ 1176355 ].
  [alecm]

- Changed processForm to check for id conflicts using check_ids if available,
  otherwise just `id in parent`. Also commit sub-transaction to make rename
  work after portal_factory.
  [alecm]

- Added version migration system mostly copied from plone. Works automatically
  during Plone 2.1 migration to bring plone 2.0 sites that started with ATCT
  >= 0.2 up to date including changing and uncatalogging ATTopic criteria and
  migrating CMF Topics.
  [alecm]

- Fixed a small bug in Topic migration introduced during the merge.
  [alecm]

- Made topic.addCriterion() return the newly added criterion object. That
  it didn't before made things hard for python product developers.
  [alecm]

- Fixed bug #3773 (http://plone.org/collector/3773) validation check for
  empty/non-existant files/images.
  [alecm]

- Changed the behavior of the date criteria to make the meaning of
  each field clearer.  Now queries like 'More than 2 weeks ago' can be used,
  and will behave as expected.  This causes some inconsistency in importing
  CMFTopics.  Queries that were of the form 'min' 'x days' 'ago' are now
  'less than x days ago' which is a min:max query with an upper limit of now.
  The same goes for 'max' 'x days' 'ahead', all other queries should be close
  to identical (modulo an earliestTime() where it makes sense).  The
  inconsistency shouldn't be too important as the CMF date criteria was
  entirely inscrutable.  Also changed some strings for criteria descriptions
  for consistency. Fixes bug [ 1181418 ]. Thanks to Dean Jackson for filing
  this bug and devising a reasonably usable UI.
  [alecm]

- Made the portal_types criteria work properly with either Types or
  portal_types indexes.  Disabled types restrictions in TopicTool, now uses the
  new Plone 2.1 search blacklist for types (site_properties.unfriendly_types).
  This creates a plone 2.1 dependency. Also a change was made to the
  atct_subtopic_form so that it now uses a macro from plone 2.1, this fixes
  issue [ 1164541 ].
  [alecm]

- Reworked linked select lists for criteria to use custom XMLHTTPRequest code,
  contained in modifySelectList.js.  I will eventually turn this into an AT
  MasterSelectWidget for the master select of two linked select lists.
  [alecm]

- Added and enabled configlet for Topics, and unit tests for the criteria.
  Fixed a persistency bug in TopicsTool, and a sort bug the in criteria
  listing.  Added Missing.MV as a possible false value for Boolean Criterion.
  [alecm]

- Removed some configuration vars from config.py and the ZConfig schema.
  [tiran]

- Moved external types from ATCT to the new ATCTAddons product.
  [tiran]

- Remove path of filename from ATFile's title when upload a file using MS IE.
  [panjunyong]

- Merged uiteam-plip73-sanitize-short-names from the old plone
  svn repos: diff http://svn.plone.org/svn/plone/ATContentTypes/branches/1.0@6168
  http://svn.plone.org/svn/plone/ATContentTypes/branches/uiteam-plip73-sanitize-short-names
  [tiran]

- Added flag to determine whether an content object has undergone a successful
  initial edit.  Use this flag along with detection of default naming to
  rename object on inital edit.
  [alecm]

- Merged the topic tool branch into 1.0 XXX: insert history here.
  [tiran]

- Refactored ConstrainTypesMixin to support PLIP 78:

   - DISABLED means use standard allowed types from portal_types
   - ENABLED means use restrictions set
   - ACQUIRE means use types from parent if parent is of same portal type,
     else same as ENABLED (doesn't make sense to inherit from any content type)
   - immediatelyAddableTypes field - for subset of allowed types to show in
     the "add" menu
   - turned off and removed disable constrain-types flag

  [tiran]

- Turn on TemplateMixin for everything - now directly supported in Plone
  via "display" menu.
  [tiran]

- Merged plip #3 branch: auto ordering / sorting into the 1.0 branch.
  Features / Changes:

   - Added getObjPositioninParent and getObjSize as helper methods for
     the catalog based folder listing to all types
   - Added AutoSortSuppot and AutoOrderSupport to ATCT. AutoSortSupport is
     used for the catalog based folder listing and AutoOrderSupport also
     adds some auto ordering based on OrderedFolder
   - Subclass ATFolder from AutoOrderSupport+AutoSortSupport, ATBTreeFolder
     only from AutoSortSupport

  [tiran]

- ATEvent: Removed end date and start date from searchable text.
  [tiran]

- Implemented PLIP #2 of ATCT: using ZConfig to configure the types and
  features of ATContentTypes.
  [tiran]

- Changed default output of Document, Event and News Item to text/x-safe-html.
  X-safe-html is using CMFDefault.utils.scrubHTML to remove harmful tags
  like script.
  [tiran]

- Merged tiran-notypesdir-branch. It's renaming and moving lot's of modules
  around. All content types are in the content/ package, criteria were moved
  to criteria/, tools to tool/ and modules like history aware to lib/. Also
  all modules and packages were renamed to be lower case.
  [tiran]

- Added history support ATEvent's text field just like Document and News Item.
  [tiran]

- Updated README.txt and INSTALL.txt: new versions, update from ATCT 0.2 and
  some other informations.
  [tiran]

- Changed permission of ATNewsItem.EditableBody() to ModifyPortalContent.
  [tiran]

- Added some tabs to the ZMI view of the portal_atct tool: Overview, rescale
  migrate and recatalog. The usage of the external methods is deprecated in
  favor of the tool.
  [tiran]

- Restored Plone 2.0.x compatibility.
  [deo]

- Don't show PloneSite, TempFolder and criteria in constrain types list.
  [tiran]

- Disabled validator for ATEvent's phone field. Some people have reported that
  they have issues because numbers and especially extensions are handle
  differently in every country. Also see [ 974102 ] Can't enter phone extension
  in phone number field.
  [tiran]

- Added XXX report tool to ATCT. It's mostly a copy from the Zope3 XXX tools.
  Note: XXX is a marker to show "here is something" wrong. It's not porn. :)
  The tool also reports TODO and BBB (for backward compatibility).
  [tiran]

- Fixed [ 1049018 ] url field on Link doesn't allow mailto. Also added an
  isMailto validator to validation and enhanced the isUrl validator to support
  more protocols.
  [tiran]

- Fixed [ 1114696 ] use correct mimetype for reStructuredText and [ 1122135 ]
  ATCT edit not preserving text type selection, not ATCT bug be renaming
  text/restructured to text/x-rst.
  [tiran]

- Fixed [ 1158950 ] ATTopic default view wrong. This fix needs also a svn up
  of CMFPlone 2.1.
  [tiran]

- Moved external storage based variants for ATFile and ATImage to a seperate
  module. They won't make it in the official trunk unless the storage is
  working well and the types are tested.
  [tiran]

- Added 'atct_album_view' and 'atct_album_image' templates based on the
  templates of CMFPhotoAlbum.
  [tiran]

- Replaced the config vars for permissions with new permissions:

   - ModifyConstrainTypes for constrain types mixin
   - ModifyViewTemplate for template mixin
   - ViewHistory for history mixin
   - UploadViaURL for the new upload via url feature

  By default the permissions are restricted to manager only.
  [tiran]

- Added new upload via url feature to upload a file or image using an url. The
  file is downloaded from the remote server using urllib2. Since this feature
  isn't finished it's not available by default.
  [tiran]

- Implemented some very useful functions based on CMFPhoto code for ATImage.
  The new features are:

   - getting the exif informations from images using Gene Cash's exif lib
   - getting the image orientation from exif data (rotation and mirror)
   - Rotating and flipping images using the PIL library incl. a new tab

  [tiran]

  The CMFPhoto exif and transform code was written by several ppl including
  Oliver Baltzer and me. I'm unable to determine the other coders. Please
  write me an email if you want credits for your great work!
  [tiran]

1.0-alpha1
----------

- Refactored huge parts of the migration suite. More later.
  [tiran]

- Fixed [ 1026616 ] Actions aren't migrated. Actions are migrated from
  the cmf fti if an action with the id doesn't exist on the atct fti.
  [tiran]

- Migrating filter content types, allowed content types and allow
  discussion from cmf fti to atct fti.
  [tiran]

- Updated requirements to CMFQuickinstaller 1.5/cvs,
  [tiran]

- Starting to remove the switch* and migrate* external methods.
  [tiran]

- Fixed default view of ATFolder. Pointing to view again makes a loop and
  raises a hard to debug exception because TemplateMixin is trying to use
  itself as default view which doesn't work.
  [tiran]

- FTests: install kupu and epoz when available. Moved function test suite to
  ftests/
  [tiran]

- Fixed [ 1157812 ] ival/vcal action icons not available
  [tiran]

- Fixed ATTopic to use atct_edit like all other ATCT types.
  [tiran]

- Added ERRATA.txt which covers known issues.
  [tiran]

- Added integration tests for discussions.
  [tiran]

- Ported topic migration and criteria enhancements + additional criteria
  from ender topic branch. Thx to Alec Mitchell for his great work! The new
  criteria are: ATSelectionCriterion, ATDateRangeCriterion,
  ATReferenceCriterion and ATBooleanCriterion.
  [allecm, tiran]

- Changed archetype names of criteria and removed the AT prefix.
  [tiran]

- Added unit tests for criteria and ATTopic.
  [allecm, tiran]

- Added translate tab when LinguaPlone is available at installation or
  reinstallation time.
  [tiran]

- Added mini scale with 200x200.
  [tiran]

- Added integration tests for view and edit templates.
  [tiran]

- I made major changes to the unit test suite. Also I've added more field
  tests, some important interface tests and cleaner and better base classes
  for tests.
  [tiran]

- prepare ATFolder for use with TemplateMixin, use generic /view instead of
  /folder_listing as default and immediate view.
  [yenzenz]

- Changed the way ConstrainTypes gets mixed in: Now ATCT is always subclassing
  folders from the ConstrainTypes class and the schema is always in the folder
  schema. Before this change ppl couldn't rely on the api. When the feature
  is disabled the fields are not shown in the schema and the overwritten
  methods are using a "shortcut" to the default methods.
  [tiran]

- Renamed some methods in the constrain mixin to start with _ct_ for a clean
  name space.
  [tiran]

- Added a tag methods to NewsItem for its image. Also changed the caption from
  TextField to StringField since it should contain only a small sentence or
  similar. The caption is applied as title to the news item image.
  [tiran]

- When running unit tests all features like constrain mixin and template
  mixin are forced to be enabled in order to keep the tests sane and to test
  all features under all circumstances.
  [tiran]

- Dismembered the big beast schemata.py in types/ and types/criteria. The
  schemata are in the same modules as the types.
  [tiran]

- Added content module which contains all important classes.
  [tiran]

- Replaced all `from foo import *` by explicit imports.
  [tiran]

- Used some code from Ben's great Bricolite product to have an add permission
  per type. It allows fine granulated permission settings.
  [tiran]

- Fixed bug [ 1154073 ] criterion_edit_form.cpt(.metadata) has no default
  action. The default action for the criterion edit form is save.
  [tiran]

- Added portal_atct tool. The new tool will be used for the new topic features
  and for the plone control panel.
  [tiran]

- Interface geddon: Merged all interfaces into a single file.
  [tiran]

- Merged limi's ui branch which adds a text field to ATEvent and an image plus
  image caption to ATNewsItem.
  [limi, tiran]

- Added related items reference field to all types using Danny's reference
  browser widget. The ATReferenceBrowserWidget has to be available.
  http://svn.plone.org/archetypes/MoreFieldsAndWidgets/ATReferenceBrowserWidget.
  [tiran]

- Removed old debian/ directory. I don't maintain it any more so there is no
  reason of having it in the CVS.
  [tiran]

- Removed QuotaSupport.py. It should never be in the official tree of ATCT.
  [tiran]

- Introduced great chances in the migration system: The portal type names of
  the ATCT types are the same as the CMF types. CMF types will be renamed at
  install time.
  [tiran]

- Introduced ZConfig based configuration. It will replace the customconfig.py
  file.
  [tiran]

0.2.0-rc5 - 2005-02-26
----------------------

- Updated requirements to Zope 2.7.4+, Python 2.3.4+ and AT 1.3.2-rc1+.
  [tiran]

- Cleaned up the migration suite a little bit and enhanced the doc strings.
  [tiran]

- Replaces the globalAllow hack by createTypeByName which doesn't make
  security checks like "is the type implicitly or explicitly addable in the
  folder". It shares the same codebase as the function from PloneUtilities
  I once wrote to unfuck the create member area method.
  [tiran]

- Better traceback support inside the migration suite.
  [tiran]

- Added knob to toggle the installation of LinguaPlone in ATCT install.
  [tiran]

- Added explicit portal type name to all ATCT types.
  [tiran]

- Renamed newTypeFor to _actc_newTypeFor. The former name was confusing
  people.
  [tiran]

- Added feature to access the name of the last editor through IHistoryAware.
  [ctheune]

- Fixed a bug in the migration walker. Empty folders aren't skipped any
  more.
  [panjunyong]

- Increase debugging in Migration suite to find issues with missing types
  in globalAllow.
  [tiran]

- Ported atct_topic_view icon fix from HEAD.
  [tiran]

- Don't create ATDocuments when uploading .pdf and .doc files.
  [batlogg]

- Resurrected warning message when we hit a broken object in the folder
  migration.
  [tiran]

- Local roles and Creator are kept when migration.
  [panjunyong]

- Update requirements to the soon to release AT 1.3.2 version and SVN.
  [tiran]

- Added update_data and manage_edit compat. methods to ATFile and ATImage.
  [tiran]

- Added temporary fix for [ 1095242 ] EditableBody in ATNewsItem requires
  Modify portal content. It will stay in ATNewsItem until Plone is fixed.
  [tiran]

- Fixed [ 1075193 ] infinite recursion in ATEvent. The __cmp__ hook was fixed
  a while ago but I forgot to mention it here.
  [tiran]

- Fixed [ 1098347 ] validate_add_criterion.vpy has errors. The file was
  DOS encoded.
  [tiran]

- Applied patch from [ 1104069 ] ATCT migration -- more ordering issues
  which fixes some more ordering issues.
  [hahnfeld]

- atct_topic_view now doesn't call getObject() anymore and is a small
  bit more performant. This also takes some burden from waking up objects.
  (Bug 1079030)
  [ctheune]

- Made HTML the default content type for documents (and news items).
  [ctheune]

- Fixed [ 1080729 ] Wrong permissions for ATDocument.EditableText /
  setFormat.
  [tiran]

- Use StdoutStringIO in migration to be more verbose.
  [tiran]

- Fixed atct_topcic_view: Make sure there is an object before referencing
  attributes. This can typically happen if there are problems with the
  AccessContentsInfo permission.
  [tesdal]

- Removed support of Python 2.1 and 2.2 from INSTALL.txt. Some code like
  migration requires new features of Python 2.3 like generators.
  [tiran]

- Added note to INSTALL.txt that ATCT will soon drop support for Zope < 2.7.2.
  [tiran]

0.2.0-rc4 - 2004-11-30
----------------------

- ATTopic: Adding the criterion type to the generated id, so you can sort
  and filter on the same field.
  [ctheune]

- Fixed unit tests to work without (and hopefully with too) runner again.
  [ctheune]

- Added feature that doesn't show users non-sortable criterions in the form.
  [ctheune]

- Added feature that removes double or stupid criterions (allowedRolesAndUsers,
  id/getId).
  [ctheune]

- Sorting criterion lists (by their translations).
  [ctheune]

- Added german translation.
  [ctheune]

- More i18n support in the templates.
  [ctheune]

- Fixed _very_ annoying problem with bad ids. this should be bullet proof.
  [ctheune]

- Extended german translations.
  [ctheune]

- Fixed ATDocument to not kill uploaded files on the submission of an empty
  text area.
  [ctheune]

- Fixed small bug in id protection.
  [ctheune]

- Fixed the case where the portal doesn't has a 'Members' folder or
  when it has another name.
  [deo]

- Fixed [ 1055347 ] id problems when member preferences are set to not
  display and [ 1055348 ] ATCTFile id problems with portal_factory in
  ATCTFileContent._setATCTFileContent().
  [tiran]

- Disabled external storages based types because neither I nor MrTopf have
  time to support it right now.
  [tiran]

- Added long description field and image tag to ATImage. Fixed [ 1056050 ]
  Add longdesc to ATImage.
  [tiran]

- Fixed [ 1057691 ] Make ATContentTypes tests works with testrunner.py.
  Thanks to dan_t.
  [dan_t, tiran]

- Added fix for [ 1063549 ] ATCT migration doesn't migrate order to
  migrator.py.
  [tiran]

- Fixed [ 1067719 ] Install.py bug: property modified but not assigned by
  removing unnecessary code from Install.py. AT itself is already handling
  use_folder_tabs.
  [tiran]

0.2.0-rc3 - 2004-10-17
----------------------

- Added ATContentTypes Site customization policy.
  [tiran]

- Fixed [ 1041830 ] TypeError: cmf_edit() takes at least 3 non-keyword
  arguments by changing the edit() implementation. A class var named
  cmf_edit_kws was introduced to fix the issue.
  [tiran]

- ATLink: Use urlparse library to sanify the url to strip of additional
  slashes. This is fixing http://plone.org/collector/3296 for ATCT.
  [tiran]

- Added support for the clear format feature of CMF Document.
  [tiran]

0.2.0-rc2 - 2004-10-06
----------------------

- Fixed problem with isIDAutoGenerated if the object was not wrapped in
  a site.
  [tiran]

- Fixed download tab
  [tiran]

- Made image/file viewable when invoked directly by adding an index_html.
  [tiran]

- Replaced tag method of ATImage.
  [tiran]

- Fixed migration: Migration failed when there was a broken object in a
  folder.
  [tiran]

- Fixed property migration: continue if the object already has this
  attribute.
  [tiran]

- Added talkback discussion migration.
  [tiran]

- Set description as primary field for ATEvent. Also use an easier syntax
  for setting description to isMetadata = False.
  [tiran]

- Renamed tab from history to last changes. Added big warning that the
  history is based on zodb revisions.
  [tiran]

- Added ExtendingType howto (more to follow).
  [tiran]

- Recoded migration walkers to use a generator instead returning a list to
  make them much more memory efficient.
  [tiran]

- Rewritten folder migration to use the depth inside the folder structur
  instead of recursing into the full side.
  [tiran]

- Added a findStaledObjects external method to ATCT to find staled objects.
  It is very useful to clean up a site before running the migration.
  [tiran]

- Fixed an ugly bug in ATDocument which was screwing up references on copy.
  [tiran]

- Merged ConstrainTypesMixin from the branch into the HEAD. Thanks to
  Leonardo Rochael Almeida and Jens Werner Klein for their work.
  [yenzens, rochael]

- Fixed [ 1013853 ] File upload image shows mime-type in widget.
  [tiran]

- Removed call to markCreationFlag().
  [tiran]

- Fixed problem with ATFavorite: Migration to ATFavorite failed when the
  object was gone or the user wasn't allowed to access it.
  [tiran]

- Fixed [ 1027070 ] Download permission. Now the download tab is shown for
  all logged in users with View permission.
  [tiran]

- Fixed [ 1027093 ] Edit permission topics. The edit action of ATTopic now
  requires ChangeTopic permission.
  [tiran]

- Fixed [ 1027094 ] folderlisting action for ATTopic. Removed folderlisting
  action using a module level modify_fti function in ATTopic.py.
  [tiran]

- Fixed [ 1026379 ] ATDocument: skipField in setContentType throws error by
  removing the custom setContentType method. It's not required any more.
  [tiran]

- Use a copy of the ATContentTypeSchema for every schema to make customizations
  easier. Fixed [ 1027283 ] Schema editing very hard.
  [tiran]

- Fixed [ 1035380 ] Problems with createMemberArea and ATCT by adding a
  setFormat() method to ATDocument which is using the translate method to
  map between stupid CMF content types and real mime types.
  [tiran]

- Changed mx.Tidy test to work around [ 1033396 ] Error on refresh.
  [tiran]

- Fixed [ 1036267 ] Some typos in customconfig.py.
  [tiran]

- Fixed [ 1036255 ] switchCMF2ATCT: Favorite can't be added anymore. The type
  was disabled inside the switch script.
  [tiran]

- Fixed [ 1027108 ] Inherit criteria not working.
  [tiran]

- Fixed [ 1030660 ] ConstrainMixin: All types are addable in an ATFolder by
  using a default_method to initialize the list of addable types. The method
  _globalAddableTypeIds was added to generate the list.
  [tiran]

- Fixed a possible problem in allowedContentTypes: Now the method is using
  fti.isConstructionAllowed(context) to verify that the type is constructable.
  [tiran]

- Added an option called enableConstrainMixin which is a boolean value
  (checkbox). When set to false the constrain mixin is disabled and the
  default list of addable types is generated by using the default values
  from portal_types.
  [tiran]

- Fixed [ 1030662 ] ConstrainMixin: Can't add an ATTopic to portal root by
  not subclassing ConstrainTypesMixin for ATCTFolder. ATCTFolder must ONLY
  to used as a base class for folderish but non folder types.
  [tiran]

- Added max_depth workaround and logging for [ 1039846 ] Ghosts in catalog
  while migration and endless loop.
  [tiran]

0.2.0-rc1 - 2004-07-28
----------------------

- Removed 'contents' tab and 'add new item' menu from ATTopic.
  [gotcha]

- Changed criteria tab to table UI.
  [gotcha]

- Added message when clicking remove on criteria without selecting first.
  [gotcha]

- Depend on new AT 1.3.0-beta3 release.
  [tiran]

- Changed ZMI add name of topic related types to 'ATContentTypes Topic'.
  [tiran]

0.2-beta8 - 2004-07-21

- Fixed validation problem with mx tidy validator and file uploads.
  [tiran]

- Changed time range ints in FriendlyDateCriterion to strings.
  [tiran]

- Reenable implicitly addable for ATFavorite.
  [tiran]

- Added validation for setup of sort order on topics.
  [gotcha]

- Added getSize, getHeight, getWidth methods and width/height attributes to
  ATImage.
  [tiran]

0.2-beta7 - 2004-06-27

- Moved around some code from ATFolder to ATContentType.
  [tiran]

- Fixed problem with index_html in ATBTreeFolder.
  [tiran]

- Fixed wrong portal type in Members ATBTreeFolder after migration.
  [tiran]

- Added initializeArchetype() to ATContentType base class and changed it to
  use edit() instead of update() to make invokeFactory compatible with the old
  cmf types syntax.
  [tiran]

- Fixed problem with _getPortalTypeName in initializeArchetype() phase of
  object creation. Before the fix the portal type name was the original type
  name (e.g. ATDocument) because it was changed after the initializeArchetype
  call by the portal types tool. This issue has caused some wired problems with
  LinguaPlone and workflows.
  [tiran]

- ATFile file field and ATImage image field are now language independend.
  Later I will add a I18NImage and I18NFile if needed. Having a seperate type
  for language dependend content for file and image is in my opinion easier to
  understand for people. Besides it's like Zope3.
  [tiran]

- Removed TemplateMixin specific code from ATContentType base class. It was
  moved to TemplateMixin some time ago.
  [tiran]

- Better error reporting for migration errors.
  [tiran]

- Fixed migration problem when LinguaPlone was installed.
  [tiran]

- Added - as valid char for ids.
  [tiran]

- Reindex only Type, portal_type and meta_type in switching script.
  [tiran]

- Wrapped field tests in a portal to fix a problem with missing tools.
  [tiran]

- Fixed migration problem of modified date and created date and also fixed
  a problem with the unit test that was testing the right date. I was
  trying to compare the mod date after editing the objects. %-)
  [tiran]

- Default type of ATDocument and ATNewsItem is configurable in
  customconfig.py.
  [tiran]

- Fixed issues with content type registry and registered templates after
  switching from or to ATCT mode.
  [tiran]

- Added validation to ATEvent: end date must be after start date.
  [tiran]

- First release with all unit tests of Archetypes, ATCT and CMFPlone
  tiran-atct-integration branch passing!
  [tiran]

0.2-beta6 - 2004-06-20
----------------------

- Added max upload size validator to ATFile and ATImage.
  [tiran]

- Changed permission for download tab an ATFile. Dont confuse the average
  user with the green edit frame.
  [jensens]

- Added a new class ATCTFileContent which contains some code for ATFile
  and ATImage.
  [tiran]

- Set title from the filename of an uploaded file (ATImage, ATFile).
  [tiran]

- Added limit for ATTopic.
  [gotcha]

- Added EditableBody method to ATDocument.
  [tiran]

- Added validation of Criterion support for a specific index.
  [gotcha]

- Added edit() methods for backward compatibility to CMF.
  [tiran]

- Added restrained folder support.
  [jensens]

- Disabled restrained folder support until it's fixed.
  [tiran]

0.2-beta5
---------

- Fixed multiple small bugs and added features requested in the bug
  tracker on sf.net.
  [tiran]

- Auto set id from filename for ATImage and ATFile.
  [tiran]

- Fixed python 2.1 compatibility problem with CMFCore/WorkflowTool.
  Thanks to Tiziano Lattisi.
  [tiran]

- Moved to validation chains.
  [tiran]

- Fixed security of HistoryAwareMixin.
  [tiran]

- Added iCal/vCal export to AT Event.
  [tiran]

- Added LinguaPlone support.
  [gotcha]

0.2-beta4
---------

- Added AT Dyn Document. It's a CMFDynamicDocument like type that supports
  rendering of TAL inside the body text.
  [tiran]

- Moved AT Dyn Document to a new product.
  [tiran]

- Fixed the migration.
  [tiran]

- Fixed and improved the switch from/to "ATCT as default types" methods.
  [tiran]

- Updated docs.
  [tiran]

- Moved helper methods to utils.
  [tiran]

- Switch objects in content_type_registry, too.
  [lelit]

- Added isSwitchedToATCT method.
  [tiran]

- Fixed misc UI problems like doubled folderContents.
  [tiran]

0.2-beta3 - 2004-04-20
----------------------

- Updated INSTALL.txt [tiran]

- Fixed default view of ATBTreeFolder and ATFolder (stage 2). Both types
  are using ATContentTypeSchema with TemplateMixinSchema.
  [tiran]

- Added a recreateATImageScales method as external method.
  [tiran]

- Added missing sharing tab to all ATCTContent based types.
  [tiran]

- Fixed AT Favorite.
  [jensens]

- Fixed atct_edit macro.
  [tiran]

0.2-beta2 - 2004-04-11
----------------------

- Update validators to reflect the last changes and fixes of the archetypes
  and validation packages.
  [tiran]

- Added uml diagram of ATCT classes.
  [tiran]

- misc small fixes and improvements.
  [tiran]

0.2-beta1 - 2004-04-09
----------------------

- First official beta release for testing.
  [tiran]
