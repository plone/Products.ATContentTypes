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

import logging
from cStringIO import StringIO

from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.migration.common import registerATCTMigrator
from Products.ATContentTypes.migration.common import getMigrator
from Products.ATContentTypes.migration.walker import CatalogWalker
from Products.ATContentTypes.migration.walker import CatalogWalkerWithLevel
from Products.ATContentTypes.migration.migrator import CMFItemMigrator
from Products.ATContentTypes.migration.migrator import CMFFolderMigrator
from Products.ATContentTypes.migration.catalogpatch import applyCatalogPatch
from Products.ATContentTypes.migration.catalogpatch import removeCatalogPatch

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from Acquisition import aq_base
from Products.CMFPlone import transaction

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

LOG = logging.getLogger('ATCT.migration')

CRIT_MAP = {'Integer Criterion': 'ATSimpleIntCriterion',
                'String Criterion': 'ATSimpleStringCriterion',
                'Friendly Date Criterion': 'ATFriendlyDateCriteria',
                'List Criterion': 'ATListCriterion',
                'Sort Criterion': 'ATSortCriterion'}

REV_CRIT_MAP = dict([[v,k] for k,v in CRIT_MAP.items()])

class DocumentMigrator(CMFItemMigrator):
    walkerClass = CatalogWalker
    map = {'text' : 'setText'}

    def custom(self):
        oldFormat = self.old.text_format
        # Need to convert between old mimetype and new
        self.new.setContentType(translateMimetypeAlias(oldFormat))

registerATCTMigrator(DocumentMigrator, document.ATDocument)

class EventMigrator(CMFItemMigrator):
    walkerClass = CatalogWalker
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

class TopicMigrator(CMFFolderMigrator):
    walkerClass = CatalogWalker
    map = {'acquireCriteria' : 'setAcquireCriteria'}

    def custom(self):
        for old_crit in self.new.objectValues(CRIT_MAP.keys()):
            self.new._delObject(old_crit.getId())
            old_crit = aq_base(old_crit)
            old_meta = old_crit.meta_type
            new_meta = CRIT_MAP[old_meta]
            self.new.addCriterion(old_crit.field or old_crit.index, new_meta)
            new_crit = self.new.getCriterion('%s_%s'%(old_crit.field or old_crit.index, new_meta))
            if new_meta not in ('ATSortCriterion', 'ATSimpleIntCriterion'):
                new_crit.setValue(old_crit.value)
            elif new_meta == 'ATSortCriterion':
                new_crit.setReversed(old_crit.reversed)
            if new_meta == 'ATFriendlyDateCriteria':
                old_op = old_crit.operation
                DATE_RANGE = ( old_crit.daterange == 'old' and '-') or '+'
                if old_op == 'max':
                    new_op = (DATE_RANGE == '-' and 'more') or 'less'
                elif old_op == 'min':
                    new_op = (DATE_RANGE == '-' and 'less') or 'more'
                else:
                    new_op = old_op
                new_crit.setOperation(new_op)
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
    walkerClass = CatalogWalker
    # mapped in custom()
    # map = { 'file' : 'setFile' }

    def custom(self):
        ctype = self.old.getContentType()
        file = str(self.old)
        self.new.setFile(file, mimetype = ctype)

registerATCTMigrator(FileMigrator, file.ATFile)

class ImageMigrator(CMFItemMigrator):
    walkerClass = CatalogWalker
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
    walkerClass = CatalogWalker
    map = {'remote_url' : 'setRemoteUrl'}

registerATCTMigrator(LinkMigrator, link.ATLink)

class FavoriteMigrator(LinkMigrator):
    walkerClass = CatalogWalker
    # see LinkMigrator
    # map = {'remote_url' : 'setRemoteUrl'}
    pass

registerATCTMigrator(FavoriteMigrator, favorite.ATFavorite)

