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
__author__  = ''
__docformat__ = 'restructuredtext'

from cgi import escape

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from ComputedAttribute import ComputedAttribute
from OFS.Image import Image

from Products.Archetypes.public import Schema
from Products.Archetypes.public import ImageField
from Products.Archetypes.public import ImageWidget
from Products.Archetypes.public import PrimaryFieldMarshaller

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.config import MAX_IMAGE_SIZE
from Products.ATContentTypes.types.ATContentType import registerATCT
from Products.ATContentTypes.types.ATContentType import ATCTFileContent
from Products.ATContentTypes.types.ATContentType import cleanupFilename
from Products.ATContentTypes.interfaces import IATImage
from Products.ATContentTypes.types.schemata import ATContentTypeSchema
from Products.ATContentTypes.types.schemata import relatedItemsField
from Products.validation.validators.SupplValidators import MaxSizeValidator


ATImageSchema = ATContentTypeSchema.copy() + Schema((
    ImageField('image',
               required=True,
               primary=True,
               languageIndependent=True,
               #swallowResizeExceptions=True,
               sizes= {'preview' : (400, 400),
                       'mini'    : (200, 200),
                       'thumb'   : (128, 128),
                       'tile'    :  (64, 64),
                       'icon'    :  (32, 32),
                       'listing' :  (16, 16),
                      },
               validators = MaxSizeValidator('checkFileMaxSize',
                                             maxsize=MAX_IMAGE_SIZE),
               widget = ImageWidget(
                        #description = "Select the image to be added by clicking the 'Browse' button.",
                        #description_msgid = "help_image",
                        description = "",
                        label= "Image",
                        label_msgid = "label_image",
                        i18n_domain = "plone",
                        show_content_type = False,)),
    ), marshall=PrimaryFieldMarshaller()
    )
ATImageSchema.addField(relatedItemsField)

ATExtImageSchema = ATImageSchema.copy()
# XXX ATExtImageSchema['image'].storage = ExternalStorage(prefix='atct', archive=False)

class ATImage(ATCTFileContent):
    """An Archetypes derived version of CMFDefault's Image"""

    schema         =  ATImageSchema

    content_icon   = 'image_icon.gif'
    meta_type      = 'ATImage'
    portal_type    = 'ATImage'
    archetype_name = 'Image'
    immediate_view = 'image_view'
    default_view   = 'image_view'
    suppl_views    = ()
    _atct_newTypeFor = {'portal_type' : 'Image', 'meta_type' : 'Portal Image'}
    typeDescription= ("Using this form, you can enter details about the image, \n"
                      "and upload an image if required.")
    typeDescMsgId  = 'description_edit_image'
    assocMimetypes = ('image/*', )
    assocFileExt   = ('jpg', 'jpeg', 'png', 'gif', )
    cmf_edit_kws   = ('file', )

    __implements__ = ATCTFileContent.__implements__, IATImage

    security       = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setImage')
    def setImage(self, value, **kwargs):
        """Set id to uploaded id
        """
        self._setATCTFileContent(value, **kwargs)

    security.declareProtected(CMFCorePermissions.View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

    def __str__(self):
        """cmf compatibility
        """
        return self.tag()
    
    security.declareProtected(CMFCorePermissions.View, 'getSize')
    def getSize(self, scale=None):
        field = self.getField('image')
        return field.getSize(self, scale=scale)
    
    security.declareProtected(CMFCorePermissions.View, 'getWidth')
    def getWidth(self, scale=None):
        return self.getSize(scale)[0]

    security.declareProtected(CMFCorePermissions.View, 'getHeight')
    def getHeight(self, scale=None):
        return self.getSize(scale)[1]
    
    width = ComputedAttribute(getWidth, 1)
    height = ComputedAttribute(getHeight, 1)

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, precondition='', file=None, title=None):
        if file is not None:
            self.setImage(file)
        if title is not None:
            self.setTitle(title)
        self.reindexObject()

registerATCT(ATImage, PROJECTNAME)


class ATExtImage(ATImage):
    """An Archetypes derived version of CMFDefault's Image with
    external storage
    """

    schema         =  ATExtImageSchema

    content_icon   = 'image_icon.gif'
    meta_type      = 'ATExtImage'
    portal_type    = 'ATATExtImage'
    archetype_name = 'AT Ext Image'
    _atct_newTypeFor = None
    assocMimetypes = ()
    assocFileExt   = ()

    security       = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.View, 'getImage')
    def getImage(self, **kwargs):
        """Return the image with proper content type
        """
        field  = self.getField('image')
        image  = field.get(self, **kwargs)
        ct     = self.getContentType()
        parent = aq_parent(self)
        i      = Image(self.getId(), self.Title(), image, ct)
        return i.__of__(parent)

# XXX external storage based types are currently disabled due the lack of time
# and support for ext storage. Neither MrTopf nor I have time to work on ext
# storage.
#if HAS_EXT_STORAGE:
#    registerATCT(ATExtImage, PROJECTNAME)
