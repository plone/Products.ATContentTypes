#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
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

from Products.Archetypes.public import *
from DateTime import DateTime
import Products.ATContentTypes.Validators
from Products.ATContentTypes.Permissions import ChangeEvents
from Products.ATContentTypes.config import *
from Products.ATContentTypes.ConstrainTypesMixin import ConstrainTypesMixinSchema
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from Products.validation.validators.SupplValidators import MaxSizeValidator

# for ATContentTypes we want to have the description in the edit view
# just like CMF
ATContentTypeBaseSchema = BaseSchema.copy()
ATContentTypeBaseSchema['id'].validators = ('isValidId',)
ATContentTypeBaseSchema['description'].isMetadata = False
ATContentTypeBaseSchema['description'].schemata = 'default'

RelatedField = ReferenceField('relatedItems',
        relationship = 'relatesTo', 
        multiValued = True,
        isMetadata = True,
        write_permission = CMFCorePermissions.ModifyPortalContent,
        widget = ReferenceBrowserWidget(
            allow_search = True,
            allow_browse = True,
            show_indexes = False,
            force_close_on_insert = True,

            label = "Related items",
            label_msgid = "label_related_items",
            description = "Select one or more related items",
            description_msgid = "help_related_items",
            i18n_domain = "plone",
            
            visible={'view' : 'hidden',
                     #'edit' : ENABLE_RELATED_ITEMS and 'visible' or 'hidden'
                    },
            )
        )

ATContentTypeSchema = ATContentTypeBaseSchema + Schema((
    # TemplateMixin
    StringField('layout',
                accessor="getLayout",
                mutator="setLayout",
                write_permission=TEMPLATE_MIXIN_PERMISSION,
                default_method="getDefaultLayout",
                vocabulary="_voc_templates",
                #enforceVocabulary=True,
                widget=SelectionWidget(
                    description="Choose a template that will be used for viewing this item.",
                    description_msgid = "help_template_mixin",
                    label = "View template",
                    label_msgid = "label_template_mixin",
                    i18n_domain = "plone",
                    visible={'view' : 'hidden',
                             'edit' : ENABLE_TEMPLATE_MIXIN and 'visible' or 'hidden'},
    )),
    ))

###
# AT Content Type Document
###
ATDocumentSchema = ATContentTypeSchema.copy() + Schema((
    TextField('text',
              required=True,
              searchable=True,
              primary=True,
              validators = ('isTidyHtmlWithCleanup',),
              #validators = ('isTidyHtml',),
              default_content_type = ATDOCUMENT_CONTENT_TYPE,
              default_output_type = 'text/html',
              allowable_content_types = ('text/structured',
                                         'text/restructured',
                                         'text/html',
                                         'text/plain',
                                         'text/plain-pre',
                                         'text/python-source',),
              widget = RichWidget(
                        description = "The body text of the document.",
                        description_msgid = "help_body_text",
                        label = "Body text",
                        label_msgid = "label_body_text",
                        rows = 25,
                        i18n_domain = "plone")),
    ), marshall=RFC822Marshaller()
    )
ATDocumentSchema.addField(RelatedField)

###
# AT Content Type Event
###

