##############################################################################
#
# ATContentTypes http://sf.net/projects/collective/
# Archetypes reimplementation of the CMF core types
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003-2004 AT Content Types development team
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Topic:

$Id: ATReferenceCriterion.py,v 1.1.4.1 2005/03/08 01:03:45 tiran Exp $
"""

__author__  = 'Alec Mitchell'
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.types.criteria import registerCriterion
from Products.ATContentTypes.types.criteria import LIST_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.types.criteria.ATSelectionCriterion import ATSelectionCriterion

class ATReferenceCriterion(ATSelectionCriterion):
    """A reference criterion"""

    __implements__ = ATSelectionCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    meta_type      = 'ATReferenceCriterion'
    archetype_name = 'AT Reference Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'reference field select list'


    def getCurrentValues(self):
        catalog = getToolByName(self, 'portal_catalog')
        uid_cat = getToolByName(self, 'uid_catalog')
        options = catalog.uniqueValuesFor(self.Field())

        brains = uid_cat(UID=options, sort_on='Title')
        display_list = DisplayList([(b.UID, b.Title or b.id) for b in brains])

        return display_list

registerCriterion(ATReferenceCriterion, LIST_INDICES)