#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""


"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.ATFolder'

from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.config import ENABLE_CONSTRAIN_TYPES_MIXIN
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTOrderedFolder
from Products.ATContentTypes.content.base import ATCTBTreeFolder
from Products.ATContentTypes.interfaces import IATFolder
from Products.ATContentTypes.interfaces import IATBTreeFolder
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import relatedItemsField
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema

ATFolderSchema      = ATContentTypeSchema.copy() + ConstrainTypesMixinSchema
ATBTreeFolderSchema = ATContentTypeSchema.copy() + ConstrainTypesMixinSchema

ATFolderSchema.addField(relatedItemsField)
ATBTreeFolderSchema.addField(relatedItemsField)

class ATFolder(ATCTOrderedFolder):
    """A simple folderish archetype"""

    schema         =  ATFolderSchema

    content_icon   = 'folder_icon.gif'
    meta_type      = 'ATFolder'
    portal_type    = 'Folder'
    archetype_name = 'Folder'
    immediate_view = 'folder_listing'
    default_view   = 'folder_listing'
    suppl_views    = ('atct_album_view', )
    _atct_newTypeFor = {'portal_type' : 'CMF Folder', 'meta_type' : 'Plone Folder'}
    typeDescription= ''
    typeDescMsgId  = ''
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    __implements__ = ATCTOrderedFolder.__implements__, IATFolder

    security       = ClassSecurityInfo()

##    actions = updateActions(ATCTOrderedFolder,
##        ({
##         'id'          : 'folderContents',
##         'name'        : 'Contents',
##         'action'      : 'string:${folder_url}/folder_contents',
##         'permissions' : (CMFCorePermissions.ListFolderContents,),
##         'condition'   : 'python:object.displayContentsTab()'
##          },
##        )
##    )

registerATCT(ATFolder, PROJECTNAME)

class ATBTreeFolder(ATCTBTreeFolder):
    """A simple btree folderish archetype"""
    schema         =  ATBTreeFolderSchema

    content_icon   = 'folder_icon.gif'
    meta_type      = 'ATBTreeFolder'
    portal_type    = 'Large Plone Folder'
    archetype_name = 'Large Folder'
    immediate_view = 'folder_listing'
    default_view   = 'folder_listing'
    suppl_views    = ('atct_album_view', )
    global_allow   = False
    _atct_newTypeFor = {'portal_type' : 'CMF Large Plone Folder',
                        'meta_type' : 'Large Plone Folder'}
    TypeDescription= ''
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    __implements__ = ATCTBTreeFolder.__implements__, IATBTreeFolder

    security       = ClassSecurityInfo()

registerATCT(ATBTreeFolder, PROJECTNAME)
