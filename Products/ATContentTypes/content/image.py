from zope.interface import implements

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from ComputedAttribute import ComputedAttribute

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import ImageField
from Products.Archetypes.atapi import ImageWidget
from Products.Archetypes.atapi import PrimaryFieldMarshaller
from Products.Archetypes.atapi import AnnotationStorage

from Products.ATContentTypes.config import MAX_FILE_SIZE
from Products.ATContentTypes.config import MAX_IMAGE_DIMENSION
from Products.ATContentTypes.config import PIL_CONFIG_QUALITY
from Products.ATContentTypes.config import PIL_CONFIG_RESIZE_ALGO
from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.config import SWALLOW_IMAGE_RESIZE_EXCEPTIONS
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.interfaces import IATImage as z2IATImage
from Products.ATContentTypes.interface import IATImage

from Products.ATContentTypes.lib.imagetransform import ATCTImageTransform

from Products.ATContentTypes import ATCTMessageFactory as _

from Products.validation.config import validation
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED

validation.register(MaxSizeValidator('checkImageMaxSize',
                                     maxsize=MAX_FILE_SIZE))


ATImageSchema = ATContentTypeSchema.copy() + Schema((
    ImageField('image',
               required=True,
               primary=True,
               languageIndependent=True,
               storage = AnnotationStorage(migrate=True),
               swallowResizeExceptions = SWALLOW_IMAGE_RESIZE_EXCEPTIONS,
               pil_quality = PIL_CONFIG_QUALITY,
               pil_resize_algo = PIL_CONFIG_RESIZE_ALGO,
               max_size = MAX_IMAGE_DIMENSION,
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
                        description = '',
                        label= _(u'label_image', default=u'Image'),
                        show_content_type = False,)),

    ), marshall=PrimaryFieldMarshaller()
    )

# Title is pulled from the file name if we don't specify anything,
# so it's not strictly required, unlike in the rest of ATCT.
ATImageSchema['title'].required = False

finalizeATCTSchema(ATImageSchema)


class ATImage(ATCTFileContent, ATCTImageTransform):
    """An image, which can be referenced in documents."""

    schema         =  ATImageSchema

    portal_type    = 'Image'
    archetype_name = 'Image'
    _atct_newTypeFor = {'portal_type' : 'CMF Image', 'meta_type' : 'Portal Image'}
    assocMimetypes = ('image/*', )
    assocFileExt   = ('jpg', 'jpeg', 'png', 'gif', )
    cmf_edit_kws   = ('file', )

    implements(IATImage)

    security       = ClassSecurityInfo()

    def exportImage(self, format, width, height):
        return '',''

    security.declareProtected(ModifyPortalContent, 'setImage')
    def setImage(self, value, refresh_exif=True, **kwargs):
        """Set id to uploaded id
        """
        # set exif first because rotation might screw up the exif data
        # the exif methods can handle str, Pdata, OFSImage and file
        # like objects
        self.getEXIF(value, refresh=refresh_exif)
        self._setATCTFileContent(value, **kwargs)

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

    def __str__(self):
        """cmf compatibility
        """
        return self.tag()

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """ZMI / Plone get size method

        BBB: ImageField.get_size() returns the size of the original image + all
        scales but we want only the size of the original image.
        """
        img = self.getImage()
        if not getattr(aq_base(img), 'get_size', False):
            return 0
        return img.get_size()

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


registerATCT(ATImage, PROJECTNAME)
