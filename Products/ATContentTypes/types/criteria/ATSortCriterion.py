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


"""

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget

from Products.ATContentTypes.types.criteria import registerCriterion
from Products.ATContentTypes.types.criteria import SORT_INDICES
from Products.ATContentTypes.interfaces import IATTopicSortCriterion
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATBaseCriterionSchema

ATSortCriterionSchema = ATBaseCriterionSchema + Schema((
    BooleanField('reversed',
                required=0,
                mode="rw",
                write_permission=ChangeTopics,
                default=0,
                widget=BooleanWidget(
                    label="Reverse",
                    #label_msgid="label_criterion_field_name",
                    #description="Should not contain spaces, underscores or mixed case. "\
                    #            "Short Name is part of the item's web address.",
                    #description_msgid="help_criterion_field_name",
                    i18n_domain="plone"),
                ),

    ))

class ATSortCriterion(ATBaseCriterion):
    """A sort criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSortCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATSortCriterionSchema
    meta_type      = 'ATSortCriterion'
    archetype_name = 'AT Sort Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'Sort'

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = [('sort_on', self.Field())]

        if self.getReversed():
            result.append(('sort_order', 'reverse'))

        return tuple(result)

registerCriterion(ATSortCriterion, SORT_INDICES)
