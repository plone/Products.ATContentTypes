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
"""AT Image

The basics for the EXIF information, orientation code and the rotation code
were taken from CMFPhoto.
"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.ATImage'

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from Acquisition import aq_parent
from ComputedAttribute import ComputedAttribute
from Globals import InitializeClass

from Products.Archetypes.public import Schema
from Products.Archetypes.public import ImageField
from Products.Archetypes.public import ImageWidget
from Products.Archetypes.public import PrimaryFieldMarshaller
from Products.Archetypes.public import AnnotationStorage
from Products.Archetypes.public import log_exc

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.config import HAS_PLONE2
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.content.base import updateActions
from Products.ATContentTypes.content.base import InvalidContentType
from Products.ATContentTypes.interfaces import IATImage
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.schemata import urlUploadField
from Products.ATContentTypes.lib.imagetransform import ATCTImageTransform

from Products.validation.config import validation
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED

validation.register(MaxSizeValidator('checkImageMaxSize',
                                     maxsize=zconf.ATImage.max_file_size))

from Products.validation.validators.SupplValidators import MaxSizeValidator

ATImageSchema = ATContentTypeSchema.copy() + Schema((
    ImageField('image',
               required=True,
               primary=True,
               languageIndependent=True,
               storage = AnnotationStorage(migrate=True),
               swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
               pil_quality = zconf.pil_config.quality,
               pil_resize_algo = zconf.pil_config.resize_algo,
               max_size = zconf.ATImage.max_image_dimension,
               sizes= {'large'   : (768, 768),
                       'preview' : (400, 400),
                       'mini'    : (200, 200),
                       'thumb'   : (128, 128),
                       'tile'    :  (64, 64),
                       'icon'    :  (32, 32),
                       'listing' :  (16, 16),
                      },
               validators = (('isNonEmptyFile', V_REQUIRED),
                             ('checkImageMaxSize', V_REQUIRED)),
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
#ATImageSchema.addField(urlUploadField)
finalizeATCTSchema(ATImageSchema)


class ATImage(ATCTFileContent, ATCTImageTransform):
    """An image, which can be referenced in documents or displayed in an album."""

    schema         =  ATImageSchema

    content_icon   = 'image_icon.gif'
    meta_type      = 'ATImage'
    portal_type    = 'Image'
    archetype_name = 'Image'
    immediate_view = 'image_view'
    default_view   = 'image_view'
    suppl_views    = ()
    _atct_newTypeFor = {'portal_type' : 'CMF Image', 'meta_type' : 'Portal Image'}
    typeDescription= 'An image, which can be referenced in documents or displayed in an album.'
    typeDescMsgId  = 'description_edit_image'
    assocMimetypes = ('image/*', )
    assocFileExt   = ('jpg', 'jpeg', 'png', 'gif', )
    cmf_edit_kws   = ('file', )

    __implements__ = ATCTFileContent.__implements__, IATImage
    
    actions = updateActions(ATCTFileContent, ATCTImageTransform.actions)

    security       = ClassSecurityInfo()

    security.declareProtected(ModifyPortalContent, 'setImage')
    def setImage(self, value, **kwargs):
        """Set id to uploaded id
        """
        self._setATCTFileContent(value, **kwargs)
        # set exif because rotation might screw up the exif data
        self.getEXIF(refresh=kwargs.get('refresh_exif', True))

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)
    
    def __str__(self):
        """cmf compatibility
        """
        return self.tag()
    
    security.declareProtected(View, 'getSize')
    def getSize(self, scale=None):
        field = self.getField('image')
        return field.getSize(self, scale=scale)
    
    security.declareProtected(View, 'getWidth')
    def getWidth(self, scale=None):
        return self.getSize(scale)[0]

    security.declareProtected(View, 'getHeight')
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

    def __bobo_traverse__(self, REQUEST, name, RESPONSE=None):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image
        
        return ATCTFileContent.__bobo_traverse__(self, REQUEST, name, RESPONSE=None)

registerATCT(ATImage, PROJECTNAME)
