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

from DateTime import DateTime
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import IntDisplayList

from Products.ATContentTypes.types.criteria import registerCriterion
from Products.ATContentTypes.types.criteria import DATE_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.Permissions import ChangeTopics
from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.schemata import ATBaseCriterionSchema

DateOptions = IntDisplayList((
                    (     0, 'Now'      )
                  , (     1, '1 Day'    )
                  , (     2, '2 Days'   )
                  , (     5, '5 Days'   )
                  , (     7, '1 Week'   )
                  , (    14, '2 Weeks'  )
                  , (    31, '1 Month'  )
                  , (  31*3, '3 Months' )
                  , (  31*6, '6 Months' )
                  , (   365, '1 Year'   )
                  , ( 365*2, '2 Years'  )
    ))

CompareOperations = DisplayList((
                    ('min', 'min')
                  , ('max', 'max')
                  , ('within_day', 'within_day')
    ))

RangeOperations = DisplayList((
                    ('-', 'old')
                  , ('+', 'ahead')
    ))


ATDateCriteriaSchema = ATBaseCriterionSchema + Schema((
    IntegerField('value',
                required=1,
                mode="rw",
                accessor="Value",
                mutator="setValue",
                write_permission=ChangeTopics,
                default=None,
                vocabulary=DateOptions,
                widget=SelectionWidget(
                    label="Date",
                    label_msgid="label_date_criteria_value",
                    description="Reference date",
                    description_msgid="help_date_criteria_value",
                    i18n_domain="plone"),
                ),
    StringField('operation',
                required=1,
                mode="rw",
                default=None,
                write_permission=ChangeTopics,
                vocabulary=CompareOperations,
                enforceVocabulary=1,
                widget=SelectionWidget(
                    label="Operation name",
                    label_msgid="label_date_criteria_operation",
                    description="Operation applied to the values",
                    description_msgid="help_date_criteria_operation",
                    i18n_domain="plone"),
                ),
    StringField('dateRange',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                default=None,
                vocabulary=RangeOperations,
                enforceVocabulary=1,
                widget=SelectionWidget(
                    label="date range",
                    label_msgid="label_date_criteria_range",
                    description="Specify if the range is ahead of "
                    "the reference date or not.",
                    description_msgid="help_date_criteria_range",
                    i18n_domain="plone"),
                ),
    ))


class ATDateCriteria(ATBaseCriterion):
    """A date criteria"""


    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )

    security       = ClassSecurityInfo()
    schema         = ATDateCriteriaSchema
    meta_type      = 'ATFriendlyDateCriteria'
    archetype_name = 'Friendly Date Criteria'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'exact date value'

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        """Return a sequence of items to be used to build the catalog query.
        """
        if self.value is not None:
            field = self.Field()
            value = self.Value()

            # Negate the value for 'old' days
            if self.getDateRange() == '-':
                value = -value

            date = DateTime() + value

            operation = self.getOperation()
            if operation == 'within_day':
                range = ( date.earliestTime(), date.latestTime() )
                return ( ( field, {'query': range, 'range': 'min:max'} ), )
            else:
                return ( ( field, {'query': date, 'range': operation} ), )
        else:
            return ()

registerCriterion(ATDateCriteria, DATE_INDICES)
