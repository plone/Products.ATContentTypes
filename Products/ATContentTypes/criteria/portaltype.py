##############################################################################
#
# ATContentTypes http://sf.net/projects/collective/
# Archetypes reimplementation of the CMF core types
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003-2005 AT Content Types development team
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
__old_name__ = 'Products.ATContentTypes.types.criteria.ATPortalTypeCriterion'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo


from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import DisplayList

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import FIELD_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.selection import ATSelectionCriterion
from Products.ATContentTypes.config import TOOLNAME


ATPortalTypeCriterionSchema = ATSelectionCriterion.schema.copy()

val_widget = ATPortalTypeCriterionSchema['value'].widget
val_widget.description="One of the registered portal types."
val_widget.description_msgid="help_portal_type_criteria_value"
val_widget.label_msgid="label_portal_type_criteria_value"
ATPortalTypeCriterionSchema['value'].widget = val_widget

    
class ATPortalTypeCriterion(ATSelectionCriterion):
    """A portal_types criterion"""

    __implements__ = ATSelectionCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATPortalTypeCriterionSchema
    meta_type      = 'ATPortalTypeCriterion'
    archetype_name = 'Portal Types Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'portal types values'

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCurrentValues(self):
         """Return enabled portal types"""
         topic_tool = getToolByName(self, TOOLNAME)
         portal_types = topic_tool.getAllowedPortalTypes()
         portal_types = [t[1] or t[0] for t in portal_types]
         return DisplayList(zip(portal_types,portal_types))

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        if self.Value() is not '':
            result.append((self.Field(), self.Value()))

        return tuple(result)

registerCriterion(ATPortalTypeCriterion, FIELD_INDICES)
