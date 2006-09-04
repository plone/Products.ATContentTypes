##############################################################################
#
# ATContentTypes http://plone.org/products/atcontenttypes/
# Archetypes reimplementation of the CMF core types
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003-2006 AT Content Types development team
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

"""
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import IdWidget
from Products.Archetypes.atapi import StringWidget
from Products.ATContentTypes.permission import ChangeTopics

from Products.CMFPlone import PloneMessageFactory as _

###
# AT Base Criterion
###

ATBaseCriterionSchema = Schema((
    StringField('id',
                required=1,
                mode="r",
                default=None,
                write_permission=ChangeTopics,
                widget=IdWidget(
                    label=_(u'label_short_name', default=u'Short Name'),
                    description=_(u'help_shortname',
                                  default=u"Should not contain spaces, underscores or mixed case. "
                                           "Short Name is part of the item's web address."),
                    visible={'view' : 'invisible'}
                    ),
                ),
    StringField('field',
                required=1,
                mode="r",
                accessor="Field",
                write_permission=ChangeTopics,
                default=None,
                widget=StringWidget(
                    label=_(u'label_criteria_field_name', default=u'Field name'),
                    description=_(u'help_criteria_field_name',
                                  default=u"Should not contain spaces, underscores or mixed case. "
                                           "Short Name is part of the item's web address.")
                    ),
                ),
    ))
