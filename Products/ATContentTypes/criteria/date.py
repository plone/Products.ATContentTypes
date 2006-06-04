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

__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.criteria.ATDateCriteria'

from DateTime import DateTime
from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import IntegerField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import IntDisplayList

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import DATE_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

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
                    ('more', 'More than')
                  , ('less', 'Less than')
                  , ('within_day', 'On the day')
    ))

RangeOperations = DisplayList((
                    ('-', 'in the past')
                  , ('+', 'in the future')
    ))


ATDateCriteriaSchema = ATBaseCriterionSchema + Schema((
    StringField('operation',
                required=1,
                mode="rw",
                default=None,
                write_permission=ChangeTopics,
                vocabulary=CompareOperations,
                enforceVocabulary=1,
                widget=SelectionWidget(
                    label="More or less",
                    label_msgid="label_date_criteria_operation",
                    description="Select the date criteria operation.",
                    description_msgid="help_date_criteria_operation",
                    i18n_domain="atcontenttypes",
                    format="select"),
                ),
    IntegerField('value',
                required=1,
                mode="rw",
                accessor="Value",
                mutator="setValue",
                write_permission=ChangeTopics,
                default=None,
                vocabulary=DateOptions,
                widget=SelectionWidget(
                    label="Which day",
                    label_msgid="label_date_criteria_value",
                    description="Select the date criteria value.",
                    description_msgid="help_date_criteria_value",
                    i18n_domain="atcontenttypes"),
                ),
    StringField('dateRange',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                default=None,
                vocabulary=RangeOperations,
                enforceVocabulary=1,
                widget=SelectionWidget(
                    label="In the past or future",
                    label_msgid="label_date_criteria_range",
                    description="Select the date criteria range. Ignore this if you selected 'Now' above.",
                    description_msgid="help_date_criteria_range",
                    i18n_domain="atcontenttypes",
                    format="select"),
                ),
    ))


class ATDateCriteria(ATBaseCriterion):
    """A relative date criterion"""


    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )

    security       = ClassSecurityInfo()
    schema         = ATDateCriteriaSchema
    meta_type      = 'ATFriendlyDateCriteria'
    archetype_name = 'Friendly Date Criteria'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'Relative date'

    security.declareProtected(View, 'getCriteriaItems')
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
            current_date = DateTime()

            operation = self.getOperation()
            if operation == 'within_day':
                date_range = ( date.earliestTime(), date.latestTime() )
                return ( ( field, {'query': date_range, 'range': 'min:max'} ), )
            elif operation == 'more':
                if value != 0:
                    range_op = (self.getDateRange() == '-' and 'max') or 'min'
                    return ( ( field, {'query': date.earliestTime(), 'range': range_op} ), )
                else:
                    return ( ( field, {'query': date, 'range': 'min'} ), )
            elif operation == 'less':
                if value != 0:
                    date_range = (self.getDateRange() == '-' and
                                  (date.earliestTime(), current_date)
                                  ) or (current_date, date.latestTime())
                    return ( ( field, {'query': date_range, 'range': 'min:max'} ), )
                else:
                    return ( ( field, {'query': date, 'range': 'max'} ), )
        else:
            return ()

registerCriterion(ATDateCriteria, DATE_INDICES)
