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
"""


"""
__author__  = ''
__docformat__ = 'restructuredtext'


from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import IdWidget
from Products.Archetypes.atapi import StringWidget
from Products.ATContentTypes.permission import ChangeTopics

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
                    label="Short Name",
                    label_msgid="label_short_name",
                    description=("Should not contain spaces, underscores or mixed case. "
                                 "Short Name is part of the item's web address."),
                    description_msgid="help_shortname",
                    visible={'view' : 'invisible'},
                    i18n_domain="plone"),
                ),
    StringField('field',
                required=1,
                mode="r",
                accessor="Field",
                write_permission=ChangeTopics,
                default=None,
                widget=StringWidget(
                    label="Field name",
                    label_msgid="label_criteria_field_name",
                    description=("Should not contain spaces, underscores or mixed case. "
                                 "Short Name is part of the item's web address."),
                    description_msgid="help_criteria_field_name",
                    i18n_domain="plone"),
                ),

    ))

