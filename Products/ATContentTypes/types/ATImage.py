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
__author__  = ''
__docformat__ = 'restructuredtext'

from cgi import escape

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from ComputedAttribute import ComputedAttribute
from OFS.Image import Image
from cStringIO import StringIO

from Products.Archetypes.public import Schema
from Products.Archetypes.public import ImageField
from Products.Archetypes.public import ImageWidget
from Products.Archetypes.public import PrimaryFieldMarshaller
from Products.Archetypes.Storage import Storage

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.config import MAX_IMAGE_SIZE
from Products.ATContentTypes.config import HAS_EXT_STORAGE
from Products.ATContentTypes.config import EXT_STORAGE_ENABLE
from Products.ATContentTypes.types.ATContentType import registerATCT
from Products.ATContentTypes.types.ATContentType import ATCTFileContent
from Products.ATContentTypes.types.ATContentType import cleanupFilename
from Products.ATContentTypes.types.ATContentType import updateActions
from Products.ATContentTypes.interfaces import IATImage
from Products.ATContentTypes.types.schemata import ATContentTypeSchema
from Products.ATContentTypes.types.schemata import relatedItemsField
from Products.ATContentTypes.lib import exif
from OFS.Image import Image as OFSImage

from Products.validation.validators.SupplValidators import MaxSizeValidator

# the following code is based on the rotation code of Photo
try:
    import PIL.Image
    HAS_PIL=True
except ImportError:
    HAS_PIL=False
else:
    from PIL.Image import NEAREST
    from PIL.Image import BILINEAR
    from PIL.Image import BICUBIC
    from PIL.Image import ANTIALIAS

    # NEAREST (use nearest neighbour)
    # BILINEAR (linear interpolation in a 2x2 environment)
    # BICUBIC (cubic spline interpolation in a 4x4 environment)
    # ANTIALIAS (a high-quality downsampling filter)
    # antialiasing is the best algorithm for shrinking pictures
    RESIZING_ALGO = ANTIALIAS
    # PIL doesn't support antialiasing for rotating!
    ROTATING_ALGO = BICUBIC

# transpose constants, taken from PIL.Image to maintain compatibilty
FLIP_LEFT_RIGHT = 0
FLIP_TOP_BOTTOM = 1
ROTATE_90 = 2
ROTATE_180 = 3
ROTATE_270 = 4

DEFAULT_QUALITY=100

TRANSPOSE_MAP = {
    FLIP_LEFT_RIGHT : "Flip around vertical axis",
    FLIP_TOP_BOTTOM : "Flip around horizontal axis",
    ROTATE_270      : "Rotate 90 clockwise",
    ROTATE_180      : "Rotate 180",
    ROTATE_90       : "Rotate 90 counterclockwise",
   }
   
AUTO_ROTATE_MAP = {
    0   : None,
    90  : ROTATE_270,
    180 : ROTATE_180,
    270 : ROTATE_90,
    }

if HAS_EXT_STORAGE:
    from Products.ExternalStorage.ExternalStorage import ExternalStorage
else:
    class ExternalStorage(Storage):
        """Dummy storage
        """
        def __init__(self, *args, **kwargs):
            pass

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
imageField = ATExtImageSchema['image']
imageField.storage = ExternalStorage(prefix = 'atct',
                                     archive = False,
                                     rename = True)
# re-register storage layer
imageField.registerLayer('storage', imageField.storage)


