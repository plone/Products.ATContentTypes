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
"""Auto sorting / auto ordering support
"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

from ExtensionClass import Base
from Globals import InitializeClass
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from OFS.IOrderSupport import IOrderedContainer
from Products.Archetypes.OrderedBaseFolder import OrderedBaseFolder
from Products.Archetypes.OrderedBaseFolder import OrderedContainer
from Products.Archetypes.OrderedBaseFolder import IOrderedContainer
from Products.Archetypes.OrderedBaseFolder import IZopeOrderedContainer

from Interface import Interface
from Interface import Attribute

_marker = object()

class IAutoSortSupport(Interface):
    """Interface for auto sorting
    """

    _default_sort_key = Attribute('Sort key, default: Title')
    _default_sort_reverse = Attribute('Reverse, default: False')
    _default_sort_folderish_first = Attribute('Sort folderish first, default: True')
    # auto sort flag is required to make tpValues happy
    _default_sort_auto = Attribute('Enable auto, default: True')

    def setDefaultSorting(key, reverse=_marker):
        """Set default sorting key and direction.
        """

    def getDefaultSorting():
        """Get default sorting key and direction.

        Return sort_on attribute, reverse
        sort_on attribute is either an attribute or method name
        """

    def setSortFolderishFirst(value):
        """Set the value for sorting folderish objects before ordinary items
        """

    def getSortFolderishFirst():
        """Get the value for sorting folderish objects before ordinary items
        """

    def setSortReverse(value):
        """Set reverse sort setting
        """

    def getSortReverse():
        """Get reverse sort setting
        """

    def setSortAuto(value):
       """Set auto sort setting
       """

    def getSortAuto():
        """Get auto sort setting
        """

class IAutoOrderSupport(IAutoSortSupport, IOrderedContainer, IZopeOrderedContainer):
    """Interface for auto sorting and auto ordering
    """

    def autoOrderItems():
        """Auto order all containing items according to the settings
        """

    def moveObjectsByDelta(ids, delta, subset_ids=None, disable_auto_sort=True):
        """Move specified sub-objects by delta.

        Overwritten to disable auto sort
        """

    def manage_renameObject(id, new_id, REQUEST=None):
        """Rename a particular sub-object without changing its position.

        Overwritten to keep auto sort
        """

    def manage_afterAdd(item, container):
        """after add hook

        Overwritten to auto sort items
        """

# implementation

class AutoSortSupport(Base):

    __implements__ = (IAutoSortSupport, )

    security = ClassSecurityInfo()

    _default_sort_key = 'Title'
    _default_sort_reverse = False
    _default_sort_folderish_first = True
    _default_sort_auto = True

    security.declareProtected(ModifyPortalContent, 'setDefaultSorting')
    def setDefaultSorting(self, key, reverse=_marker):
        """Set default sorting key and direction.
        """
        self._default_sort_key = key
        if reverse is not _marker:
            self._default_sort_reverse = bool(reverse)

    security.declareProtected(View, 'getDefaultSorting')
    def getDefaultSorting(self):
        """Get default sorting key and direction.
        """
        return self._default_sort_key, self._default_sort_reverse

    security.declareProtected(ModifyPortalContent, 'setSortFolderishFirst')
    def setSortFolderishFirst(self, value):
        """Set the value for sorting folderish objects before ordinary items
        """
        self._default_sort_folderish_first = bool(value)

    security.declareProtected(View, 'getSortFolderishFirst')
    def getSortFolderishFirst(self):
        """Get the value for sorting folderish objects before ordinary items
        """
        return self._default_sort_folderish_first

    security.declareProtected(ModifyPortalContent, 'setSortReverse')
    def setSortReverse(self, value):
        """Set reverse sort setting
        """
        self._default_sort_reverse = bool(value)

    security.declareProtected(View, 'getSortReverse')
    def getSortReverse(self):
        """Get reverse sort setting
        """
        return self._default_sort_reverse

    security.declareProtected(ModifyPortalContent, 'setSortAuto')
    def setSortAuto(self, value):
       """Set auto sort setting
       """
       self._default_sort_auto = bool(value)

    security.declareProtected(View, 'getSortAuto')
    def getSortAuto(self):
        """Get auto sort setting
        """
        return self._default_sort_auto

InitializeClass(AutoSortSupport)


class AutoOrderSupport(AutoSortSupport, OrderedContainer):

    __implements__ = (IAutoOrderSupport, )

    security = ClassSecurityInfo()

    security.declarePrivate('autoOrderItems')
    def autoOrderItems():
        """Auto order all containing items according to the settings
        """
        if not self.getSortAuto():
            return
        key, reverse = self.getDefaultSorting()
        folderish_first = self.getSortFolderishFirst()

        self.orderObjects(key, reverse)
        # TODO: folderish first is missing, use the catalog to resort it!

    security.declareProtected(ModifyPortalContent, 'moveObject')
    def moveObject(self, id, position):
        obj_idx  = self.getObjectPosition(id)
        if obj_idx == position:
            return None
        elif position < 0:
            position = 0

        metadata = list(self._objects)
        obj_meta = metadata.pop(obj_idx)
        metadata.insert(position, obj_meta)
        self._objects = tuple(metadata)

    def moveObjectsByDelta(self, ids, delta, subset_ids=None, disable_auto_sort=True):
        """Move specified sub-objects by delta.

        Overwritten to disable auto sort
        """
        OrderedContainer.moveObjectsByDelta(self, ids, delta, subset_ids=subset_ids)
        self.setSortAuto(disable_auto_sort)

    def manage_renameObject(self, id, new_id, REQUEST=None):
        """Rename a particular sub-object without changing its position.

        Overwritten to keep auto sort
        """
        old_position = self.getObjectPosition(id)
        old_sort_auto = self.getSortAuto()
        result = OrderedBaseFolder.manage_renameObject(self, id, new_id, REQUEST)
        self.moveObjectToPosition(new_id, old_position)
        putils = getToolByName(self, 'plone_utils')
        putils.reindexOnReorder(self)
        self.setSortAuto(old_sort_auto)
        return result

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """after add hook

        Overwritten to auto sort items
        CAUTION: Make sure that you call this method explictly!
        """
        # XXX: disabled
        # we need a proper event system to make it work
        #if item.aq_inner.aq_parent == self:
        #    self.autoOrderItems()

InitializeClass(AutoOrderSupport)
