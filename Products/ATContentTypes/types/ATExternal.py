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
"""External storage variants of ATFile and ATImage

USE AT OWN RISK! Highly unstable
"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.Archetypes.Storage import Storage

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.types.ATContentType import registerATCT
from Products.ATContentTypes.config import HAS_EXT_STORAGE
from Products.ATContentTypes.config import EXT_STORAGE_ENABLE
from Products.ATContentTypes.types.ATFile import ATFile
from Products.ATContentTypes.types.ATFile import ATFileSchema
from Products.ATContentTypes.types.ATImage import ATImage
from Products.ATContentTypes.types.ATImage import ATImageSchema

if HAS_EXT_STORAGE:
    from Products.ExternalStorage.ExternalStorage import ExternalStorage
else:
    class ExternalStorage(Storage):
        """Dummy storage
        """
        def __init__(self, *args, **kwargs):
            pass

ATExtImageSchema = ATImageSchema.copy()
imageField = ATExtImageSchema['image']
imageField.storage = ExternalStorage(prefix = 'atct',
                                     archive = False,
                                     rename = True)
# re-register storage layer
imageField.registerLayer('storage', imageField.storage)

ATExtFileSchema = ATFileSchema.copy()
fileField = ATExtFileSchema['file']
fileField.storage = ExternalStorage(prefix = 'atct',
                                    archive = False,
                                    rename = False)
# re-register storage layer
fileField.registerLayer('storage', fileField.storage)


class ATExtFile(ATFile):
    """
    """

    schema         =  ATExtFileSchema

    content_icon   = 'file_icon.gif'
    portal_type    = 'ATExtFile'
    meta_type      = 'ATExtFile'
    archetype_name = 'File (ext)'
    _atct_newTypeFor = None
    assocMimetypes = ()
    assocFileExt   = ()

    security       = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.View, 'index_html')
    def index_html(self):
        """Allows file direct access download."""
        field = self.getPrimaryField()
        field.download(self)

if HAS_EXT_STORAGE and EXT_STORAGE_ENABLE:
    registerATCT(ATExtFile, PROJECTNAME)


class ATExtImage(ATImage):
    """An Archetypes derived version of CMFDefault's Image with
    external storage
    """

    schema         =  ATExtImageSchema

    content_icon   = 'image_icon.gif'
    meta_type      = 'ATExtImage'
    portal_type    = 'ATExtImage'
    archetype_name = 'Image (ext)'
    _atct_newTypeFor = None
    assocMimetypes = ()
    assocFileExt   = ()

    security       = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.View, 'index_html')
    def index_html(self):
        """Allows file direct access download."""
        field = self.getPrimaryField()
        field.download(self)

if HAS_EXT_STORAGE and EXT_STORAGE_ENABLE:
    registerATCT(ATExtImage, PROJECTNAME)

