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

__author__  = 'Godefroid Chapelle'
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo


from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import DisplayList

from Products.ATContentTypes.types.criteria import registerCriterion
from Products.ATContentTypes.types.criteria import STRING_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATBaseCriterionSchema


ATPortalTypeCriterionSchema = ATBaseCriterionSchema + Schema((
    StringField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="getValue",
                mutator="setValue",
                default=None,
                widget=MultiSelectionWidget(
                    label="Value",
                    label_msgid="label_portal_type_criteria_value",
                    description="One of the registered portal types.",
                    description_msgid="help_portal_type_criteria_value",
                    i18n_domain="plone"),
                ),

    ))

class ATPortalTypeCriterion(ATBaseCriterion):
    """A portal_types criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATPortalTypeCriterionSchema
    meta_type      = 'ATPortalTypeCriterion'
    archetype_name = 'Portal Types Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'portal types values'

    security.declareProtected(CMFCorePermissions.View, 'getValue')
    def getValue(self):
        # refresh vocabulary
        types_tool = getToolByName(self, 'portal_types')
        portal_types = types_tool.listContentTypes()
        portal_types = [(portal_type, portal_type)
                        for portal_type in portal_types]
        self.schema['value'].vocabulary = DisplayList(list(portal_types))
        return self.getField('value').get(self)


    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        if self.getValue() is not '':
            result.append((self.Field(), self.getValue()))

        return tuple(result)

registerCriterion(ATPortalTypeCriterion, STRING_INDICES)
