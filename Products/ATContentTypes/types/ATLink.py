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

import urlparse

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.types.ATContentType import registerATCT
from Products.ATContentTypes.types.ATContentType import ATCTContent
from Products.ATContentTypes.interfaces import IATLink
from Products.ATContentTypes.types.schemata import ATContentTypeSchema
from Products.ATContentTypes.types.schemata import relatedItemsField

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
ATLinkSchema.addField(relatedItemsField)

class ATLink(ATCTContent):
    """An Archetypes derived version of CMFDefault's Link"""

    schema         =  ATLinkSchema

    content_icon   = 'link_icon.gif'
    meta_type      = 'ATLink'
    portal_type    = 'ATLink'
    archetype_name = 'Link'
    immediate_view = 'link_view'
    default_view   = 'link_view'
    suppl_views    = ()
    _atct_newTypeFor = {'portal_type' : 'Link', 'meta_type' : 'Link'}
    typeDescription= ("A link is a pointer to a location on "
                      "the internet or intranet.\n"
                      "Enter the relevant details below, and press 'Save'.")
    typeDescMsgId  = 'description_edit_link_item'
    assocMimetypes = ()
    assocFileExt   = ('link', 'url', )
    cmf_edit_kws   = ('remote_url', )

    __implements__ = ATCTContent.__implements__, IATLink

    security       = ClassSecurityInfo()
    
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setRemoteUrl')
    def setRemoteUrl(self, value, **kwargs):
        """remute url mutator
        
        Use urlparse to sanify the url
        Also see http://plone.org/collector/3296
        """
        if value:
            value = urlparse.urlunparse(urlparse.urlparse(value))
        self.getField('remoteUrl').set(self, value, **kwargs)

    security.declareProtected(CMFCorePermissions.View, 'remote_url')
    def remote_url(self):
        """CMF compatibility method
        """
        return self.getRemoteUrl()

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, remote_url=None, **kwargs):
        if not remote_url:
            remote_url = kwargs.get('remote_url', None)
        self.update(remoteUrl = remote_url, **kwargs)

registerATCT(ATLink, PROJECTNAME)
