#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
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
    archetype_name = 'Boolean Criterion'
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
