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

from Products.Archetypes.Storage.annotation import migrateStorageOfType
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content.event import ATEventSchema
from Products.ATContentTypes.content.file import ATFileSchema
from Products.ATContentTypes.content.image import ATImageSchema
from Products.ATContentTypes.content.newsitem import ATNewsItemSchema

_marker = object()

MIGRATION_LIST = (
    ('Document', ATDocumentSchema),
    ('Event', ATEventSchema),
    ('File', ATFileSchema),
    ('Image', ATImageSchema),
    ('News Item', ATNewsItemSchema),
    )

def storageMigration(portal):
    for portal_type, schema in MIGRATION_LIST:
        migrateStorageOfType(portal, portal_type, schema)

