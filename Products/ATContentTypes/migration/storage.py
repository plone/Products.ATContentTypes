"""Migration tools for ATContentTypes

Migration system for the migration from CMFDefault/Event types to archetypes
based CMFPloneTypes (http://sf.net/projects/collective/).

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

from copy import copy

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base
from Acquisition import aq_parent
from Acquisition import aq_inner

from Products.ATContentTypes.config import TOOLNAME
from Products.Archetypes.public import getAnnotation
from Products.Archetypes.public import AT_ANN_STORAGE
from Products.Archetypes.public import AT_MD_STORAGE

_marker = object()

MIGRATION_LIST = (
    ('Document', ('text',), ()),
    ('Event', ('text',), ()),
    ('File', ('file',), ()),
    ('Image', ('image',), ()),
    ('News Item', ('text', 'image'), ()),
    )

def storageMigration(portal):
    for portal_type, fields, md_fields in MIGRATION_LIST:
        migrateStorageOfType(portal, portal_type, fields, md_fields)

def migrateStorageOfType(portal, portal_type, fields, md_fields):
    """Migrate storage from attribute to annotation storage
    
    portal - portal
    portal_type - portal type to migrate
    fields - list of field names to migrate from attribute storage
    md_fields - list of field names to migrate from metadata storage
    """
    catalog = getToolByName(portal, 'portal_catalog')
    brains = catalog(Type = portal_type)
    for brain in brains:
        obj = brain.getObject()
        if obj is None:
            continue
        
        try: state = obj._p_changed
        except: state = 0
        
        ann = getAnnotation(obj)
        clean_obj = aq_base(obj)
        attr2ann(clean_obj, ann, fields)
        meta2ann(clean_obj, ann, md_fields)
        
        if state is None: obj._p_deactivate()

def attr2ann(clean_obj, ann, fields):
    """Attribute 2 annotation
    """
    for field in fields:
        if not ann.hasSubkey(AT_ANN_STORAGE, field):
            value = getattr(clean_obj, field, _marker)
            if value is not _marker:
                ann.setSubkey(AT_ANN_STORAGE, value, subkey=field)
                delattr(obj, field)
        else:
            value = getattr(clean_obj, field, _marker)
            if value is not _marker:
                delattr(obj, field)
    
def meta2ann(clean_obj, ann, fields):
    """metadata 2 annotation
    """
    md = clean_obj._md
    for field in fields:
        if not ann.hasSubkey(AT_MD_STORAGE, field):
            value = md.get(field, _marker)
            if value is not _marker:
                ann.setSubkey(AT_MD_STORAGE, value, subkey=field)
                del md[field]
        else:
            try:
                del md[field]
            except KeyError:
                pass
