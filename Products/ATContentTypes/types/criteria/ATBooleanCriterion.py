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

__author__  = 'Alec Mitchell'
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget

from Products.ATContentTypes.types.criteria import registerCriterion
from Products.ATContentTypes.types.criteria import FIELD_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATBaseCriterionSchema

ATBooleanCriterionSchema = ATBaseCriterionSchema + Schema((
    BooleanField('bool',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                default=None,
                widget=BooleanWidget(
                    label="Value",
                    label_msgid="label_boolean_criteria_bool",
                    description="True or false",
                    description_msgid="help_boolean_criteria_bool",
                    i18n_domain="plone"),
                ),
    ))

class ATBooleanCriterion(ATBaseCriterion):
    """A boolean criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATBooleanCriterionSchema
    meta_type      = 'ATBooleanCriterion'
    archetype_name = 'AT Boolean Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'Boolean (true/false)'

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []
        if self.getBool():
            value = [1,True,'1','True']
        else:
            value = [0,'',False,'0','False', None, (), [], {}]
        result.append((self.Field(), value))

        return tuple( result )

registerCriterion(ATBooleanCriterion, FIELD_INDICES)
