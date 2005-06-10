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
__old_name__ = 'Products.ATContentTypes.types.ATFavorite'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from ComputedAttribute import ComputedAttribute
from ZODB.POSException import ConflictError

from Products.Archetypes.debug import _zlogger
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.interfaces import IATFavorite
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

ATFavoriteSchema = ATContentTypeSchema.copy() + Schema((
    StringField('remoteUrl',
                required=True,
                searchable=True,
                accessor='_getRemoteUrl',
                primary=True,
                validators = (),
                widget = StringWidget(
                        description=("Add http:// to link outside the portal."),
                        description_msgid = "help_url",
                        label = "URL",
                        label_msgid = "label_url",
                        i18n_domain = "plone")),
    ))
finalizeATCTSchema(ATFavoriteSchema, moveDiscussion=False)

class ATFavorite(ATCTContent):
    """A placeholder item linking to a favorite object in the portal."""

    schema         =  ATFavoriteSchema

    content_icon   = 'favorite_icon.gif'
    meta_type      = 'ATFavorite'
    portal_type    = 'Favorite'
    archetype_name = 'Favorite'
    default_view   = 'favorite_view'
    immediate_view = 'favorite_view'
    suppl_views    = ()
    include_default_actions = False
    global_allow   = True
    filter_content_types  = True
    allowed_content_types = ()
    _atct_newTypeFor = {'portal_type' : 'CMF Favorite', 'meta_type' : 'Favorite'}
    typeDescription = 'A placeholder item linking to a favorite object in the portal.'
    typeDescMsgId  = 'description_edit_favorite'
    assocMimetypes = ()
    assocFileExt   = ('fav', )
    cmf_edit_kws   = ('remote_url',)

    __implements__ = ATCTContent.__implements__, IATFavorite

    security       = ClassSecurityInfo()

    # Support for preexisting api
    security.declareProtected(CMFCorePermissions.View, 'getRemoteUrl')
    def getRemoteUrl(self):
        """returns the remote URL of the Link
        """
        # need to check why this is different than PortalLink
        utool  = getToolByName(self, 'portal_url')
        remote = self._getRemoteUrl()
        if remote:
            if remote.startswith('/'):
                remote = remote[1:]
            return '%s/%s' % (utool(), remote)
        else:
            return utool()

    remote_url = ComputedAttribute(getRemoteUrl, 1)

    security.declareProtected(CMFCorePermissions.View, 'getIcon')
    def getIcon(self, relative_to_portal=0):
        """Instead of a static icon, like for Link objects, we want
        to display an icon based on what the Favorite links to.
        """
        obj =  self.getObject()
        if obj:
            return obj.getIcon(relative_to_portal)
        else:
            return 'favorite_broken_icon.gif'

    security.declareProtected(CMFCorePermissions.View, 'getObject')
    def getObject(self):
        """Return the actual object that the Favorite is
        linking to
        """
        utool  = getToolByName(self, 'portal_url')
        portal = utool.getPortalObject()
        remote = self._getRemoteUrl()
        try:
            obj = portal.restrictedTraverse(remote)
        except ConflictError:
            raise
        except (KeyError, AttributeError, Unauthorized, 'Unauthorized', ):
            _zlogger.log_exc()
            obj = None
        return obj

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, remote_url=None, **kwargs):
        if not remote_url:
            remote_url = kwargs.get('remote_url', None)
        self.update(remoteUrl = remote_url, **kwargs)

    security.declareProtected(CMFCorePermissions.View, 'get_size')
    def get_size(self):
        """Returns the size of the remote url."""
        return len(self.getRemoteUrl()) or 1

registerATCT(ATFavorite, PROJECTNAME)
