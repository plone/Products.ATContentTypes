"""Migration tools for ATContentTypes

Migration system for the migration from CMFDefault/Event types to archetypes
based ATContentTypes (http://sf.net/projects/collective/).

Copyright (c) 2004-2005, Christian Heimes <ch@comlounge.net> and contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 * Neither the name of the author nor the names of its contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.
"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.migration.common import registerATCTMigrator
from Products.ATContentTypes.migration.common import LOG
from Products.ATContentTypes.migration.walker import CatalogWalker
from Products.ATContentTypes.migration.walker import CatalogWalkerWithLevel
from Products.ATContentTypes.migration.walker import useLevelWalker
from Products.ATContentTypes.migration.migrator import CMFItemMigrator
from Products.ATContentTypes.migration.migrator import CMFFolderMigrator
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent

from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import event
from Products.ATContentTypes.content import favorite
from Products.ATContentTypes.content import file
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import image
from Products.ATContentTypes.content import link
from Products.ATContentTypes.content import newsitem
from Products.ATContentTypes.content import topic
from Products.ATContentTypes.content.base import translateMimetypeAlias

CRIT_MAP = {'Integer Criterion': 'ATSimpleIntCriterion',
                'String Criterion': 'ATSimpleStringCriterion',
                'Friendly Date Criterion': 'ATFriendlyDateCriteria',
                'List Criterion': 'ATListCriterion',
                'Sort Criterion': 'ATSortCriterion'}

REV_CRIT_MAP = dict([[v,k] for k,v in CRIT_MAP.items()])

class DocumentMigrator(CMFItemMigrator):
    walker = CatalogWalker
    map = {'text' : 'setText'}

    def custom(self):
        oldFormat = self.old.text_format
        # Need to convert between old mimetype and new
        self.new.setContentType(translateMimetypeAlias(oldFormat))

registerATCTMigrator(DocumentMigrator, document.ATDocument)

class EventMigrator(CMFItemMigrator):
    walker = CatalogWalker
    map = {
            'location'      : 'setLocation',
            'Subject'       : 'setEventType',
            'event_url'     : 'setEventUrl',
            #'start_date'    : 'setStartDate',
            #'end_date'      : 'setEndDate',
            'contact_name'  : 'setContactName',
            'contact_email' : 'setContactEmail',
            'contact_phone' : 'setContactPhone',
          }

    def custom(self):
        sdate = self.old.start_date
        edate = self.old.end_date

        if sdate is None:
            sdate = self.old.created()
        if edate is None:
            edate = sdate

        self.new.setStartDate(sdate)
        self.new.setEndDate(edate)

registerATCTMigrator(EventMigrator, event.ATEvent)

class TopicMigrator(CMFItemMigrator):
    walker = CatalogWalker
    # XXX can't handle nested topics
    map = {'acquireCriteria' : 'setAcquireCriteria'}

    def custom(self):
        for old_crit in self.old.listCriteria():
            old_meta = old_crit.meta_type
            new_meta = CRIT_MAP[old_meta]
            self.new.addCriterion(old_crit.field or old_crit.index, new_meta)
            new_crit = self.new.getCriterion('%s_%s'%(old_crit.field or old_crit.index, new_meta))
            if new_meta not in ('ATSortCriterion', 'ATSimpleIntCriterion'):
                new_crit.setValue(old_crit.value)
            elif new_meta == 'ATSortCriterion':
                new_crit.setReversed(old_crit.reversed)
            if new_meta == 'ATFriendlyDateCriteria':
                new_crit.setOperation(old_crit.operation)
                DATE_RANGE = ( old_crit.daterange == 'old' and '-') or '+'
                new_crit.setDateRange(DATE_RANGE)
            if new_meta == 'ATListCriterion':
                new_crit.setOperator(old_crit.operator)
            if new_meta == 'ATSimpleIntCriterion':
                old_val = old_crit.value
                if isinstance(old_val, (tuple,list)):
                    new_crit.setValue(old_val[0])
                    new_crit.setValue2(old_val[1])
                elif isinstance(old_val, int):
                    new_crit.setValue(old_val)
                else:
                    raise AttributeError, 'Int Criteria for topic %s has invalid value %s'%(old_crit.title_or_id(), old_val)
                new_crit.setDirection(old_crit.direction)

registerATCTMigrator(TopicMigrator, topic.ATTopic)

class FileMigrator(CMFItemMigrator):
    walker = CatalogWalker
    # mapped in custom()
    # map = { 'file' : 'setFile' }

    def custom(self):
        ctype = self.old.getContentType()
        file = str(self.old)
        self.new.setFile(file, mimetype = ctype)

registerATCTMigrator(FileMigrator, file.ATFile)

class ImageMigrator(CMFItemMigrator):
    walker = CatalogWalker
    # mapped in custom()
    # map = {'image':'setImage'}

    def custom(self):
        ctype = self.old.getContentType()
        # to retrieve the binary data
        # it is not sufficient to just use str(self.old)
        image = self.old.data
        self.new.setImage(image, mimetype = ctype)

registerATCTMigrator(ImageMigrator, image.ATImage)

class LinkMigrator(CMFItemMigrator):
    walker = CatalogWalker
    map = {'remote_url' : 'setRemoteUrl'}

registerATCTMigrator(LinkMigrator, link.ATLink)

class FavoriteMigrator(LinkMigrator):
    walker = CatalogWalker
    # see LinkMigrator
    # map = {'remote_url' : 'setRemoteUrl'}
    pass

registerATCTMigrator(FavoriteMigrator, favorite.ATFavorite)

class NewsItemMigrator(DocumentMigrator):
    walker = CatalogWalker
    # see DocumentMigrator
    map = {'text' : 'setText'}

registerATCTMigrator(NewsItemMigrator, newsitem.ATNewsItem)

class FolderMigrator(CMFFolderMigrator):
    walker = CatalogWalkerWithLevel
    map = {}

registerATCTMigrator(FolderMigrator, folder.ATFolder)

class LargeFolderMigrator(CMFFolderMigrator):
    walker = CatalogWalkerWithLevel
    # no other attributes to migrate
    map = {}

registerATCTMigrator(LargeFolderMigrator, folder.ATBTreeFolder)

migrators = (DocumentMigrator, EventMigrator, FavoriteMigrator, FileMigrator,
             ImageMigrator, LinkMigrator, NewsItemMigrator,
            )

folderMigrators = ( FolderMigrator, LargeFolderMigrator, TopicMigrator,)

def migrateAll(portal):
    # first fix Members folder
    kwargs = {}
    catalog = getToolByName(portal, 'portal_catalog')
    pprop = getToolByName(portal, 'portal_properties')
    atct = getToolByName(portal, TOOLNAME)
    # XXX atct._fixLargePloneFolder()
    try:
        kwargs['default_language'] = pprop.aq_explicit.site_properties.default_language
    except (AttributeError, KeyError):
        kwargs['default_language'] = 'en'
        
    out = []
    for migrator in migrators:
        #out.append('\n\n*** Migrating %s to %s ***\n' % (migrator.src_portal_type, migrator.dst_portal_type))
        out.append('*** Migrating %s to %s ***' % (migrator.src_portal_type, migrator.dst_portal_type))
        w = CatalogWalker(migrator, catalog)
        out.append(w.go(**kwargs))
    for migrator in folderMigrators:
        #out.append('\n\n*** Migrating %s to %s ***\n' % (migrator.src_portal_type, migrator.dst_portal_type))
        out.append('*** Migrating %s to %s ***' % (migrator.src_portal_type, migrator.dst_portal_type))
        useLevelWalker(portal, migrator, out=out, **kwargs)
                
    #out.append('\nCommitting full transaction')
    #get_transaction().commit()
    #get_transaction().begin()

    wf = getToolByName(catalog, 'portal_workflow')
    LOG('starting wf migration')
    count = wf.updateRoleMappings()
    #out.append('\n\n*** Workflow: %d object(s) updated. ***\n' % count)
    out.append('Workflow: %d object(s) updated.' % count)
    
    #out.append('\nCommitting full transaction')
    #get_transaction().commit()
    #get_transaction().begin()
    
    LOG('starting catalog update')
    ct = getToolByName(catalog, 'portal_catalog')
    ct.refreshCatalog(clear=1)
    out.append('Portal catalog updated.')

    return '\n'.join(out)