ATEventSchema = ATContentTypeSchema.copy() + Schema((
    StringField('location',
                searchable=True,
                write_permission = ChangeEvents,
                widget = StringWidget(
                    description = "Enter the location where the event will take place.",
                    description_msgid = "help_event_location",
                    label = "Event Location",
                    label_msgid = "label_event_location",
                    i18n_domain = "plone")),

    TextField('text',
              required=False,
              searchable=True,
              primary=True,
              validators = ('isTidyHtmlWithCleanup',),
              #validators = ('isTidyHtml',),
              default_content_type = ATDOCUMENT_CONTENT_TYPE,
              default_output_type = 'text/html',
              allowable_content_types = ('text/structured',
                                         'text/restructured',
                                         'text/html',
                                         'text/plain',
                                         'text/plain-pre',),
              widget = RichWidget(
                        description = "The full text of the event announcement.",
                        description_msgid = "help_body_text",
                        label = "Body text",
                        label_msgid = "label_body_text",
                        rows = 25,
                        i18n_domain = "plone")),

    LinesField('attendees',
               languageIndependent=True,
               searchable=True,
               write_permission=ChangeEvents,
               widget=LinesWidget(label="Attendees",
                                  label_msgid="label_event_attendees",
                                  description=("People who are attending "
                                               "the event."),
                                  description_msgid="help_event_attendees",
                                  i18n_domain="plone")),

    LinesField('eventType',
               required=True,
               searchable=True,
               write_permission = ChangeEvents,
               vocabulary = 'getEventTypes',
               languageIndependent=True,
               widget = MultiSelectionWidget(
                        size = 6,
                        description=("Select the type of event. "
                                     "Multiple event types possible."),
                        description_msgid = "help_event_type",
                        label = "Event Type",
                        label_msgid = "label_event_type",
                        i18n_domain = "plone")),

    StringField('eventUrl',
                required=False,
                searchable=True,
                accessor='event_url',
                write_permission = ChangeEvents,
                validators = ('isURL',),
                widget = StringWidget(
                        description = ("Enter an optional web address of a page "
                                       "containing more info about the event, if"
                                       " required."),
                        description_msgid = "help_url",
                        label = "Event URL",
                        label_msgid = "label_url",
                        i18n_domain = "plone")),

    DateTimeField('startDate',
                  required=True,
                  searchable=True,
                  accessor='start',
                  write_permission = ChangeEvents,
                  default_method=DateTime,
                  languageIndependent=True,
                  widget = CalendarWidget(
                        description=("Enter the starting date and time, or click "
                                     "the calendar icon and select it. "),
                        description_msgid = "help_event_start",
                        label="Event Starts",
                        label_msgid = "label_event_start",
                        i18n_domain = "plone")),

    DateTimeField('endDate',
                  required=True,
                  searchable=True,
                  accessor='end',
                  write_permission = ChangeEvents,
                  default_method=DateTime,
                  languageIndependent=True,
                  widget = CalendarWidget(
                        description=("Enter the ending date and time, or click "
                                     "the calendar icon and select it. "),
                        description_msgid = "help_event_end",
                        label = "Event Ends",
                        label_msgid = "label_event_end",
                        i18n_domain = "plone")),

    StringField('contactName',
                required=False,
                searchable=True,
                accessor='contact_name',
                write_permission = ChangeEvents,
                widget = StringWidget(
                        description=("Enter a contact person or "
                                     "organization for the event."),
                        description_msgid = "help_contact_name",
                        label = "Contact Name",
                        label_msgid = "label_contact_name",
                        i18n_domain = "plone")),

    StringField('contactEmail',
                required=False,
                searchable=True,
                accessor='contact_email',
                write_permission = ChangeEvents,
                validators = ('isEmail',),
                widget = StringWidget(
                        description = ("Enter an e-mail address to use for "
                                       "information regarding the event."),
                        description_msgid = "help_contact_email",
                        label = "Contact E-mail",
                        label_msgid = "label_contact_email",
                        i18n_domain = "plone")),
    StringField('contactPhone',
                required=False,
                searchable=True,
                accessor='contact_phone',
                write_permission = ChangeEvents,
                validators = ('isInternationalPhoneNumber',),
                widget = StringWidget(
                        description = ("Enter the phone number to call for "
                                       "information and/or booking."),
                        description_msgid = "help_contact_phone",
                        label = "Contact Phone",
                        label_msgid = "label_contact_phone",
                        i18n_domain = "plone")),
    ), marshall = RFC822Marshaller()
    )
ATEventSchema.addField(RelatedField)

###
# AT Content Type Favorite
###
ATFavoriteSchema = ATContentTypeSchema.copy() + Schema((
    StringField('remoteUrl',
                required=True,
                searchable=True,
                accessor='_getRemoteUrl',
                primary=True,
                validators = (),
                widget = StringWidget(
                        description=("The address of the location. Prefix is "
                                     "optional; if not provided, the link will be relative."),
                        description_msgid = "help_url",
                        label = "URL",
                        label_msgid = "label_url",
                        i18n_domain = "plone")),
    ))
ATFavoriteSchema.addField(RelatedField)

###
# AT Content Type File
###

ATFileSchema = ATContentTypeSchema.copy() + Schema((
    FileField('file',
              required=True,
              primary=True,
              languageIndependent=True,
              validators = MaxSizeValidator('checkFileMaxSize',
                                            maxsize=MAX_FILE_SIZE),
              widget = FileWidget(
                        #description = "Select the file to be added by clicking the 'Browse' button.",
                        #description_msgid = "help_file",
                        description = "",
                        label= "File",
                        label_msgid = "label_file",
                        i18n_domain = "plone",
                        show_content_type = False,)),
    ), marshall=PrimaryFieldMarshaller()
    )
ATFileSchema.addField(RelatedField)

ATExtFileSchema = ATFileSchema.copy()
# XXX ATExtFileSchema['file'].storage = ExternalStorage(prefix='atct', archive=False)

###
# AT Content Type Folder
###

ATFolderSchema      = ATContentTypeSchema.copy()
ATBTreeFolderSchema = ATContentTypeSchema.copy()

