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

from DateTime import DateTime

from Products.Archetypes.public import BaseSchema
from Products.Archetypes.public import Schema
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import SelectionWidget

from Products.CMFCore import CMFCorePermissions

from Products.ATContentTypes import permission as ATCTPermissions
from Products.ATContentTypes.config import ENABLE_TEMPLATE_MIXIN
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

# for ATContentTypes we want to have the description in the edit view
# just like CMF
ATContentTypeBaseSchema = BaseSchema.copy()
ATContentTypeBaseSchema['id'].validators = ('isValidId',)
ATContentTypeBaseSchema['id'].searchable = True
ATContentTypeBaseSchema['description'].schemata = 'default'

relatedItemsField = ReferenceField('relatedItems',
        relationship = 'relatesTo', 
        multiValued = True,
        isMetadata = True,
        languageIndependent = False,
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

urlUploadField = StringField('urlUpload',
        required = False,
        mode = 'w', # write only field
        languageIndependent = True,
        validators = ('isURL',),
        write_permission = ATCTPermissions.UploadViaURL,
        widget = StringWidget(
            description="Upload a file from another server by url.",
            description_msgid = "help_upload_url",
            label = "Upload from server",
            label_msgid = "label_upload_url",
            i18n_domain = "plone",
            visible={'view' : 'hidden',
                     'edit' : 'hidden'},
            ),
        )

ATContentTypeSchema = ATContentTypeBaseSchema + Schema((
    # TemplateMixin
    StringField('layout',
                accessor="getLayout",
                mutator="setLayout",
                languageIndependent = True,
                write_permission=ATCTPermissions.ModifyViewTemplate,
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

__all__ = ('ATContentTypeSchema', 'relatedItemsField',)
