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

$Id: ATSelectionCriterion.py,v 1.1.4.2 2005/03/08 01:08:24 tiran Exp $
"""

__author__  = 'Alec Mitchell'
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import MultiSelectionWidget

from Products.ATContentTypes.types.criteria import registerCriterion
from Products.ATContentTypes.types.criteria import LIST_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATBaseCriterionSchema

from types import StringType

ATSelectionCriterionSchema = ATBaseCriterionSchema + Schema((
    LinesField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default=[],
                vocabulary="getCurrentValues",
                widget=MultiSelectionWidget(
                    label="Value",
                    label_msgid="label_selection_criteria_value",
                    description="Existing values.",
                    description_msgid="help_selection_criteria_value",
                    i18n_domain="plone"),
                ),
    ))

class ATSelectionCriterion(ATBaseCriterion):
    """A selection criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATSelectionCriterionSchema
    meta_type      = 'ATSelectionCriterion'
    archetype_name = 'Selection Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'select list'


    def getCurrentValues(self):
        catalog = getToolByName(self, 'portal_catalog')
        options = catalog.uniqueValuesFor(self.Field())
        # AT is currently broken, and does not accept ints as
        # DisplayList keys though it is supposed to (it should
        # probably accept Booleans as well) so we only accept strings
        # for now
        options = [o for o in options if type(o) is StringType]
        return options

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        if self.Value() is not '':
            result.append((self.Field(), self.Value()))

        return tuple( result )

registerCriterion(ATSelectionCriterion, LIST_INDICES)