class NewsItemMigrator(DocumentMigrator):
    walkerClass = CatalogWalker
    # see DocumentMigrator
    map = {'text' : 'setText'}

registerATCTMigrator(NewsItemMigrator, newsitem.ATNewsItem)

class FolderMigrator(CMFFolderMigrator):
    walkerClass = CatalogWalkerWithLevel
    map = {}

registerATCTMigrator(FolderMigrator, folder.ATFolder)

class LargeFolderMigrator(CMFFolderMigrator):
    walkerClass = CatalogWalkerWithLevel
    # no other attributes to migrate
    map = {}

registerATCTMigrator(LargeFolderMigrator, folder.ATBTreeFolder)

migrators = (DocumentMigrator, EventMigrator, FavoriteMigrator, FileMigrator,
             ImageMigrator, LinkMigrator, NewsItemMigrator,
            )

folderMigrators = ( FolderMigrator, LargeFolderMigrator, TopicMigrator,)

def migrateAll(portal, **kwargs):
    LOG.debug('Starting ATContentTypes type migration')
    
    kwargs = kwargs.copy()
    for remove in ('src_portal_type', 'dst_portal_type'):
        if remove in kwargs:
            del kwarg[remove]
        
    out = StringIO()
    for migrator in migrators+folderMigrators:
        src_portal_type = migrator.src_portal_type
        dst_portal_type = migrator.dst_portal_type
        ttool = getToolByName(portal, 'portal_types')
        if (getattr(ttool, src_portal_type, None) is None or
                getattr(ttool, dst_portal_type, None) is None):
            
            LOG.debug('Missing FTI for %s or %s'%(src_portal_type, dst_portal_type))
            print >>out, ("Couldn't migrate src_portal_type due to missing FTI")
            continue
        migratePortalType(portal, src_portal_type, dst_portal_type, out=out,
                      migrator=migrator, **kwargs)
                    
    #transaction.commit()
    
    LOG.debug('Finished ATContentTypes type migration')
    
    return out.getvalue()

def migratePortalType(portal, src_portal_type, dst_portal_type, out=None,
                      migrator=None, use_catalog_patch=False, **kwargs):
    """Migrate from src portal type to dst portal type
    
    Additional **kwargs are applied to the walker
    """
    if not out:
        out = StringIO()
        
    # migrators are also registered by (src meta type, dst meta type)
    # let's find the right migrator for us
    ttool = getToolByName(portal, 'portal_types')
    src = ttool.getTypeInfo(src_portal_type)
    dst = ttool.getTypeInfo(dst_portal_type)
    if src is None or dst is None:
        raise ValueError, "Unknown src or dst portal type: %s -> %s" % (
                           src_portal_type, dst_portal_type,)
    
    key = (src.Metatype(), dst.Metatype())
    migratorFromRegistry = getMigrator(key)
    if migratorFromRegistry is None:
        raise ValueError, "No registered migrator for '%s' found" % key
    
    if migrator is not None:
        # got a migrator, make sure it is the right one
        if migrator is not migratorFromRegistry:
            raise ValueError, "ups"
    else:
        migrator = migratorFromRegistry 

    Walker = migrator.walkerClass
    
    msg = '--> Migrating %s to %s with %s' % (src_portal_type,
           dst_portal_type, Walker.__name__)
    print >> out, msg
    LOG.debug(msg)
    
    walk = Walker(portal, migrator, src_portal_type=src_portal_type,
                  dst_portal_type=dst_portal_type, **kwargs)
    # wrap catalog patch inside a try/finally clause to make sure that the catalog
    # is unpatched under *any* circumstances (hopely)
    try:
        if use_catalog_patch:
            applyCatalogPatch(portal)
        walk.go()
    finally:
        if use_catalog_patch:
            removeCatalogPatch(portal)
    
    print >>out, walk.getOutput()       
    LOG.debug('<-- Migrating %s to %s done' % (src_portal_type, dst_portal_type))
    
    return out