class ATImage(ATCTFileContent):
    """An Archetypes derived version of CMFDefault's Image"""

    schema         =  ATImageSchema

    content_icon   = 'image_icon.gif'
    meta_type      = 'ATImage'
    portal_type    = 'Image'
    archetype_name = 'Image'
    immediate_view = 'image_view'
    default_view   = 'image_view'
    suppl_views    = ()
    _atct_newTypeFor = {'portal_type' : 'CMF Image', 'meta_type' : 'Portal Image'}
    typeDescription= ("Using this form, you can enter details about the image, \n"
                      "and upload an image if required.")
    typeDescMsgId  = 'description_edit_image'
    assocMimetypes = ('image/*', )
    assocFileExt   = ('jpg', 'jpeg', 'png', 'gif', )
    cmf_edit_kws   = ('file', )

    __implements__ = ATCTFileContent.__implements__, IATImage
    
    actions = updateActions(ATCTFileContent, (
        {
        'id'          : 'transform',
        'name'        : 'Transform',
        'action'      : 'string:${object_url}/atct_image_transform',
        'permissions' : (CMFCorePermissions.ModifyPortalContent,),
        'condition'   : 'object/hasPIL',
         },
        ))

    security       = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setImage')
    def setImage(self, value, **kwargs):
        """Set id to uploaded id
        """
        self._setATCTFileContent(value, **kwargs)
        # set exif because rotation might screw up the exif data
        self.getEXIF(refresh=kwargs.get('refresh_exif', True))

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

    security.declarePrivate('getImageAsFile')
    def getImageAsFile(self, scale=None):
        """Get the img as file like object
        """
        f = self.getField('image')
        img = f.getScale(self, scale)
        # img.data contains the image as string or Pdata chain
        if isinstance(img, OFSImage):
            data = str(img.data)
        else:
            data = str(img)
        if data:
            return StringIO(data)
        else:
            return None
    
    security.declarePrivate('cmf_edit')
    def cmf_edit(self, precondition='', file=None, title=None):
        if file is not None:
            self.setImage(file)
        if title is not None:
            self.setTitle(title)
        self.reindexObject()

    # image related code like exif and rotation
    # partly based on CMFPhoto
    
    security.declareProtected(CMFCorePermissions.View, 'getEXIF')
    def getEXIF(self, refresh=False):
        """Get the exif informations of the file
        
        The information is cached in _v_image_exif
        
        XXX check if PIL removes EXIF when rescaling with orig_size
        XXX remove 'JPEGThumbnail' and 'TIFFThumbnail'?
        """
        cache = '_image_exif'
        
        if refresh:
            setattr(self, cache, None)
        
        exif_data = getattr(self, cache, None)
        
        if exif_data is None or not isinstance(exif_data, dict):
            img = self.getImageAsFile(scale=None)
            if img:
                exif_data = exif.process_file(img, debug=False, noclose=True)
                # remove some unwanted elements lik thumb nails
                for key in ('JPEGThumbnail', 'TIFFThumbnail'):
                    if key in exif_data:
                        del exif_data[key]
        
        setattr(self, cache, exif_data)
        
        if not exif_data:
            # alawys return a dict
            exif_data = {}
        return exif_data

    security.declareProtected(CMFCorePermissions.View, 'getEXIFOrientation')
    def getEXIFOrientation(self):
        """Get the rotation and mirror orientation from the EXIF data
        
        Some cameras are storing the informations about rotation and mirror in
        the exif data. It can be used for autorotation.
        """
        exif = self.getEXIF()
        mirror = 0
        rotation = 0
        code = exif.get('Image Orientation', None)
        
        if code is None:
            return (mirror, rotation)
        
        try:
            code = int(code)
        except ValueError:
            return (mirror, rotation)
            
        if code in (2, 4, 5, 7):
            mirror = 1
        if code in (1, 2):
            rotation = 0
        elif code in (3, 4):
            rotation = 180
        elif code in (5, 6):
            rotation = 90
        elif code in (7, 8):
            rotation = 270
       
        return (mirror, rotation)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 
                              'transformImage')
    def transformImage(self, method, REQUEST=None):
        """
        Transform an Image:
            FLIP_LEFT_RIGHT
            FLIP_TOP_BOTTOM
            ROTATE_90 (rotate counterclockwise)
            ROTATE_180
            ROTATE_270 (rotate clockwise)
        """ 
        method = int(method)
        if method not in TRANSPOSE_MAP:
            raise RuntimeError, "Unknown method %s" % method
        
        target = self.absolute_url() + '/atct_image_transform'
        
        if not HAS_PIL:
            # XXX should add a note for the user
            if REQUEST:
                REQUEST.RESPONSE.redirect(target)
        
        image = self.getImageAsFile()
        image2 = StringIO()
        
        if image:
            img = PIL.Image.open(image)
            del image
            fmt = img.format
            img = img.transpose(method)
            img.save(image2, fmt, quality=DEFAULT_QUALITY)
            
            field = self.getField('image')
            mimetype = field.getContentType(self)
            filename = field.getFilename(self)
            
            # because AT tries to get mimetype and filename from a file like
            # object by attribute access I'm passing a string along
            self.setImage(image2.getvalue(), mimetype=mimetype,
                          filename=filename, refresh_exif=False)
        
        if REQUEST:
             REQUEST.RESPONSE.redirect(target)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 
                              'autoTransformImage')
    def autoTransformImage(self, REQUEST=None):
        """Auto transform image according to EXIF data
        
        XXX isn't using mirror
        """
        target = self.absolute_url() + '/atct_image_transform'
        mirror, rotation = self.getEXIFOrientation()
        if rotation:
            transform = AUTO_ROTATE_MAP.get(rotation)
            if transform:
                self.transformImage(transform)
        if REQUEST:
             REQUEST.RESPONSE.redirect(target)
             
    security.declareProtected(CMFCorePermissions.View, 'getTransformMap')
    def getTransformMap(self):
        """Get map for tranforming the image
        """
        return [{'name' : n, 'value' : v} for v, n in TRANSPOSE_MAP.items()]
    
    security.declareProtected(CMFCorePermissions.View, 'hasPIL')
    def hasPIL(self):
        """Is PIL installed?
        """
        return HAS_PIL

registerATCT(ATImage, PROJECTNAME)


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

# XXX use at own risk
if HAS_EXT_STORAGE and EXT_STORAGE_ENABLE:
    registerATCT(ATExtImage, PROJECTNAME)