if ENABLE_CONSTRAIN_TYPES_MIXIN:
    ATFolderSchema      = ATFolderSchema + ConstrainTypesMixinSchema
    ATBTreeFolderSchema = ATBTreeFolderSchema + ConstrainTypesMixinSchema

ATFolderSchema.addField(RelatedField)
ATBTreeFolderSchema.addField(RelatedField)

###
# AT Content Type Image
###

ATImageSchema = ATContentTypeSchema.copy() + Schema((
    ImageField('image',
               required=True,
               primary=True,
               languageIndependent=True,
               #swallowResizeExceptions=True,
               sizes= {'preview' : (400, 400),
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
ATImageSchema.addField(RelatedField)

ATExtImageSchema = ATImageSchema.copy()
# XXX ATExtImageSchema['image'].storage = ExternalStorage(prefix='atct', archive=False)

###
# AT Content Type Link
###
ATLinkSchema = ATContentTypeSchema.copy() + Schema((
    StringField('remoteUrl',
                required=True,
                searchable=True,
                primary=True,
                validators = ('isURL',),
                widget = StringWidget(
                        description=("The address of the location. Prefix is "
                                     "optional; if not provided, the link will be relative."),
                        description_msgid = "help_url",
                        label = "URL",
                        label_msgid = "label_url",
                        i18n_domain = "plone")),
    ))
ATLinkSchema.addField(RelatedField)

###
# AT Content Type News Item
###
ATNewsItemSchema = ATContentTypeSchema.copy() + Schema((
    TextField('text',
              required=True,
              searchable=True,
              primary=True,
              validators = ('isTidyHtmlWithCleanup',),
              #validators = ('isTidyHtml',),
              default_content_type = ATDOCUMENT_CONTENT_TYPE,
              default_output_type = 'text/html',
              allowable_content_types = ('text/structured',
                                         'text/restructured',
                                         'text/html',
                                         'text/plain',
                                         ),
              widget = RichWidget(
                        description = "The body text of the document.",
                        description_msgid = "help_body_text",
                        label = "Body text",
                        label_msgid = "label_body_text",
                        rows = 25,
                        i18n_domain = "plone")),
    ImageField('image',
               required=False,
               languageIndependent=True,
               sizes= {'preview' : (400, 400),
                       'thumb'   : (128, 128),
                       'tile'    :  (64, 64),
                       'icon'    :  (32, 32),
                       'listing' :  (16, 16),
                      },
               validators = MaxSizeValidator('checkFileMaxSize',
                                             maxsize=MAX_IMAGE_SIZE),
               widget = ImageWidget(
                        description = "Add an optional image by clicking the 'Browse' button. This will be shown in the news listing, and in the news item itself. It will automatically scale the picture you upload to a sensible size.",
                        description_msgid = "help_image",
                        label= "Image",
                        label_msgid = "label_image",
                        i18n_domain = "plone",
                        show_content_type = False,)),
    TextField('imageCaption',
              required=False,
              searchable=True,
              widget = StringWidget(
                        description = "A caption text for the image.",
                        description_msgid = "help_image_caption",
                        label = "Image caption",
                        label_msgid = "label_image_caption",
                        size = 40,
                        i18n_domain = "plone")),
    ), marshall=RFC822Marshaller()
    )
ATNewsItemSchema.addField(RelatedField)

###
# AT Content Type Topic
###
ATTopicSchema = ATContentTypeSchema.copy() + Schema((
    BooleanField('acquireCriteria',
                required=False,
                mode="rw",
                default=False,
                widget=BooleanWidget(
                        label="Inherit Criteria",
                        label_msgid="label_inherit_criteria",
                        description=("Toggles inheritance of criteria. For example, if you "
                                     "have specified that only items from the last three days "
                                     "should be shown in a Topic above the current one, this "
                                     "Topic will also have that criterion automatically."),
                        description_msgid="help_inherit_criteria",
                        i18n_domain = "plone"),
                ),
    BooleanField('limitNumber',
                required=False,
                mode="rw",
                default=False,
                widget=BooleanWidget(
                        label="Limit Number of Items",
                        label_msgid="label_limit_number",
                        description=("Toggles limitation of number of items displayed. "
                                     "If selected, only the first 'Number of Items' "
                                     "will be displayed."),
                        description_msgid="help_limit_number",
                        i18n_domain = "plone"),
                ),
    IntegerField('itemCount',
                required=False,
                mode="rw",
                default=0,
                widget=IntegerWidget(
                        label="Number of Items",
                        label_msgid="label_item_count",
                        description="If 'Limit Number of Items' is "
                        "selected, only the first "
                        "'Number of Items' will be "
                        "displayed ",
                        description_msgid="help_item_count",
                        i18n_domain = "plone"),
                 ),
    ))
ATTopicSchema.addField(RelatedField)
