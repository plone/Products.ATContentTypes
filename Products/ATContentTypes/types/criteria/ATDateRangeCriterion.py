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

$Id: ATDateRangeCriterion.py,v 1.1.4.1 2005/03/08 01:03:45 tiran Exp $
"""

__author__  = 'Alec Mitchell'
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema
from Products.Archetypes.public import DateTimeField
from Products.Archetypes.public import CalendarWidget

from Products.ATContentTypes.types.criteria import registerCriterion
from Products.ATContentTypes.types.criteria import DATE_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATBaseCriterionSchema

RELEVANT_INDICES=list(DATE_INDICES)
RELEVANT_INDICES.remove('DateRangeIndex')
RELEVANT_INDICES = tuple(RELEVANT_INDICES)

ATDateRangeCriterionSchema = ATBaseCriterionSchema + Schema((
    DateTimeField('start',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                default=None,
                widget=CalendarWidget(
                    label="Start Date",
                    label_msgid="label_date_range_criteria_start",
                    description="The beginning of the date range to search",
                    description_msgid="help_date_range_criteria_start",
                    i18n_domain="plone"),
                ),
    DateTimeField('end',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                default=None,
                widget=CalendarWidget(
                    label="End Date",
                    label_msgid="label_date_range_criteria_end",
                    description="The beginning of the date range to search",
                    description_msgid="help_date_range_criteria_end",
                    i18n_domain="plone"),
                ),
    ))

class ATDateRangeCriterion(ATBaseCriterion):
    """A date range criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATDateRangeCriterionSchema
    meta_type      = 'ATDateRangeCriterion'
    archetype_name = 'AT Date Range Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'date range value'

    security.declareProtected(CMFCorePermissions.View, 'getValue')
    def Value(self):
        return (self.getStart(), self.getEnd())

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        field = self.Field()
        value = self.Value()

        return ( ( field, {'query': value, 'range': 'min:max'} ), )

registerCriterion(ATDateRangeCriterion, RELEVANT_INDICES)