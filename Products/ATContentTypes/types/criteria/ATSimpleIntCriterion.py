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
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import IntegerWidget

from Products.ATContentTypes.types.criteria import registerCriterion
from Products.ATContentTypes.types.criteria import STRING_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATBaseCriterionSchema

ATSimpleIntCriterionSchema = ATBaseCriterionSchema + Schema((
    IntegerField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default=None,
                widget=IntegerWidget(
                    label="Value",
                    label_msgid="label_int_criteria_value",
                    description="An integer number.",
                    description_msgid="help_int_criteria_value",
                    i18n_domain="plone"),
                ),

    ))

class ATSimpleIntCriterion(ATBaseCriterion):
    """A simple int criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATSimpleIntCriterionSchema
    meta_type      = 'ATSimpleIntCriterion'
    archetype_name = 'Simple Int Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'exact integer value'

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        if self.Value() or self.Value() == 0:
            result.append((self.Field(), self.Value()))

        return tuple(result)

registerCriterion(ATSimpleIntCriterion, STRING_INDICES)
