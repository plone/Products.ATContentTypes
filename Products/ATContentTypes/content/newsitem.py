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
__old_name__ = 'Products.ATContentTypes.types.ATNewsItem'

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions

from Products.Archetypes.public import Schema
from Products.Archetypes.public import ImageField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import TextField
from Products.Archetypes.public import ImageWidget
from Products.Archetypes.public import RichWidget
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import RFC822Marshaller
from Products.Archetypes.public import AnnotationStorage

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import translateMimetypeAlias
from Products.ATContentTypes.content.base import updateActions
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.image import ATCTImageTransform
from Products.ATContentTypes.interfaces import IATNewsItem
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import relatedItemsField

from Products.validation.config import validation
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED

validation.register(MaxSizeValidator('checkNewsImageMaxSize',
                                             maxsize=zconf.ATNewsItem.max_size))

from Products.validation.validators.SupplValidators import MaxSizeValidator

ATNewsItemSchema = ATContentTypeSchema.copy() + Schema((
    TextField('text',
        required = True,
        searchable = True,
        primary = True,
        storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        #validators = ('isTidyHtml',),
        default_content_type = zconf.ATNewsItem.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATNewsItem.allowed_content_types,
        widget = RichWidget(
            description = "The body text of the document.",
            description_msgid = "help_body_text",
            label = "Body text",
            label_msgid = "label_body_text",
            rows = 25,
            i18n_domain = "plone",
            allow_file_upload = zconf.ATDocument.allow_document_upload)
        ),
    ImageField('image',
        required = False,
        torage = AnnotationStorage(migrate=True),
        languageIndependent = True,
        sizes= {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (200, 200),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
               },
        validators = (('isNonEmptyFile', V_REQUIRED),
                             ('checkNewsImageMaxSize', V_REQUIRED)),
        widget = ImageWidget(
            description = "Add an optional image by clicking the 'Browse' button. This will be shown in the news listing, and in the news item itself. It will automatically scale the picture you upload to a sensible size.",
            description_msgid = "help_image",
            label= "Image",
            label_msgid = "label_image",
            i18n_domain = "plone",
            show_content_type = False)
        ),
    StringField('imageCaption',
        required = False,
        searchable = True,
        widget = StringWidget(
            description = "A caption text for the image.",
            description_msgid = "help_image_caption",
            label = "Image caption",
            label_msgid = "label_image_caption",
            size = 40,
            i18n_domain = "plone")
        ),
    ), marshall=RFC822Marshaller()
    )
ATNewsItemSchema.addField(relatedItemsField)

class ATNewsItem(ATDocument, ATCTImageTransform):
    """An announcement that will show up on the news portlet and in the news listing."""

    schema         =  ATNewsItemSchema

    content_icon   = 'newsitem_icon.gif'
    meta_type      = 'ATNewsItem'
    portal_type    = 'News Item'
    archetype_name = 'News Item'
    immediate_view = 'newsitem_view'
    default_view   = 'newsitem_view'
    suppl_views    = ()
    _atct_newTypeFor = {'portal_type' : 'CMF News Item', 'meta_type' : 'News Item'}
    typeDescription = 'An announcement that will show up on the news portlet and in the news listing.'
    typeDescMsgId  = 'description_edit_news_item'
    assocMimetypes = ()
    assocFileExt   = ('news', )
    cmf_edit_kws   = ATDocument.cmf_edit_kws

    __implements__ = ATDocument.__implements__, IATNewsItem
    
    actions = updateActions(ATDocument, ATCTImageTransform.actions)

    security = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            kwargs['title'] = self.getImageCaption()
        return self.getField('image').tag(self, **kwargs)

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, text, description=None, text_format=None, **kwargs):
        if description is not None:
            self.setDescription(description)
        self.setText(text, mimetype=translateMimetypeAlias(text_format))
        self.update(**kwargs)
    
    def __bobo_traverse__(self, REQUEST, name, RESPONSE=None):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            if name == 'image':
                return field.getScale(self)
            else:
                scalename = name[len('image_'):]
                return field.getScale(self, scale=scalename)
        return ATCTDocument.__bobo_traverse__(self, REQUEST, name, RESPONSE=None)

registerATCT(ATNewsItem, PROJECTNAME)
