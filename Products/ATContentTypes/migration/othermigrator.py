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

from Products.ATContentTypes.migration.common import registerMigrator
from Products.ATContentTypes.migration.common import migratePortalType
from Products.ATContentTypes.migration.atctmigrator import ImageMigrator
from Products.ATContentTypes.migration.atctmigrator import FolderMigrator
from Products.ATContentTypes.migration.atctmigrator import LargeFolderMigrator

# migrators for CMFPhoto and CMFPhotoAlbum
# you have to create a portal type either based on ATFolder or ATBTreeFolder first!

class CMFPhotoMigrator(ImageMigrator):
    src_meta_type = 'Photo'
    src_portal_type = 'Photo'
    dst_meta_type = 'ATImage'
    dst_portal_type = 'Image'

registerMigrator(CMFPhotoMigrator)

class CMFPhotoAlbumMigrator2OrderedFolder(FolderMigrator):
    src_meta_type = 'Photo Album'
    src_portal_type = 'Photo Album'
    dst_meta_type = 'ATFolder'
    dst_portal_type = 'Photo Folder'

registerMigrator(CMFPhotoAlbumMigrator2OrderedFolder)

class CMFPhotoAlbumMigrator2LargeFolder(LargeFolderMigrator):
    src_meta_type = 'Photo Album'
    src_portal_type = 'Photo Album'
    dst_meta_type = 'ATBTreeFolder'
    dst_portal_type = 'Photo Folder'

registerMigrator(CMFPhotoAlbumMigrator2LargeFolder)
    